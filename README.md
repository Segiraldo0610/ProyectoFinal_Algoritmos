# Asignación de horarios estudiantiles

**Análisis de Algoritmos · Proyecto 2026-30 · Pontificia Universidad Javeriana**  
Cesar Santiago Canro Cabra y Samuel Enrique Giraldo Sabogal

El proyecto arma horarios a partir de las materias que pide cada estudiante y los cupos de los grupos. En la ventana se puede ver qué clases le tocaron, qué materias quedaron pendientes y si el horario cumple las reglas. Los ejemplos usan datos simulados.

## Cómo abrirlo en PyCharm

En Windows basta con tener **Python 3.10 o posterior** con Tkinter, que viene
con la instalación estándar.

1. Descarga el proyecto con **Code → Download ZIP** y descomprímelo.
2. En PyCharm, entra a **File → Open** y selecciona la carpeta donde quedaron
   el README y la subcarpeta `implementacion`.
3. Si PyCharm pide un intérprete, selecciona tu Python local en el menú
   **Python Interpreter**. [Ayuda de PyCharm para configurar el intérprete](https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html).
4. Abre [implementacion/interfaz.py](implementacion/interfaz.py), haz clic
   derecho en el archivo y elige **Run 'interfaz'**. La ventana ya trae un
   ejemplo cargado para que puedas probarla de una vez.

También puedes abrir la ventana desde el explorador de Windows con doble
clic en [Abrir interfaz.pyw](Abrir%20interfaz.pyw).

## Qué probar en la ventana

1. Elige **Pequeño**, deja la semilla `202630` y pulsa **Generar CSV**.
   En **Datos CSV**, abre `solicitudes.csv`, `grupos.csv` y `horarios.csv`.
   Sigue una misma materia desde la solicitud hasta el grupo y sus clases.
2. Pulsa **Asignar horarios**. El método propuesto atiende **10 de 15
   solicitudes (66,7 %)**. Cambia a **E005** para ver las clases que recibió
   y la materia que le quedó pendiente.
3. Pulsa **Verificar resultado** para ver si se cumplen las cuatro reglas
   del horario. Con **Guardar resultado JSON** puedes llevarte la salida
   y sus métricas en un archivo.

Para mostrar qué aporta el algoritmo, entra a **Casos para la sustentación →
Reparación**. Corre **Base · voraz** y luego **Propuesto · con reparación**.
Vas a ver cómo cambiar una sección permite pasar de una a dos materias
asignadas.

## Archivos del proyecto

| Contenido | Dónde encontrarlo |
| --- | --- |
| Primera entrega corregida, con el diccionario de datos CSV y su validación | [Fuente de Overleaf](docs/primera-entrega/main.tex) |
| Entrega final, con el algoritmo, su argumento de corrección y complejidad | [Documentación técnica](implementacion/README.md) |
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
