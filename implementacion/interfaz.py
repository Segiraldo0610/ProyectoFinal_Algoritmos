"""Ventana de escritorio para la demostración del asignador."""

from pathlib import Path
from tempfile import TemporaryDirectory
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from sesion_demo import CARPETA_PROGRAMA, Sesion


ESCENARIOS = {"Pequeño · 5 estudiantes": "pequeno", "Mediano · 50 estudiantes": "mediano",
              "Grande · 500 estudiantes": "grande"}
METODOS = {"Propuesto · backtracking": "propuesto", "Base · voraz": "base",
           "Exacto · casos pequeños": "exacto"}
DIAS = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes")
REGLAS = ("Las franjas de cada estudiante son compatibles.",
          "Cada grupo respeta su cupo.",
          "Cada estudiante tiene máximo un grupo por materia.",
          "Todos los grupos pertenecen a materias solicitadas.")
FONDO = "#f1f5f8"
PANEL = "#ffffff"
TINTA = "#132b3d"
MUTED = "#486175"
ACENTO = "#09675c"


def porcentaje(valor):
    return f"{valor:.1%}".replace(".", ",").replace("%", " %")


def hora(minutos):
    return f"{minutos // 60:02}:{minutos % 60:02}"


def vaciar(tabla):
    tabla.delete(*tabla.get_children())


def configurar_columnas(tabla, titulos, anchos=None):
    columnas = tuple(f"c{i}" for i in range(len(titulos)))
    tabla.configure(columns=columnas)
    for i, (columna, titulo) in enumerate(zip(columnas, titulos)):
        tabla.heading(columna, text=titulo, anchor="w")
        ancho = anchos[i] if anchos else max(118, len(titulo) * 9)
        tabla.column(columna, width=ancho, minwidth=min(85, ancho), anchor="w", stretch=True)


def llenar(tabla, filas):
    vaciar(tabla)
    for i, fila in enumerate(filas):
        tabla.insert("", "end", values=fila, tags=("alterno",) if i % 2 else ())


def cuadricula(padre, alto=7):
    marco = ttk.Frame(padre, style="Card.TFrame")
    marco.columnconfigure(0, weight=1)
    marco.rowconfigure(0, weight=1)
    tabla = ttk.Treeview(marco, show="headings", height=alto, selectmode="browse")
    vertical = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    horizontal = ttk.Scrollbar(marco, orient="horizontal", command=tabla.xview)
    tabla.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
    tabla.tag_configure("alterno", background="#eff6f8")
    tabla.grid(row=0, column=0, sticky="nsew")
    vertical.grid(row=0, column=1, sticky="ns")
    horizontal.grid(row=1, column=0, sticky="ew")
    return marco, tabla


class Aplicacion:
    def __init__(self, raiz):
        self.raiz = raiz
        self.sesion = Sesion()
        self.temporales = None
        self.raiz.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.raiz.title("Asignación de horarios · Sustentación")
        self.raiz.configure(background=FONDO)
        self.raiz.minsize(930, 615)
        ancho = min(1190, raiz.winfo_screenwidth() - 60)
        alto = min(800, raiz.winfo_screenheight() - 100)
        self.raiz.geometry(f"{max(930, ancho)}x{max(615, alto)}")
        self.configurar_estilos()
        self.escenario = tk.StringVar(value=next(iter(ESCENARIOS)))
        self.semilla = tk.StringVar(value="202630")
        self.metodo = tk.StringVar(value=next(iter(METODOS)))
        self.archivo = tk.StringVar(value="solicitudes.csv")
        self.estudiante = tk.StringVar()
        self.fuente = tk.StringVar(value="Abre una carpeta CSV para empezar.")
        self.estado = tk.StringVar()
        self.detalle_csv = tk.StringVar()
        self.detalle_estudiante = tk.StringVar()
        self.titulo_verificacion = tk.StringVar()
        self.detalle_verificacion = tk.StringVar()
        self.kpi_cobertura = tk.StringVar(value="—")
        self.kpi_asignadas = tk.StringVar(value="—")
        self.kpi_pendientes = tk.StringVar(value="—")
        self.kpi_validacion = tk.StringVar(value="Por verificar")
        self.pantalla()
        self.ejecutar("Abrir ejemplo CSV", self.cargar_ejemplo)

    def configurar_estilos(self):
        estilo = ttk.Style(self.raiz)
        estilo.theme_use("clam")
        estilo.configure(".", font=("Segoe UI", 10))
        estilo.configure("TFrame", background=FONDO)
        estilo.configure("Card.TFrame", background=PANEL)
        estilo.configure("TLabel", background=FONDO, foreground=TINTA)
        estilo.configure("Card.TLabel", background=PANEL, foreground=TINTA)
        estilo.configure("Mute.TLabel", background=PANEL, foreground=MUTED)
        estilo.configure("MutedPage.TLabel", background=FONDO, foreground=MUTED)
        estilo.configure("Title.TLabel", font=("Segoe UI", 24, "bold"))
        estilo.configure("Section.TLabel", background=PANEL, foreground=TINTA,
                         font=("Segoe UI", 12, "bold"))
        estilo.configure("Number.TLabel", background=PANEL, foreground=ACENTO,
                         font=("Segoe UI", 18, "bold"))
        estilo.configure("TButton", padding=(12, 7))
        estilo.configure("Accent.TButton", background=ACENTO, foreground="#ffffff",
                         bordercolor=ACENTO, padding=(12, 7))
        estilo.map("Accent.TButton", background=[("disabled", "#b8d1cc"), ("active", "#0e786b")],
                   foreground=[("disabled", "#526b65"), ("!disabled", "#ffffff")])
        estilo.configure("Treeview", rowheight=29, background=PANEL, fieldbackground=PANEL,
                         foreground=TINTA, borderwidth=0)
        estilo.configure("Treeview.Heading", background="#e5edf2", foreground=TINTA,
                         font=("Segoe UI", 10, "bold"), padding=(6, 6))
        estilo.map("Treeview", background=[("selected", "#d3eee6")],
                   foreground=[("selected", TINTA)])
        estilo.configure("TNotebook", background=FONDO, borderwidth=0, padding=0)
        estilo.configure("TNotebook.Tab", padding=(17, 9), foreground=TINTA)
        estilo.map("TNotebook.Tab", background=[("selected", PANEL), ("!selected", "#e0eaf0")])

    def pantalla(self):
        pagina = ttk.Frame(self.raiz, padding=(22, 16, 22, 12))
        pagina.pack(fill="both", expand=True)
        ttk.Label(pagina, text="Asignación de horarios", style="Title.TLabel").pack(anchor="w")
        ttk.Label(pagina, text="Análisis de Algoritmos · Pontificia Universidad Javeriana",
                  style="MutedPage.TLabel").pack(anchor="w", pady=(0, 14))
        cuerpo = ttk.Frame(pagina)
        cuerpo.pack(fill="both", expand=True)
        acciones = ttk.Frame(cuerpo, style="Card.TFrame", padding=14)
        acciones.pack(side="left", fill="y", padx=(0, 12))
        principal = ttk.Frame(cuerpo)
        principal.pack(side="left", fill="both", expand=True)
        self.hacer_panel(acciones)

        indicadores = ttk.Frame(principal)
        indicadores.pack(fill="x", pady=(0, 12))
        for i, (texto, variable) in enumerate((
            ("Cobertura global", self.kpi_cobertura), ("Solicitudes asignadas", self.kpi_asignadas),
            ("Solicitudes pendientes", self.kpi_pendientes), ("Validación", self.kpi_validacion),
        )):
            indicadores.columnconfigure(i, weight=1, uniform="indicador")
            tarjeta = ttk.Frame(indicadores, style="Card.TFrame", padding=(11, 7))
            tarjeta.grid(row=0, column=i, sticky="nsew", padx=(0, 6 if i < 3 else 0))
            ttk.Label(tarjeta, text=texto, style="Mute.TLabel").pack(anchor="w")
            ttk.Label(tarjeta, textvariable=variable, style="Number.TLabel").pack(anchor="w")

        self.pestanas = ttk.Notebook(principal)
        self.pestanas.pack(fill="both", expand=True)
        self.pagina_csv = ttk.Frame(self.pestanas, style="Card.TFrame", padding=14)
        self.pagina_agenda = ttk.Frame(self.pestanas, style="Card.TFrame", padding=14)
        self.pagina_verificar = ttk.Frame(self.pestanas, style="Card.TFrame", padding=14)
        self.pestanas.add(self.pagina_csv, text="Datos CSV")
        self.pestanas.add(self.pagina_agenda, text="Horario y pendientes")
        self.pestanas.add(self.pagina_verificar, text="Validación")
        self.hacer_csv()
        self.hacer_agenda()
        self.hacer_validacion()
        ttk.Label(pagina, textvariable=self.estado, style="MutedPage.TLabel",
                  wraplength=850).pack(anchor="w", pady=(9, 0))

    def hacer_panel(self, panel):
        def boton(texto, accion, principal=False):
            widget = ttk.Button(panel, text=texto, command=lambda: self.ejecutar(texto, accion),
                                style="Accent.TButton" if principal else "TButton")
            widget.pack(fill="x", pady=(0, 5))
            return widget

        ttk.Label(panel, text="1. Datos de entrada", style="Section.TLabel").pack(anchor="w")
        ttk.Label(panel, text="Escenario sintético", style="Mute.TLabel").pack(anchor="w", pady=(7, 2))
        ttk.Combobox(panel, textvariable=self.escenario, values=tuple(ESCENARIOS),
                     state="readonly", width=26).pack(fill="x")
        ttk.Label(panel, text="Semilla", style="Mute.TLabel").pack(anchor="w", pady=(6, 2))
        ttk.Entry(panel, textvariable=self.semilla, width=23).pack(fill="x", pady=(0, 8))
        self.boton_generar = boton("Generar CSV", self.generar, True)
        boton("Abrir carpeta CSV", self.abrir_carpeta)
        boton("Cargar ejemplo", self.cargar_ejemplo)
        casos = ttk.Menubutton(panel, text="Casos para la sustentación")
        menu = tk.Menu(casos, tearoff=False)
        for caso, etiqueta in (("reparacion", "Cambio de sección"), ("cupo", "Cupo compartido"),
                               ("brecha", "Reasignación entre estudiantes")):
            menu.add_command(label=etiqueta, command=lambda c=caso: self.ejecutar(
                "Cargar caso", lambda: self.cargar_caso(c)))
        casos.configure(menu=menu)
        casos.pack(fill="x", pady=(0, 10))
        ttk.Separator(panel).pack(fill="x", pady=(1, 9))
        ttk.Label(panel, text="2. Asignación", style="Section.TLabel").pack(anchor="w", pady=(0, 7))
        ttk.Combobox(panel, textvariable=self.metodo, values=tuple(METODOS),
                     state="readonly", width=26).pack(fill="x", pady=(0, 8))
        self.boton_asignar = boton("Asignar horarios", self.asignar, True)
        self.boton_verificar = boton("Verificar resultado", self.verificar)
        self.boton_guardar = boton("Guardar resultado JSON", self.guardar)
        for widget in (self.boton_asignar, self.boton_verificar, self.boton_guardar):
            widget.state(["disabled"])

    def hacer_csv(self):
        pagina = self.pagina_csv
        ttk.Label(pagina, textvariable=self.fuente, style="Section.TLabel",
                  wraplength=620).pack(anchor="w", pady=(0, 9))
        selector = ttk.Frame(pagina, style="Card.TFrame")
        selector.pack(fill="x", pady=(0, 9))
        ttk.Label(selector, text="Archivo", style="Card.TLabel").pack(side="left", padx=(0, 8))
        elegir = ttk.Combobox(selector, textvariable=self.archivo, width=27, state="readonly",
                              values=tuple(f"{nombre}.csv" for nombre in self.sesion.tablas))
        elegir.pack(side="left")
        elegir.bind("<<ComboboxSelected>>", lambda _: self.ejecutar("Leer CSV", self.mostrar_csv))
        ttk.Label(selector, textvariable=self.detalle_csv, style="Mute.TLabel").pack(side="right")
        marco, self.tabla_csv = cuadricula(pagina, 10)
        marco.pack(fill="both", expand=True)

    def hacer_agenda(self):
        pagina = self.pagina_agenda
        barra = ttk.Frame(pagina, style="Card.TFrame")
        barra.pack(fill="x", pady=(0, 6))
        ttk.Label(barra, text="Estudiante", style="Section.TLabel").pack(side="left", padx=(0, 8))
        self.selector_estudiante = ttk.Combobox(barra, textvariable=self.estudiante,
                                                state="disabled", width=13)
        self.selector_estudiante.pack(side="left")
        self.selector_estudiante.bind("<<ComboboxSelected>>", lambda _: self.mostrar_estudiante())
        ttk.Label(pagina, textvariable=self.detalle_estudiante, style="Mute.TLabel").pack(
            anchor="w", pady=(0, 9))
        marco, self.tabla_agenda = cuadricula(pagina, 5)
        configurar_columnas(self.tabla_agenda,
                             ("Día", "Inicio", "Fin", "Materia", "Grupo", "Profesor", "Salón"),
                             (104, 70, 70, 86, 98, 86, 72))
        marco.pack(fill="both", expand=True)
        ttk.Label(pagina, text="Materias pendientes", style="Section.TLabel").pack(
            anchor="w", pady=(10, 4))
        marco_pendientes, self.tabla_pendientes = cuadricula(pagina, 3)
        configurar_columnas(self.tabla_pendientes, ("Materia", "Prioridad"))
        marco_pendientes.pack(fill="x")
        self.vaciar_resultado()

    def hacer_validacion(self):
        pagina = self.pagina_verificar
        ttk.Label(pagina, textvariable=self.titulo_verificacion, style="Number.TLabel").pack(anchor="w")
        ttk.Label(pagina, textvariable=self.detalle_verificacion, style="Card.TLabel",
                  justify="left", wraplength=650).pack(anchor="w", pady=(12, 0))

    def ejecutar(self, titulo, accion):
        try:
            accion()
        except (OSError, ValueError, KeyError, RuntimeError) as error:
            self.estado.set(f"{titulo}: {error}")
            messagebox.showerror(titulo, str(error), parent=self.raiz)

    def generar(self):
        try:
            semilla = int(self.semilla.get())
        except ValueError as error:
            raise ValueError("La semilla debe ser un número entero.") from error
        elegida = filedialog.askdirectory(parent=self.raiz, title="Guardar los CSV en una subcarpeta")
        if not elegida:
            return
        escenario = ESCENARIOS[self.escenario.get()]
        base = Path(elegida) / f"horarios-{escenario}-{semilla}"
        carpeta = base
        numero = 2
        while carpeta.exists():
            carpeta = base.with_name(f"{base.name}-{numero}")
            numero += 1
        self.sesion.generar_csv(carpeta, escenario, semilla)
        self.mostrar_entrada(f"CSV generados · semilla {semilla}")

    def abrir_carpeta(self):
        elegida = filedialog.askdirectory(parent=self.raiz, title="Selecciona la carpeta con los 11 CSV")
        if elegida:
            self.sesion.cargar_csv(Path(elegida))
            self.mostrar_entrada("Carpeta CSV cargada")

    def cargar_ejemplo(self):
        self.sesion.cargar_csv(CARPETA_PROGRAMA / "ejemplo_csv")
        self.mostrar_entrada("Ejemplo CSV · Semilla 202630")

    def cargar_caso(self, caso):
        if self.temporales is None:
            self.temporales = TemporaryDirectory(prefix="horarios-casos-")
        carpeta = Path(self.temporales.name) / caso
        if carpeta.exists():
            self.sesion.cargar_csv(carpeta)
        else:
            self.sesion.cargar_caso(caso, carpeta)
        self.mostrar_entrada({"reparacion": "Caso de cambio de sección", "cupo": "Caso de cupo compartido",
                              "brecha": "Caso de reasignación entre estudiantes"}[caso])

    def mostrar_entrada(self, etiqueta):
        self.fuente.set(etiqueta)
        self.vaciar_resultado()
        self.archivo.set("solicitudes.csv")
        self.mostrar_csv()
        self.boton_asignar.state(["!disabled"])
        self.pestanas.select(self.pagina_csv)

    def mostrar_csv(self):
        columnas, filas = self.sesion.tabla(Path(self.archivo.get()).stem)
        configurar_columnas(self.tabla_csv, columnas)
        llenar(self.tabla_csv, filas)
        self.detalle_csv.set(f"{len(filas):,} filas · {len(self.sesion.tablas)} CSV".replace(",", "."))
        self.estado.set(str(self.sesion.carpeta))

    def vaciar_resultado(self):
        self.estudiante.set("")
        self.selector_estudiante.configure(values=(), state="disabled")
        vaciar(self.tabla_agenda)
        vaciar(self.tabla_pendientes)
        self.detalle_estudiante.set("Presiona «Asignar horarios» para consultar un resultado.")
        for indicador in (self.kpi_cobertura, self.kpi_asignadas, self.kpi_pendientes):
            indicador.set("—")
        self.kpi_validacion.set("Por verificar")
        self.titulo_verificacion.set("Verificación pendiente")
        self.detalle_verificacion.set("Asigna horarios y presiona «Verificar resultado».")
        self.boton_verificar.state(["disabled"])
        self.boton_guardar.state(["disabled"])

    def asignar(self):
        resultado = self.sesion.asignar(METODOS[self.metodo.get()])
        self.vaciar_resultado()
        metricas = resultado["metricas"]
        self.kpi_cobertura.set(porcentaje(metricas["cobertura"]))
        self.kpi_asignadas.set(f"{metricas['asignadas']} / {metricas['solicitadas']}")
        self.kpi_pendientes.set(str(metricas["solicitadas"] - metricas["asignadas"]))
        estudiantes = tuple(sorted(resultado["horarios"]))
        self.selector_estudiante.configure(values=estudiantes, state="readonly")
        self.estudiante.set(estudiantes[0])
        self.mostrar_estudiante()
        self.boton_verificar.state(["!disabled"])
        self.boton_guardar.state(["!disabled"])
        self.pestanas.select(self.pagina_agenda)
        resumen = f"{self.metodo.get()} · {resultado['tiempo_s'] * 1000:.2f} ms"
        busqueda = resultado.get("busqueda")
        if busqueda:
            detalle = ("Óptimo comprobado" if busqueda["completa"]
                       else "Límite alcanzado · mejor solución encontrada")
            resumen += f" · {busqueda['nodos']:,} nodos · {detalle}".replace(",", ".")
        self.estado.set(resumen)

    def mostrar_estudiante(self):
        e = self.estudiante.get()
        if not e or self.sesion.resultado is None:
            return
        m = self.sesion.resultado["metricas"]["estudiantes"][e]
        texto = f"Cobertura individual {porcentaje(m['cobertura'])} · {m['asignadas']} de {m['solicitadas']}"
        if not m["pendientes"]:
            texto += " · Sin materias pendientes"
        self.detalle_estudiante.set(texto)
        llenar(self.tabla_agenda, ((DIAS[dia - 1], hora(inicio), hora(fin), *datos)
                                   for dia, inicio, fin, *datos in self.sesion.agenda(e)))
        prioridades = self.sesion.instancia.estudiantes[e].solicitudes
        llenar(self.tabla_pendientes, ((a, prioridades[a]) for a in m["pendientes"]))

    def verificar(self):
        errores = self.sesion.verificar()
        if errores:
            self.titulo_verificacion.set("Asignación inválida")
            self.kpi_validacion.set("Inválida")
            self.detalle_verificacion.set("\n\n".join(errores))
        else:
            self.titulo_verificacion.set("Asignación válida")
            self.kpi_validacion.set("Válida")
            self.detalle_verificacion.set("\n\n".join(f"Cumple · {regla}" for regla in REGLAS))
        self.pestanas.select(self.pagina_verificar)

    def guardar(self):
        elegida = filedialog.asksaveasfilename(parent=self.raiz, title="Guardar la asignación y sus métricas",
                                               defaultextension=".json",
                                               filetypes=[("Resultado JSON", "*.json")],
                                               initialfile="salida-horarios.json")
        if elegida:
            self.sesion.guardar(Path(elegida))
            self.estado.set(f"Resultado guardado en {elegida}")

    def cerrar(self):
        if self.temporales:
            self.temporales.cleanup()
        self.raiz.destroy()


def main():
    raiz = tk.Tk()
    Aplicacion(raiz)
    if raiz.tk.call("tk", "windowingsystem") == "win32":
        raiz.state("zoomed")
    raiz.mainloop()


if __name__ == "__main__":
    main()
