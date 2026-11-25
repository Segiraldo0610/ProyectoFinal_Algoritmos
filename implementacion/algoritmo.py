"""Asignación voraz, backtracking con poda y referencia exhaustiva."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from itertools import product

from modelo import Instancia, evaluar, validar


LIMITE_NODOS = 15_000
SIN_ALTERNATIVA = object()


@dataclass(frozen=True)
class ResultadoBusqueda:
    horarios: dict[str, list[str]]
    nodos: int
    limite_nodos: int
    completa: bool


def opciones(x: Instancia) -> dict[str, list[str]]:
    por_materia = defaultdict(list)
    for nombre, g in sorted(x.grupos.items()):
        por_materia[g.asignatura].append(nombre)
    return por_materia


def detector_cruces(x):
    @lru_cache(maxsize=100_000)
    def cruzan(g, otro):
        return any(a.dia == b.dia and a.inicio < b.fin and b.inicio < a.fin
                   for a in x.grupos[g].franjas for b in x.grupos[otro].franjas)

    return cruzan


def construir_voraz(x, alternativas, cruzan):
    h = {e: [] for e in sorted(x.estudiantes)}
    libres = {g: v.capacidad for g, v in x.grupos.items()}
    for e in h:
        for a in sorted(x.estudiantes[e].solicitudes):
            for g in alternativas[a]:
                if libres[g] and all(not cruzan(g, otro) for otro in h[e]):
                    h[e].append(g)
                    libres[g] -= 1
                    break
    return {e: sorted(grupos) for e, grupos in h.items()}


def resolver(x: Instancia, metodo: str = "propuesto") -> dict[str, list[str]]:
    if metodo == "base":
        return construir_voraz(x, opciones(x), detector_cruces(x))
    if metodo in {"propuesto", "backtracking"}:
        return backtracking(x).horarios
    raise ValueError(f"método desconocido: {metodo}")


def backtracking(x: Instancia, limite_nodos: int = LIMITE_NODOS) -> ResultadoBusqueda:
    """Explora decisiones en profundidad y restaura horarios y cupos al retroceder."""
    if limite_nodos < 1:
        raise ValueError("el límite de nodos debe ser positivo")
    alternativas = opciones(x)
    cruzan = detector_cruces(x)
    mejor = construir_voraz(x, alternativas, cruzan)
    mejor_valor = evaluar(x, mejor)["objetivo"]
    pedidos = sorted(
        ((e, a, p) for e, alumno in x.estudiantes.items()
         for a, p in alumno.solicitudes.items() if alternativas[a]),
        key=lambda solicitud: (len(alternativas[solicitud[1]]), -solicitud[2],
                               solicitud[0], solicitud[1]),
    )
    if not pedidos:
        return ResultadoBusqueda(mejor, 1, limite_nodos, True)

    h = {e: [] for e in mejor}
    libres = {g: grupo.capacidad for g, grupo in x.grupos.items()}
    libres_materia = Counter()
    for g, grupo in x.grupos.items():
        libres_materia[grupo.asignatura] += libres[g]

    pendientes = Counter(a for _, a, _ in pedidos)
    prefijos = defaultdict(lambda: [0])
    for _, a, p in pedidos:
        prefijos[a].append(prefijos[a][-1] + p)

    def cota_materia(a):
        # Las solicitudes de una misma materia quedaron en orden de prioridad.
        cantidad = min(pendientes[a], libres_materia[a])
        acum = prefijos[a]
        i = len(acum) - 1 - pendientes[a]
        return cantidad, acum[i + cantidad] - acum[i]

    cotas = [cota_materia(a) for a in pendientes]
    posibles = sum(n for n, _ in cotas)
    prioridad_posible = sum(p for _, p in cotas)
    asignadas = prioridad = 0

    def mover(i, grupo, paso):
        """Aplica (paso=1) o revierte (paso=-1) una decisión."""
        nonlocal posibles, prioridad_posible, asignadas, prioridad
        e, a, p = pedidos[i]
        antes_n, antes_p = cota_materia(a)
        pendientes[a] -= paso
        if grupo is not None:
            if paso == 1:
                h[e].append(grupo)
            else:
                h[e].pop()
            libres[grupo] -= paso
            libres_materia[a] -= paso
            asignadas += paso
            prioridad += paso * p
        despues_n, despues_p = cota_materia(a)
        posibles += despues_n - antes_n
        prioridad_posible += despues_p - antes_p

    def decisiones(i):
        e, a, _ = pedidos[i]
        for g in alternativas[a]:
            if libres[g] and all(not cruzan(g, otro) for otro in h[e]):
                yield g
        yield None  # También se permite dejar pendiente la solicitud.

    # Cada iterador guarda la siguiente opción de un nivel del árbol.
    # La pila explícita admite instancias con miles de solicitudes.
    pila = [decisiones(0)]
    camino = []
    nodos = 1
    while pila:
        i = len(pila) - 1
        g = next(pila[-1], SIN_ALTERNATIVA)
        if g is SIN_ALTERNATIVA:
            pila.pop()
            if camino:
                mover(i - 1, camino.pop(), -1)
            continue
        if nodos == limite_nodos:
            return ResultadoBusqueda(mejor, nodos, limite_nodos, False)
        nodos += 1
        mover(i, g, 1)
        if (asignadas + posibles, prioridad + prioridad_posible) >= tuple(mejor_valor[:2]):
            if i + 1 < len(pedidos):
                camino.append(g)
                pila.append(decisiones(i + 1))
                continue
            valor = evaluar(x, h)["objetivo"]
            if valor > mejor_valor:
                mejor_valor = valor
                mejor = {e: sorted(grupos) for e, grupos in h.items()}
        mover(i, g, -1)
    return ResultadoBusqueda(mejor, nodos, limite_nodos, True)


def exacto(x: Instancia, limite: int = 50_000) -> dict[str, list[str]]:
    """Enumera la opción de omitir o elegir una sección por solicitud."""
    alternativas = opciones(x)
    pedidos = [(e, a) for e in sorted(x.estudiantes)
               for a in sorted(x.estudiantes[e].solicitudes) if alternativas[a]]
    elecciones = []
    combinaciones = 1
    for _, a in pedidos:
        combinaciones *= 1 + len(alternativas[a])
        if combinaciones > limite:
            raise ValueError(f"el oráculo supera el límite de {limite} combinaciones")
        elecciones.append([None, *alternativas[a]])

    mejor = None
    mejor_valor = None
    for grupos in product(*elecciones):
        h = {e: [] for e in sorted(x.estudiantes)}
        for (e, _), g in zip(pedidos, grupos):
            if g is not None:
                h[e].append(g)
        if validar(x, h):
            continue
        valor = evaluar(x, h)["objetivo"]
        if mejor_valor is None or valor > mejor_valor:
            mejor, mejor_valor = h, valor
    return {e: sorted(grupos) for e, grupos in mejor.items()}
