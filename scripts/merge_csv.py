import sys
import pandas as pd
import os

# Uso: python merge_csv.py output.csv input1.csv input2.csv ...

def merge_csvs(output_path, input_paths):
    dfs = []
    for p in input_paths:
        print(f"Leyendo {p}...")
        df = pd.read_csv(p)
        dfs.append(df)
    df_all = pd.concat(dfs, ignore_index=True)
    print(f"Escribiendo {output_path} con {len(df_all)} filas...")
    df_all.to_csv(output_path, index=False)
    print("¡Merge completado!")

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print("Uso: python merge_csv.py output.csv in1.csv in2.csv ...")
        sys.exit(1)
    output = args[0]
    inputs = args[1:]
    merge_csvs(output, inputs)