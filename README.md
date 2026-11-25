# Asignación de horarios estudiantiles

**Análisis de Algoritmos · Proyecto 2026-30 · Pontificia Universidad Javeriana**  
Cesar Santiago Canro Cabra y Samuel Enrique Giraldo Sabogal

El programa asigna grupos a estudiantes según sus solicitudes y los cupos disponibles. Comprueba los cruces de horario y reporta las asignaturas pendientes, la cobertura y las métricas de preferencias. Los datos de ejemplo son sintéticos.

## Ejecutar en PyCharm

Requisito: **Python 3.10 o posterior con Tkinter**. En Windows, Tkinter viene
con la instalación estándar de Python. El proyecto usa la biblioteca estándar.

1. En GitHub, elige **Code → Download ZIP** y extrae el contenido.
2. En PyCharm, elige **File → Open** y abre la carpeta extraída que contiene
   este README y la subcarpeta `implementacion`.
3. En el selector **Python Interpreter** de la barra de estado, elige tu
   instalación local de Python. Si no aparece, ábrela desde la
   [configuración de intérpretes de PyCharm](https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html).
4. En el panel **Project**, abre [implementacion/interfaz.py](implementacion/interfaz.py).
   Haz clic derecho sobre el archivo y elige **Run 'interfaz'**. La ventana
   abre con las solicitudes del ejemplo CSV ya cargadas.

En Windows también puedes iniciar la ventana con doble clic en
[Abrir interfaz.pyw](Abrir%20interfaz.pyw). En Visual Studio Code, abre
`implementacion/interfaz.py` y selecciona **Run Python File**.

## Demostración visual

1. Con el escenario **Pequeño** y la semilla `202630`, pulsa **Generar CSV**
   y elige dónde guardar la carpeta. En **Datos CSV**, muestra cómo se
   relacionan `solicitudes.csv`, `grupos.csv` y `horarios.csv`.
2. Pulsa **Asignar horarios**. Con el ejemplo se cubren **10 de 15
   solicitudes (66,7 %)**. Selecciona **E005** para ver su agenda y una
   materia pendiente.
3. Pulsa **Verificar resultado** para mostrar las cuatro restricciones.
   Usa **Guardar resultado JSON** para exportar las asignaciones y métricas.

En **Casos para la sustentación → Reparación**, ejecuta **Base · voraz** y
después **Propuesto · con reparación**. El caso pasa de una a dos asignaturas
cubiertas.

## Archivos del proyecto

| Contenido | Dónde encontrarlo |
| --- | --- |
| Primera entrega corregida, con el diccionario de datos CSV y su validación | [Fuente de Overleaf](docs/primera-entrega/main.tex) |
| Entrega final, con el algoritmo, su argumento de corrección y complejidad | [Documentación técnica](implementacion/README.md) |
| Archivos CSV de ejemplo, listos para resolver | [Datos de entrada](implementacion/ejemplo_csv/) |
| Casos manuales y resultados reproducibles | [Casos de referencia](implementacion/casos/), [resultados por semilla](implementacion/resultados.json) |
| Sustentación individual | [Guion y demostraciones](implementacion/SUSTENTACION.md) |

## Demostración desde la terminal

Se requiere Python 3.10 o posterior. Desde la raíz del repositorio, ejecuta:

~~~text
cd implementacion
python -B horarios.py resolver ejemplo_csv salida-csv.json
python -B horarios.py verificar ejemplo_csv salida-csv.json
python -B -m unittest -v
~~~

El verificador confirma si la asignación es válida y recalcula las métricas. El código conserva una línea base voraz, una heurística con reparación local y una referencia exacta para casos pequeños. Los experimentos incluyen nueve instancias de hasta 500 estudiantes.
