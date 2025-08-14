#!/usr/bin/env python3
# backtest_rolling_windows_posrate.py
#
# Modificación de backtest_rolling_windows.py para incluir
# el porcentaje de ventanas con YIELD positivo.

"""
Backtest con ventanas móviles de N picks: calcula yield por ventana y genera un informe en Markdown.

Uso:
    python backtest_rolling_windows_posrate.py datos/merged.csv simulaciones/report_bloques_moviles.md
"""

import sys
import pandas as pd
import numpy as np


def load_and_filter(path: str) -> pd.DataFrame:
    """
    Lee el CSV merged y aplica el filtro del sistema:
      - Usamos columnas: FTR, B365H, B365D, B365A
      - Filtro: 2.0 <= B365H <= 3.0 y B365D >= 3.1
    """
    df = pd.read_csv(path)
    df = df[["FTR", "B365H", "B365D", "B365A"]].dropna()
    mask = (df["B365H"] >= 2.5) & (df["B365H"] <= 5) & (df["B365D"] >= 3.6)
    return df.loc[mask].reset_index(drop=True)


def compute_pnls(df: pd.DataFrame, stake: float = 1.0) -> np.ndarray:
    """
    P&L por pick:
      - Si FTR == 'D' (empate): ganancia = (B365D - 1) * stake
      - Si no: pérdida = -1 * stake
    Devuelve un array de floats con el P&L por pick.
    """
    pnl = np.where(df["FTR"] == "D", df["B365D"] - 1.0, -1.0)
    return pnl * stake


def rolling_yields(pnls: np.ndarray, window: int) -> np.ndarray:
    """
    Yield por ventana móvil de tamaño `window`.
    Definición de yield de ventana: (suma P&L de la ventana) / window,
    que equivale a P&L medio por pick dentro de la ventana.
    """
    L = len(pnls)
    if L < window:
        return np.array([])
    cumsum = np.concatenate([[0.0], np.cumsum(pnls)])
    sums = cumsum[window:] - cumsum[:-window]
    return sums / window


def summarize(yields: np.ndarray) -> dict:
    """
    Resumen estadístico de los yields por ventana, incluyendo:
      - n_windows
      - mean_yield, median_yield, max_yield, min_yield
      - pct_pos_windows: % de ventanas con yield > 0
    """
    n = int(len(yields))
    if n == 0:
        return {
            "n_windows": 0,
            "mean_yield": np.nan,
            "median_yield": np.nan,
            "max_yield": np.nan,
            "min_yield": np.nan,
            "pct_pos_windows": np.nan,
        }
    positive = float(np.sum(yields > 0.0))
    return {
        "n_windows": n,
        "mean_yield": float(np.mean(yields)),
        "median_yield": float(np.median(yields)),
        "max_yield": float(np.max(yields)),
        "min_yield": float(np.min(yields)),
        "pct_pos_windows": float(100.0 * positive / n),
    }


def main():
    if len(sys.argv) != 3:
        print("Uso: python backtest_rolling_windows_posrate.py merged.csv report_bloques_moviles.md")
        sys.exit(1)

    merged_csv = sys.argv[1]
    report_md = sys.argv[2]

    # 1) Carga y filtro del dataset según el sistema
    df = load_and_filter(merged_csv)
    pnls = compute_pnls(df, stake=1.0)

    # 2) Tamaños de ventana a evaluar
    window_sizes = [10, 25, 50, 75, 100, 125, 150, 175, 200, 250, 300, 400, 500]

    # 3) Estadísticas por tamaño de ventana
    stats = {}
    for w in window_sizes:
        ys = rolling_yields(pnls, w)
        stats[w] = summarize(ys)

    # 4) Generar informe en Markdown
    lines = []
    lines.append("# Backtest con Ventanas Móviles")
    lines.append("")
    lines.append(f"- **Total picks filtrados:** {len(pnls)}")
    lines.append("")
    lines.append("## Estadísticas por Tamaño de Ventana")
    lines.append("")
    lines.append("| Ventana (picks) | Nº ventanas | Yield medio (%) | Yield mediano (%) | Yield máximo (%) | Yield mínimo (%) | Ventanas > 0 (%) |")
    lines.append("|---------------:|------------:|----------------:|------------------:|-----------------:|-----------------:|-----------------:|")

    def fmt_pct(x: float) -> str:
        # Convierte un valor fraccional (e.g. 0.031) a porcentaje con 2 decimales, manejando NaN
        return "nan" if not (x == x) else f"{x * 100.0:0.2f}"

    for w in window_sizes:
        s = stats[w]
        line = (
            f"| {w:>15} "
            f"| {s['n_windows']:>12} "
            f"| {fmt_pct(s['mean_yield']):>15} "
            f"| {fmt_pct(s['median_yield']):>17} "
            f"| {fmt_pct(s['max_yield']):>15} "
            f"| {fmt_pct(s['min_yield']):>15} "
            f"| {('nan' if not (s['pct_pos_windows'] == s['pct_pos_windows']) else f'{s['pct_pos_windows']:0.2f}'):>15} |"
        )
        lines.append(line)

    # 5) Guardar reporte
    with open(report_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Informe generado en Markdown: {report_md}")


if __name__ == "__main__":
    main()
