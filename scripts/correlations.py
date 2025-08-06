#!/usr/bin/env python3
# correlations.py

"""
Script para calcular correlaciones Pearson entre variables de cuota y beneficio.

Uso:
    python correlations.py value_bets.csv corr_output.csv

Ejemplo:
    python correlations.py apuestas_valor.csv correlaciones.csv
"""

import sys
import pandas as pd

def pearson_corr(x, y):
    xm = x.mean(); ym = y.mean()
    num = ((x - xm) * (y - ym)).sum()
    den = ((x - xm)**2).sum()**0.5 * ((y - ym)**2).sum()**0.5
    return num / den if den != 0 else 0

def main():
    if len(sys.argv) != 3:
        print("Uso: python correlations.py value_bets.csv corr_output.csv")
        sys.exit(1)

    input_csv  = sys.argv[1]
    output_csv = sys.argv[2]

    # 1) Leer datos
    df = pd.read_csv(input_csv)

    # 2) Asegurar que tenemos la columna 'ganancia'
    if 'ganancia' not in df.columns:
        print("ERROR: tu CSV debe incluir una columna 'ganancia' con el P&L de cada apuesta.")
        sys.exit(1)

    # 3) Generar métricas derivadas si no existen
    if 'spread_max_min' not in df.columns:
        df['spread_max_min'] = df[['B365H','B365D','B365A']].max(axis=1) - df[['B365H','B365D','B365A']].min(axis=1)
    if 'ratio_HD' not in df.columns:
        df['ratio_HD'] = df['B365H'] / df['B365D']
    if 'ratio_AD' not in df.columns:
        df['ratio_AD'] = df['B365A'] / df['B365D']
    if 'ratio_1X' not in df.columns:
        df['ratio_1X'] = df['B365H'] / df['B365A']

    # 4) Seleccionar columnas numéricas relevantes
    features = ['B365H','B365D','B365A','spread_max_min','ratio_HD','ratio_AD','ratio_1X']
    results = []

    # 5) Calcular correlación Pearson de cada feature vs ganancia
    for f in features:
        corr = pearson_corr(df['ganancia'], df[f])
        results.append((f, corr))

    # 6) Crear DataFrame y ordenar
    corr_df = pd.DataFrame(results, columns=['feature','pearson_corr'])
    corr_df = corr_df.sort_values('pearson_corr', ascending=False)

    # 7) Exportar
    corr_df.to_csv(output_csv, index=False)
    print(f"Correlaciones exportadas en '{output_csv}'.")

if __name__ == "__main__":
    main()
