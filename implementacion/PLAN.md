# Plan de implementación y sustentación

Base: sección 4.2 del enunciado 2026-30 y formalización de la primera entrega.

| Requisito o evidencia | Trabajo | Criterio de aceptación |
| --- | --- | --- |
| Implementación basada en la semana 10 | Modelar solicitudes, grupos, franjas, cupos y preferencias. | La salida por estudiante cumple las cuatro postcondiciones. |
| Estrategia de datos | Generar instancias reproducibles y usar casos manuales, enumeración y una línea base. | Se registran cobertura, calidad y tiempo para 5, 50 y 500 estudiantes. |
| Ingeniería de software | Separar modelo, algoritmo, verificador, experimentos e interfaz. | El README describe el contrato y las pruebas detectan salidas inválidas. |
| Sustentación individual | Preparar demo, ejemplo manual, invariante, complejidad y preguntas. | Cada integrante puede reproducir y justificar el resultado. |

## Diseño elegido

Python 3.10+ y biblioteca estándar. La interfaz de terminal permite generar, resolver, verificar y evaluar instancias. El voraz simple da la línea base. El método propuesto construye dos horarios iniciales, uno simple y otro guiado por el número de opciones y las prioridades. Repara ambos cambiando como máximo una sección ya asignada al mismo estudiante para recuperar cada solicitud. Devuelve el mejor de los dos. La enumeración se reserva para instancias diminutas.

El orden de evaluación es lexicográfico: número de solicitudes cubiertas, suma de prioridades satisfechas y puntaje de preferencias. El método escalable es heurístico y el oráculo permite medir su brecha frente al óptimo de casos concretos.

## Ejecución

- [x] Modelo de entrada, verificador independiente y métricas. Probar solapamientos parciales, colindancia, cupos, duplicados y preferencias.
- [x] Voraz simple, heurística y enumeración exacta. Probar una reparación y una brecha frente al óptimo.
- [x] Generador por semilla y CLI. Ejecutar los casos de referencia y comparar con la línea base en 5, 50 y 500 estudiantes.
- [x] Documentar trazabilidad, corrección, complejidad y resultados. Preparar una demo reproducible y preguntas de sustentación.
