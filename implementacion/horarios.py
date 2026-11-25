"""Genera entradas, asigna horarios, verifica salidas y mide resultados."""
import argparse
import json
from pathlib import Path
from platform import python_version
import sys
from time import perf_counter

from algoritmo import LIMITE_NODOS, backtracking, exacto, resolver
from archivos_csv import escribir_tablas, leer_tablas
from datos import ESCENARIOS, generar
from modelo import Instancia, evaluar, validar


def leer(ruta):
    def pares_sin_repetir(pares):
        resultado = {}
        for k, v in pares:
            if k in resultado:
                raise ValueError(f"clave JSON repetida: {k}")
            resultado[k] = v
        return resultado
    return json.loads(ruta.read_text(encoding="utf-8-sig"), object_pairs_hook=pares_sin_repetir)


def emitir(datos, ruta=None):
    texto = json.dumps(datos, ensure_ascii=ruta is None, indent=2, sort_keys=True) + "\n"
    if ruta is None:
        print(texto, end="")
    else:
        ruta.write_text(texto, encoding="utf-8")


def generar_csv(escenario, semilla, carpeta):
    escribir_tablas(generar(escenario, semilla), carpeta)
    emitir(dict(escenario=escenario, semilla=semilla, esquema_csv=1,
                python=python_version()), carpeta / "meta.json")


def procesar(x, metodo, limite_nodos=LIMITE_NODOS):
    inicio = perf_counter()
    if metodo in ("propuesto", "backtracking"):
        busqueda = backtracking(x, limite_nodos)
        h = busqueda.horarios
    else:
        busqueda = None
        h = exacto(x) if metodo == "exacto" else resolver(x, metodo)
    tiempo = perf_counter() - inicio
    errores = validar(x, h)
    if errores:
        raise RuntimeError("el solucionador devolvió una salida inválida: " + ", ".join(errores))
    salida = dict(metodo=metodo, tiempo_s=round(tiempo, 6), horarios=h, metricas=evaluar(x, h))
    if busqueda is not None:
        salida["busqueda"] = dict(nodos=busqueda.nodos, limite_nodos=busqueda.limite_nodos,
                                  completa=busqueda.completa)
    return salida


def comparar(semillas):
    filas = []
    for escala in ESCENARIOS:
        for semilla in semillas:
            x = Instancia.desde(generar(escala, semilla))
            fila = {"escenario": escala, "semilla": semilla,
                    "estudiantes": len(x.estudiantes), "grupos": len(x.grupos)}
            for metodo in ("base", "propuesto"):
                resultado = procesar(x, metodo)
                fila[metodo] = {k: v for k, v in resultado["metricas"].items() if k != "estudiantes"}
                fila[metodo]["tiempo_s"] = resultado["tiempo_s"]
                if "busqueda" in resultado:
                    fila[metodo]["busqueda"] = resultado["busqueda"]
            filas.append(fila)
    return filas


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="accion", required=True)
    gen = sub.add_parser("generar", help="crea una instancia sintética")
    gen.add_argument("escenario", choices=ESCENARIOS)
    gen.add_argument("salida", type=Path, help="archivo JSON o carpeta CSV nueva")
    gen.add_argument("--semilla", type=int, default=202630)
    gen.add_argument("--formato", choices=("json", "csv"), default="json")
    sol = sub.add_parser("resolver", help="asigna grupos y reporta métricas")
    sol.add_argument("entrada", type=Path)
    sol.add_argument("salida", type=Path)
    sol.add_argument("--metodo", choices=("base", "propuesto", "backtracking", "exacto"),
                     default="propuesto")
    sol.add_argument("--limite-nodos", type=int, default=LIMITE_NODOS,
                     help="máximo de nodos del backtracking")
    ver = sub.add_parser("verificar", help="valida una asignación y recalcula sus métricas")
    ver.add_argument("entrada", type=Path)
    ver.add_argument("resultado", type=Path)
    bench = sub.add_parser("evaluar", help="compara base y propuesta en las tres escalas")
    bench.add_argument("salida", type=Path)
    bench.add_argument("--semillas", nargs="+", type=int, default=[202630, 202631, 202632])
    args = parser.parse_args(argv)
    try:
        if args.accion == "generar":
            if args.formato == "csv":
                generar_csv(args.escenario, args.semilla, args.salida)
            else:
                emitir(generar(args.escenario, args.semilla), args.salida)
        elif args.accion == "evaluar":
            emitir(comparar(args.semillas), args.salida)
        else:
            entrada = leer_tablas(args.entrada) if args.entrada.is_dir() else leer(args.entrada)
            x = Instancia.desde(entrada)
            if args.accion == "resolver":
                if args.entrada.resolve() == args.salida.resolve():
                    raise ValueError("use una ruta diferente para el resultado")
                if args.entrada.is_dir() and args.salida.resolve().is_relative_to(args.entrada.resolve()):
                    raise ValueError("guarde el resultado fuera de la carpeta CSV de entrada")
                emitir(procesar(x, args.metodo, args.limite_nodos), args.salida)
            else:
                h = leer(args.resultado)["horarios"]
                errores = validar(x, h)
                salida = {"valida": not errores, "errores": errores}
                if not errores:
                    salida["metricas"] = evaluar(x, h)
                emitir(salida)
                return int(bool(errores))
    except (ValueError, TypeError, KeyError, OSError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
