import csv
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from datos import generar
from modelo import Instancia


class DatosCSVTest(unittest.TestCase):
    def test_vuelta_completa_conserva_el_modelo(self):
        from archivos_csv import escribir_tablas, leer_tablas
        with TemporaryDirectory() as tmp:
            carpeta = Path(tmp) / "entrada"
            datos = generar("pequeno", 202630)
            escribir_tablas(datos, carpeta)
            self.assertEqual(Instancia.desde(datos), Instancia.desde(leer_tablas(carpeta)))
            with self.assertRaises(FileExistsError):
                escribir_tablas(datos, carpeta)

    def test_validacion_identifica_archivo_fila_y_clave(self):
        from archivos_csv import escribir_tablas, leer_tablas
        for archivo, fila, mensaje in (
            ("solicitudes.csv", "E001,A01,1", "clave duplicada"),
            ("solicitudes.csv", "E999,A01,1", "referencia desconocida"),
            ("horarios.csv", "A01-G1,1,601,600", "franja inválida"),
            ("preferencias_profesor.csv", "E001,P999,4", "referencia desconocida"),
        ):
            with self.subTest(archivo=archivo, fila=fila), TemporaryDirectory() as tmp:
                carpeta = Path(tmp) / "entrada"
                escribir_tablas(generar("pequeno"), carpeta)
                ruta = carpeta / archivo
                if mensaje == "clave duplicada":
                    with ruta.open(encoding="utf-8", newline="") as flujo:
                        lector = csv.reader(flujo)
                        next(lector)
                        fila = ",".join(next(lector))
                with ruta.open("a", encoding="utf-8", newline="") as flujo:
                    flujo.write(fila + "\n")
                with self.assertRaisesRegex(ValueError, rf"{archivo}:\d+:.*{mensaje}"):
                    leer_tablas(carpeta)

    def test_encabezado_incorrecto_y_distancia_faltante(self):
        from archivos_csv import escribir_tablas, leer_tablas
        for archivo, esperado in (("grupos.csv", "encabezado"), ("distancias.csv", "matriz incompleta")):
            with self.subTest(archivo=archivo), TemporaryDirectory() as tmp:
                carpeta = Path(tmp) / "entrada"
                escribir_tablas(generar("pequeno"), carpeta)
                ruta = carpeta / archivo
                lineas = ruta.read_text(encoding="utf-8").splitlines()
                lineas = ["incorrecto", *lineas[1:]] if archivo == "grupos.csv" else lineas[:-1]
                ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, esperado):
                    leer_tablas(carpeta)

    def test_cli_genera_y_resuelve_directamente_csv(self):
        import json
        cli = Path(__file__).with_name("horarios.py")
        with TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            carpeta, salida = tmp / "entrada", tmp / "salida.json"
            for args in (("generar", "pequeno", carpeta, "--formato", "csv"),
                         ("resolver", carpeta, salida),
                         ("verificar", carpeta, salida)):
                r = subprocess.run([sys.executable, "-B", str(cli), *map(str, args)],
                                   capture_output=True)
                self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(json.loads(r.stdout)["valida"])
            self.assertEqual(len(json.loads(salida.read_text(encoding="utf-8"))["horarios"]), 5)
            self.assertEqual(json.loads((carpeta / "meta.json").read_text())["semilla"], 202630)


if __name__ == "__main__":
    unittest.main()
