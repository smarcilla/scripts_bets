python .\scripts\analyze_draw_value.py .\datos\I1\I1_merged.csv --outdir reports 


python .\scripts\backtest_rolling_windows.py .\datos\I1\I1_merged.csv .\simulaciones\I1_report_bloques_moviles_5.md


# Para otra liga sustituir E0 por el nombre de esa liga
python scripts\merge_csv.py datos\I1\I1_merged.csv datos\I1\I1_1516.csv datos\I1\I1_1617.csv datos\I1\I1_1718.csv datos\I1\I1_1819.csv datos\I1\I1_1920.csv datos\I1\I1_2021.csv datos\I1\I1_2122.csv datos\I1\I1_2223.csv datos\I1\I1_2324.csv datos\I1\I1_2425.csv