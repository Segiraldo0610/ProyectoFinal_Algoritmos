"""Contrato de entrada, verificación independiente y medición de horarios."""
from collections import Counter
from dataclasses import dataclass


def entero(valor, minimo, maximo=None):
    if (type(valor) is not int or valor < minimo
            or (maximo is not None and valor > maximo)):
        raise ValueError(f"entero fuera de dominio: {valor!r}")
    return valor


def identificador(valor):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"identificador inválido: {valor!r}")
    return valor


def mapa(valor):
    if not isinstance(valor, dict):
        raise ValueError("se esperaba un objeto JSON")
    return valor


def lista(valor):
    if not isinstance(valor, list):
        raise ValueError("se esperaba un arreglo JSON")
    return valor


@dataclass(frozen=True, order=True)
class Franja:
    dia: int
    inicio: int
    fin: int

    @classmethod
    def desde(cls, bruto):
        dia, inicio, fin = lista(bruto)
        entero(dia, 1, 5)
        entero(inicio, 0, 1439)
        entero(fin, inicio + 1, 1440)
        return cls(dia, inicio, fin)


@dataclass(frozen=True)
class Grupo:
    asignatura: str
    profesor: str
    salon: str
    capacidad: int
    franjas: tuple[Franja, ...]


@dataclass(frozen=True)
class Estudiante:
    solicitudes: dict[str, int]
    profesor: dict[str, int]
    inicio_min: int
    fin_max: int
    compacto: bool
    dias_libres: frozenset[int]
    companeros: frozenset[str]


@dataclass(frozen=True)
class Instancia:
    grupos: dict[str, Grupo]
    estudiantes: dict[str, Estudiante]
    distancias: dict[str, dict[str, int]]

    @classmethod
    def desde(cls, bruto):
        datos = mapa(bruto)
        grupos = {}
        for reg in lista(datos["grupos"]):
            fila = mapa(reg)
            nombre = identificador(fila["id"])
            franjas = tuple(sorted(Franja.desde(f) for f in lista(fila["franjas"])))
            if nombre in grupos or not franjas:
                raise ValueError(f"grupo duplicado o sin franjas: {nombre}")
            if any(a.dia == b.dia and b.inicio < a.fin for a, b in zip(franjas, franjas[1:])):
                raise ValueError(f"franjas internas solapadas: {nombre}")
            grupos[nombre] = Grupo(
                identificador(fila["asignatura"]), identificador(fila["profesor"]),
                identificador(fila["salon"]), entero(fila["capacidad"], 1), franjas,
            )

        distancias = {}
        for sala, fila in mapa(datos["distancias"]).items():
            distancias[identificador(sala)] = {
                identificador(otra): entero(d, 0) for otra, d in mapa(fila).items()
            }
        if any(g.salon not in distancias for g in grupos.values()):
            raise ValueError("falta un salón en la matriz de distancias")
        for sala, fila in distancias.items():
            if fila.keys() != distancias.keys() or fila[sala] != 0:
                raise ValueError(f"matriz incompleta o diagonal distinta de cero: {sala}")
        for sala, fila in distancias.items():
            if any(d != distancias[otra][sala] for otra, d in fila.items()):
                raise ValueError(f"matriz de distancias asimétrica: {sala}")

        estudiantes = {}
        for reg in lista(datos["estudiantes"]):
            fila = mapa(reg)
            nombre = identificador(fila["id"])
            solicitudes = {
                identificador(a): entero(p, 1) for a, p in mapa(fila["solicitudes"]).items()
            }
            if nombre in estudiantes or not solicitudes:
                raise ValueError(f"estudiante duplicado o sin solicitudes: {nombre}")
            inicio = entero(fila.get("inicio_min", 0), 0, 1439)
            compacto = fila.get("compacto", False)
            if type(compacto) is not bool:
                raise ValueError(f"compacto debe ser booleano: {nombre}")
            estudiantes[nombre] = Estudiante(
                solicitudes,
                {identificador(p): entero(v, 0, 5)
                 for p, v in mapa(fila.get("profesor", {})).items()},
                inicio,
                entero(fila.get("fin_max", 1440), inicio + 1, 1440),
                compacto,
                frozenset(entero(d, 1, 5) for d in lista(fila.get("dias_libres", []))),
                frozenset(identificador(e) for e in lista(fila.get("companeros", []))),
            )
        if not estudiantes:
            raise ValueError("se requiere al menos un estudiante")
        for nombre, e in estudiantes.items():
            if nombre in e.companeros or not e.companeros <= estudiantes.keys():
                raise ValueError(f"compañeros inválidos: {nombre}")
        return cls(grupos, estudiantes, distancias)


def validar(x: Instancia, horarios: dict[str, list[str]]) -> list[str]:
    """Verifica H sin llamar al solucionador ni usar su regla de compatibilidad."""
    if not isinstance(horarios, dict):
        return ["la asignación debe ser un objeto por estudiante"]
    errores = []
    cupos = Counter()
    if horarios.keys() != x.estudiantes.keys():
        errores.append("la asignación debe contener exactamente a los estudiantes de la entrada")
    for nombre, e in x.estudiantes.items():
        asignados = horarios.get(nombre, [])
        if not isinstance(asignados, list):
            errores.append(f"{nombre}: se esperaba una lista de grupos")
            continue
        materias = set()
        franjas = []
        for identificador_grupo in asignados:
            if not isinstance(identificador_grupo, str) or identificador_grupo not in x.grupos:
                errores.append(f"{nombre}: grupo desconocido {identificador_grupo!r}")
                continue
            g = x.grupos[identificador_grupo]
            if g.asignatura not in e.solicitudes:
                errores.append(f"{nombre}: asignatura no solicitada {g.asignatura}")
            if g.asignatura in materias:
                errores.append(f"{nombre}: asignatura repetida {g.asignatura}")
            materias.add(g.asignatura)
            cupos[identificador_grupo] += 1
            franjas.extend(g.franjas)
        ordenadas = sorted(franjas)
        if any(a.dia == b.dia and b.inicio < a.fin
               for a, b in zip(ordenadas, ordenadas[1:])):
            errores.append(f"{nombre}: cruce de horario")
    for g, total in sorted(cupos.items()):
        if total > x.grupos[g].capacidad:
            errores.append(f"{g}: cupo excedido ({total}/{x.grupos[g].capacidad})")
    return errores


def medir(x: Instancia, nombre: str, grupos: list[str], horarios) -> dict:
    e = x.estudiantes[nombre]
    asignaturas = {x.grupos[g].asignatura for g in grupos}
    clases = sorted((franja, x.grupos[g].salon) for g in grupos for franja in x.grupos[g].franjas)
    huecos = distancia = 0
    for (a, sala_a), (b, sala_b) in zip(clases, clases[1:]):
        if a.dia == b.dia:
            huecos += b.inicio - a.fin
            distancia += x.distancias[sala_a][sala_b]
    fuera = sum(f.fin - f.inicio - max(0, min(f.fin, e.fin_max)
                - max(f.inicio, e.inicio_min)) for f, _ in clases)
    dia_libre = sum(f.dia in e.dias_libres for f, _ in clases)
    notas = [e.profesor.get(x.grupos[g].profesor, 0) for g in grupos]
    notas_informadas = [nota for nota in notas if nota]
    coincidencias = sum(g in horarios[otro] for otro in e.companeros for g in grupos)
    calidad = (60 * sum(notas) + 120 * coincidencias - fuera - 120 * dia_libre
               - (huecos if e.compacto else 0) - distancia // 10)
    return {
        "solicitadas": len(e.solicitudes), "asignadas": len(asignaturas),
        "pendientes": sorted(e.solicitudes.keys() - asignaturas),
        "prioridad_atendida": sum(e.solicitudes[a] for a in asignaturas),
        "cobertura": len(asignaturas) / len(e.solicitudes),
        "huecos_min": huecos, "distancia_m": distancia, "min_fuera": fuera,
        "clases_en_dias_libres": dia_libre, "coincidencias": coincidencias,
        "profesor_promedio": (sum(notas_informadas) / len(notas_informadas)
                              if notas_informadas else None),
        "calidad": calidad,
    }


def evaluar(x: Instancia, horarios: dict[str, list[str]]) -> dict:
    por_estudiante = {e: medir(x, e, horarios[e], horarios) for e in sorted(x.estudiantes)}
    campos = ("solicitadas", "asignadas", "prioridad_atendida", "calidad",
              "huecos_min", "distancia_m", "min_fuera", "clases_en_dias_libres", "coincidencias")
    totales = {k: sum(m[k] for m in por_estudiante.values()) for k in campos}
    totales["cobertura"] = totales["asignadas"] / totales["solicitadas"]
    totales["objetivo"] = [totales[k] for k in ("asignadas", "prioridad_atendida", "calidad")]
    totales["estudiantes"] = por_estudiante
    return totales
