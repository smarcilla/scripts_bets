#!/usr/bin/env python3
# prepare_value_bets.py

"""
Script para generar un CSV con las apuestas de valor y la columna 'ganancia'
necesaria para usar correlations.py.

Uso:
    python prepare_value_bets.py merged.csv value_bets.csv

Ejemplo:
    python prepare_value_bets.py merged.csv value_bets.csv
"""

import sys
import pandas as pd

def main():
    if len(sys.argv) != 3:
        print("Uso: python prepare_value_bets.py merged.csv value_bets.csv")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_csv = sys.argv[2]

    # 1) Leer el CSV fusionado
    df = pd.read_csv(input_csv)

    # 2) Filtrar columnas clave y eliminar filas con NaN
    df = df[['FTR', 'B365H', 'B365D', 'B365A']].dropna()

    # 3) Aplicar filtro de valor:
    #    - cuota 1 entre 2.00 y 3.59
    #    - cuota empate >= 3.00
    mask = (
        (df['B365H'] >= 2.00) &
        (df['B365H'] < 3.60) &
        (df['B365D'] >= 3.00)
    )
    df_val = df[mask].copy()

    # 4) Calcular la columna 'ganancia'
    #    Si FTR == 'D', ganancia = B365D - 1; si no, ganancia = -1
    df_val['ganancia'] = df_val.apply(
        lambda row: row['B365D'] - 1 if row['FTR'] == 'D' else -1,
        axis=1
    )

    # 5) Guardar el CSV de salida
    df_val.to_csv(output_csv, index=False)
    print(f"Generado '{output_csv}' con {len(df_val)} filas y columna 'ganancia'.")

if __name__ == "__main__":
    main()
