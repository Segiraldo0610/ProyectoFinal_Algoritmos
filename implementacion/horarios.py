"""Genera entradas, asigna horarios, verifica salidas y mide resultados."""
import argparse
import json
from pathlib import Path
from platform import python_version
import sys
from time import perf_counter

from algoritmo import exacto, resolver
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


def procesar(x, metodo):
    inicio = perf_counter()
    h = exacto(x) if metodo == "exacto" else resolver(x, metodo)
    tiempo = perf_counter() - inicio
    errores = validar(x, h)
    if errores:
        raise RuntimeError("el solucionador devolvió una salida inválida: " + ", ".join(errores))
    return dict(metodo=metodo, tiempo_s=round(tiempo, 6), horarios=h, metricas=evaluar(x, h))


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
    sol.add_argument("--metodo", choices=("base", "propuesto", "exacto"), default="propuesto")
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
                emitir(procesar(x, args.metodo), args.salida)
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
