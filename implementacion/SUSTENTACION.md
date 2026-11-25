# Guía de sustentación individual

Cesar Santiago Canro Cabra · Samuel Enrique Giraldo Sabogal

El enunciado fija la sustentación individual en la última sesión de clase. El siguiente guion es una práctica de seis minutos. Cada integrante debe poder explicar el proceso completo y reproducir las salidas con su propia explicación.

## Ruta sin consola

Abre el lanzador de la raíz con doble clic o ejecuta `interfaz.py` desde
PyCharm. Selecciona **Pequeño**, deja la semilla 202630 y pulsa **Generar CSV**.
En la pestaña **Datos CSV**, compara `solicitudes.csv`, `grupos.csv` y `horarios.csv`.
Pulsa **Asignar horarios** y cambia de E001 a E005 para mostrar la cobertura
individual y una materia pendiente. Luego pulsa **Verificar resultado** para
mostrar las cuatro reglas.

Para la comparación, abre **Casos para la sustentación → Reparación**. Asigna
primero con **Base · voraz** y después con **Propuesto · con reparación**.
Compara 1/2 con 2/2 y explica qué sección cambió. En el caso de brecha, compara
la propuesta con **Exacto · casos pequeños**.

## Guion de seis minutos

| Tiempo | Qué mostrar | Qué explicar |
| --- | --- | --- |
| 0:00–0:45 | Entrada y salida en el README | El contrato de semana 10. Pedidos, grupo, franjas, cupos y $H(e)$. Las solicitudes pendientes siguen siendo un resultado válido. |
| 0:45–1:45 | Pizarra o terminal con el caso de reparación | Cómo se toman decisiones en el voraz y cómo un cambio de sección incorpora otra solicitud. |
| 1:45–2:45 | Función `construir` en `algoritmo.py` | Cupos restantes, regla de solapamiento, orden de solicitudes y aceptación de una reparación. |
| 2:45–3:30 | Verificador y argumento de corrección | El horario vacío satisface las restricciones. Cada paso mantiene el invariante y la reparación suma una asignación. |
| 3:30–4:45 | Resultados y oráculo | Diferencia entre validez, mejor resultado observado y optimalidad exacta. Resultados de 5, 50 y 500 estudiantes. |
| 4:45–6:00 | Caso `brecha.json` y síntesis | Cuándo falla la reparación local, por qué el oráculo crece exponencialmente y qué costo tiene la mejora frente a la base. |

## Demo 1 · Recuperar una materia

El lunes, A1 va de 08:00 a 09:00 y A2 de 09:00 a 10:00. B1 va de 08:00 a 08:30 y B2 de 08:30 a 09:00. El estudiante pide A con prioridad 3 y B con prioridad 1.

- La base toma A1. A1 se cruza con las dos secciones de B. Queda 1 de 2.
- En la reparación, cambiar A1 por A2 libera la mañana temprana. B1 o B2 encaja. Queda 2 de 2. Los intervalos colindantes se permiten.
- Las ternas esperadas son `[1, 3, 0]` para la base y `[2, 4, 0]` para el propuesto y el exacto. Puede haber más de un horario con el mismo valor.

~~~text
python -B horarios.py resolver casos/reparacion.json demo-base.json --metodo base
python -B horarios.py resolver casos/reparacion.json demo-propuesto.json
python -B horarios.py verificar casos/reparacion.json demo-propuesto.json
~~~

## Demo 2 · Mostrar el límite

En `brecha.json`, E1 ocupa A1. E2 tiene B1 el martes. A2 también es el martes y se cruza con B1. La heurística conserva dos asignaciones. El oráculo mueve a E1 a A2 y entrega A1 a E2, que también conserva B1. Llega a tres asignaciones. E1 además pide C y la entrada carece de oferta para C. Por eso la cobertura máxima del caso es 3/4.

~~~text
python -B horarios.py resolver casos/brecha.json brecha-propuesto.json
python -B horarios.py resolver casos/brecha.json brecha-exacto.json --metodo exacto
~~~

## Preguntas para practicar

**¿Cómo se construyen y validan los CSV?**  
Los catálogos contienen los identificadores. Los grupos enlazan asignatura, profesor y salón. Las sesiones y solicitudes tienen sus propias filas. El lector comprueba encabezados, claves y referencias antes de construir el horario. Para demostrarlo, ejecuta el programa con la carpeta `ejemplo_csv` e identifica en `horarios.csv` dos sesiones con el mismo `grupo_id`.

**¿Cómo saben que la salida es válida?**  
La construcción mantiene las restricciones y los cupos por inducción. Además, el verificador reconstruye la agenda y cuenta los cupos a partir de $H$. Implementa el chequeo temporal con sesiones ordenadas, mientras el solucionador compara pares de franjas entre grupos.

**¿Dos clases de 08:00–09:00 y 09:00–10:00 se cruzan?**  
Pueden coexistir. Para que exista cruce, ambos inicios deben ser estrictamente anteriores al fin de la otra clase y deben ocurrir el mismo día. El desplazamiento entre salones se registra como preferencia de calidad.

**¿Por qué un mejor puntaje de profesor puede acompañar un peor resultado?**  
La comparación empieza por cobertura y sigue por prioridad. El puntaje de preferencias decide cuando ambas coinciden. El reporte conserva las medidas originales para interpretar el intercambio.

**¿Qué cambia si una materia tiene un solo grupo o no tiene ninguno?**  
Con una sola sección, el inicio guiado prioriza esa solicitud frente a otras con más alternativas. Cuando no hay oferta, la solicitud permanece pendiente. El caso de un solo cupo permite mostrar que el inicio guiado puede atender al estudiante con mayor prioridad.

**¿Cómo se sabe que el resultado del oráculo sí es óptimo?**  
La enumeración genera todas las combinaciones de una sección u omisión por cada solicitud. Descarta salidas inválidas y conserva el mayor objetivo. Esto es viable en los casos pequeños porque su espacio de combinaciones es reducido.

**¿Por qué conservar dos inicios?**  
Separar las solicitudes por escasez y prioridad cambia qué cupos se ocupan temprano. Dado que un inicio alternativo a veces cubre menos, ambos horarios pasan por la reparación y se comparan con la misma terna. La reparación aumenta cobertura o deja el candidato igual. El candidato de origen simple garantiza el piso de la base.

**¿Qué demuestra la medición?**  
Ambos métodos recibieron las mismas nueve entradas. La propuesta mejoró cobertura en cinco, mejoró prioridad con igual cobertura en dos y empató en dos. La comparación mide comportamiento bajo demanda, cupos y preferencias simulados. Para extrapolar al campus se requieren entradas reales o anonimizadas.

**¿Cómo ampliarían el algoritmo?**  
Una reparación que permita cambios entre estudiantes podría resolver el caso de brecha. Para incorporarla se necesitarían límites de búsqueda y pruebas específicas de que las reasignaciones preservan cupos y horarios de todos los afectados.

## Ensayo entre los dos

Cada integrante ejecuta las dos demos con el mismo paquete. El otro le pide justificar un paso de la prueba, interpretar una fila de resultados y predecir el efecto de cambiar una franja o un cupo. Luego intercambian roles. En la sustentación usen ejemplos de contribuciones propias y expliquen qué parte verificó cada integrante.
