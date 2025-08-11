#!/usr/bin/env python3
"""
Analyze draw % and value (EV) by odds ranges for football leagues.

Inputs: one or more CSV files with match results and odds.
Outputs: markdown/CSV summaries per file with %draw and EV by draw-odds and home-odds.

Definition of value (EV) for DRAW market: EV = p_draw * avg_draw_odds - 1
  where p_draw = draws / n in a given odds bin.

IMPORTANT FIX (2025-08-11):
- When grouping by HOME-odds bins, we STILL compute EV with the DRAW odds.
  The previous version incorrectly used the home odds in that table.

The script auto-detects:
  - Result column (FTR-like) or infers from goals (FTHG, FTAG)
  - Draw odds (prefers b365d, else any numeric *draw*/*b365*/*pin*)
  - Home odds (prefers b365h, else any numeric *home*/*b365*/*pin*)

You can customize odds bins via CLI flags (see --help).

Example
-------
python analyze_draw_value.py F2_merged.csv SP1_merged.csv \
  --outdir reports \
  --draw-bins "0,2.25,2.5,2.75,3.0,3.25,3.5,4.0,5.0,6.0,inf" \
  --home-bins "0,1.4,1.6,1.8,2.0,2.25,2.5,3.0,4.0,5.0,inf" \
  --min-n 30

This will create, per CSV:
  reports/<name>_overview.md
  reports/<name>_by_draw_odds.csv
  reports/<name>_by_home_odds.csv  (grouped by home-odds but EV uses draw odds)
  reports/<name>_summary.md
  and an aggregated _combined_summary.md if multiple files are processed.
"""

from __future__ import annotations
import argparse
import math
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

# ----------------------------- Utilities -----------------------------

PREF_RESULT_COLS = [
    "ftr", "result", "res", "full_time_result", "ft_result", "outcome"
]
PREF_HOME_ODDS = [
    "b365h", "home_odds", "odds_home", "odd_h", "odds_h"
]
PREF_DRAW_ODDS = [
    "b365d", "draw_odds", "odds_draw", "odd_d", "odds_d"
]
GOALS_HOME_CAND = ["fthg", "home_goals", "goals_home", "home_ft_goals", "hg"]
GOALS_AWAY_CAND = ["ftag", "away_goals", "goals_away", "away_ft_goals", "ag"]

DEFAULT_DRAW_BINS = [0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 4.0, 5.0, 6.0, math.inf]
DEFAULT_HOME_BINS = [0, 1.4, 1.6, 1.8, 2.0, 2.25, 2.5, 3.0, 4.0, 5.0, math.inf]


def norm_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def detect_result_col(df: pd.DataFrame) -> Optional[str]:
    for c in PREF_RESULT_COLS:
        if c in df.columns:
            vals = df[c].dropna().astype(str).str.upper().unique().tolist()
            if any(v in ["H", "D", "A", "HOME", "DRAW", "AWAY", "1", "X", "2"] for v in vals):
                return c
    gh = next((c for c in GOALS_HOME_CAND if c in df.columns), None)
    ga = next((c for c in GOALS_AWAY_CAND if c in df.columns), None)
    if gh and ga:
        res = np.where(df[gh] > df[ga], "H", np.where(df[gh] < df[ga], "A", "D"))
        df["__ftr_inferred__"] = res
        return "__ftr_inferred__"
    return None


def detect_odds_col(df: pd.DataFrame, priority: List[str], keywords: Tuple[str, ...]) -> Optional[str]:
    for c in priority:
        if c in df.columns and pd.api.types.is_numeric_dtype(df[c]):
            return c
    for c in df.columns:
        if pd.api.types.is_numeric_dtype(df[c]) and any(k in c for k in keywords):
            return c
    return None


def to_draw_flag(x) -> float:
    x = str(x).upper()
    if x in ["D", "DRAW", "X"]:
        return 1.0
    if x in ["H", "HOME", "1", "A", "AWAY", "2"]:
        return 0.0
    return float("nan")


def parse_bins(s: Optional[str], defaults: List[float]) -> List[float]:
    if s is None:
        return defaults
    # Accept empty/whitespace-only strings as "use defaults"
    if isinstance(s, str) and not s.strip():
        return defaults
    parts = [p.strip().lower() for p in s.split(",") if p.strip()]
    if not parts:
        return defaults
    out = []
    for p in parts:
        if p in {"inf", "+inf", "infinity"}:
            out.append(math.inf)
        else:
            out.append(float(p))
    if not out:
        return defaults
    if out[0] > 0:
        out = [0.0] + out
    if out[-1] != math.inf:
        out = out + [math.inf]
    return out


def labels_from_bins(bins: List[float]) -> List[str]:
    labels = []
    for i in range(len(bins) - 1):
        lo, hi = bins[i], bins[i + 1]
        if lo == 0 and hi != math.inf:
            labels.append(f"≤{hi:.2f}")
        elif hi == math.inf:
            labels.append(">" + ("{:.2f}".format(lo)))
        else:
            labels.append(f"{lo:.2f}–{hi:.2f}")
    return labels


def group_by_draw_bins(df: pd.DataFrame, draw_col: str, bins: List[float], min_n: int) -> pd.DataFrame:
    """Group by draw-odds bins and compute EV for the draw market."""
    tmp = df.dropna(subset=[draw_col, "is_draw"]).copy()
    labels = labels_from_bins(bins)
    tmp["bin"] = pd.cut(tmp[draw_col], bins=bins, labels=labels, include_lowest=True, right=True)
    g = tmp.groupby("bin", observed=True).agg(
        n=("is_draw", "size"),
        draws=("is_draw", "sum"),
        prob_draw=("is_draw", "mean"),
        avg_draw_odds=(draw_col, "mean"),
    ).reset_index()
    g["draw_rate_%"] = (g["prob_draw"] * 100).round(2)
    g["ev_est"] = g["prob_draw"] * g["avg_draw_odds"] - 1
    g["avg_draw_odds"] = g["avg_draw_odds"].round(3)
    g["ev_est"] = g["ev_est"].round(4)
    # Wilson CI for prob
    z = 1.96
    p = g["prob_draw"].astype(float)
    n = g["n"].astype(float)
    denom = 1 + z**2 / n.replace(0, np.nan)
    center = (p + z**2 / (2 * n)) / denom
    margin = (z * np.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)) / denom
    g["prob_low_%"], g["prob_high_%"] = (center - margin) * 100, (center + margin) * 100
    g["prob_low_%"] = g["prob_low_%"].round(2)
    g["prob_high_%"] = g["prob_high_%"].round(2)
    g["enough_n"] = g["n"] >= min_n
    return g[["bin", "n", "draws", "draw_rate_%", "prob_low_%", "prob_high_%", "avg_draw_odds", "ev_est", "enough_n"]]


def group_by_home_bins_draw_ev(df: pd.DataFrame, home_col: str, draw_col: str, bins: List[float], min_n: int) -> pd.DataFrame:
    """Group by HOME-odds bins but compute EV using the DRAW odds."""
    tmp = df.dropna(subset=[home_col, draw_col, "is_draw"]).copy()
    labels = labels_from_bins(bins)
    tmp["bin"] = pd.cut(tmp[home_col], bins=bins, labels=labels, include_lowest=True, right=True)
    g = tmp.groupby("bin", observed=True).agg(
        n=("is_draw", "size"),
        draws=("is_draw", "sum"),
        prob_draw=("is_draw", "mean"),
        avg_draw_odds=(draw_col, "mean"),  # NOTE: draw odds, not home odds
        avg_home_odds=(home_col, "mean"),  # informative only
    ).reset_index()
    g["draw_rate_%"] = (g["prob_draw"] * 100).round(2)
    g["ev_est"] = g["prob_draw"] * g["avg_draw_odds"] - 1
    g["avg_draw_odds"] = g["avg_draw_odds"].round(3)
    g["avg_home_odds"] = g["avg_home_odds"].round(3)
    g["ev_est"] = g["ev_est"].round(4)
    # Wilson CI
    z = 1.96
    p = g["prob_draw"].astype(float)
    n = g["n"].astype(float)
    denom = 1 + z**2 / n.replace(0, np.nan)
    center = (p + z**2 / (2 * n)) / denom
    margin = (z * np.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)) / denom
    g["prob_low_%"], g["prob_high_%"] = (center - margin) * 100, (center + margin) * 100
    g["prob_low_%"] = g["prob_low_%"].round(2)
    g["prob_high_%"] = g["prob_high_%"].round(2)
    g["enough_n"] = g["n"] >= min_n
    return g[["bin", "n", "draws", "draw_rate_%", "prob_low_%", "prob_high_%", "avg_home_odds", "avg_draw_odds", "ev_est", "enough_n"]]


# ----------------------------- Main analysis -----------------------------

def analyze_file(path: Path, draw_bins: List[float], home_bins: List[float], outdir: Path, min_n: int):
    name = path.stem
    df = pd.read_csv(path)
    df = norm_cols(df)

    # detect columns
    res_col = detect_result_col(df)
    if not res_col:
        raise ValueError(f"[{name}] No result column found or inferrable from goals")

    draw_col = detect_odds_col(df, PREF_DRAW_ODDS, ("draw", "b365", "pin", "odd"))
    home_col = detect_odds_col(df, PREF_HOME_ODDS, ("home", "b365", "pin", "odd", "1"))

    if not draw_col:
        raise ValueError(f"[{name}] No draw-odds column detected; cannot compute EV for draws.")

    # flag draw
    df["is_draw"] = df[res_col].apply(to_draw_flag).astype(float)
    df = df.dropna(subset=["is_draw"]).copy()

    # overview
    overview = pd.DataFrame({
        "metric": ["file", "rows", "%draw_global", "result_col", "draw_odds_col", "home_odds_col"],
        "value": [name, len(df), round(df["is_draw"].mean() * 100, 2), res_col, draw_col, home_col],
    })

    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / f"{name}_overview.md").write_text(overview.to_markdown(index=False), encoding="utf-8")

    # grouped by bins
    by_draw = group_by_draw_bins(df, draw_col, draw_bins, min_n)
    by_draw.to_csv(outdir / f"{name}_by_draw_odds.csv", index=False)

    by_home = pd.DataFrame()
    if home_col:
        by_home = group_by_home_bins_draw_ev(df, home_col, draw_col, home_bins, min_n)
        by_home.to_csv(outdir / f"{name}_by_home_odds.csv", index=False)

    # summary markdown with top bins by EV (only bins with enough_n)
    lines = [f"# Summary: {name}", "", "Parameters:", f"- min_n: {min_n}", f"- draw_bins: {draw_bins}", f"- home_bins: {home_bins}", ""]

    lines.append("## Top bins by EV (Draw odds bins, EV uses draw odds)")
    topd = by_draw[by_draw["enough_n"]].sort_values("ev_est", ascending=False).head(5)
    lines.append(topd.to_markdown(index=False))
    lines.append("")

    lines.append("## Top bins by EV (Home odds bins, EV uses draw odds)")
    if not by_home.empty:
        toph = by_home[by_home["enough_n"]].sort_values("ev_est", ascending=False).head(5)
        lines.append(toph.to_markdown(index=False))
    else:
        lines.append("(No home-odds column detected)")

    (outdir / f"{name}_summary.md").write_text("\n".join(lines), encoding="utf-8")

    return overview, by_draw, by_home


def main():
    ap = argparse.ArgumentParser(description="Analyze draw % and value by odds ranges.")
    ap.add_argument("files", nargs="+", help="CSV files to analyze")
    ap.add_argument("--outdir", default="reports", help="Output directory")
    ap.add_argument("--draw-bins", default=None, help="Comma-separated edges for draw odds (e.g., '0,2.8,3.2,4,inf')")
    ap.add_argument("--home-bins", default=None, help="Comma-separated edges for home odds")
    ap.add_argument("--min-n", type=int, default=30, help="Minimum samples per bin to consider it reliable")
    args = ap.parse_args()

    draw_bins = parse_bins(args.draw_bins, DEFAULT_DRAW_BINS)
    home_bins = parse_bins(args.home_bins, DEFAULT_HOME_BINS)

    outdir = Path(args.outdir)

    # aggregate summary across files
    combined_lines = ["# Combined summary (top EV bins per file)", ""]

    for f in args.files:
        path = Path(f)
        if not path.exists():
            print(f"[WARN] File not found: {path}")
            continue
        try:
            overview, by_draw, by_home = analyze_file(path, draw_bins, home_bins, outdir, args.min_n)
            name = path.stem
            combined_lines.append(f"## {name}")
            topd = by_draw[by_draw["enough_n"]].sort_values("ev_est", ascending=False).head(3)
            combined_lines.append("### Draw odds (EV uses draw odds)")
            combined_lines.append(topd.to_markdown(index=False))
            if not by_home.empty:
                toph = by_home[by_home["enough_n"]].sort_values("ev_est", ascending=False).head(3)
                combined_lines.append("### Home odds (grouped by home, EV uses draw odds)")
                combined_lines.append(toph.to_markdown(index=False))
            combined_lines.append("")
        except Exception as e:
            print(f"[ERROR] {path.name}: {e}")

    (outdir / "_combined_summary.md").write_text("\n".join(combined_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
