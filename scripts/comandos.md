python .\scripts\analyze_draw_value.py .\datos\SP1\SP1_merged.csv .\datos\F2\F2_merged.csv `
  --outdir reports 


python .\scripts\backtest_rolling_windows.py .\datos\E0\E0_merged.csv .\simulaciones\E0_report_bloques_moviles_v2.md


# Para otra liga sustituir E0 por el nombre de esa liga
python scripts\merge_csv.py datos\E0\E0_merged.csv datos\E0\E0_1516.csv datos\E0\E0_1617.csv datos\E0\E0_1718.csv datos\E0\E0_1819.csv datos\E0\E0_1920.csv datos\E0\E0_2021.csv datos\E0\E0_2122.csv datos\E0\E0_2223.csv datos\E0\E0_2324.csv datos\E0\E0_2425.csv