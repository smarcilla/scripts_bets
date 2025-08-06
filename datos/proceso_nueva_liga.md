**Resumen del modelo actual**

* **Filtro principal:**

  * **Cuota al 1 (B365H)** entre **2.00 y 3.59**
  * **Cuota al empate (B365D)** ≥ **3.15**
* **Stake:** 1 € por pick
* **P\&L por pick:**

  * Si el partido acaba empate → ganancia = B365D − 1
  * Si no → pérdida = −1
* **Métricas clave calculadas:**

  * **Yield global** (beneficio total / nº de picks)
  * **Backtest por bloques fijos** (10, 50, 100, 200 picks) → media, mediana, máximo, mínimo
  * **Backtest con ventanas móviles** (rolling windows de 10, 25, 50, …, 500 picks) → media, mediana, máximo, mínimo
  * **Hit-rate**: 32.7 % de aciertos (empates) vs 67.3 % de fallos

---

## Proceso completo para repetir en otra liga

1. **Recolectar datos**

   * Descarga CSVs de partidos de la nueva liga (una temporada o varias). Deben incluir, al menos:

     ```text
     FTR  (Full Time Result: H/D/A)
     B365H (Home win odds)
     B365D (Draw odds)
     B365A (Away win odds)
     ```
2. **Fusionar CSVs**

   * Usar `merge_csv.py` (o su versión Python):

     ```bash
     python merge_csv.py merged_ligaX.csv ligaX_1920.csv ligaX_2021.csv …
     ```
3. **Aplicar filtros**

   * En un script (p. ej. `backtest_*.py`) o notebook, carga `merged_ligaX.csv` y filtra:

     ```python
     df = pd.read_csv("merged_ligaX.csv")
     df = df[(df.B365H>=2.00)&(df.B365H<3.60)&(df.B365D>=3.15)]
     ```
4. **Calcular P\&L por pick**

   ```python
   df["pnl"] = df.apply(lambda r: (r.B365D-1) if r.FTR=="D" else -1, axis=1)
   ```
5. **Yield global**

   ```python
   yield_global = df["pnl"].sum() / len(df)
   ```
6. **Backtest por bloques fijos**

   * Ejecuta `backtest_chunks_md.py merged_ligaX.csv report_fijos.md`
   * Obtén media, mediana, máximos y mínimos para bloques de 10, 50, 100, 200 picks
7. **Backtest con ventanas móviles**

   * Ejecuta `backtest_rolling_windows.py merged_ligaX.csv report_rolling.md`
   * Estudia la distribución de yield en ventanas de 10, 25, … 500 picks
8. **Hit-rate**

   ```python
   aciertos = (df.FTR=="D").sum()
   hit_rate = aciertos / len(df)
   ```
9. **Informe y visualización**

   * Abre los Markdown generados (`report_fijos.md`, `report_rolling.md`)
   * Opcionalmente crea gráficos de histograma o heatmaps en Python/Plotly

---

### Puntos de control y ajustes

* **Revisa la calidad de las cuotas** en la nueva liga: quizá necesites ajustar los umbrales (p. ej. B365D ≥ 3.00 o ≥ 3.20).
* **Benchmark**: compara yield y hit-rate con la Segunda División para calibrar dificultad.
* **Itera**: si el yield cae demasiado, explora otros rangos de cuotas al 1 o añade filtros extra (forma reciente, over/under).

Con este flujo modular podrás replicar y adaptar la simulación a cualquier campeonato, asegurándote de medir tanto la rentabilidad como la robustez de tu estrategia.
