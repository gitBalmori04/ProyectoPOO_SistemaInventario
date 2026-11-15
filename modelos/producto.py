"""Módulo que define las clases del dominio para el sistema de inventario de abarrotes."""

from datetime import datetime
from utils.excepciones import ProductoNoEncontradoError, StockInsuficienteError


class Precio:
    """Representa el precio unitario de un producto con validación de monto y divisa."""

    def __init__(self, valor: float, moneda: str = "MXN"):
        """Inicializa el precio validando desde el constructor que no sea negativo."""
        if not moneda or not str(moneda).strip():
            raise ValueError("La moneda no puede estar vacía.")
        self._moneda = str(moneda).strip().upper()
        self.valor = valor  # Invoca al setter para validar desde __init__

    @property
    def valor(self) -> float:
        """Devuelve el monto numérico del precio."""
        return self._valor

    @valor.setter
    def valor(self, nuevoValor: float):
        """Asigna un nuevo monto verificando que sea mayor o igual a cero."""
        valorFloat = float(nuevoValor)
        if valorFloat < 0:
            raise ValueError("El precio no puede ser negativo.")
        self._valor = valorFloat

    @property
    def moneda(self) -> str:
        """Devuelve el código de moneda (ej. MXN)."""
        return self._moneda

    def obtenerValor(self) -> float:
        """Retorna el valor numérico del precio."""
        return self._valor

    def actualizarValor(self, nuevoValor: float):
        """Actualiza el valor del precio pasando por la validación del setter."""
        self.valor = nuevoValor

    def __str__(self) -> str:
        """Devuelve el precio formateado con símbolo y divisa."""
        return f"${self._valor:.2f} {self._moneda}"


class Categoria:
    """Representa una categoría de productos dentro de la tienda."""

    def __init__(self, idCategoria: int, nombre: str):
        """Inicializa la categoría validando su identificador y nombre."""
        if int(idCategoria) <= 0:
            raise ValueError("El ID de la categoría debe ser mayor a cero.")
        if not nombre or not str(nombre).strip():
            raise ValueError("El nombre de la categoría no puede estar vacío.")
        self._idCategoria = int(idCategoria)
        self._nombre = str(nombre).strip()
        self._listaProductos = []

    @property
    def idCategoria(self) -> int:
        """Devuelve el identificador numérico de la categoría."""
        return self._idCategoria

    @property
    def nombre(self) -> str:
        """Devuelve el nombre de la categoría."""
        return self._nombre

    @property
    def listaProductos(self) -> list:
        """Devuelve una copia de los productos registrados en la categoría."""
        return list(self._listaProductos)

    def agregarProducto(self, producto):
        """Asocia un producto a esta categoría."""
        if producto not in self._listaProductos:
            self._listaProductos.append(producto)

    def listarProductos(self) -> list:
        """Retorna la lista de productos pertenecientes a la categoría."""
        return list(self._listaProductos)

    def __str__(self) -> str:
        """Devuelve el nombre de la categoría."""
        return self._nombre


class Producto:
    """Clase base que modela un artículo general del inventario."""

    def __init__(self, codigo: str, nombre: str, stock: int, precio: Precio, categoria: Categoria):
        """Inicializa un producto validando que código, nombre y stock sean válidos."""
        if not codigo or not str(codigo).strip():
            raise ValueError("El código del producto no puede estar vacío.")
        if not nombre or not str(nombre).strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
        if not isinstance(precio, Precio):
            raise TypeError("El precio debe ser una instancia de Precio.")
        if not isinstance(categoria, Categoria):
            raise TypeError("La categoría debe ser una instancia de Categoria.")

        self._codigo = str(codigo).strip()
        self._nombre = str(nombre).strip()
        self.stock = stock  # Invoca al setter para rechazar stock negativo desde __init__
        self._precio = precio
        self._categoria = categoria
        self._categoria.agregarProducto(self)

    @property
    def codigo(self) -> str:
        """Devuelve el código único del producto."""
        return self._codigo

    @property
    def nombre(self) -> str:
        """Devuelve el nombre del producto."""
        return self._nombre

    @property
    def stock(self) -> int:
        """Devuelve las existencias actuales del producto."""
        return self._stock

    @stock.setter
    def stock(self, nuevoStock: int):
        """Asigna un nuevo valor de stock verificando que no sea negativo."""
        if isinstance(nuevoStock, bool):
            raise TypeError("El stock debe ser un número entero, no booleano.")
        stockInt = int(nuevoStock)
        if stockInt < 0:
            raise ValueError("El stock no puede ser negativo.")
        self._stock = stockInt

    @property
    def precio(self) -> Precio:
        """Devuelve el objeto Precio asociado al producto."""
        return self._precio

    @property
    def categoria(self) -> Categoria:
        """Devuelve el objeto Categoria asociado al producto."""
        return self._categoria

    def actualizarStock(self, cantidad: int):
        """Incrementa o decrementa el stock; lanza StockInsuficienteError si no alcanza."""
        cantidadInt = int(cantidad)
        if self._stock + cantidadInt < 0:
            raise StockInsuficienteError(
                f"Stock insuficiente para '{self._nombre}'. Disponible: {self._stock}, solicitado: {abs(cantidadInt)}."
            )
        self._stock += cantidadInt

    def obtenerPrecio(self) -> Precio:
        """Retorna el objeto Precio del producto."""
        return self._precio

    def estaDisponible(self) -> bool:
        """Indica si existe al menos una unidad disponible."""
        return self._stock > 0

    def __str__(self) -> str:
        """Devuelve la representación textual del producto."""
        return (
            f"Código: {self._codigo} | Nombre: {self._nombre} | "
            f"Categoría: {self._categoria.nombre} (ID:{self._categoria.idCategoria}) | "
            f"Stock: {self._stock} | Precio: {self._precio}"
        )


class Perecedero(Producto):
    """Subclase de Producto para artículos con fecha de caducidad y control térmico."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        stock: int,
        precio: Precio,
        categoria: Categoria,
        fechaCaducidad: str,
        temperaturaConservacion: float,
    ):
        """Inicializa un producto perecedero validando el formato de su fecha de caducidad."""
        super().__init__(codigo, nombre, stock, precio, categoria)
        self._fechaCaducidad = str(fechaCaducidad).strip()
        self._obtenerFechaDate()  # Valida que la fecha sea real desde el constructor
        self._temperaturaConservacion = float(temperaturaConservacion)

    @property
    def fechaCaducidad(self) -> str:
        """Devuelve la fecha de caducidad en texto."""
        return self._fechaCaducidad

    @property
    def temperaturaConservacion(self) -> float:
        """Devuelve la temperatura de conservación en grados Celsius."""
        return self._temperaturaConservacion

    def _obtenerFechaDate(self):
        """Convierte la fecha de caducidad a objeto date (acepta YYYY-MM-DD o DD/MM/YYYY)."""
        for formato in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(self._fechaCaducidad, formato).date()
            except ValueError:
                continue
        raise ValueError(
            f"Formato de fecha inválido: '{self._fechaCaducidad}'. Use YYYY-MM-DD."
        )

    def verificarCaducidad(self) -> bool:
        """Evalúa si el producto ya caducó comparando su fecha contra la fecha actual."""
        fechaCad = self._obtenerFechaDate()
        return fechaCad < datetime.now().date()

    def requiereRefrigeracion(self) -> bool:
        """Retorna True si el producto requiere temperatura menor a 10 °C."""
        return self._temperaturaConservacion < 10.0

    def __str__(self) -> str:
        """Devuelve la descripción del producto perecedero y su estado de caducidad."""
        estado = "CADUCADO" if self.verificarCaducidad() else "Vigente"
        return (
            super().__str__()
            + f" [Perecedero - Caduca: {self._fechaCaducidad} ({estado})]"
        )


class NoPerecedero(Producto):
    """Subclase de Producto para artículos de almacén sin caducidad inmediata."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        stock: int,
        precio: Precio,
        categoria: Categoria,
        materialEmpaque: str,
    ):
        """Inicializa un producto no perecedero validando su material de empaque."""
        super().__init__(codigo, nombre, stock, precio, categoria)
        if not materialEmpaque or not str(materialEmpaque).strip():
            raise ValueError("El material de empaque no puede estar vacío.")
        self._materialEmpaque = str(materialEmpaque).strip()

    @property
    def materialEmpaque(self) -> str:
        """Devuelve el material de empaque del producto."""
        return self._materialEmpaque

    def esDeLargaDuracion(self) -> bool:
        """Evalúa si el material de empaque garantiza conservación prolongada."""
        empaquesLargaDuracion = {
            "lata",
            "vidrio",
            "enlatado",
            "frasco",
            "metal",
            "tetra pak",
            "tetrapak",
            "aluminio",
            "plastico sellado",
            "plástico sellado",
        }
        return self._materialEmpaque.lower() in empaquesLargaDuracion

    def __str__(self) -> str:
        """Devuelve la descripción del producto no perecedero y su empaque."""
        duracion = "Larga duración" if self.esDeLargaDuracion() else "Duración estándar"
        return (
            super().__str__()
            + f" [No Perecedero - Empaque: {self._materialEmpaque} ({duracion})]"
        )


class Proveedor:
    """Representa un proveedor encargado de suministrar mercancía a la tienda."""

    def __init__(self, idProveedor: int, nombre: str, telefono: str):
        """Inicializa un proveedor validando su identificador, nombre y teléfono."""
        if int(idProveedor) <= 0:
            raise ValueError("El ID del proveedor debe ser mayor a cero.")
        if not nombre or not str(nombre).strip():
            raise ValueError("El nombre del proveedor no puede estar vacío.")
        if not telefono or not str(telefono).strip():
            raise ValueError("El teléfono del proveedor no puede estar vacío.")

        self._idProveedor = int(idProveedor)
        self._nombre = str(nombre).strip()
        self._telefono = str(telefono).strip()

    @property
    def idProveedor(self) -> int:
        """Devuelve el identificador del proveedor."""
        return self._idProveedor

    @property
    def nombre(self) -> str:
        """Devuelve el nombre del proveedor."""
        return self._nombre

    @property
    def telefono(self) -> str:
        """Devuelve el teléfono de contacto del proveedor."""
        return self._telefono

    def suministrarProducto(self, producto: Producto, cantidad: int):
        """Abastece unidades de un producto incrementando su stock."""
        if int(cantidad) <= 0:
            raise ValueError("La cantidad suministrada debe ser mayor a cero.")
        producto.actualizarStock(int(cantidad))

    def actualizarDatos(self, nuevoTelefono: str):
        """Actualiza el número telefónico del proveedor."""
        if not nuevoTelefono or not str(nuevoTelefono).strip():
            raise ValueError("El teléfono no puede estar vacío.")
        self._telefono = str(nuevoTelefono).strip()

    def __str__(self) -> str:
        """Devuelve la representación textual del proveedor."""
        return f"Proveedor #{self._idProveedor}: {self._nombre} (Tel: {self._telefono})"


class DetalleVenta:
    """Representa una línea de producto y cantidad dentro de una venta."""

    def __init__(self, producto: Producto, cantidad: int):
        """Inicializa un detalle validando cantidad positiva y existencias disponibles."""
        cantidadInt = int(cantidad)
        if cantidadInt <= 0:
            raise ValueError("La cantidad en el detalle debe ser mayor a cero.")
        if cantidadInt > producto.stock:
            raise StockInsuficienteError(
                f"Stock insuficiente para '{producto.nombre}'. Disponible: {producto.stock}, solicitado: {cantidadInt}."
            )

        self._producto = producto
        self._cantidad = cantidadInt
        self._subtotal = self.calcularSubtotal()

    @property
    def producto(self) -> Producto:
        """Devuelve el producto asociado al detalle."""
        return self._producto

    @property
    def cantidad(self) -> int:
        """Devuelve la cantidad de unidades incluidas en el detalle."""
        return self._cantidad

    @property
    def subtotal(self) -> float:
        """Devuelve el subtotal calculado del detalle."""
        return self._subtotal

    def calcularSubtotal(self) -> float:
        """Calcula el subtotal multiplicando el precio unitario por la cantidad."""
        return self._producto.obtenerPrecio().obtenerValor() * self._cantidad

    def actualizarCantidad(self, nuevaCantidad: int):
        """Actualiza la cantidad del detalle y recalcula su subtotal."""
        cantidadInt = int(nuevaCantidad)
        if cantidadInt <= 0:
            raise ValueError("La cantidad en el detalle debe ser mayor a cero.")
        if cantidadInt > self._producto.stock:
            raise StockInsuficienteError(
                f"Stock insuficiente para '{self._producto.nombre}' (Disponible: {self._producto.stock})."
            )
        self._cantidad = cantidadInt
        self._subtotal = self.calcularSubtotal()

    def __str__(self) -> str:
        """Devuelve la línea formateada del detalle de venta."""
        return f"{self._cantidad}x {self._producto.nombre} - Subtotal: ${self._subtotal:.2f}"


class Venta:
    """Representa una transacción de venta con sus detalles y total."""

    def __init__(self, numero: int, fecha: str):
        """Inicializa una venta con número de ticket y fecha."""
        if int(numero) <= 0:
            raise ValueError("El número de venta debe ser mayor a cero.")
        if not fecha or not str(fecha).strip():
            raise ValueError("La fecha de la venta no puede estar vacía.")

        self._numero = int(numero)
        self._fecha = str(fecha).strip()
        self._listaDetalles = []
        self._total = 0.0

    @property
    def numero(self) -> int:
        """Devuelve el número de folio de la venta."""
        return self._numero

    @property
    def fecha(self) -> str:
        """Devuelve la fecha de la venta."""
        return self._fecha

    @property
    def listaDetalles(self) -> list:
        """Devuelve una copia de la lista de detalles de la venta."""
        return list(self._listaDetalles)

    @property
    def total(self) -> float:
        """Devuelve el total acumulado de la venta."""
        return self._total

    def agregarDetalle(self, detalle: DetalleVenta):
        """Agrega un detalle, descuenta el stock del producto y actualiza el total."""
        detalle.producto.actualizarStock(-detalle.cantidad)
        self._listaDetalles.append(detalle)
        self._total = self.calcularTotal()

    def calcularTotal(self) -> float:
        """Suma los subtotales de todos los detalles mediante su propiedad pública."""
        return sum(d.subtotal for d in self._listaDetalles)

    def generarTicket(self) -> str:
        """Genera el ticket de compra formateado."""
        ticket = f"\n--- TICKET DE VENTA #{self._numero} ---\nFecha: {self._fecha}\n"
        for det in self._listaDetalles:
            ticket += f"  - {det}\n"
        ticket += f"TOTAL A PAGAR: ${self._total:.2f}\n--------------------------------------"
        return ticket


class Tienda:
    """Representa la tienda de abarrotes y administra su catálogo e inventario."""

    def __init__(self, nombre: str, direccion: str):
        """Inicializa la tienda con su nombre, dirección e inventario vacío."""
        if not nombre or not str(nombre).strip():
            raise ValueError("El nombre de la tienda no puede estar vacío.")
        if not direccion or not str(direccion).strip():
            raise ValueError("La dirección de la tienda no puede estar vacía.")

        self._nombre = str(nombre).strip()
        self._direccion = str(direccion).strip()
        self._inventario = []
        self._indiceCodigos = {}

    @property
    def nombre(self) -> str:
        """Devuelve el nombre de la tienda."""
        return self._nombre

    @property
    def direccion(self) -> str:
        """Devuelve la dirección de la tienda."""
        return self._direccion

    @property
    def inventario(self) -> list:
        """Devuelve una copia de la lista de productos en inventario."""
        return list(self._inventario)

    def agregarProducto(self, producto: Producto):
        """Agrega un producto al inventario y lo indexa por su código."""
        clave = producto.codigo.upper()
        if clave in self._indiceCodigos:
            raise ValueError(f"Ya existe un producto con el código '{producto.codigo}'.")
        self._inventario.append(producto)
        self._indiceCodigos[clave] = producto

    def buscarProductoPorCodigo(self, codigo: str) -> Producto:
        """Busca un producto por código; lanza ProductoNoEncontradoError si no existe."""
        clave = str(codigo).strip().upper()
        try:
            return self._indiceCodigos[clave]
        except KeyError as e:
            raise ProductoNoEncontradoError(
                f"No se encontró el producto con código '{codigo}'."
            ) from e

    def reemplazarInventario(self, nuevaLista: list):
        """Reemplaza el inventario actual de forma segura manteniendo el encapsulamiento."""
        self._inventario = []
        self._indiceCodigos = {}
        for prod in nuevaLista:
            self.agregarProducto(prod)

    def consultarInventario(self) -> list:
        """Retorna una copia de los productos registrados en la tienda."""
        return list(self._inventario)

    def __str__(self) -> str:
        """Devuelve la descripción general de la tienda."""
        return f"Tienda: {self._nombre} | Dirección: {self._direccion}"
