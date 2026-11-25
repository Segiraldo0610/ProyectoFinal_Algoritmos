# Guía de sustentación individual

Cesar Santiago Canro Cabra · Samuel Enrique Giraldo Sabogal

Esta guía sirve para ensayar la sustentación individual. La idea es empezar con los datos, correr un caso y explicar qué decisiones tomó el programa.

## Ruta sin consola

Abre la ventana con los [pasos del README](../README.md#cómo-abrirlo-en-pycharm).
Elige **Pequeño**, deja la semilla 202630 y pulsa **Generar CSV**. En **Datos CSV**,
sigue la solicitud de A01 de E001 desde `solicitudes.csv` hasta su grupo en
`grupos.csv` y su sesión en `horarios.csv`.

Pulsa **Asignar horarios**. En este ejemplo se cubren 10 de 15 solicitudes.
Abre E005 para mostrar una materia pendiente y luego pulsa **Verificar resultado**.
Aquí puedes explicar por qué un horario puede ser válido aunque queden
materias sin asignar.

## Guion de seis minutos

| Tiempo | Qué mostrar | Qué explicar |
| --- | --- | --- |
| 0:00–1:15 | Generador y pestaña Datos CSV | Cómo se repite una entrada con la semilla y cómo se relacionan solicitudes, grupos y sesiones. |
| 1:15–2:15 | Horario de E005 y validación | Qué recibió el estudiante, qué le falta y cuáles son las cuatro reglas. |
| 2:15–3:45 | Caso de reparación | Qué grupo escoge la base y qué cambio permite atender otra solicitud. |
| 3:45–4:45 | Verificador y código de `construir` | Cómo se mantienen los cupos y la validez al agregar o cambiar un grupo. |
| 4:45–6:00 | Resultados y caso de brecha | Qué mejoró con 5, 50 y 500 estudiantes y en qué caso el método exacto encuentra una mejor asignación. |

## Recuperar una materia

En la ventana, abre **Casos para la sustentación → Reparación**. El lunes,
A1 va de 08:00 a 09:00 y A2 de 09:00 a 10:00. B1 va de 08:00 a 08:30 y B2 de
08:30 a 09:00. El estudiante pide A con prioridad 3 y B con prioridad 1.

- Con **Base · voraz**, A1 queda asignada y bloquea las dos secciones de B. Se cubre 1 de 2.
- Con **Propuesto · con reparación**, A2 reemplaza a A1 y deja espacio para B. Se cubren 2 de 2. B2 puede terminar justo cuando empieza A2.
- La terna de la base es `[1, 3, 0]`. La del propuesto y el exacto es `[2, 4, 0]`. Puede haber horarios distintos con la misma terna.

Pulsa **Verificar resultado** después de la reparación.

## Mostrar el límite

Abre **Brecha frente al exacto**. Compara **Propuesto · con reparación** con
**Exacto · casos pequeños**. La propuesta deja a E1 en A1 y a E2 en B1. El
exacto encuentra una combinación de tres asignaciones al poner a E1 en A2
y a E2 en A1 y B1. La materia C carece de grupos, así que el máximo es
3 de 4 solicitudes.

## Preguntas para practicar

**¿Cómo se construyen y validan los CSV?**  
Los catálogos contienen los identificadores. Los grupos enlazan asignatura, profesor y salón. Las sesiones y solicitudes tienen sus propias filas. El lector comprueba encabezados, claves y referencias antes de construir el horario. Para demostrarlo, ejecuta el programa con la carpeta `ejemplo_csv` e identifica en `horarios.csv` dos sesiones con el mismo `grupo_id`.

**¿Cómo saben que la salida es válida?**  
El horario vacío cumple las reglas. Cada agregado y cada cambio de grupo
revisa cupos y cruces, así que las reglas siguen cumpliéndose después de cada
paso. El verificador ordena las sesiones y cuenta las matrículas de nuevo
a partir de lo que quedó asignado.

**¿Dos clases de 08:00–09:00 y 09:00–10:00 se cruzan?**  
Pueden coexistir. Para que exista cruce, ambos inicios deben ser estrictamente anteriores al fin de la otra clase y deben ocurrir el mismo día. El desplazamiento entre salones se registra como preferencia de calidad.

**¿Por qué un mejor puntaje de profesor puede acompañar un peor resultado?**  
La comparación empieza por cobertura y sigue por prioridad. El puntaje de preferencias decide cuando ambas coinciden. El reporte conserva las medidas originales para interpretar el intercambio.

**¿Qué cambia si una materia tiene un solo grupo o no tiene ninguno?**  
Con una sola sección, el inicio guiado prioriza esa solicitud frente a otras con más alternativas. Cuando no hay oferta, la solicitud permanece pendiente. El caso de un solo cupo permite mostrar que el inicio guiado puede atender al estudiante con mayor prioridad.

**¿Cómo se sabe que el resultado del oráculo sí es óptimo?**  
La enumeración genera todas las combinaciones de una sección u omisión por cada solicitud. Descarta salidas inválidas y conserva el mayor objetivo. Esto es viable en los casos pequeños porque su espacio de combinaciones es reducido.

**¿Por qué conservar dos inicios?**  
Cambiar el orden de las solicitudes cambia qué cupos se llenan primero.
Una reparación añade una materia o deja el horario igual. Al conservar
también el horario que empezó con el mismo orden que la base, siempre hay
un candidato que iguala o supera el resultado base.

**¿Qué demuestra la medición?**  
Ambos métodos recibieron las mismas nueve entradas. La propuesta mejoró cobertura en cinco, mejoró prioridad con igual cobertura en dos y empató en dos. La comparación mide comportamiento bajo demanda, cupos y preferencias simulados. Para extrapolar al campus se requieren entradas reales o anonimizadas.

**¿Cómo ampliarían el algoritmo?**  
Una reparación que permita cambios entre estudiantes podría resolver el caso de brecha. Para incorporarla se necesitarían límites de búsqueda y pruebas específicas de que las reasignaciones preservan cupos y horarios de todos los afectados.

## Ensayo entre los dos

Cada integrante ejecuta las dos demos con el mismo paquete. El otro le pide justificar un paso de la prueba, interpretar una fila de resultados y predecir el efecto de cambiar una franja o un cupo. Luego intercambian roles. En la sustentación usen ejemplos de contribuciones propias y expliquen qué parte verificó cada integrante.
