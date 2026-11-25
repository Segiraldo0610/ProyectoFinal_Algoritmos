# Asignación de horarios estudiantiles

**Análisis de Algoritmos · Proyecto 2026-30 · Pontificia Universidad Javeriana**  
Cesar Santiago Canro Cabra y Samuel Enrique Giraldo Sabogal

El programa asigna grupos a estudiantes según sus solicitudes y los cupos disponibles. Comprueba los cruces de horario y reporta las asignaturas pendientes, la cobertura y las métricas de preferencias. Los datos de ejemplo son sintéticos.

| Contenido | Dónde encontrarlo |
| --- | --- |
| Primera entrega corregida, con el diccionario de datos CSV y su validación | [Fuente de Overleaf](docs/primera-entrega/main.tex) |
| Entrega final, con el algoritmo, su argumento de corrección y complejidad | [Documentación técnica](implementacion/README.md) |
| Archivos CSV de ejemplo, listos para resolver | [Datos de entrada](implementacion/ejemplo_csv/) |
| Casos manuales y resultados reproducibles | [Casos de referencia](implementacion/casos/), [resultados por semilla](implementacion/resultados.json) |
| Sustentación individual | [Guion y demostraciones](implementacion/SUSTENTACION.md) |

## Ejecutar la demostración

Se requiere Python 3.10 o posterior. Desde la raíz del repositorio, ejecuta:

~~~text
cd implementacion
python -B horarios.py resolver ejemplo_csv salida-csv.json
python -B horarios.py verificar ejemplo_csv salida-csv.json
python -B -m unittest -v
~~~

El verificador confirma si la asignación es válida y recalcula las métricas. El código conserva una línea base voraz, una heurística con reparación local y una referencia exacta para casos pequeños. Los experimentos incluyen nueve instancias de hasta 500 estudiantes.
