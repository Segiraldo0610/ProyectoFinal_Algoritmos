# Asignación de horarios estudiantiles

**Análisis de Algoritmos · Proyecto 2026-30 · Pontificia Universidad Javeriana**  
Cesar Santiago Canro Cabra y Samuel Enrique Giraldo Sabogal

Este proyecto presenta el diseño y la implementación de un algoritmo de
asignación de horarios estudiantiles. El programa recibe las solicitudes de
los estudiantes y la oferta de grupos, con sus franjas y cupos. La salida
registra las secciones asignadas y las solicitudes pendientes. Un verificador
independiente comprueba que la asignación cumpla las restricciones del problema.

La estrategia de datos utiliza once archivos CSV relacionados por
identificadores. Los experimentos comparan el método propuesto con una
asignación voraz de referencia y, en casos pequeños, con una búsqueda exhaustiva.

## Informes

- [Informe final en LaTeX](docs/entrega-final/main.tex). Incluye el diseño formal, la estructura de los CSV, la implementación, el argumento de correctitud, la complejidad y los resultados.
- [Primera entrega corregida](docs/primera-entrega/main.tex). Contiene la definición inicial del problema y el detalle de la estrategia de datos.

Para compilar el informe final en Overleaf, descarga su `main.tex` y úsalo
como archivo principal de un proyecto en blanco.

## Ejecución en PyCharm

Se requiere **Python 3.10 o posterior con Tkinter**. La instalación estándar
de Python para Windows incluye Tkinter.

1. Descarga el repositorio con **Code → Download ZIP** y extrae su contenido.
2. En PyCharm, selecciona **File → Open** y abre la carpeta que contiene
   este README y la subcarpeta `implementacion`.
3. Selecciona una instalación local de Python en **Python Interpreter**.
   [Guía de configuración del intérprete en PyCharm](https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html).
4. Haz clic derecho en [implementacion/interfaz.py](implementacion/interfaz.py)
   y selecciona **Run 'interfaz'**. La ventana abre con los CSV del ejemplo
   incluidos en el repositorio.

También puedes abrir la ventana desde el explorador de Windows con doble
clic en [Abrir interfaz.pyw](Abrir%20interfaz.pyw).

## Demostración de la asignación

1. Selecciona el escenario **Pequeño** y la semilla `202630`. Pulsa
   **Generar CSV**. En **Datos CSV**, consulta `solicitudes.csv`,
   `grupos.csv` y `horarios.csv` para seguir una solicitud hasta las
   secciones ofrecidas y sus sesiones.
2. Pulsa **Asignar horarios**. En esta instancia se atienden **10 de 15
   solicitudes (66,7 %)**. El horario de **E005** permite consultar sus
   sesiones asignadas y la materia A04 pendiente.
3. Pulsa **Verificar resultado** para comprobar las cuatro restricciones.
   **Guardar resultado JSON** exporta la asignación y sus métricas.

En **Casos para la sustentación → Reparación**, ejecuta **Base · voraz**
y después **Propuesto · con reparación**. En este caso, cambiar una sección
permite pasar de una a dos solicitudes atendidas.

## Archivos del proyecto

| Contenido | Dónde encontrarlo |
| --- | --- |
| Formato de entrada, algoritmo y resultados | [Documentación técnica](implementacion/README.md) |
| Archivos CSV de ejemplo, listos para resolver | [Datos de entrada](implementacion/ejemplo_csv/) |
| Casos manuales y resultados reproducibles | [Casos de referencia](implementacion/casos/), [resultados por semilla](implementacion/resultados.json) |
| Sustentación individual | [Guion y demostraciones](implementacion/SUSTENTACION.md) |

## Comandos para repetir las pruebas

Desde la carpeta principal del proyecto:

~~~text
cd implementacion
python -B horarios.py resolver ejemplo_csv salida-csv.json
python -B horarios.py verificar ejemplo_csv salida-csv.json
python -B -m unittest -v
~~~

Los comandos resuelven y verifican el mismo ejemplo que abre la interfaz.
El último ejecuta las pruebas del proyecto.
