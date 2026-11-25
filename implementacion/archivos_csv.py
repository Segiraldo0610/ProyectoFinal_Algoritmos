"""Contrato CSV v1 de una instancia y adaptación al modelo de horarios."""
import csv
from pathlib import Path

from modelo import Instancia


# Columnas, cantidad de campos de la clave y referencias a catálogos.
ESQUEMA = {
    "asignaturas": ("asignatura_id", 1, {}),
    "profesores": ("profesor_id", 1, {}),
    "salones": ("salon_id", 1, {}),
    "estudiantes": ("estudiante_id inicio_min fin_max compacto", 1, {}),
    "grupos": ("grupo_id asignatura_id profesor_id salon_id capacidad", 1,
               {1: "asignaturas", 2: "profesores", 3: "salones"}),
    "horarios": ("grupo_id dia inicio fin", 4, {0: "grupos"}),
    "solicitudes": ("estudiante_id asignatura_id prioridad", 2,
                    {0: "estudiantes", 1: "asignaturas"}),
    "preferencias_profesor": ("estudiante_id profesor_id valor", 2,
                              {0: "estudiantes", 1: "profesores"}),
    "dias_libres": ("estudiante_id dia", 2, {0: "estudiantes"}),
    "companeros": ("estudiante_id companero_id", 2, {0: "estudiantes", 1: "estudiantes"}),
    "distancias": ("origen_id destino_id metros", 2, {0: "salones", 1: "salones"}),
}


def numero(celda, lugar, minimo, maximo=None):
    if not (celda.isascii() and celda.isdecimal()) or (len(celda) > 1 and celda[0] == "0"):
        raise ValueError(f"{lugar}: se esperaba un entero, se recibió {celda!r}")
    valor = int(celda)
    if valor < minimo or (maximo is not None and valor > maximo):
        raise ValueError(f"{lugar}: entero fuera de dominio: {valor}")
    return valor


def leer_filas(carpeta, nombre, columnas):
    ruta = carpeta / f"{nombre}.csv"
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.reader(archivo, strict=True)
        try:
            if next(lector, None) != columnas:
                raise ValueError(f"{ruta.name}:1: encabezado esperado: {','.join(columnas)}")
            for fila in lector:
                lugar = f"{ruta.name}:{lector.line_num}"
                if len(fila) != len(columnas) or any(not v or v != v.strip() for v in fila):
                    raise ValueError(f"{lugar}: columnas incompletas o espacios en los extremos")
                yield lugar, fila
        except csv.Error as error:
            raise ValueError(f"{ruta.name}:{lector.line_num}: CSV inválido: {error}") from error


def leer_tablas(carpeta: Path) -> dict:
    filas = {}
    claves = {}
    for nombre, (cabecera, longitud, referencias) in ESQUEMA.items():
        filas[nombre] = []
        claves[nombre] = set()
        for lugar, fila in leer_filas(carpeta, nombre, cabecera.split()):
            clave = tuple(fila[:longitud])
            if clave in claves[nombre]:
                raise ValueError(f"{lugar}: clave duplicada {clave}")
            for indice, destino in referencias.items():
                if (fila[indice],) not in claves[destino]:
                    raise ValueError(f"{lugar}: referencia desconocida {fila[indice]!r} en {destino}.csv")
            claves[nombre].add(clave)
            filas[nombre].append((lugar, fila))

    estudiantes = {}
    for lugar, (e, inicio, fin, compacto) in filas["estudiantes"]:
        h_min = numero(inicio, lugar, 0, 1439)
        estudiantes[e] = dict(id=e, inicio_min=h_min, fin_max=numero(fin, lugar, h_min + 1, 1440),
                              compacto=bool(numero(compacto, lugar, 0, 1)), solicitudes={},
                              profesor={}, dias_libres=[], companeros=[])
    grupos = {
        g: dict(id=g, asignatura=a, profesor=p, salon=s, capacidad=numero(c, lugar, 1), franjas=[])
        for lugar, (g, a, p, s, c) in filas["grupos"]
    }
    for lugar, (g, dia, ini, fin) in filas["horarios"]:
        d = numero(dia, lugar, 1, 5)
        a, b = numero(ini, lugar, 0, 1439), numero(fin, lugar, 1, 1440)
        if b <= a:
            raise ValueError(f"{lugar}: franja inválida, fin debe ser mayor que inicio")
        grupos[g]["franjas"].append([d, a, b])
    for lugar, (e, a, p) in filas["solicitudes"]:
        estudiantes[e]["solicitudes"][a] = numero(p, lugar, 1)
    for lugar, (e, p, v) in filas["preferencias_profesor"]:
        estudiantes[e]["profesor"][p] = numero(v, lugar, 0, 5)
    for lugar, (e, d) in filas["dias_libres"]:
        estudiantes[e]["dias_libres"].append(numero(d, lugar, 1, 5))
    for lugar, (e, amigo) in filas["companeros"]:
        if e == amigo:
            raise ValueError(f"{lugar}: un estudiante no puede ser su propio compañero")
        estudiantes[e]["companeros"].append(amigo)
    distancias = {s: {} for _, (s,) in filas["salones"]}
    for lugar, (a, b, metros) in filas["distancias"]:
        distancias[a][b] = numero(metros, lugar, 0)
    datos = dict(grupos=list(grupos.values()), estudiantes=list(estudiantes.values()),
                 distancias=distancias)
    Instancia.desde(datos)
    return datos


def escribir_tablas(datos: dict, carpeta: Path) -> None:
    """Emite archivos estables para una entrada validada en una carpeta nueva."""
    x = Instancia.desde(datos)
    filas = {nombre: [] for nombre in ESQUEMA}
    asignaturas = set()
    profesores = set()
    for nombre, g in x.grupos.items():
        asignaturas.add(g.asignatura)
        profesores.add(g.profesor)
        filas["grupos"].append((nombre, g.asignatura, g.profesor, g.salon, g.capacidad))
        filas["horarios"].extend((nombre, f.dia, f.inicio, f.fin) for f in g.franjas)
    for nombre, e in x.estudiantes.items():
        asignaturas.update(e.solicitudes)
        profesores.update(e.profesor)
        filas["estudiantes"].append((nombre, e.inicio_min, e.fin_max, int(e.compacto)))
        filas["solicitudes"].extend((nombre, a, p) for a, p in e.solicitudes.items())
        filas["preferencias_profesor"].extend((nombre, p, v) for p, v in e.profesor.items())
        filas["dias_libres"].extend((nombre, d) for d in e.dias_libres)
        filas["companeros"].extend((nombre, amigo) for amigo in e.companeros)
    filas["asignaturas"] = [(a,) for a in asignaturas]
    filas["profesores"] = [(p,) for p in profesores]
    filas["salones"] = [(s,) for s in x.distancias]
    filas["distancias"] = [(a, b, d) for a, otros in x.distancias.items() for b, d in otros.items()]
    carpeta.mkdir(parents=True, exist_ok=False)
    for nombre, (cabecera, _, _) in ESQUEMA.items():
        with (carpeta / f"{nombre}.csv").open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo, lineterminator="\n")
            escritor.writerow(cabecera.split())
            escritor.writerows(sorted(filas[nombre]))
