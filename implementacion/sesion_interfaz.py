"""Gestiona los datos y las asignaciones de la interfaz de escritorio."""

import csv
from pathlib import Path

from archivos_csv import ESQUEMA, escribir_tablas, leer_tablas
from horarios import emitir, generar_csv, leer, procesar
from modelo import Instancia, validar


CARPETA_PROGRAMA = Path(__file__).resolve().parent
CASOS = ("reparacion", "cupo", "brecha")


class Sesion:
    tablas = tuple(ESQUEMA)

    def __init__(self):
        self.carpeta = None
        self.instancia = None
        self.resultado = None

    def cargar_csv(self, carpeta):
        instancia = Instancia.desde(leer_tablas(carpeta))
        self.carpeta = carpeta.resolve()
        self.instancia = instancia
        self.resultado = None

    def generar_csv(self, carpeta, escenario, semilla):
        generar_csv(escenario, semilla, carpeta)
        self.cargar_csv(carpeta)

    def cargar_caso(self, caso, carpeta):
        if caso not in CASOS:
            raise ValueError("Caso de prueba desconocido.")
        datos = leer(CARPETA_PROGRAMA / "casos" / f"{caso}.json")
        escribir_tablas(datos, carpeta)
        self.cargar_csv(carpeta)

    def tabla(self, nombre):
        if self.carpeta is None or nombre not in self.tablas:
            raise ValueError("Selecciona una tabla CSV.")
        with (self.carpeta / f"{nombre}.csv").open(encoding="utf-8-sig", newline="") as archivo:
            lector = csv.reader(archivo)
            return next(lector), list(lector)

    def asignar(self, metodo):
        if self.instancia is None:
            raise ValueError("Carga una carpeta CSV para continuar.")
        self.resultado = procesar(self.instancia, metodo)
        return self.resultado

    def verificar(self):
        return validar(self.instancia, self._resultado()["horarios"])

    def agenda(self, estudiante):
        resultado = self._resultado()
        sesiones = []
        for nombre in resultado["horarios"][estudiante]:
            grupo = self.instancia.grupos[nombre]
            for franja in grupo.franjas:
                sesiones.append((franja.dia, franja.inicio, franja.fin, grupo.asignatura,
                                 nombre, grupo.profesor, grupo.salon))
        return sorted(sesiones)

    def guardar(self, ruta):
        resultado = self._resultado()
        if ruta.resolve().is_relative_to(self.carpeta):
            raise ValueError("Guarda el resultado fuera de la carpeta CSV de entrada.")
        emitir(resultado, ruta)

    def _resultado(self):
        if self.resultado is None:
            raise ValueError("Asigna un horario para continuar.")
        return self.resultado
