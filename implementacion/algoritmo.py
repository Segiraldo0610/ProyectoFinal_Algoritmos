"""Asignación voraz, backtracking con poda y fuerza bruta.

En los tres métodos, x es la Instancia cargada. Reúne a los estudiantes
con sus solicitudes, prioridades y preferencias, los grupos con sus
sesiones y cupos, y las distancias entre salones.
Usamos e para un estudiante, a para una asignatura y g para un grupo.
Un horario h relaciona cada estudiante con los grupos que se le asignaron.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from itertools import product

from modelo import Instancia, evaluar, validar


LIMITE_NODOS = 15_000  # Máximo de nodos del backtracking, incluida la raíz.
SIN_ALTERNATIVA = object()  # El nivel se agotó. None significa dejar pendiente.


@dataclass(frozen=True)
class ResultadoBusqueda:
    """Mejor horario válido, trabajo realizado y estado de la búsqueda.

    completa indica que se agotó el árbol con poda y se comprobó el
    óptimo. Si se alcanza el límite, horarios conserva el mejor hallado.
    """

    horarios: dict[str, list[str]]
    nodos: int
    limite_nodos: int
    completa: bool


def opciones(x: Instancia) -> dict[str, list[str]]:
    """Construye alternativas[a], la lista de IDs de grupos de la materia a.

    Las listas se ordenan por ID de grupo. Una asignatura sin oferta
    devuelve una lista vacía.
    """
    por_materia = defaultdict(list)
    for nombre, g in sorted(x.grupos.items()):
        por_materia[g.asignatura].append(nombre)
    return por_materia


def detector_cruces(x):
    """Crea la función que compara grupos y recuerda los cruces consultados."""
    @lru_cache(maxsize=100_000)
    def cruzan(g, otro):
        """Devuelve True si dos grupos tienen sesiones que se solapan.

        g y otro son IDs de grupos. Hay cruce si dos sesiones son del
        mismo día y comparten tiempo. Si una termina justo cuando
        empieza la otra, se pueden asignar ambas.
        """
        return any(a.dia == b.dia and a.inicio < b.fin and b.inicio < a.fin
                   for a in x.grupos[g].franjas for b in x.grupos[otro].franjas)

    return cruzan


def construir_voraz(x, alternativas, cruzan):
    """Toma el primer grupo compatible con cupo por cada solicitud.

    x contiene los datos de entrada. alternativas[a] guarda los IDs
    de los grupos de la asignatura a. cruzan(g, otro) indica si el grupo
    que se está probando se solapa con otro que ya tiene el estudiante.
    """
    h = {e: [] for e in sorted(x.estudiantes)}
    # libres[g] cuenta los cupos que todavía se pueden usar en el grupo g.
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
    """Explora decisiones y deshace cambios al retroceder.

    limite_nodos es el máximo de estados que se pueden visitar desde
    la raíz, contando también los que se descartan con la poda.
    Si quedan ramas al llegar al límite, devuelve la mejor asignación
    válida encontrada hasta ese momento.
    """
    if limite_nodos < 1:
        raise ValueError("el límite de nodos debe ser positivo")
    alternativas = opciones(x)
    cruzan = detector_cruces(x)
    # mejor guarda una asignación válida para todo el conjunto de estudiantes,
    # aunque algunas solicitudes queden sin atender.
    mejor = construir_voraz(x, alternativas, cruzan)
    # La terna compara cobertura, suma de prioridades y puntaje de preferencias.
    mejor_valor = evaluar(x, mejor)["objetivo"]
    # Cada pedido (e, a, p) es una solicitud con prioridad p.
    # Primero van las materias con menos grupos y luego las de mayor prioridad.
    # Las materias sin oferta quedan pendientes sin abrir ramas para ellas.
    pedidos = sorted(
        ((e, a, p) for e, alumno in x.estudiantes.items()
         for a, p in alumno.solicitudes.items() if alternativas[a]),
        key=lambda solicitud: (len(alternativas[solicitud[1]]), -solicitud[2],
                               solicitud[0], solicitud[1]),
    )
    if not pedidos:
        return ResultadoBusqueda(mejor, 1, limite_nodos, True)

    # h es el horario parcial de la rama actual.
    h = {e: [] for e in mejor}
    libres = {g: grupo.capacidad for g, grupo in x.grupos.items()}
    # libres_materia[a] suma los cupos libres de todos los grupos de a.
    libres_materia = Counter()
    for g, grupo in x.grupos.items():
        libres_materia[grupo.asignatura] += libres[g]

    # pendientes[a] cuenta las solicitudes de a aún sin decisión en esta rama.
    pendientes = Counter(a for _, a, _ in pedidos)
    # prefijos[a][j] suma las prioridades de los primeros j pedidos de a.
    # Así se puede calcular la suma de cualquier tramo con una resta.
    prefijos = defaultdict(lambda: [0])
    for _, a, p in pedidos:
        prefijos[a].append(prefijos[a][-1] + p)

    def cota_materia(a):
        """Acota cuántas solicitudes de a cabrían y qué prioridad sumarían."""
        cantidad = min(pendientes[a], libres_materia[a])
        acum = prefijos[a]
        # i indica cuántas solicitudes de a ya se decidieron en esta rama.
        i = len(acum) - 1 - pendientes[a]
        return cantidad, acum[i + cantidad] - acum[i]

    cotas = [cota_materia(a) for a in pendientes]
    # Cotas adicionales de todas las materias. Se suman al valor de h.
    posibles = sum(n for n, _ in cotas)
    prioridad_posible = sum(p for _, p in cotas)
    # Número de solicitudes atendidas y suma de prioridades en h.
    asignadas = prioridad = 0

    def mover(i, grupo, paso):
        """Aplica (paso=1) o revierte (paso=-1) la decisión de pedidos[i].

        Con grupo=None la decisión consiste en dejar la solicitud pendiente.
        En ese caso cambian las solicitudes por explorar y su cota.
        """
        nonlocal posibles, prioridad_posible, asignadas, prioridad
        e, a, p = pedidos[i]
        # Se recalcula únicamente la cota de la materia que cambió.
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
        """Genera las opciones de grupo u omisión para la solicitud i."""
        e, a, _ = pedidos[i]
        for g in alternativas[a]:
            if libres[g] and all(not cruzan(g, otro) for otro in h[e]):
                yield g
        yield None  # También se permite dejar pendiente la solicitud.

    # Cada iterador guarda la siguiente opción de un nivel del árbol.
    # La pila explícita admite instancias con miles de solicitudes.
    pila = [decisiones(0)]
    # camino guarda las decisiones activas para revertirlas en orden inverso.
    camino = []
    nodos = 1  # La raíz cuenta como el primer nodo.
    while pila:
        i = len(pila) - 1  # Profundidad actual e índice dentro de pedidos.
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
        # Se poda solo si la cota queda por debajo del mejor par. Con empate
        # todavía puede mejorar el tercer componente, las preferencias.
        if (asignadas + posibles, prioridad + prioridad_posible) >= tuple(mejor_valor[:2]):
            if i + 1 < len(pedidos):
                camino.append(g)
                pila.append(decisiones(i + 1))
                continue
            # Este nodo ya tiene una decisión para cada solicitud con oferta.
            valor = evaluar(x, h)["objetivo"]
            if valor > mejor_valor:
                mejor_valor = valor
                mejor = {e: sorted(grupos) for e, grupos in h.items()}
        mover(i, g, -1)
    return ResultadoBusqueda(mejor, nodos, limite_nodos, True)


def fuerza_bruta(x: Instancia, limite: int = 50_000) -> dict[str, list[str]]:
    """Aplica fuerza bruta y conserva la mejor asignación válida.

    limite es el máximo de combinaciones permitido. Si hay más,
    se avisa antes de probarlas.
    """
    alternativas = opciones(x)
    pedidos = [(e, a) for e in sorted(x.estudiantes)
               for a in sorted(x.estudiantes[e].solicitudes) if alternativas[a]]
    # elecciones[i] contiene None y los grupos del i-ésimo pedido.
    elecciones = []
    # combinaciones es el producto de las opciones de cada pedido, contando
    # las combinaciones que podrían resultar inválidas. Dos pedidos de dos
    # grupos cada uno dan (2 + 1) × (2 + 1) = 9 combinaciones.
    combinaciones = 1
    for _, a in pedidos:
        combinaciones *= 1 + len(alternativas[a])
        if combinaciones > limite:
            raise ValueError(f"el oráculo supera el límite de {limite} combinaciones")
        elecciones.append([None, *alternativas[a]])

    mejor = None  # Primera solución válida aún por encontrar.
    mejor_valor = None  # Terna de esa solución una vez evaluada.
    # product genera una tupla por vez. zip enlaza cada decisión con su pedido.
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


# Nombre anterior para los programas que ya lo importaban.
exacto = fuerza_bruta
