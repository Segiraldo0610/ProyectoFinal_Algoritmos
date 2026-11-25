from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


class DemoTest(unittest.TestCase):
    def test_genera_visualiza_y_verifica_una_instancia_csv(self):
        from sesion_demo import Sesion

        with TemporaryDirectory() as temp:
            s = Sesion()
            s.generar_csv(Path(temp) / "demo", "pequeno", 202630)
            self.assertEqual(len(s.tablas), 11)
            columnas, filas = s.tabla("solicitudes")
            self.assertEqual(columnas, ["estudiante_id", "asignatura_id", "prioridad"])
            self.assertEqual(filas[0], ["E001", "A01", "5"])
            resultado = s.asignar("propuesto")
            self.assertEqual(resultado["metricas"]["asignadas"], 10)
            self.assertEqual(resultado["metricas"]["solicitadas"], 15)
            self.assertEqual(s.verificar(), [])
            self.assertEqual(len(s.agenda("E001")), 3)
            self.assertTrue(any(e["pendientes"] for e in resultado["metricas"]["estudiantes"].values()))

    def test_cambiar_entrada_invalida_el_resultado_previsto(self):
        from sesion_demo import Sesion

        with TemporaryDirectory() as temp:
            carpeta = Path(temp)
            s = Sesion()
            s.generar_csv(carpeta / "demo", "pequeno", 202630)
            s.asignar("propuesto")
            s.cargar_caso("reparacion", carpeta / "reparacion")
            self.assertIsNone(s.resultado)
            self.assertEqual(s.asignar("base")["metricas"]["estudiantes"]["E1"]["pendientes"], ["B"])
            self.assertEqual(s.asignar("propuesto")["metricas"]["asignadas"], 2)
            self.assertEqual(s.verificar(), [])

    def test_carga_fallida_preserva_la_instancia_actual(self):
        from sesion_demo import Sesion

        with TemporaryDirectory() as temp:
            carpeta = Path(temp)
            s = Sesion()
            s.cargar_caso("reparacion", carpeta / "valida")
            s.asignar("base")
            with self.assertRaises(OSError):
                s.cargar_csv(carpeta / "sin-archivos")
            self.assertTrue(s.carpeta.samefile(carpeta / "valida"))
            self.assertEqual(s.resultado["metodo"], "base")

    def test_verificador_detecta_cruce_y_bloquea_exportar_a_la_entrada(self):
        from sesion_demo import Sesion

        with TemporaryDirectory() as temp:
            base = Path(temp)
            s = Sesion()
            s.cargar_caso("reparacion", base / "entrada")
            resultado = s.asignar("propuesto")
            s.guardar(base / "salida.json")
            self.assertTrue((base / "salida.json").is_file())
            with self.assertRaises(ValueError):
                s.guardar(base / "entrada" / "solicitudes.csv")
            resultado["horarios"]["E1"] = ["A1", "B1"]
            self.assertIn("cruce", " ".join(s.verificar()))

    def test_botones_y_vistas_conectan_con_el_motor(self):
        import tkinter as tk
        from tkinter import filedialog
        from unittest.mock import patch
        from interfaz import Aplicacion

        try:
            raiz = tk.Tk()
        except tk.TclError as exc:
            self.skipTest(f"se necesita una sesión gráfica: {exc}")
        raiz.withdraw()
        try:
            with TemporaryDirectory() as temp:
                app = Aplicacion(raiz)
                with patch.object(filedialog, "askdirectory", return_value=temp):
                    app.boton_generar.invoke()
                self.assertEqual(len(list(Path(temp).glob("*/*.csv"))), 11)
                app.boton_asignar.invoke()
                self.assertEqual(app.kpi_cobertura.get(), "66,7 %")
                self.assertIn("Óptimo comprobado", app.estado.get())
                self.assertGreater(len(app.tabla_agenda.get_children()), 0)
                app.estudiante.set("E005")
                app.mostrar_estudiante()
                self.assertTrue(app.tabla_pendientes.get_children())
                app.boton_verificar.invoke()
                self.assertEqual(app.titulo_verificacion.get(), "Asignación válida")
                self.assertEqual(app.pestanas.index(app.pestanas.select()), 2)
        finally:
            raiz.destroy()


if __name__ == "__main__":
    unittest.main()
