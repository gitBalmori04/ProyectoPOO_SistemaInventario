# Módulo de la interfaz gráfica principal del Sistema de Control de Abarrotes Don Beto.

import os
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from modelos.producto import (
    Precio,
    Categoria,
    Perecedero,
    NoPerecedero,
    Proveedor,
    Venta,
    DetalleVenta,
    Tienda,
)
from modelos.persistencia import GestorArchivos
from utils.excepciones import (
    ProductoNoEncontradoError,
    StockInsuficienteError,
    registrarError,
)


# Ventana emergente para registrar ventas y generar tickets.
class VentanaVenta(tk.Toplevel):
    # Inicializa la ventana modal de punto de venta conectada a la tienda.
    def __init__(self, padre, tienda: Tienda, alFinalizarVenta):
        super().__init__(padre)
        self.tienda = tienda
        self.alFinalizarVenta = alFinalizarVenta
        self.ventaActual = None

        self.colorAzulMarino = "#162E52"
        self.colorNaranja = "#F5A638"
        self.colorFondo = "#F4F6F9"
        self.fuenteGeneral = ("Arial", 12)
        self.fuenteNegrita = ("Arial", 12, "bold")

        self.title("Registrar Venta - Abarrotes Don Beto")
        self.geometry("680x540")
        self.configure(bg=self.colorFondo)
        self.resizable(False, False)
        self.grab_set()

        self._construirInterfaz()

    # Construye los controles del formulario de venta y el área del ticket.
    def _construirInterfaz(self):
        encabezado = tk.Frame(self, bg=self.colorAzulMarino, pady=12)
        encabezado.pack(fill="x")
        tk.Label(
            encabezado,
            text="PUNTO DE VENTA Y TICKET",
            font=("Arial", 15, "bold"),
            bg=self.colorAzulMarino,
            fg=self.colorNaranja,
        ).pack()

        marcoDatos = tk.LabelFrame(
            self,
            text=" Datos del Ticket ",
            font=self.fuenteNegrita,
            bg="#FFFFFF",
            fg=self.colorAzulMarino,
            padx=12,
            pady=10,
        )
        marcoDatos.pack(fill="x", padx=15, pady=10)

        tk.Label(marcoDatos, text="Folio Venta:", font=self.fuenteGeneral, bg="#FFFFFF").grid(
            row=0, column=0, sticky="w", padx=5, pady=4
        )
        self.entryFolio = tk.Entry(marcoDatos, font=self.fuenteGeneral, width=12)
        self.entryFolio.insert(0, "1")
        self.entryFolio.grid(row=0, column=1, sticky="w", padx=5, pady=4)

        tk.Label(marcoDatos, text="Fecha:", font=self.fuenteGeneral, bg="#FFFFFF").grid(
            row=0, column=2, sticky="w", padx=5, pady=4
        )
        self.entryFecha = tk.Entry(marcoDatos, font=self.fuenteGeneral, width=14)
        self.entryFecha.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.entryFecha.grid(row=0, column=3, sticky="w", padx=5, pady=4)

        tk.Label(marcoDatos, text="Producto:", font=self.fuenteGeneral, bg="#FFFFFF").grid(
            row=1, column=0, sticky="w", padx=5, pady=6
        )
        opcionesProductos = [
            f"{p.codigo} - {p.nombre} (Disp: {p.stock} | ${p.precio.valor:.2f})"
            for p in self.tienda.consultarInventario()
        ]
        self.comboProducto = ttk.Combobox(
            marcoDatos,
            values=opcionesProductos,
            font=self.fuenteGeneral,
            state="readonly",
            width=42,
        )
        if opcionesProductos:
            self.comboProducto.current(0)
        self.comboProducto.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=6)

        tk.Label(marcoDatos, text="Cantidad:", font=self.fuenteGeneral, bg="#FFFFFF").grid(
            row=2, column=0, sticky="w", padx=5, pady=4
        )
        self.entryCantidad = tk.Entry(marcoDatos, font=self.fuenteGeneral, width=12)
        self.entryCantidad.insert(0, "1")
        self.entryCantidad.grid(row=2, column=1, sticky="w", padx=5, pady=4)

        btnAgregar = tk.Button(
            marcoDatos,
            text="+ Agregar al Ticket",
            font=self.fuenteNegrita,
            bg=self.colorNaranja,
            fg=self.colorAzulMarino,
            cursor="hand2",
            command=self._agregarArticulo,
        )
        btnAgregar.grid(row=2, column=2, columnspan=2, sticky="e", padx=5, pady=4)

        marcoTicket = tk.LabelFrame(
            self,
            text=" Vista Previa del Comprobante ",
            font=self.fuenteNegrita,
            bg="#FFFFFF",
            fg=self.colorAzulMarino,
            padx=10,
            pady=8,
        )
        marcoTicket.pack(fill="both", expand=True, padx=15, pady=5)

        self.textoTicket = tk.Text(
            marcoTicket,
            font=("Consolas", 11),
            height=10,
            bg="#F8FAFC",
            fg=self.colorAzulMarino,
            state="disabled",
        )
        self.textoTicket.pack(fill="both", expand=True)

        marcoBotones = tk.Frame(self, bg=self.colorFondo, pady=10)
        marcoBotones.pack(fill="x", padx=15)

        tk.Button(
            marcoBotones,
            text="Confirmar Venta y Guardar",
            font=self.fuenteNegrita,
            bg=self.colorAzulMarino,
            fg="#FFFFFF",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._confirmarVenta,
        ).pack(side="right", padx=5)

        tk.Button(
            marcoBotones,
            text="Cerrar",
            font=self.fuenteGeneral,
            bg="#D5DCE4",
            fg=self.colorAzulMarino,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.destroy,
        ).pack(side="right", padx=5)

    # Agrega un producto a la venta actual validando stock y datos numéricos.
    def _agregarArticulo(self):
        try:
            seleccion = self.comboProducto.get().strip()
            if not seleccion:
                raise ValueError("Debe seleccionar un producto del catálogo.")

            if self.ventaActual is None:
                folio = int(self.entryFolio.get().strip())
                fecha = self.entryFecha.get().strip()
                self.ventaActual = Venta(folio, fecha)
                self.entryFolio.config(state="disabled")
                self.entryFecha.config(state="disabled")

            codigoProd = seleccion.split(" - ")[0].strip()
            producto = self.tienda.buscarProductoPorCodigo(codigoProd)
            cantidad = int(self.entryCantidad.get().strip())

            detalle = DetalleVenta(producto, cantidad)
            self.ventaActual.agregarDetalle(detalle)

            self._actualizarVistaTicket()
            self._refrescarComboProductos()
        except (ValueError, ProductoNoEncontradoError, StockInsuficienteError) as e:
            registrarError(f"{type(e).__name__} en VentanaVenta: {e}")
            messagebox.showerror("Error en Venta", str(e), parent=self)

    # Actualiza el contenido visual del ticket en el widget Text.
    def _actualizarVistaTicket(self):
        self.textoTicket.config(state="normal")
        self.textoTicket.delete("1.0", tk.END)
        if self.ventaActual:
            self.textoTicket.insert(tk.END, self.ventaActual.generarTicket())
        self.textoTicket.config(state="disabled")

    # Actualiza el listado desplegable con las existencias restantes.
    def _refrescarComboProductos(self):
        opciones = [
            f"{p.codigo} - {p.nombre} (Disp: {p.stock} | ${p.precio.valor:.2f})"
            for p in self.tienda.consultarInventario()
        ]
        self.comboProducto["values"] = opciones
        if opciones:
            self.comboProducto.current(0)

    # Finaliza la venta, persiste el inventario y cierra la ventana modal.
    def _confirmarVenta(self):
        if self.ventaActual is None or len(self.ventaActual.listaDetalles) == 0:
            messagebox.showwarning(
                "Ticket Vacío",
                "Agregue al menos un artículo antes de confirmar la venta.",
                parent=self,
            )
            return

        self.alFinalizarVenta()
        messagebox.showinfo(
            "Venta Registrada",
            f"Ticket #{self.ventaActual.numero} registrado.\nTotal cobrado: ${self.ventaActual.total:.2f}",
            parent=self,
        )
        self.destroy()


# Ventana principal de la aplicación gráfica de Abarrotes Don Beto.
class VentanaPrincipal:
    # Inicializa la ventana principal, colores, estilos, backend y widgets.
    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        self.rutaBase = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.archivoDatos = os.path.join(self.rutaBase, "inventario.txt")

        # Paleta de colores inspirada en el logotipo (Azul Marino y Naranja Amarillento)
        self.colorAzulMarino = "#162E52"
        self.colorAzulMedio = "#2B548E"
        self.colorNaranja = "#F5A638"
        self.colorNaranjaHover = "#E08E1E"
        self.colorFondo = "#F4F6F9"
        self.colorBlanco = "#FFFFFF"
        self.colorRojo = "#C0392B"

        # Tipografía Arial 12 solicitada
        self.fuenteGeneral = ("Arial", 12)
        self.fuenteNegrita = ("Arial", 12, "bold")
        self.fuenteTitulo = ("Arial", 18, "bold")
        self.fuenteSubtitulo = ("Arial", 12)

        # Inicialización de objetos del modelo de negocio
        self.tienda = Tienda("Abarrotes Don Beto", "Av. 5 de Febrero #76118, Querétaro")
        self.proveedorPrincipal = Proveedor(
            1, "Distribuidora Mayorista del Centro", "442-215-8890"
        )
        self.imagenLogo = None

        self._configurarVentana()
        self._configurarEstilos()
        self._cargarDatosIniciales()
        self._construirInterfaz()
        self._actualizarTabla()

    # Configura el título, dimensiones y color de fondo de la ventana raíz.
    def _configurarVentana(self):
        self.raiz.title("Abarrotes Don Beto - Sistema de Control de Inventario")
        self.raiz.geometry("1240x730")
        self.raiz.minsize(1100, 660)
        self.raiz.configure(bg=self.colorFondo)

    # Configura los estilos ttk (Treeview y Combobox) en Arial 12 y colores institucionales.
    def _configurarEstilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")

        estilo.configure(
            "Treeview",
            background=self.colorBlanco,
            foreground=self.colorAzulMarino,
            rowheight=30,
            fieldbackground=self.colorBlanco,
            font=self.fuenteGeneral,
        )
        estilo.configure(
            "Treeview.Heading",
            background=self.colorAzulMarino,
            foreground=self.colorBlanco,
            font=self.fuenteNegrita,
            padding=(6, 6),
        )
        estilo.map(
            "Treeview",
            background=[("selected", self.colorNaranja)],
            foreground=[("selected", self.colorAzulMarino)],
        )
        estilo.configure("TCombobox", font=self.fuenteGeneral, padding=4)

    # Carga los productos guardados previamente en inventario.txt.
    def _cargarDatosIniciales(self):
        try:
            cargados = GestorArchivos.cargarInventario(self.archivoDatos)
            self.tienda.reemplazarInventario(cargados)
        except (PermissionError, OSError, ValueError) as e:
            registrarError(f"Error al cargar inventario inicial en GUI: {type(e).__name__} - {e}")
            messagebox.showerror(
                "Error de Carga",
                f"No se pudo leer el archivo de inventario:\n{e}",
            )

    # Busca y carga la imagen del logotipo desde la carpeta assets o raíz del proyecto.
    def _cargarImagenLogo(self, contenedor):
        posiblesRutas = [
            os.path.join(self.rutaBase, "assets", "logo_don_beto.png"),
            os.path.join(self.rutaBase, "assets", "logo_don_beto.jpg"),
            os.path.join(self.rutaBase, "assets", "logo.png"),
            os.path.join(self.rutaBase, "assets", "logo.jpg"),
            os.path.join(self.rutaBase, "logo_don_beto.png"),
            os.path.join(self.rutaBase, "logo_don_beto.jpg"),
        ]

        rutaEncontrada = None
        for ruta in posiblesRutas:
            if os.path.exists(ruta):
                rutaEncontrada = ruta
                break

        if rutaEncontrada:
            try:
                from PIL import Image, ImageTk

                img = Image.open(rutaEncontrada).resize((92, 92), Image.LANCZOS)
                self.imagenLogo = ImageTk.PhotoImage(img)
                etiquetaLogo = tk.Label(
                    contenedor, image=self.imagenLogo, bg=self.colorAzulMarino
                )
                etiquetaLogo.pack(side="left", padx=(15, 12))
                return
            except ImportError:
                # Si Pillow no está instalado, Tkinter nativo solo admite PNG/GIF
                if rutaEncontrada.lower().endswith((".png", ".gif")):
                    try:
                        imgNativa = tk.PhotoImage(file=rutaEncontrada)
                        factor = max(1, imgNativa.width() // 92, imgNativa.height() // 92)
                        if factor > 1:
                            imgNativa = imgNativa.subsample(factor, factor)
                        self.imagenLogo = imgNativa
                        etiquetaLogo = tk.Label(
                            contenedor, image=self.imagenLogo, bg=self.colorAzulMarino
                        )
                        etiquetaLogo.pack(side="left", padx=(15, 12))
                        return
                    except tk.TclError as e:
                        registrarError(f"Error al cargar PNG nativo: {e}")
                else:
                    registrarError(
                        "Para mostrar el logo .jpg instala Pillow ('pip install pillow') o guárdalo como .png"
                    )
            except Exception as e:
                registrarError(f"No se pudo cargar imagen de logo: {e}")

        # Emblema de respaldo si no hay Pillow para .jpg o no existe el archivo
        lienzoLogo = tk.Canvas(
            contenedor,
            width=90,
            height=90,
            bg=self.colorAzulMarino,
            highlightthickness=0,
        )
        lienzoLogo.pack(side="left", padx=(15, 12))
        lienzoLogo.create_oval(5, 5, 85, 85, fill=self.colorAzulMedio, outline=self.colorBlanco, width=3)
        lienzoLogo.create_text(
            45, 36, text="DON", fill=self.colorNaranja, font=("Arial", 13, "bold")
        )
        lienzoLogo.create_text(
            45, 56, text="BETO", fill=self.colorNaranja, font=("Arial", 13, "bold")
        )

    # Construye toda la estructura visual de la ventana principal.
    def _construirInterfaz(self):
        # 1. ENCABEZADO SUPERIOR (AZUL MARINO + LOGO + TÍTULO NARANJA AMARILLENTO)
        frameHeader = tk.Frame(self.raiz, bg=self.colorAzulMarino, height=110)
        frameHeader.pack(fill="x", side="top")
        frameHeader.pack_propagate(False)

        self._cargarImagenLogo(frameHeader)

        frameTitulos = tk.Frame(frameHeader, bg=self.colorAzulMarino)
        frameTitulos.pack(side="left", fill="y", pady=18)

        tk.Label(
            frameTitulos,
            text="ABARROTES DON BETO — DESPENSA & MÁS",
            font=self.fuenteTitulo,
            bg=self.colorAzulMarino,
            fg=self.colorNaranja,
        ).pack(anchor="w")

        tk.Label(
            frameTitulos,
            text=f"{self.tienda.direccion}  |  {self.proveedorPrincipal}",
            font=self.fuenteSubtitulo,
            bg=self.colorAzulMarino,
            fg=self.colorBlanco,
        ).pack(anchor="w", pady=(4, 0))

        # Botones superiores de operaciones globales
        frameAccionesTop = tk.Frame(frameHeader, bg=self.colorAzulMarino)
        frameAccionesTop.pack(side="right", padx=18)

        tk.Button(
            frameAccionesTop,
            text="Registrar Venta",
            font=self.fuenteNegrita,
            bg=self.colorNaranja,
            fg=self.colorAzulMarino,
            activebackground=self.colorNaranjaHover,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._abrirVentanaVenta,
        ).pack(side="top", fill="x", pady=3)

        tk.Button(
            frameAccionesTop,
            text="Ver Bitácora Errores",
            font=("Arial", 11, "bold"),
            bg=self.colorAzulMedio,
            fg=self.colorBlanco,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._mostrarBitacoraErrores,
        ).pack(side="top", fill="x", pady=3)

        # Franja decorativa naranja amarillento debajo del encabezado
        tk.Frame(self.raiz, bg=self.colorNaranja, height=5).pack(fill="x")

        # 2. CONTENEDOR CENTRAL DIVIDIDO EN FORMULARIO (IZQUIERDA) Y TABLA (DERECHA)
        frameCuerpo = tk.Frame(self.raiz, bg=self.colorFondo)
        frameCuerpo.pack(fill="both", expand=True, padx=14, pady=12)

        # --- PANEL IZQUIERDO: FORMULARIO DE PRODUCTO ---
        frameFormulario = tk.LabelFrame(
            frameCuerpo,
            text=" Gestión de Productos ",
            font=self.fuenteNegrita,
            bg=self.colorBlanco,
            fg=self.colorAzulMarino,
            padx=14,
            pady=10,
            relief="groove",
            bd=2,
        )
        frameFormulario.pack(side="left", fill="y", padx=(0, 12))

        self._construirFormulario(frameFormulario)

        # --- PANEL DERECHO: BÚSQUEDA, ACCIONES Y LISTADO (TREEVIEW) ---
        frameDerecho = tk.Frame(frameCuerpo, bg=self.colorFondo)
        frameDerecho.pack(side="right", fill="both", expand=True)

        self._construirPanelTabla(frameDerecho)

        # 3. BARRA DE ESTADO INFERIOR
        self.varEstado = tk.StringVar(value="Listo. Datos sincronizados con inventario.txt")
        barraEstado = tk.Label(
            self.raiz,
            textvariable=self.varEstado,
            font=("Arial", 11),
            bg=self.colorAzulMarino,
            fg=self.colorBlanco,
            anchor="w",
            padx=15,
            pady=6,
        )
        barraEstado.pack(fill="x", side="bottom")

    # Crea todos los campos de captura y botones CRUD dentro del panel izquierdo.
    def _construirFormulario(self, padre):
        campos = [
            ("Tipo de Producto:", "tipo"),
            ("Código Único:", "codigo"),
            ("Nombre:", "nombre"),
            ("Stock (Existencias):", "stock"),
            ("Precio Unitario ($):", "precio"),
            ("ID Categoría:", "idCat"),
            ("Categoría:", "nombreCat"),
        ]

        self.entradas = {}

        for fila, (etiqueta, clave) in enumerate(campos):
            tk.Label(
                padre,
                text=etiqueta,
                font=self.fuenteGeneral,
                bg=self.colorBlanco,
                fg=self.colorAzulMarino,
            ).grid(row=fila, column=0, sticky="w", pady=5, padx=(0, 8))

            if clave == "tipo":
                widget = ttk.Combobox(
                    padre,
                    values=["Perecedero", "NoPerecedero"],
                    font=self.fuenteGeneral,
                    state="readonly",
                    width=20,
                )
                widget.current(0)
                widget.bind("<<ComboboxSelected>>", self._alternarCamposPorTipo)
            elif clave == "nombreCat":
                widget = ttk.Combobox(
                    padre,
                    values=["Lácteos", "Abarrotes", "Bebidas", "Enlatados", "Limpieza"],
                    font=self.fuenteGeneral,
                    width=20,
                )
                widget.set("Lácteos")
            else:
                widget = tk.Entry(
                    padre,
                    font=self.fuenteGeneral,
                    width=22,
                    bg="#F8FAFC",
                    fg=self.colorAzulMarino,
                    relief="solid",
                    bd=1,
                )

            widget.grid(row=fila, column=1, sticky="ew", pady=5)
            self.entradas[clave] = widget

        # Campos específicos dinámicos (Perecedero vs NoPerecedero)
        self.lblExtra1 = tk.Label(
            padre,
            text="Caducidad (YYYY-MM-DD):",
            font=self.fuenteGeneral,
            bg=self.colorBlanco,
            fg=self.colorAzulMarino,
        )
        self.lblExtra1.grid(row=7, column=0, sticky="w", pady=5, padx=(0, 8))

        self.entryExtra1 = tk.Entry(
            padre,
            font=self.fuenteGeneral,
            width=22,
            bg="#F8FAFC",
            fg=self.colorAzulMarino,
            relief="solid",
            bd=1,
        )
        self.entryExtra1.grid(row=7, column=1, sticky="ew", pady=5)

        self.lblExtra2 = tk.Label(
            padre,
            text="Temperatura (°C):",
            font=self.fuenteGeneral,
            bg=self.colorBlanco,
            fg=self.colorAzulMarino,
        )
        self.lblExtra2.grid(row=8, column=0, sticky="w", pady=5, padx=(0, 8))

        self.entryExtra2 = tk.Entry(
            padre,
            font=self.fuenteGeneral,
            width=22,
            bg="#F8FAFC",
            fg=self.colorAzulMarino,
            relief="solid",
            bd=1,
        )
        self.entryExtra2.grid(row=8, column=1, sticky="ew", pady=5)

        # Cuadrícula de botones CRUD
        frameBotonesCrud = tk.Frame(padre, bg=self.colorBlanco)
        frameBotonesCrud.grid(row=9, column=0, columnspan=2, pady=(16, 6), sticky="ew")
        frameBotonesCrud.columnconfigure(0, weight=1)
        frameBotonesCrud.columnconfigure(1, weight=1)

        tk.Button(
            frameBotonesCrud,
            text="Registrar",
            font=self.fuenteNegrita,
            bg=self.colorNaranja,
            fg=self.colorAzulMarino,
            activebackground=self.colorNaranjaHover,
            pady=7,
            cursor="hand2",
            command=self._registrarProducto,
        ).grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        tk.Button(
            frameBotonesCrud,
            text="Modificar",
            font=self.fuenteNegrita,
            bg=self.colorAzulMarino,
            fg=self.colorBlanco,
            activebackground=self.colorAzulMedio,
            pady=7,
            cursor="hand2",
            command=self._modificarProducto,
        ).grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        tk.Button(
            frameBotonesCrud,
            text="Eliminar",
            font=self.fuenteNegrita,
            bg=self.colorRojo,
            fg=self.colorBlanco,
            pady=7,
            cursor="hand2",
            command=self._eliminarProducto,
        ).grid(row=1, column=0, padx=4, pady=4, sticky="ew")

        tk.Button(
            frameBotonesCrud,
            text="Limpiar",
            font=self.fuenteGeneral,
            bg="#D5DCE4",
            fg=self.colorAzulMarino,
            pady=7,
            cursor="hand2",
            command=self._limpiarFormulario,
        ).grid(row=1, column=1, padx=4, pady=4, sticky="ew")

    # Crea la barra de búsqueda, botón de proveedor y la tabla Treeview.
    def _construirPanelTabla(self, padre):
        frameBarra = tk.Frame(
            padre, bg=self.colorBlanco, padx=12, pady=10, relief="groove", bd=2
        )
        frameBarra.pack(fill="x", pady=(0, 10))

        tk.Label(
            frameBarra,
            text="Buscar (Código/Nombre):",
            font=self.fuenteGeneral,
            bg=self.colorBlanco,
            fg=self.colorAzulMarino,
        ).pack(side="left", padx=(0, 6))

        self.entryBusqueda = tk.Entry(
            frameBarra, font=self.fuenteGeneral, width=18, relief="solid", bd=1
        )
        self.entryBusqueda.pack(side="left", padx=4)
        self.entryBusqueda.bind("<Return>", lambda e: self._buscarEnTabla())

        tk.Button(
            frameBarra,
            text="Buscar",
            font=self.fuenteNegrita,
            bg=self.colorAzulMarino,
            fg=self.colorBlanco,
            padx=10,
            cursor="hand2",
            command=self._buscarEnTabla,
        ).pack(side="left", padx=4)

        tk.Button(
            frameBarra,
            text="Mostrar Todo",
            font=self.fuenteGeneral,
            bg="#D5DCE4",
            fg=self.colorAzulMarino,
            padx=8,
            cursor="hand2",
            command=self._actualizarTabla,
        ).pack(side="left", padx=4)

        tk.Button(
            frameBarra,
            text="+ Abastecer (Proveedor)",
            font=self.fuenteNegrita,
            bg=self.colorNaranja,
            fg=self.colorAzulMarino,
            padx=10,
            cursor="hand2",
            command=self._abastecerConProveedor,
        ).pack(side="right", padx=4)

        # Contenedor de Treeview con Scrollbars
        frameTabla = tk.Frame(padre, bg=self.colorBlanco, relief="groove", bd=2)
        frameTabla.pack(fill="both", expand=True)

        columnas = ("codigo", "nombre", "tipo", "categoria", "stock", "precio", "detalle")
        self.tabla = ttk.Treeview(
            frameTabla, columns=columnas, show="headings", selectmode="browse"
        )

        encabezados = {
            "codigo": ("Código", 90),
            "nombre": ("Nombre Producto", 190),
            "tipo": ("Tipo", 120),
            "categoria": ("Categoría", 130),
            "stock": ("Stock", 75),
            "precio": ("Precio", 105),
            "detalle": ("Caducidad / Empaque", 230),
        }

        for col, (texto, ancho) in encabezados.items():
            self.tabla.heading(col, text=texto)
            alineacion = "center" if col in ("codigo", "stock", "precio") else "w"
            self.tabla.column(col, width=ancho, anchor=alineacion)

        scrollY = ttk.Scrollbar(frameTabla, orient="vertical", command=self.tabla.yview)
        scrollX = ttk.Scrollbar(frameTabla, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scrollY.set, xscrollcommand=scrollX.set)

        scrollY.pack(side="right", fill="y")
        scrollX.pack(side="bottom", fill="x")
        self.tabla.pack(fill="both", expand=True)

        self.tabla.tag_configure("par", background="#FFFFFF")
        self.tabla.tag_configure("impar", background="#EBF1F8")
        self.tabla.bind("<<TreeviewSelect>>", self._alSeleccionarFila)

    # Ajusta las etiquetas y estado del formulario según Perecedero o NoPerecedero.
    def _alternarCamposPorTipo(self, evento=None):
        tipoSeleccionado = self.entradas["tipo"].get()
        if tipoSeleccionado == "Perecedero":
            self.lblExtra1.config(text="Caducidad (YYYY-MM-DD):")
            self.lblExtra2.grid()
            self.entryExtra2.grid()
        else:
            self.lblExtra1.config(text="Material de Empaque:")
            self.lblExtra2.grid_remove()
            self.entryExtra2.grid_remove()

    # Limpia todos los campos del formulario y habilita el campo de código.
    def _limpiarFormulario(self, limpiarSeleccion: bool = True):
        self.entradas["codigo"].config(state="normal")
        self.entradas["tipo"].config(state="readonly")
        for clave in ("codigo", "nombre", "stock", "precio", "idCat"):
            self.entradas[clave].delete(0, tk.END)
        self.entradas["nombreCat"].set("Lácteos")
        self.entryExtra1.delete(0, tk.END)
        self.entryExtra2.delete(0, tk.END)
        if limpiarSeleccion:
            self.tabla.selection_remove(self.tabla.selection())

    # Rellena el formulario automáticamente al seleccionar un renglón de la tabla.
    def _alSeleccionarFila(self, evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return

        valores = self.tabla.item(seleccion[0], "values")
        codigo = valores[0]

        try:
            prod = self.tienda.buscarProductoPorCodigo(codigo)
            # Se pasa limpiarSeleccion=False para NO borrar la selección activa de la tabla
            self._limpiarFormulario(limpiarSeleccion=False)

            esPerecedero = isinstance(prod, Perecedero)
            self.entradas["tipo"].set("Perecedero" if esPerecedero else "NoPerecedero")
            self._alternarCamposPorTipo()
            self.entradas["tipo"].config(state="disabled")

            self.entradas["codigo"].insert(0, prod.codigo)
            self.entradas["codigo"].config(state="disabled")
            self.entradas["nombre"].insert(0, prod.nombre)
            self.entradas["stock"].insert(0, str(prod.stock))
            self.entradas["precio"].insert(0, f"{prod.precio.valor:.2f}")
            self.entradas["idCat"].insert(0, str(prod.categoria.idCategoria))
            self.entradas["nombreCat"].set(prod.categoria.nombre)

            if esPerecedero:
                self.entryExtra1.insert(0, prod.fechaCaducidad)
                self.entryExtra2.insert(0, str(prod.temperaturaConservacion))
            else:
                self.entryExtra1.insert(0, prod.materialEmpaque)
        except ProductoNoEncontradoError as e:
            registrarError(f"ProductoNoEncontradoError en selección de tabla: {e}")

    # Valida los campos del formulario y construye un objeto Perecedero o NoPerecedero.
    def _construirProductoDesdeFormulario(self, codigoForzado: str = None):
        tipo = self.entradas["tipo"].get().strip()
        codigo = codigoForzado if codigoForzado else self.entradas["codigo"].get().strip()
        nombre = self.entradas["nombre"].get().strip()
        stockTexto = self.entradas["stock"].get().strip()
        precioTexto = self.entradas["precio"].get().strip()
        idCatTexto = self.entradas["idCat"].get().strip()
        nombreCat = self.entradas["nombreCat"].get().strip()
        extra1 = self.entryExtra1.get().strip()
        extra2 = self.entryExtra2.get().strip()

        if not all([codigo, nombre, stockTexto, precioTexto, idCatTexto, nombreCat, extra1]):
            raise ValueError("Todos los campos obligatorios deben estar llenos.")

        stock = int(stockTexto)
        valorPrecio = float(precioTexto)
        idCat = int(idCatTexto)

        categoria = Categoria(idCat, nombreCat)
        precio = Precio(valorPrecio)

        if tipo == "Perecedero":
            if not extra2:
                raise ValueError("Debe ingresar la temperatura de conservación (°C).")
            temp = float(extra2)
            return Perecedero(codigo, nombre, stock, precio, categoria, extra1, temp)
        return NoPerecedero(codigo, nombre, stock, precio, categoria, extra1)

    # Registra un nuevo producto en la tienda y lo guarda en inventario.txt.
    def _registrarProducto(self):
        try:
            self.entradas["codigo"].config(state="normal")
            nuevoProducto = self._construirProductoDesdeFormulario()
            self.tienda.agregarProducto(nuevoProducto)
            self._guardarYRefrescar(f"Producto '{nuevoProducto.nombre}' registrado y guardado.")
            self._limpiarFormulario()
            messagebox.showinfo(
                "Registro Exitoso",
                f"El producto '{nuevoProducto.nombre}' ({nuevoProducto.codigo}) fue registrado correctamente.",
            )
        except (ValueError, TypeError) as e:
            registrarError(f"{type(e).__name__} al registrar producto en GUI: {e}")
            messagebox.showerror("Error de Validación", str(e))

    # Modifica los datos de un producto existente seleccionado en la tabla.
    def _modificarProducto(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning(
                "Sin Selección",
                "Seleccione un producto de la tabla para poder modificarlo.",
            )
            return

        codigoActual = self.tabla.item(seleccion[0], "values")[0]
        try:
            prodExistente = self.tienda.buscarProductoPorCodigo(codigoActual)
            prodValidado = self._construirProductoDesdeFormulario(codigoForzado=codigoActual)

            prodExistente.nombre = prodValidado.nombre
            prodExistente.stock = prodValidado.stock
            prodExistente.precio.actualizarValor(prodValidado.precio.valor)
            prodExistente.categoria = prodValidado.categoria

            if isinstance(prodExistente, Perecedero) and isinstance(prodValidado, Perecedero):
                prodExistente.fechaCaducidad = prodValidado.fechaCaducidad
                prodExistente.temperaturaConservacion = prodValidado.temperaturaConservacion
            elif isinstance(prodExistente, NoPerecedero) and isinstance(prodValidado, NoPerecedero):
                prodExistente.materialEmpaque = prodValidado.materialEmpaque

            self._guardarYRefrescar(f"Producto '{prodExistente.codigo}' modificado y guardado.")
            self._limpiarFormulario()
            messagebox.showinfo(
                "Modificación Exitosa",
                f"Los datos de '{prodExistente.nombre}' se actualizaron correctamente.",
            )
        except (ValueError, TypeError, ProductoNoEncontradoError) as e:
            registrarError(f"{type(e).__name__} al modificar producto '{codigoActual}': {e}")
            messagebox.showerror("Error al Modificar", str(e))

    # Elimina el producto seleccionado previa confirmación del usuario.
    def _eliminarProducto(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning(
                "Sin Selección",
                "Seleccione un producto de la tabla para eliminarlo.",
            )
            return

        valores = self.tabla.item(seleccion[0], "values")
        codigo = valores[0]
        nombre = valores[1]

        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar '{nombre}' (Código: {codigo}) del inventario?",
        )
        if not confirmar:
            return

        try:
            self.tienda.eliminarProducto(codigo)
            self._guardarYRefrescar(f"Producto '{codigo}' eliminado del inventario.")
            self._limpiarFormulario()
            messagebox.showinfo("Eliminado", f"El producto '{nombre}' fue eliminado.")
        except ProductoNoEncontradoError as e:
            registrarError(f"ProductoNoEncontradoError al eliminar '{codigo}': {e}")
            messagebox.showerror("Error al Eliminar", str(e))

    # Permite reabastecer existencias usando la clase Proveedor.
    def _abastecerConProveedor(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning(
                "Seleccione un Producto",
                "Seleccione primero un producto en la tabla para registrar entrega del proveedor.",
            )
            return

        codigo = self.tabla.item(seleccion[0], "values")[0]
        try:
            prod = self.tienda.buscarProductoPorCodigo(codigo)
            cantidad = simpledialog.askinteger(
                "Reabastecimiento de Proveedor",
                f"Proveedor: {self.proveedorPrincipal.nombre}\n"
                f"Producto: {prod.nombre} (Stock actual: {prod.stock})\n\n"
                "Ingrese la cantidad de unidades entregadas:",
                parent=self.raiz,
            )
            if cantidad is None:
                return

            self.proveedorPrincipal.suministrarProducto(prod, cantidad)
            self._guardarYRefrescar(
                f"Abastecimiento de +{cantidad} unidades para '{prod.nombre}'."
            )
            self._limpiarFormulario()
            messagebox.showinfo(
                "Inventario Reabastecido",
                f"{self.proveedorPrincipal.nombre} suministró {cantidad} unidades.\n"
                f"Nuevo stock de '{prod.nombre}': {prod.stock}",
            )
        except (ValueError, ProductoNoEncontradoError) as e:
            registrarError(f"{type(e).__name__} en abastecimiento GUI: {e}")
            messagebox.showerror("Error de Abastecimiento", str(e))

    # Filtra los productos de la tabla por código o coincidencia de nombre.
    def _buscarEnTabla(self):
        termino = self.entryBusqueda.get().strip().lower()
        if not termino:
            self._actualizarTabla()
            return

        filtrados = [
            p
            for p in self.tienda.consultarInventario()
            if termino in p.codigo.lower() or termino in p.nombre.lower()
        ]

        if not filtrados:
            err = ProductoNoEncontradoError(
                f"No se encontraron productos que coincidan con '{termino}'."
            )
            registrarError(f"ProductoNoEncontradoError en búsqueda GUI: {err}")
            messagebox.showinfo("Sin Resultados", str(err))
            return

        self._actualizarTabla(listaMostrar=filtrados)

    # Guarda el inventario en inventario.txt y refresca la tabla visual.
    def _guardarYRefrescar(self, mensajeEstado: str = ""):
        GestorArchivos.guardarInventario(self.archivoDatos, self.tienda.consultarInventario())
        self._actualizarTabla()
        if mensajeEstado:
            self.varEstado.set(mensajeEstado)

    # Recarga los renglones del Treeview con la lista de productos indicada.
    def _actualizarTabla(self, listaMostrar: list = None):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        productos = (
            listaMostrar
            if listaMostrar is not None
            else self.tienda.consultarInventario()
        )

        valorTotalInventario = 0.0
        for idx, p in enumerate(productos):
            esPerecedero = isinstance(p, Perecedero)
            tipoTexto = "Perecedero" if esPerecedero else "No Perecedero"
            catTexto = f"{p.categoria.idCategoria} - {p.categoria.nombre}"

            if esPerecedero:
                estadoCad = "CADUCADO" if p.verificarCaducidad() else "Vigente"
                detalleTexto = (
                    f"Cad: {p.fechaCaducidad} ({estadoCad}) | {p.temperaturaConservacion}°C"
                )
            else:
                duracion = "Larga duración" if p.esDeLargaDuracion() else "Estándar"
                detalleTexto = f"Empaque: {p.materialEmpaque} ({duracion})"

            etiquetaFila = "par" if idx % 2 == 0 else "impar"
            self.tabla.insert(
                "",
                "end",
                values=(
                    p.codigo,
                    p.nombre,
                    tipoTexto,
                    catTexto,
                    p.stock,
                    f"${p.precio.valor:.2f}",
                    detalleTexto,
                ),
                tags=(etiquetaFila,),
            )
            valorTotalInventario += p.stock * p.precio.valor

        self.varEstado.set(
            f"Productos mostrados: {len(productos)}   |   "
            f"Valor total en inventario: ${valorTotalInventario:,.2f} MXN   |   "
            f"Archivo: inventario.txt"
        )

    # Abre la ventana emergente de punto de venta.
    def _abrirVentanaVenta(self):
        if not self.tienda.consultarInventario():
            messagebox.showwarning(
                "Inventario Vacío",
                "No hay productos disponibles para registrar una venta.",
            )
            return

        VentanaVenta(
            self.raiz,
            self.tienda,
            lambda: self._guardarYRefrescar("Venta registrada e inventario actualizado."),
        )

    # Muestra el contenido actual de log_errores.txt en una ventana emergente.
    def _mostrarBitacoraErrores(self):
        rutaLog = os.path.join(self.rutaBase, "log_errores.txt")
        ventanaLog = tk.Toplevel(self.raiz)
        ventanaLog.title("Bitácora de Errores (log_errores.txt)")
        ventanaLog.geometry("760x420")
        ventanaLog.configure(bg=self.colorFondo)

        tk.Label(
            ventanaLog,
            text="REGISTRO DE EXCEPCIONES Y ERRORES DEL SISTEMA",
            font=self.fuenteNegrita,
            bg=self.colorAzulMarino,
            fg=self.colorNaranja,
            pady=10,
        ).pack(fill="x")

        cajaTexto = tk.Text(
            ventanaLog, font=("Consolas", 11), bg="#FFFFFF", fg=self.colorAzulMarino
        )
        cajaTexto.pack(fill="both", expand=True, padx=12, pady=12)

        if os.path.exists(rutaLog):
            with open(rutaLog, "r", encoding="utf-8") as archivo:
                contenido = archivo.read()
            cajaTexto.insert(
                tk.END, contenido if contenido.strip() else "La bitácora está vacía."
            )
        else:
            cajaTexto.insert(tk.END, "Aún no se han registrado errores en log_errores.txt.")

        cajaTexto.config(state="disabled")
