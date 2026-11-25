"""Instancias sintéticas con semillas y parámetros publicados."""
from random import Random


ESCENARIOS = {
    "pequeno": (5, 5, 2, 3, 3, 3),
    "mediano": (50, 15, 3, 12, 10, 5),
    "grande": (500, 30, 4, 30, 20, 6),
}


def generar(escenario: str, semilla: int = 202630) -> dict:
    rng = Random(semilla)
    n, m, secciones, p, s, pedidos = ESCENARIOS[escenario]
    materias = [f"A{i + 1:02}" for i in range(m)]
    profesores = [f"P{i + 1:02}" for i in range(p)]
    salones = [f"S{i + 1:02}" for i in range(s)]
    ids = [f"E{i + 1:03}" for i in range(n)]
    puntos = {sala: (rng.randint(0, 500), rng.randint(0, 500)) for sala in salones}
    distancias = {a: {b: abs(ax - bx) + abs(ay - by) for b, (bx, by) in puntos.items()}
                  for a, (ax, ay) in puntos.items()}
    grupos = []
    cupo_medio = max(1, n * pedidos * 80 // (100 * m * secciones))
    for a in materias:
        for j in range(secciones):
            duracion = rng.choice((60, 90, 120))
            inicio = rng.randrange(480, 961, 30)
            dias = rng.sample(range(1, 6), k=rng.choice((1, 1, 2)))
            grupos.append({
                "id": f"{a}-G{j + 1}", "asignatura": a,
                "profesor": rng.choice(profesores), "salon": rng.choice(salones),
                "capacidad": max(1, cupo_medio + rng.randint(-(cupo_medio // 3), cupo_medio // 3)),
                "franjas": [[d, inicio, inicio + duracion] for d in sorted(dias)],
            })
    estudiantes = []
    for e in ids:
        pesos = list(range(m, 0, -1))
        candidatos = materias.copy()
        solicitudes = {}
        for _ in range(pedidos):
            a = rng.choices(candidatos, weights=pesos)[0]
            pesos.pop(candidatos.index(a))
            candidatos.remove(a)
            solicitudes[a] = rng.randint(1, 5)
        estudiantes.append({
            "id": e, "solicitudes": solicitudes,
            "profesor": {p: rng.randint(1, 5) for p in rng.sample(profesores, min(4, len(profesores)))},
            "inicio_min": rng.choice((480, 540, 600)), "fin_max": rng.choice((960, 1020, 1080)),
            "compacto": rng.choice((True, False)),
            "dias_libres": [rng.randint(1, 5)] if rng.random() < .5 else [],
            "companeros": sorted(rng.sample([otro for otro in ids if otro != e], min(3, n - 1))),
        })
    return {"grupos": grupos, "estudiantes": estudiantes, "distancias": distancias}
