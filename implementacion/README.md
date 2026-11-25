# Asignación de horarios estudiantiles
## Entrega final · Análisis de Algoritmos · Proyecto 2026-30

**Cesar Santiago Canro Cabra y Samuel Enrique Giraldo Sabogal**  
Pontificia Universidad Javeriana · Departamento de Ingeniería de Sistemas

La implementación asigna secciones de las materias solicitadas, con sujeción a los cupos y a la compatibilidad de las franjas. Para cada estudiante, la salida registra las secciones asignadas, las solicitudes pendientes y las métricas de cobertura y preferencias. Tanto la interfaz gráfica como los comandos de terminal utilizan el mismo algoritmo y el mismo verificador.

El [informe final](../docs/entrega-final/main.tex) presenta el modelo, el análisis de correctitud y la evaluación experimental. El [README principal](../README.md#ejecución-en-pycharm) describe cómo ejecutar la interfaz en PyCharm. El [guion de sustentación](SUSTENTACION.md) incluye un caso de reparación que se puede comprobar a mano.

## Correr las pruebas y los ejemplos

Los comandos se ejecutan desde la carpeta `implementacion` con Python 3.10 o posterior. Primero puedes comprobar las pruebas y el caso en que la reparación recupera una materia.

~~~text
python -B -m unittest -v
python -B horarios.py resolver casos/reparacion.json demo-base.json --metodo base
python -B horarios.py resolver casos/reparacion.json demo.json
python -B horarios.py verificar casos/reparacion.json demo.json
python -B horarios.py resolver casos/reparacion.json demo-exacto.json --metodo exacto
~~~

Para generar una entrada más grande y repetir las mediciones:

~~~text
python -B horarios.py generar grande entrada-grande --formato csv --semilla 202631
python -B horarios.py resolver entrada-grande salida-grande.json
python -B horarios.py verificar entrada-grande salida-grande.json
python -B horarios.py evaluar medicion-local.json
~~~

El comando `verificar` vuelve a calcular las métricas usando los grupos que aparecen en la salida. Devuelve 0 si el horario es válido, 1 si incumple alguna regla y 2 si hay un problema al leer los archivos. Las mediciones originales están en [resultados.json](resultados.json).

## Qué recibe el programa y qué devuelve

| Formalización | Representación y verificación |
| --- | --- |
| Estudiantes, grupos y solicitudes | IDs únicos. Cada estudiante declara las asignaturas que solicita y sus prioridades. Un grupo tiene asignatura, profesor, salón, capacidad y franjas. |
| Solapamiento | Cada franja contiene día, inicio y fin. Con el mismo día se cruzan si cada una empieza antes de que termine la otra. Dos clases que comparten solamente el extremo se permiten. |
| Capacidad global | Se cuenta cuántos estudiantes reciben cada grupo. El contador del algoritmo mide cupos disponibles. |
| Una sección por asignatura y solo solicitudes | Se procesa un par estudiante–asignatura por vez. Una reparación conserva la materia del grupo que reemplaza. |
| Salida `H` | El objeto `horarios` contiene una lista de grupos por estudiante, incluida la lista vacía. `metricas.estudiantes` informa las solicitudes pendientes. |

### Entrada CSV

Una entrada es una carpeta con once CSV. El formato usa comas, texto UTF-8 y encabezados fijos. Por ejemplo, una fila en `grupos.csv` registra el cupo de una sección y su `grupo_id`. Si esa sección se reúne dos días, `horarios.csv` tiene dos filas con ese mismo ID. Al cargar los archivos, el programa revisa que existan los IDs relacionados y que los datos tengan sentido. La salida JSON se guarda fuera de la carpeta de entrada. [Ver el ejemplo CSV](ejemplo_csv/).

| Archivo | Encabezado en orden |
| --- | --- |
| asignaturas.csv | asignatura_id |
| profesores.csv | profesor_id |
| salones.csv | salon_id |
| estudiantes.csv | estudiante_id,inicio_min,fin_max,compacto |
| grupos.csv | grupo_id,asignatura_id,profesor_id,salon_id,capacidad |
| horarios.csv | grupo_id,dia,inicio,fin |
| solicitudes.csv | estudiante_id,asignatura_id,prioridad |
| preferencias_profesor.csv | estudiante_id,profesor_id,valor |
| dias_libres.csv | estudiante_id,dia |
| companeros.csv | estudiante_id,companero_id |
| distancias.csv | origen_id,destino_id,metros |

Cada grupo tiene una fila. Cada sesión del grupo ocupa una fila en `horarios.csv`. Cada solicitud es única por pareja estudiante–asignatura. Las tablas de preferencias por profesor, días libres y compañeros pueden contener solo el encabezado. Los enteros se escriben sin relleno con ceros y `compacto` se representa con 0 o 1. Se registran ambas direcciones y la diagonal de la matriz de distancias.

Al generar los CSV, `meta.json` deja anotados la semilla, el escenario y las versiones de Python y del esquema. Puedes resolver una entrada sin ese archivo. Para repetir la generación, elige una carpeta nueva. Los CSV de ejemplo ya vienen listos para abrir en la ventana o desde la terminal:

~~~text
python -B horarios.py resolver ejemplo_csv salida-csv.json
python -B horarios.py verificar ejemplo_csv salida-csv.json
~~~

### Entrada JSON

La entrada JSON contiene `grupos`, `estudiantes` y `distancias`. Véase [casos/reparacion.json](casos/reparacion.json) para un ejemplo. Los campos de grupo son `id`, `asignatura`, `profesor`, `salon`, `capacidad` entera positiva y `franjas`, una lista no vacía de ternas `[día, minuto_inicio, minuto_fin]`. Los días van de lunes (1) a viernes (5). Los minutos van de 0 a 1440 y el inicio debe ser menor que el fin. Todas las sesiones de un grupo comparten salón.

Cada estudiante tiene `id` y un objeto no vacío `solicitudes` de asignatura a prioridad entera positiva. Las asignaturas sin oferta quedan pendientes. Los campos opcionales son `profesor` (valor de 0 a 5 por ID, con 0 para preferencia no informada), `inicio_min` (0), `fin_max` (1440), `compacto` (falso), `dias_libres` y `companeros` (arreglos vacíos por defecto). Las preferencias de compañeros son dirigidas. La matriz `distancias` incluye una fila por salón, con todas sus columnas, valores enteros no negativos en metros, diagonal cero y simetría. Los catálogos de asignaturas y profesores se representan por los identificadores referidos.

## Cómo se comparan dos horarios

Primero gana el horario que atiende más solicitudes. Si ambos atienden la misma cantidad, gana el que suma más prioridad en las materias asignadas. Si siguen empatados, se compara el puntaje de preferencias. Ese orden se guarda en la terna **(solicitudes asignadas, suma de prioridades, puntaje de preferencias)**.

Para cada estudiante, el puntaje suma 60 por punto de profesor y 120 por coincidencia dirigida de compañero y grupo. Resta un punto por minuto de clase fuera de la ventana deseada, 120 por sesión en un día libre preferido, un punto por minuto de hueco cuando el estudiante prefiere compactación y la parte entera de la distancia en metros dividida entre 10. Huecos y desplazamientos se calculan entre sesiones consecutivas del mismo día. El puntaje total es la suma de los puntajes individuales. El promedio de profesores usa las valoraciones informadas y es nulo cuando no hay ninguna. El reporte también conserva las medidas en sus unidades originales.

Estas ponderaciones se usan para comparar los resultados y elegir grupos en el inicio guiado. La cobertura global se calcula entre todos los estudiantes de la entrada. Por eso, una persona que pide cinco materias aporta cinco solicitudes al denominador.

## Cómo se arman y comprueban los horarios

1. **Base voraz.** Recorre las solicitudes por ID de estudiante y de materia. Usa el primer grupo que tenga cupo y encaje en el horario.
2. **Dos puntos de partida.** El método propuesto arma un horario con ese orden y otro que atiende primero las solicitudes con menos secciones. Desempata por prioridad, menor flexibilidad del estudiante e identificadores. En este segundo intento escoge el grupo que deje el mejor puntaje individual en ese momento.
3. **Reparación.** Revisa una vez las materias pendientes en cada intento. Si hay un grupo libre que encaja, lo agrega. Si solo una clase lo bloquea, prueba mover esa clase a otro grupo de la misma materia. Antes de aplicar el cambio comprueba cruces y cupos.
4. **Elección y verificación.** Compara los dos resultados y devuelve el que tenga mejor terna. El verificador vuelve a ordenar las sesiones y a contar los cupos desde la salida para revisar las cuatro reglas.

**Invariante.** Los horarios parciales contienen exclusivamente solicitudes, a lo sumo una sección por materia, y sesiones compatibles. Para cada grupo, cupo libre = capacidad − estudiantes asignados. El estado vacío cumple el invariante. En la construcción se inserta una solicitud nueva compatible con cupo disponible. Cada reparación añade una solicitud nueva y, si cambia un grupo previo, conserva su materia y actualiza los cupos de los tres grupos afectados. Así se preserva el invariante y cada reparación aceptada aumenta la cobertura en una unidad. El inicio simple reparado conserva o supera el objetivo de la base. Elegir el mejor de los dos candidatos conserva esa propiedad.

**Complejidad.** Sean R las solicitudes, G los grupos, E los estudiantes, B el máximo de secciones por materia, K las solicitudes por estudiante como máximo, L las sesiones por grupo como máximo y C los compañeros preferidos por estudiante como máximo. Puntuar una propuesta cuesta como máximo M = O(KL log(2+KL) + CK² + K). Un chequeo de dos grupos cuesta O(L²) sin caché. Una cota superior conservadora del método propuesto es O(G log(2+G) + E log(2+E) + R log(2+R) + R·B²·(K·L² + M) + E·M). Los dos inicios son un factor constante. El almacenamiento auxiliar incluye O(G + E + R) para listas, horarios y cupos, además de hasta 100.000 entradas en caché y O(KL) de trabajo por horario. La entrada incluye la matriz de distancias, de tamaño cuadrático en los salones.

**Método exacto para casos pequeños.** Prueba todas las combinaciones posibles, incluida la opción de dejar una materia pendiente. Entre los horarios válidos conserva el que tiene la mejor terna. El número de combinaciones es el producto de (1 + secciones) por solicitud. La búsqueda tiene un límite de 50.000 combinaciones. En [el caso de brecha](casos/brecha.json), el exacto encuentra una solicitud adicional porque puede considerar soluciones que cambian grupos de varios estudiantes.

## Resultados de la entrega

Promedios de tres semillas por escala. Tiempos del solucionador, sin carga de archivos ni verificación externa al método, medidos en Windows, Python 3.14.8 e Intel Core Ultra 7 255U. Las asignaciones y métricas se reproducen con las mismas entradas. Los tiempos varían entre ejecuciones.

| Estudiantes | Cobertura base → propuesta | Prioridad total media base → propuesta | Tiempo medio base → propuesta |
| ---: | ---: | ---: | ---: |
| 5 | 62,22 % → 62,22 % | 28,00 → 31,00 | 0,05 ms → 0,35 ms |
| 50 | 57,87 % → 58,27 % | 429,67 → 544,67 | 0,61 ms → 4,87 ms |
| 500 | 65,87 % → 65,97 % | 5953,00 → 6865,00 | 9,84 ms → 85,55 ms |

En cinco de los nueve casos, la propuesta atendió más solicitudes. En otros dos cubrió la misma cantidad y atendió materias de mayor prioridad. Los dos restantes quedaron empatados. En un caso pequeño, esa mejora en prioridad redujo el puntaje de preferencias. Probar dos órdenes y revisar las materias pendientes también tomó más tiempo, como muestra la tabla.

Los resultados corresponden a datos simulados con cupos ajustados y demanda desigual. Para revisar el comportamiento paso a paso están los [casos comprobados a mano](casos/) y sus [salidas esperadas](casos/salidas_esperadas.json).
