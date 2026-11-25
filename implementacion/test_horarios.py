import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def grupo(nombre, materia, inicio, fin, cupo=1, salon="R1", dia=1):
    return dict(id=nombre, asignatura=materia, profesor=nombre, salon=salon,
                capacidad=cupo, franjas=[[dia, inicio, fin]])


def estudiante(nombre, **solicitudes):
    return dict(id=nombre, solicitudes=solicitudes)


def entrada(grupos, estudiantes):
    return dict(grupos=grupos, estudiantes=estudiantes,
                distancias={"R1": {"R1": 0, "R2": 120},
                            "R2": {"R1": 120, "R2": 0}})


class HorariosTest(unittest.TestCase):
    def test_solapamiento_parcial_y_colindancia(self):
        from modelo import Instancia, validar
        x = Instancia.desde(entrada([
            grupo("A1", "A", 480, 540), grupo("B1", "B", 525, 600),
            grupo("B2", "B", 540, 600)], [estudiante("E1", A=1, B=1)]))
        self.assertIn("cruce", " ".join(validar(x, {"E1": ["A1", "B1"]})))
        self.assertEqual(validar(x, {"E1": ["A1", "B2"]}), [])

    def test_cupo_duplicado_y_grupo_no_solicitado(self):
        from modelo import Instancia, validar
        x = Instancia.desde(entrada([
            grupo("A1", "A", 480, 540), grupo("A2", "A", 540, 600),
            grupo("B1", "B", 600, 660)],
            [estudiante("E1", A=1), estudiante("E2", A=2)]))
        errores = " ".join(validar(x, {"E1": ["A1", "A2", "B1"], "E2": ["A1"]}))
        for palabra in ("cupo", "repetida", "no solicitada"):
            self.assertIn(palabra, errores)
        self.assertTrue(validar(x, {"E1": ["A1"]}))
        self.assertTrue(validar(x, {"E1": ["Z"], "E2": []}))

    def test_rechaza_intervalo_invertido_y_distancia_asimetrica(self):
        from modelo import Instancia
        with self.assertRaises(ValueError):
            Instancia.desde(entrada([grupo("A1", "A", 600, 540)], [estudiante("E1", A=1)]))
        raw = entrada([grupo("A1", "A", 540, 600)], [estudiante("E1", A=1)])
        raw["distancias"]["R1"]["R2"] = 10
        with self.assertRaises(ValueError):
            Instancia.desde(raw)

    def test_metricas_manuales_y_sin_asignaciones(self):
        from modelo import Instancia, evaluar
        e1 = dict(estudiante("E1", A=4, B=2, C=1), profesor={"A1": 5},
                  inicio_min=500, fin_max=630, compacto=True, dias_libres=[1],
                  companeros=["E2"])
        x = Instancia.desde(entrada([
            grupo("A1", "A", 480, 540, 2), grupo("B1", "B", 600, 660, salon="R2")],
            [e1, estudiante("E2", A=1), estudiante("E3", A=1)]))
        m = evaluar(x, {"E1": ["A1", "B1"], "E2": ["A1"], "E3": []})
        self.assertEqual(m["objetivo"], [3, 7, 58])
        self.assertEqual(m["cobertura"], .6)
        self.assertEqual(m["estudiantes"]["E1"]["huecos_min"], 60)
        self.assertEqual(m["estudiantes"]["E1"]["distancia_m"], 120)
        self.assertEqual(m["estudiantes"]["E1"]["min_fuera"], 50)
        self.assertEqual(m["estudiantes"]["E1"]["coincidencias"], 1)
        self.assertEqual(m["estudiantes"]["E1"]["pendientes"], ["C"])
        self.assertIsNone(m["estudiantes"]["E3"]["profesor_promedio"])

    def test_reparacion_alcanza_referencia_manual(self):
        from algoritmo import resolver, exacto
        from modelo import Instancia, evaluar, validar
        x = Instancia.desde(entrada([
            grupo("A1", "A", 480, 540), grupo("A2", "A", 540, 600),
            grupo("B1", "B", 480, 510), grupo("B2", "B", 510, 540)],
            [estudiante("E1", A=3, B=1)]))
        self.assertEqual(evaluar(x, resolver(x, "base"))["objetivo"][0], 1)
        h = resolver(x, "propuesto")
        self.assertEqual(validar(x, h), [])
        self.assertIn("A2", h["E1"])
        self.assertEqual(evaluar(x, h)["objetivo"], [2, 4, 0])
        self.assertEqual(evaluar(x, exacto(x))["objetivo"], [2, 4, 0])

    def test_brecha_por_reasignacion_entre_estudiantes_y_caso_sin_grupo(self):
        from algoritmo import resolver, exacto
        from modelo import Instancia, evaluar, validar
        x = Instancia.desde(entrada([
            grupo("A1", "A", 480, 540, dia=1), grupo("A2", "A", 480, 540, dia=2),
            grupo("B1", "B", 480, 540, dia=2)],
            [estudiante("E1", A=3, C=1), estudiante("E2", A=3, B=3)]))
        heuristico = resolver(x, "propuesto")
        self.assertEqual(validar(x, heuristico), [])
        self.assertEqual(evaluar(x, heuristico)["asignadas"], 2)
        self.assertEqual(evaluar(x, exacto(x))["objetivo"][:2], [3, 9])

    def test_preferencia_profesor_decide_empate(self):
        from algoritmo import resolver
        from modelo import Instancia
        x = Instancia.desde(entrada([grupo("A1", "A", 480, 540), grupo("A2", "A", 480, 540)],
                                   [dict(estudiante("E1", A=1), profesor={"A2": 5})]))
        self.assertEqual(resolver(x, "propuesto"), {"E1": ["A2"]})

    def test_inclusion_en_cupo_elige_la_mayor_prioridad(self):
        from algoritmo import resolver
        from modelo import Instancia
        x = Instancia.desde(entrada([grupo("A1", "A", 480, 540)],
                                   [estudiante("E1", A=1), estudiante("E2", A=5)]))
        self.assertEqual(resolver(x, "propuesto"), {"E1": [], "E2": ["A1"]})

    def test_propuesto_conserva_la_cobertura_de_la_base(self):
        from algoritmo import resolver
        from datos import generar
        from modelo import Instancia, evaluar
        x = Instancia.desde(generar("pequeno", 202632))
        a = evaluar(x, resolver(x, "base"))
        b = evaluar(x, resolver(x, "propuesto"))
        self.assertEqual(a["asignadas"], 10)
        self.assertGreaterEqual(b["objetivo"], a["objetivo"])

    def test_contrasta_archivos_con_referencias_manuales(self):
        from horarios import leer, procesar
        from modelo import Instancia
        casos = Path(__file__).with_name("casos")
        for caso, esperado in leer(casos / "salidas_esperadas.json").items():
            x = Instancia.desde(leer(casos / f"{caso}.json"))
            for metodo in ("base", "propuesto", "exacto"):
                with self.subTest(caso=caso, metodo=metodo):
                    metricas = procesar(x, metodo)["metricas"]
                    self.assertEqual(metricas["objetivo"], esperado[metodo])
                    if metodo == "exacto":
                        self.assertEqual(metricas["cobertura"] == 1, esperado["completa_posible"])

    def test_cli_end_to_end_y_semilla_reproducible(self):
        cli = Path(__file__).with_name("horarios.py")
        self.assertTrue(cli.is_file())
        with tempfile.TemporaryDirectory() as temp:
            x, x2, h = (Path(temp) / f"{nombre}.json" for nombre in ("x", "x2", "h"))
            for destino in (x, x2):
                subprocess.run([sys.executable, str(cli), "generar", "pequeno", str(destino)],
                               check=True, capture_output=True)
            self.assertEqual(x.read_bytes(), x2.read_bytes())
            subprocess.run([sys.executable, str(cli), "resolver", str(x), str(h)],
                           check=True, capture_output=True)
            r = subprocess.run([sys.executable, str(cli), "verificar", str(x), str(h)],
                               check=True, capture_output=True)
            self.assertTrue(json.loads(r.stdout)["valida"])
            informe = json.loads(h.read_text(encoding="utf-8"))
            self.assertEqual(len(informe["horarios"]), 5)
            self.assertGreater(informe["metricas"]["asignadas"], 0)
            informe["horarios"].pop(next(iter(informe["horarios"])))
            h.write_text(json.dumps(informe), encoding="utf-8")
            r = subprocess.run([sys.executable, str(cli), "verificar", str(x), str(h)],
                               capture_output=True)
            self.assertEqual(r.returncode, 1)
            self.assertFalse(json.loads(r.stdout)["valida"])


if __name__ == "__main__":
    unittest.main()
