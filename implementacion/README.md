# Asignación de horarios estudiantiles
## Entrega final · Análisis de Algoritmos · Proyecto 2026-30

**Cesar Santiago Canro Cabra y Samuel Enrique Giraldo Sabogal**  
Pontificia Universidad Javeriana · Departamento de Ingeniería de Sistemas

La implementación asigna secciones de las materias solicitadas, con sujeción a los cupos y a la compatibilidad de las franjas. Para cada estudiante, la salida registra las secciones asignadas, las solicitudes pendientes y las métricas de cobertura y preferencias. Tanto la interfaz gráfica como los comandos de terminal utilizan el mismo algoritmo y el mismo verificador.

El [informe final](../docs/entrega-final/main.tex) presenta el modelo, el análisis de correctitud y la evaluación experimental. El [README principal](../README.md#ejecución-en-pycharm) describe cómo ejecutar la interfaz en PyCharm. El [guion de sustentación](SUSTENTACION.md) incluye un caso de backtracking que se puede comprobar a mano.

## Correr las pruebas y los ejemplos

Los comandos se ejecutan desde la carpeta `implementacion` con Python 3.10 o posterior. El primer ejemplo muestra cómo el backtracking recupera una materia al volver sobre una decisión.

~~~text
python -B -m unittest -v
python -B horarios.py resolver casos/reparacion.json demo-base.json --metodo base
python -B horarios.py resolver casos/reparacion.json demo.json --metodo backtracking
python -B horarios.py verificar casos/reparacion.json demo.json
python -B horarios.py resolver casos/reparacion.json demo-fuerza-bruta.json --metodo fuerza_bruta
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
| Una sección por asignatura y solo solicitudes | Se procesa un par estudiante–asignatura por vez. El backtracking elige una sección o deja la solicitud pendiente. |
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

La **base voraz** atiende las solicitudes por identificador y escoge la primera sección con cupo que encaje. El **backtracking** conserva ese horario como mejor resultado inicial. Luego ordena las solicitudes por escasez de secciones, prioridad descendente e identificador. En cada nivel prueba un grupo compatible o deja la materia pendiente. Cuando retrocede, deshace la decisión y devuelve el cupo.

**Poda.** Por cada materia se toma el menor valor entre solicitudes aún por explorar y cupos libres. Esto da una cota de cobertura. Para la cota de prioridad se toman las solicitudes más prioritarias que cabrían en esos cupos. Se descarta una rama cuando esa cota queda por debajo del mejor par de cobertura y prioridad encontrado. En empate se sigue explorando, ya que podrían mejorar las preferencias.

**Presupuesto.** Por defecto se examinan hasta 15.000 nodos. Si se completa el recorrido, se comprueba el óptimo según la terna definida. Si se alcanza el límite, se devuelve la mejor solución encontrada hasta entonces. La ventana muestra el estado y el JSON incluye `busqueda.completa`, `busqueda.nodos` y `busqueda.limite_nodos`. Desde la terminal se puede comparar otro presupuesto con `--limite-nodos`.

**Validez y complejidad.** El horario parcial mantiene las cuatro restricciones y el contador de cupos se restaura al deshacer una decisión. Se utiliza una pila explícita de profundidad a lo sumo igual al número de solicitudes. El árbol crece de forma exponencial en el peor caso. El límite controla cuántos nodos se procesan en la práctica.

**Fuerza bruta.** Enumera las combinaciones de grupos y omisiones en casos de hasta 50.000 combinaciones. En [el caso de reasignación](casos/brecha.json), el backtracking y la fuerza bruta atienden 3 de 4 solicitudes.

## Resultados de la entrega

Promedios de tres semillas por tamaño. Los tiempos corresponden al solucionador en Windows, Python 3.14.8 e Intel Core Ultra 7 255U. Excluyen la carga de datos y la verificación final.

| Estudiantes | Cobertura base → backtracking | Prioridad total media base → backtracking | Tiempo medio base → backtracking |
| ---: | ---: | ---: | ---: |
| 5 | 62,22 % → 62,22 % | 28,00 → 33,00 | 0,05 ms → 4,01 ms |
| 50 | 57,87 % → 58,13 % | 429,67 → 542,67 | 0,26 ms → 499,44 ms |
| 500 | 65,87 % → 65,87 % | 5953,00 → 5953,00 | 3,62 ms → 48,30 ms |

El backtracking atendió una solicitud adicional en dos casos medianos, mejoró la prioridad con igual cobertura en cuatro instancias y conservó la terna en las tres grandes. La búsqueda se completó en los tres ejemplos pequeños. En los medianos y grandes llegó al límite de 15.000 nodos. [Resultados por semilla](resultados.json), [casos comprobados a mano](casos/) y [salidas esperadas](casos/salidas_esperadas.json).
