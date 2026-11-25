# Guía de sustentación individual

Cesar Santiago Canro Cabra · Samuel Enrique Giraldo Sabogal

## Corrida en PyCharm

Abre `implementacion/interfaz.py` y selecciona **Run 'interfaz'**. Con **Pequeño** y la semilla **202630**, pulsa **Generar CSV**. En **Datos CSV**, sigue la solicitud de A05 de E005 hasta A05-G1. La capacidad está en `grupos.csv` y las dos sesiones están en `horarios.csv`. El valor `810` equivale a las 13:30.

Pulsa **Asignar horarios** con **Propuesto · backtracking**. Se atienden 10 de 15 solicitudes y la búsqueda comprueba el óptimo. Selecciona E005 para ver sus dos materias asignadas y A04 pendiente. Pulsa **Verificar resultado** para revisar las cuatro reglas.

## Qué mostrar en seis minutos

| Tiempo | Pantalla o archivo | Qué explicar |
| --- | --- | --- |
| 0:00–1:30 | Generador y tres CSV | Cómo se crea una instancia, para qué se guarda la semilla y cómo se enlazan solicitudes, grupos y sesiones. |
| 1:30–2:30 | Horario de E005 y validación | Qué recibió, qué le falta y cuáles son las cuatro reglas. |
| 2:30–4:00 | Caso **Cambio de sección** | Qué eligió la base y cómo el backtracking deshace una decisión. |
| 4:00–5:00 | `algoritmo.py`, función `backtracking()` | Dónde se genera una rama, cuándo se poda y cómo se devuelve un cupo al retroceder. |
| 5:00–6:00 | Caso **Reasignación entre estudiantes** y tabla de resultados | Cuándo coincide con la enumeración y qué significa alcanzar el límite. |

## Cómo explicar el backtracking

En **Casos para la sustentación → Cambio de sección**, corre **Base · voraz** y después **Propuesto · backtracking**. La base toma A1 de 08:00 a 09:00 y cubre 1 de 2. Al explorar esa elección, el backtracking comprueba que ambas opciones de B se cruzan. Vuelve sobre la decisión, restaura el cupo y prueba A2 de 09:00 a 10:00. Así obtiene A2 y B1 y cubre 2 de 2.

En **Reasignación entre estudiantes**, compara los tres métodos. El voraz atiende 2 de 4. El backtracking y **Fuerza bruta · casos pequeños** atienden 3 de 4 al asignar A2 a E1 y A1 y B1 a E2. C queda pendiente porque no tiene grupos.

## Preguntas para practicar

- **¿Qué se revierte al retroceder?** Se quita el grupo del horario, se devuelve su cupo y se restauran los contadores de solicitudes y prioridades. Si la elección fue omitir, solo se restaura el registro de la solicitud.
- **¿Cuándo se descarta una rama?** Se calcula cuántas solicitudes podrían caber como máximo con los cupos restantes. Si ni ese máximo mejora el mejor resultado encontrado, se descarta. Con igual cobertura se revisa la cota de prioridad. Con ambas iguales se explora por las preferencias.
- **¿Qué significa «Óptimo comprobado»?** Se terminó el recorrido y la poda descartó solo ramas que no podían mejorar la solución. Si aparece «Límite alcanzado», se muestra la mejor solución válida que se encontró.
- **¿Qué pasa con más estudiantes?** En los escenarios medianos y grandes se alcanzó el límite de 15.000 nodos. En las tres instancias grandes se conservó el resultado voraz. La tabla del informe registra los tiempos y métricas.
