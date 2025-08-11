#!/usr/bin/env python3
# backtest_rolling_windows.py

"""
Backtest con ventanas móviles de N picks: calcula yield por ventana y genera un informe en Markdown.

Uso:
    python backtest_rolling_windows.py datos/merged.csv simulaciones/report_bloques_moviles.md
"""

import sys
import pandas as pd
import numpy as np

def load_and_filter(path):
    # Lee merged.csv y aplica el filtro óptimo
    df = pd.read_csv(path)
    df = df[['FTR','B365H','B365D','B365A']].dropna()
    return df[
        (df['B365H'] >= 2.5) &
        (df['B365H'] < 3) &
        (df['B365D'] >= 3.2)
    ].reset_index(drop=True)

def compute_pnls(df, stake=1.0):
    # Devuelve array de P&L por pick: +(cuota-1) si empate, -1 si no
    pnl = np.where(df['FTR']=='D', df['B365D'] - 1, -1)
    return pnl * stake

def rolling_yields(pnls, window):
    # Genera yields con ventanas móviles de tamaño `window`
    L = len(pnls)
    if L < window:
        return np.array([])
    # usar convolución para sumar ventanas
    cumsum = np.concatenate([[0], np.cumsum(pnls)])
    sums = cumsum[window:] - cumsum[:-window]
    return sums / window

def summarize(yields):
    # Resume estadísticas de un array de yields
    return {
        'n_windows':      int(len(yields)),
        'mean_yield':     float(np.mean(yields)) if len(yields)>0 else np.nan,
        'median_yield':   float(np.median(yields)) if len(yields)>0 else np.nan,
        'max_yield':      float(np.max(yields)) if len(yields)>0 else np.nan,
        'min_yield':      float(np.min(yields)) if len(yields)>0 else np.nan,
    }

def main():
    if len(sys.argv)!=3:
        print("Uso: python backtest_rolling_windows.py merged.csv report_bloques_moviles.md")
        sys.exit(1)

    merged_csv = sys.argv[1]
    report_md  = sys.argv[2]

    # 1) Carga y filtro
    df   = load_and_filter(merged_csv)
    pnls = compute_pnls(df, stake=1.0)

    # 2) Tamaños de ventana a testear
    window_sizes = [10, 25, 50, 75, 100, 125, 150, 175, 200, 250, 300, 400, 500]

    # 3) Calcular estadísticas por ventana
    stats = {}
    for w in window_sizes:
        ys = rolling_yields(pnls, w)
        stats[w] = summarize(ys)

    # 4) Generar Markdown
    lines = []
    lines.append("# Backtest con Ventanas Móviles")
    lines.append("")
    lines.append(f"- **Total picks filtrados:** {len(pnls)}")
    lines.append("")
    lines.append("## Estadísticas por Tamaño de Ventana")
    lines.append("")
    lines.append("| Ventana (picks) | Nº ventanas | Yield medio (%) | Yield mediano (%) | Yield máximo (%) | Yield mínimo (%) |")
    lines.append("|---------------:|------------:|----------------:|------------------:|-----------------:|-----------------:|")

    for w in window_sizes:
        s = stats[w]
        lines.append(
            f"| {w:>15} "
            f"| {s['n_windows']:>12} "
            f"| {s['mean_yield']*100:>15.2f} "
            f"| {s['median_yield']*100:>17.2f} "
            f"| {s['max_yield']*100:>15.2f} "
            f"| {s['min_yield']*100:>15.2f} |"
        )

    # 5) Guardar reporte
    with open(report_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Informe generado en Markdown: {report_md}")

if __name__=="__main__":
    main()
