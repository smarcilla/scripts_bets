#!/usr/bin/env python3
# patterns_1x2.py

"""
Script para calcular patrones en cuotas 1X2 y tasa de empates por bucket.

Uso:
    python patterns_1x2.py merged.csv patterns_output.csv

Ejemplo:
    python patterns_1x2.py merged.csv patrones.csv
"""

import sys
import pandas as pd

def main():
    if len(sys.argv) != 3:
        print("Uso: python patterns_1x2.py merged.csv patterns_output.csv")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_csv = sys.argv[2]

    # 1) Leer datos
    df = pd.read_csv(input_csv)

    # 2) Filtrar columnas clave y limpiar
    df = df[['FTR', 'B365H', 'B365D', 'B365A']].dropna()

    # 3) Crear métricas derivadas
    df['spread_max_min'] = df[['B365H','B365D','B365A']].max(axis=1) - df[['B365H','B365D','B365A']].min(axis=1)
    df['ratio_HD']        = df['B365H'] / df['B365D']
    df['ratio_AD']        = df['B365A'] / df['B365D']
    df['ratio_1X']        = df['B365H'] / df['B365A']

    # 4) Bucket de cuota al 1 (B365H)
    bins   = [0,1.5,1.8,2.0,2.2,2.5,2.8,3.2,3.6,4.0,float('inf')]
    labels = ["<1.50","1.50-1.79","1.80-1.99","2.00-2.19","2.20-2.49",
              "2.50-2.79","2.80-3.19","3.20-3.59","3.60-3.99","≥4.00"]
    df['bucket_H'] = pd.cut(df['B365H'], bins=bins, labels=labels, right=False)

    # 5) Agrupar y calcular métricas
    grp = df.groupby('bucket_H').agg(
        total_partidos = ('FTR', 'count'),
        empates        = ('FTR', lambda x: (x=='D').sum()),
        avg_H          = ('B365H', 'mean'),
        avg_D          = ('B365D', 'mean'),
        avg_A          = ('B365A', 'mean'),
    )
    grp['draw_rate'] = grp['empates'] / grp['total_partidos']

    # 6) Guardar resultados
    grp.to_csv(output_csv)
    print(f"Patrones 1X2 exportados en '{output_csv}'.")

if __name__ == "__main__":
    main()
