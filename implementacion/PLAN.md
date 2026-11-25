# Plan de implementación y sustentación

Base: sección 4.2 del enunciado 2026-30 y formalización de la primera entrega.

| Requisito o evidencia | Trabajo | Criterio de aceptación |
| --- | --- | --- |
| Implementación basada en la semana 10 | Modelar solicitudes, grupos, franjas, cupos y preferencias. | La salida por estudiante cumple las cuatro postcondiciones. |
| Estrategia de datos | Generar instancias reproducibles y usar casos manuales, enumeración y una línea base. | Se registran cobertura, calidad y tiempo para 5, 50 y 500 estudiantes. |
| Ingeniería de software | Separar modelo, algoritmo, verificador, experimentos e interfaz. | El README describe el contrato y las pruebas detectan salidas inválidas. |
| Sustentación individual | Preparar demo, ejemplo manual, invariante, complejidad y preguntas. | Cada integrante puede reproducir y justificar el resultado. |

## Diseño elegido

El proyecto usa Python 3.10 o posterior. La ventana permite generar y revisar los CSV, asignar grupos y verificar el horario. La terminal permite repetir la evaluación de los nueve escenarios. El método propuesto usa backtracking con poda. Parte de la solución voraz y explora decisiones de grupo u omisión, restituyendo los cupos al retroceder. Informa si se agotó la búsqueda o si se alcanzó el límite de nodos. Para los casos pequeños, la enumeración exhaustiva permite comprobar su resultado.

El orden de evaluación es lexicográfico: número de solicitudes cubiertas, suma de prioridades satisfechas y puntaje de preferencias. Con búsqueda completa, la poda comprueba el óptimo. Con límite alcanzado, se conserva la mejor asignación encontrada.

## Ejecución

- [x] Modelo de entrada, verificador independiente y métricas. Probar solapamientos parciales, colindancia, cupos, duplicados y preferencias.
- [x] Voraz simple, backtracking con poda y enumeración exacta. Probar cambios de sección y reasignaciones entre estudiantes.
- [x] Generador por semilla. Comparar los resultados con la línea base en los escenarios de 5, 50 y 500 estudiantes.
- [x] Ventana para la sustentación. Mostrar los CSV, las materias pendientes y el resultado de la verificación.
- [x] Documentar trazabilidad, corrección, complejidad y resultados. Preparar una demo reproducible y preguntas de sustentación.
