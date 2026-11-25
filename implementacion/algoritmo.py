"""Asignación voraz, reparación local y oráculo para pruebas diminutas."""
from collections import defaultdict
from functools import lru_cache
from itertools import product

from modelo import Instancia, evaluar, medir, validar


def opciones(x: Instancia) -> dict[str, list[str]]:
    por_materia = defaultdict(list)
    for nombre, g in sorted(x.grupos.items()):
        por_materia[g.asignatura].append(nombre)
    return por_materia


def resolver(x: Instancia, metodo: str = "propuesto") -> dict[str, list[str]]:
    if metodo not in {"base", "propuesto"}:
        raise ValueError(f"método desconocido: {metodo}")
    alternativas = opciones(x)

    @lru_cache(maxsize=100_000)
    def cruzan(g, otro):
        return any(a.dia == b.dia and a.inicio < b.fin and b.inicio < a.fin
                   for a in x.grupos[g].franjas for b in x.grupos[otro].franjas)

    base = construir(x, alternativas, cruzan, guiado=False, reparar=metodo == "propuesto")
    if metodo == "base":
        return base
    guiado = construir(x, alternativas, cruzan, guiado=True, reparar=True)
    return max((guiado, base), key=lambda h: evaluar(x, h)["objetivo"])


def construir(x, alternativas, cruzan, *, guiado, reparar):
    h = {e: [] for e in sorted(x.estudiantes)}
    libres = {g: v.capacidad for g, v in x.grupos.items()}
    pedidos = [(e, a) for e in h for a in sorted(x.estudiantes[e].solicitudes)]

    if guiado:
        flexibilidad = {
            e: sum(len(alternativas[a]) for a in alumno.solicitudes)
            for e, alumno in x.estudiantes.items()
        }
        pedidos.sort(key=lambda par: (
            len(alternativas[par[1]]), -x.estudiantes[par[0]].solicitudes[par[1]],
            flexibilidad[par[0]], *par,
        ))

    def calidad(e, propuesta):
        return medir(x, e, propuesta, h)["calidad"]

    pendientes = []
    for e, a in pedidos:
        elegibles = [g for g in alternativas[a]
                     if libres[g] and all(not cruzan(g, otro) for otro in h[e])]
        if elegibles:
            elegido = (max(elegibles, key=lambda g: calidad(e, h[e] + [g]))
                       if guiado else elegibles[0])
            h[e].append(elegido)
            libres[elegido] -= 1
        else:
            pendientes.append((e, a))

    if reparar:
        for e, a in pendientes:
            mejor = None
            mejor_calidad = None
            for nuevo in alternativas[a]:
                if not libres[nuevo]:
                    continue
                bloqueos = [g for g in h[e] if cruzan(nuevo, g)]
                if len(bloqueos) > 1:
                    continue
                if bloqueos:
                    sale = bloqueos[0]
                    resto = [g for g in h[e] if g != sale]
                    cambios = ((sale, entra, resto + [entra, nuevo])
                               for entra in alternativas[x.grupos[sale].asignatura]
                               if entra != sale and libres[entra] and not cruzan(entra, nuevo)
                               and all(not cruzan(entra, g) for g in resto))
                else:
                    cambios = iter([(None, None, h[e] + [nuevo])])
                for sale, entra, propuesta in cambios:
                    valor = calidad(e, propuesta)
                    if mejor_calidad is None or valor > mejor_calidad:
                        mejor = sale, entra, nuevo, propuesta
                        mejor_calidad = valor
            if mejor is not None:
                sale, entra, nuevo, propuesta = mejor
                h[e] = propuesta
                libres[nuevo] -= 1
                if sale is not None:
                    libres[sale] += 1
                    libres[entra] -= 1
    return {e: sorted(grupos) for e, grupos in h.items()}


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
