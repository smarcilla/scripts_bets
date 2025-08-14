python .\scripts\analyze_draw_value.py .\datos\EC\EC_merged.csv --outdir reports 


python .\scripts\backtest_rolling_windows.py .\datos\EC\EC_merged.csv .\simulaciones\EC_report_bloques_moviles.md


# Para otra liga sustituir E0 por el nombre de esa liga
python scripts\merge_csv.py datos\EC\EC_merged.csv datos\EC\EC_1516.csv datos\EC\EC_1617.csv datos\EC\EC_1718.csv datos\EC\EC_1819.csv datos\EC\EC_1920.csv datos\EC\EC_2021.csv datos\EC\EC_2122.csv datos\EC\EC_2223.csv datos\EC\EC_2324.csv datos\EC\EC_2425.csv

python scripts\merge_csv.py datos\EC\EC_merged.csv datos\EC\EC_1516.csv datos\EC\EC_1617.csv datos\EC\EC_1819.csv datos\EC\EC_1920.csv datos\EC\EC_2021.csv datos\EC\EC_2122.csv datos\EC\EC_2223.csv datos\EC\EC_2324.csv datos\EC\EC_2425.csv



