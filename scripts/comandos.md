python .\scripts\analyze_draw_value.py .\datos\SC0\SC0_merged.csv --outdir reports 


python .\scripts\backtest_rolling_windows.py .\datos\SC0\SC0_merged.csv .\simulaciones\SC0_report_bloques_moviles.md


# Para otra liga sustituir E0 por el nombre de esa liga
python scripts\merge_csv.py datos\SC0\SC0_merged.csv datos\SC0\SC0_1516.csv datos\SC0\SC0_1617.csv datos\SC0\SC0_1718.csv datos\SC0\SC0_1819.csv datos\SC0\SC0_1920.csv datos\SC0\SC0_2021.csv datos\SC0\SC0_2122.csv datos\SC0\SC0_2223.csv datos\SC0\SC0_2324.csv datos\SC0\SC0_2425.csv



