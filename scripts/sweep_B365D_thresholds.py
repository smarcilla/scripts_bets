#!/usr/bin/env python3
# sweep_B365D_thresholds.py

"""
Script para barrer umbrales de cuota al empate y comparar yield.

Uso:
    python sweep_B365D_thresholds.py merged.csv resultados_thresholds.csv

Genera un CSV con columnas:
    min_B365D, n_apuestas, n_aciertos, beneficio, yield
"""

import sys
import numpy as np
import pandas as pd

def main():
    if len(sys.argv) != 3:
        print("Uso: python sweep_B365D_thresholds.py merged.csv resultados.csv")
        sys.exit(1)

    input_csv  = sys.argv[1]
    output_csv = sys.argv[2]

    # 1) Leer datos
    df = pd.read_csv(input_csv)

    # 2) Filtro inicial cuota al 1
    df = df[['FTR', 'B365H', 'B365D', 'B365A']].dropna()
    df = df[(df['B365H'] >= 2.00) & (df['B365H'] < 3.60)]

    # 3) Definir rango de umbrales para B365D
    thresholds = np.arange(3.00, 4.05, 0.05)

    results = []
    for thr in thresholds:
        sub = df[df['B365D'] >= thr].copy()
        n = len(sub)
        if n == 0:
            continue

        # Simular P&L
        sub['ganancia'] = sub.apply(
            lambda row: row['B365D'] - 1 if row['FTR'] == 'D' else -1,
            axis=1
        )
        beneficio = sub['ganancia'].sum()
        aciertos  = (sub['FTR'] == 'D').sum()
        yld       = beneficio / n

        results.append({
            'min_B365D': round(thr,2),
            'n_apuestas': n,
            'n_aciertos': int(aciertos),
            'beneficio': round(beneficio,2),
            'yield': round(yld,4)
        })

    # 4) Exportar resultados
    res_df = pd.DataFrame(results)
    res_df.to_csv(output_csv, index=False)
    print(f"Umbrales testeados: {len(results)}. Resultados guardados en '{output_csv}'.")

if __name__ == "__main__":
    main()
