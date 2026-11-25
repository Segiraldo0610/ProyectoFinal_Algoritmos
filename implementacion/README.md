# Asignación de horarios estudiantiles
## Entrega final · Análisis de Algoritmos · Proyecto 2026-30

**Cesar Santiago Canro Cabra y Samuel Enrique Giraldo Sabogal**  
Pontificia Universidad Javeriana · Departamento de Ingeniería de Sistemas

El programa selecciona grupos para las asignaturas solicitadas por cada estudiante, verifica las cuatro postcondiciones de la primera entrega y reporta la cobertura, las solicitudes pendientes y las preferencias satisfechas. La sustentación de la semana 17 es individual. El guion y el ejercicio manual están en [SUSTENTACION.md](SUSTENTACION.md).

## Reproducir la entrega

Desde esta carpeta, con Python 3.10 o posterior y su biblioteca estándar:

~~~text
python -B -m unittest -v
python -B horarios.py resolver casos/reparacion.json demo-base.json --metodo base
python -B horarios.py resolver casos/reparacion.json demo.json
python -B horarios.py verificar casos/reparacion.json demo.json
python -B horarios.py resolver casos/reparacion.json demo-exacto.json --metodo exacto
python -B horarios.py generar grande entrada-grande --formato csv --semilla 202631
python -B horarios.py resolver entrada-grande salida-grande.json
python -B horarios.py verificar entrada-grande salida-grande.json
python -B horarios.py evaluar medicion-local.json
~~~

`verificar` devuelve código 0 para una salida válida, 1 si viola el contrato y 2 si falla la lectura o el formato. Recalcula las métricas a partir de la asignación. Las mediciones de la entrega están en [resultados.json](resultados.json).

## Contrato que viene de la semana 10

| Formalización | Representación y verificación |
| --- | --- |
| Estudiantes, grupos y solicitudes | IDs únicos. Cada estudiante declara las asignaturas que solicita y sus prioridades. Un grupo tiene asignatura, profesor, salón, capacidad y franjas. |
| Solapamiento | Cada franja contiene día, inicio y fin. Con el mismo día se cruzan si cada una empieza antes de que termine la otra. Dos clases que comparten solamente el extremo se permiten. |
| Capacidad global | Se cuenta cuántos estudiantes reciben cada grupo. El contador del algoritmo mide cupos disponibles. |
| Una sección por asignatura y solo solicitudes | Se procesa un par estudiante–asignatura por vez. Una reparación conserva la materia del grupo que reemplaza. |
| Salida `H` | El objeto `horarios` contiene una lista de grupos por estudiante, incluida la lista vacía. `metricas.estudiantes` informa las solicitudes pendientes. |

### Entrada CSV

La carpeta de entrada contiene once archivos de texto UTF-8, separados por comas y con encabezados fijos. El programa une las tablas por identificador, comprueba los dominios y verifica que las referencias existan. Las salidas se escriben en JSON fuera de la carpeta de entrada. El ejemplo completo se incluye en `ejemplo_csv`.

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

El generador registra semilla, escenario y versiones de Python y del esquema en `meta.json`. Ese archivo documenta la reproducción y es opcional para resolver. Para regenerar los datos, indica otra carpeta de destino. Los archivos de ejemplo ya se pueden usar en la demo.

~~~text
python -B horarios.py resolver ejemplo_csv salida-csv.json
python -B horarios.py verificar ejemplo_csv salida-csv.json
~~~

### Entrada JSON

La entrada JSON contiene `grupos`, `estudiantes` y `distancias`. Véase [casos/reparacion.json](casos/reparacion.json) para un ejemplo. Los campos de grupo son `id`, `asignatura`, `profesor`, `salon`, `capacidad` entera positiva y `franjas`, una lista no vacía de ternas `[día, minuto_inicio, minuto_fin]`. Los días van de lunes (1) a viernes (5). Los minutos van de 0 a 1440 y el inicio debe ser menor que el fin. Todas las sesiones de un grupo comparten salón.

Cada estudiante tiene `id` y un objeto no vacío `solicitudes` de asignatura a prioridad entera positiva. Las asignaturas sin oferta quedan pendientes. Los campos opcionales son `profesor` (valor de 0 a 5 por ID, con 0 para preferencia no informada), `inicio_min` (0), `fin_max` (1440), `compacto` (falso), `dias_libres` y `companeros` (arreglos vacíos por defecto). Las preferencias de compañeros son dirigidas. La matriz `distancias` incluye una fila por salón, con todas sus columnas, valores enteros no negativos en metros, diagonal cero y simetría. Los catálogos de asignaturas y profesores se representan por los identificadores referidos.

## Criterio de evaluación

Se maximiza lexicográficamente la terna **(solicitudes asignadas, suma de prioridades asignadas, puntaje de preferencias)**. Por ejemplo, 145 asignaciones prevalecen sobre 144. Con igual cobertura se compara la prioridad. Con ambas iguales se usa el puntaje.

Para cada estudiante, el puntaje suma 60 por punto de profesor y 120 por coincidencia dirigida de compañero y grupo. Resta un punto por minuto de clase fuera de la ventana deseada, 120 por sesión en un día libre preferido, un punto por minuto de hueco cuando el estudiante prefiere compactación y la parte entera de la distancia en metros dividida entre 10. Huecos y desplazamientos se calculan entre sesiones consecutivas del mismo día. El puntaje total es la suma de los puntajes individuales. El promedio de profesores usa las valoraciones informadas y es nulo cuando no hay ninguna. El reporte también conserva las medidas en sus unidades originales.

Las ponderaciones son decisiones explícitas de esta implementación. Las cinco preferencias afectan la evaluación y la elección de grupos en el inicio guiado. La cobertura global cuenta pares estudiante–asignatura, así que un estudiante que pide más materias aporta más solicitudes al denominador.

## Algoritmo y verificación

1. La base recorre solicitudes por identificador de estudiante y asignatura. Toma la primera sección con cupo y compatible.
2. El método propuesto construye un horario con ese orden simple y otro que procesa primero las solicitudes con menos secciones. Desempata por prioridad descendente, menor flexibilidad total del estudiante e identificadores. En el inicio guiado elige la sección cuya incorporación da el mayor puntaje individual calculado con las asignaciones disponibles en ese momento.
3. En ambos horarios, revisa una vez las solicitudes pendientes. Puede añadir una sección libre que encaje directamente. Si existe un único grupo que bloquea la nueva sección, prueba mover ese grupo a otra sección de su misma materia con cupo. Verifica la compatibilidad del horario candidato antes de actualizar los cupos.
4. Puntúa los dos horarios completos y devuelve el mayor en orden lexicográfico. La salida de cada método pasa por el mismo verificador independiente, que ordena las sesiones de cada estudiante y cuenta matrículas por grupo.

**Invariante.** Los horarios parciales contienen exclusivamente solicitudes, a lo sumo una sección por materia, y sesiones compatibles. Para cada grupo, cupo libre = capacidad − estudiantes asignados. El estado vacío cumple el invariante. En la construcción se inserta una solicitud nueva compatible con cupo disponible. Cada reparación añade una solicitud nueva y, si cambia un grupo previo, conserva su materia y actualiza los cupos de los tres grupos afectados. Así se preserva el invariante y cada reparación aceptada aumenta la cobertura en una unidad. El inicio simple reparado conserva o supera el objetivo de la base. Elegir el mejor de los dos candidatos conserva esa propiedad.

**Complejidad.** Sean R las solicitudes, G los grupos, E los estudiantes, B el máximo de secciones por materia, K las solicitudes por estudiante como máximo, L las sesiones por grupo como máximo y C los compañeros preferidos por estudiante como máximo. Puntuar una propuesta cuesta como máximo M = O(KL log(2+KL) + CK² + K). Un chequeo de dos grupos cuesta O(L²) sin caché. Una cota superior conservadora del método propuesto es O(G log(2+G) + E log(2+E) + R log(2+R) + R·B²·(K·L² + M) + E·M). Los dos inicios son un factor constante. El almacenamiento auxiliar incluye O(G + E + R) para listas, horarios y cupos, además de hasta 100.000 entradas en caché y O(KL) de trabajo por horario. La entrada incluye la matriz de distancias, de tamaño cuadrático en los salones.

**Oráculo.** Para cada solicitud enumera todas sus secciones y la opción de dejarla pendiente. El producto incluye cada asignación admisible. Descarta las que infringen las postcondiciones y conserva el máximo de la terna. El número de combinaciones es el producto de (1 + secciones) por solicitud. La CLI limita esta búsqueda a 50.000 combinaciones y la usa como referencia de instancias pequeñas. El método propuesto puede quedarse corto si necesita mover la asignación de otro estudiante, como ocurre en `casos/brecha.json`.

## Resultados de la entrega

Promedios de tres semillas por escala. Tiempos del solucionador, sin carga de archivos ni verificación externa al método, medidos en Windows, Python 3.14.8 e Intel Core Ultra 7 255U. Las asignaciones y métricas se reproducen con las mismas entradas. Los tiempos varían entre ejecuciones.

| Estudiantes | Cobertura base → propuesta | Prioridad total media base → propuesta | Tiempo medio base → propuesta |
| ---: | ---: | ---: | ---: |
| 5 | 62,22 % → 62,22 % | 28,00 → 31,00 | 0,05 ms → 0,35 ms |
| 50 | 57,87 % → 58,27 % | 429,67 → 544,67 | 0,61 ms → 4,87 ms |
| 500 | 65,87 % → 65,97 % | 5953,00 → 6865,00 | 9,84 ms → 85,55 ms |

En las nueve instancias hubo cinco mejoras en cobertura, dos mejoras en prioridad con cobertura igual y dos empates completos. En una instancia de 5 estudiantes el puntaje de preferencias bajó al atender prioridades mayores con la misma cobertura, según la jerarquía declarada. El método propuesto cuesta más por los dos inicios y la reparación. Los escenarios se diseñaron con demanda desigual y cupos ajustados, por lo que reportar pendientes es parte del resultado.

Las distancias y preferencias de estas pruebas son sintéticas. Las distancias provienen de puntos simulados y la evaluación describe estas instancias. Los archivos manuales y sus [salidas esperadas](casos/salidas_esperadas.json) comprueban tres propiedades: beneficio de la reparación, desempate por prioridad con un único cupo y brecha frente al óptimo cuando se necesita un cambio entre estudiantes.
