#!/usr/bin/env python3
# backtest_bank_md.py

"""
Backtest de estrategia de empates y salida de resultados a un fichero Markdown.

Uso:
    python backtest_bank_md.py merged.csv report.md

Ejemplo:
    python backtest_bank_md.py merged.csv backtest_report.md
"""

import sys
import pandas as pd

def simulate(df, initial_bank, stake, block_sizes):
    bank = initial_bank
    peak = bank
    max_drawdown = 0
    worst_skid = 0
    current_skid = 0
    banks = []

    for _, row in df.iterrows():
        # Calcula P&L: si empate, ganancia = cuotaX - 1; si no, -1
        pnl = (row['B365D'] - 1) if row['FTR'] == 'D' else -1
        pnl *= stake
        bank += pnl
        banks.append(bank)

        # Drawdown
        if bank > peak:
            peak = bank
        drawdown = peak - bank
        if drawdown > max_drawdown:
            max_drawdown = drawdown

        # Racha de pérdidas
        if pnl < 0:
            current_skid += 1
            worst_skid = max(worst_skid, current_skid)
        else:
            current_skid = 0

    # Resultados por bloque
    block_results = []
    for size in block_sizes:
        if size <= len(banks):
            end_bank = banks[size - 1]
        else:
            end_bank = banks[-1]
        block_results.append((size, end_bank))

    final_bank = banks[-1] if banks else initial_bank
    return max_drawdown, worst_skid, block_results, final_bank

def main():
    if len(sys.argv) != 3:
        print("Uso: python backtest_bank_md.py merged.csv report.md")
        sys.exit(1)

    merged_csv = sys.argv[1]
    report_md  = sys.argv[2]

    # 1) Leer y filtrar estrategia óptima
    df = pd.read_csv(merged_csv)
    df = df[['FTR','B365H','B365D','B365A']].dropna()
    df = df[(df['B365H'] >= 2.00) & (df['B365H'] < 3.60) & (df['B365D'] >= 3.15)].reset_index(drop=True)

    # 2) Parámetros de simulación
    initial_bank = 100.0
    stake = 1.0
    block_sizes = [10, 50, 100, 200]

    # 3) Ejecutar simulación
    max_dd, worst_skid, block_results, final_bank = simulate(df, initial_bank, stake, block_sizes)

    # 4) Construir reporte en Markdown
    lines = []
    lines.append("# Backtest Estrategia Empate")
    lines.append("")
    lines.append(f"- **Bank inicial:** €{initial_bank:.2f}")
    lines.append(f"- **Stake por pick:** €{stake:.2f}")
    lines.append(f"- **Total picks:** {len(df)}")
    lines.append(f"- **Racha máxima de pérdidas seguidas:** {worst_skid}")
    lines.append(f"- **Máximo drawdown:** €{max_dd:.2f}")
    lines.append(f"- **Bank final:** €{final_bank:.2f}")
    if final_bank <= 0:
        status = "⚠️ Quiebra"
    elif final_bank < initial_bank * 0.4:
        status = "⚠️ Bank < 40% inicial"
    else:
        status = "✅ Bank > 40% inicial"
    lines.append(f"- **Estado final:** {status}")
    lines.append("")
    lines.append("## Resultados por bloques")
    lines.append("")
    lines.append("| Bloque (picks) | Bank final (€) | Ganancia/Perdida (€) |")
    lines.append("|---------------:|---------------:|---------------------:|")
    for size, bk in block_results:
        diff = bk - initial_bank
        lines.append(f"| {size:>14} | {bk:>13.2f} | {diff:>21.2f} |")

    # 5) Guardar el fichero Markdown
    with open(report_md, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    print(f"Reporte Markdown generado en '{report_md}'")

if __name__ == "__main__":
    main()
