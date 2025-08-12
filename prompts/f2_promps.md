Voy a pasarte una captura de pantalla con las cuotas pre-partido de todos los encuentros de la Segunda División de Francia.

Un partido es CANDIDATO (✅ “bueno”) si:

La cuota al local está dentro del rango [2.25, 3]

La cuota al empate está dentro de ≥ 3

En caso contrario: NO CANDIDATO (❌ “malo”).

Tu tarea es:

Leer las cuotas (1, X, 2) de cada partido de la captura y convertirlas a formato decimal si es necesario.

Aplicar los criterios de partido candidato a cada partido para decidir si es “bueno” o “malo”.

Calcular el margen (overround) de cada partido usando la fórmula:

Probabilidad implícita = 1/cuota

Suma de probabilidades de las tres cuotas

Margen (%) = (Suma − 1) × 100

Presentar el resultado en una tabla con estas columnas:

Partido

Cuota Local (1)

Cuota Empate (X)

Cuota Visitante (2)

Estado (✅ en verde si es “bueno”, ❌ en rojo si es “malo”)

Margen (%) con dos decimales

Mantener el orden cronológico de los partidos según el horario mostrado en la captura.

No añadir explicaciones largas; el objetivo es ver rápido qué partidos cumplen o no cumplen los criterios.

Al final de la tabla incluye un breve resumen indicando:

Número total de partidos “buenos” y “malos”

El partido con menor margen y su valor

El partido con mayor margen y su valor