#!/usr/bin/env python3
# backtest_chunks_md.py

"""
Backtest por bloques de N picks: calcula yield por bloque y genera un informe en Markdown.

Uso:
    python backtest_chunks_md.py merged.csv report.md
"""

import sys
import pandas as pd
import numpy as np

def load_and_filter(path):
    # Lee merged.csv y aplica el filtro óptimo
    df = pd.read_csv(path)
    df = df[['FTR','B365H','B365D','B365A']].dropna()
    return df[
        (df['B365H'] >= 2.00) &
        (df['B365H'] < 3.60) &
        (df['B365D'] >= 3.15)
    ].reset_index(drop=True)

def compute_pnls(df, stake=1.0):
    # Devuelve array de P&L por pick: +(cuota-1) si empate, -1 si no
    pnl = np.where(df['FTR']=='D', df['B365D'] - 1, -1)
    return pnl * stake

def chunk_yields(pnls, block_size):
    # Divide pnls en bloques enteros de block_size y calcula yield por bloque
    n_blocks = len(pnls) // block_size
    yields = []
    for i in range(n_blocks):
        chunk = pnls[i*block_size:(i+1)*block_size]
        yields.append(chunk.sum() / block_size)
    return np.array(yields)

def summarize(yields):
    # Resume estadísticas de un array de yields
    return {
        'n_blocks': len(yields),
        'mean_yield': np.mean(yields) if len(yields)>0 else np.nan,
        'median_yield': np.median(yields) if len(yields)>0 else np.nan,
        'max_yield': np.max(yields) if len(yields)>0 else np.nan,
        'min_yield': np.min(yields) if len(yields)>0 else np.nan,
    }

def main():
    if len(sys.argv)!=3:
        print("Uso: python backtest_chunks_md.py merged.csv report.md")
        sys.exit(1)

    merged_csv = sys.argv[1]
    report_md  = sys.argv[2]

    # Carga y filtrado
    df   = load_and_filter(merged_csv)
    pnls = compute_pnls(df, stake=1.0)

    block_sizes = [10, 50, 100, 200]
    summary = {}

    # Calcular stats por bloque
    for size in block_sizes:
        ys = chunk_yields(pnls, size)
        stats = summarize(ys)
        summary[size] = stats

    # Construir Markdown
    lines = []
    lines.append("# Backtest por Bloques de Picks")
    lines.append("")
    lines.append(f"- **Total picks filtrados:** {len(pnls)}")
    lines.append("")
    lines.append("## Estadísticas por Tamaño de Bloque")
    lines.append("")
    lines.append("| Bloque (picks) | Nº bloques | Yield medio (%) | Yield mediano (%) | Yield máximo (%) | Yield mínimo (%) |")
    lines.append("|--------------:|-----------:|----------------:|------------------:|-----------------:|-----------------:|")

    for size in block_sizes:
        stats = summary[size]
        lines.append(
            f"| {size:>14} "
            f"| {stats['n_blocks']:>10} "
            f"| {stats['mean_yield']*100:>15.2f} "
            f"| {stats['median_yield']*100:>17.2f} "
            f"| {stats['max_yield']*100:>15.2f} "
            f"| {stats['min_yield']*100:>15.2f} |"
        )

    # Guardar Markdown
    with open(report_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Informe generado en Markdown: {report_md}")

if __name__=="__main__":
    main()

