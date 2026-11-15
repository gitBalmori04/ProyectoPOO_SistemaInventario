# Módulo que define las clases del dominio para el sistema de inventario de abarrotes.

from datetime import datetime
from utils.excepciones import ProductoNoEncontradoError, StockInsuficienteError


# Representa el precio unitario de un producto con validación de monto y divisa.
class Precio:
    # Inicializa el precio validando desde el constructor que no sea negativo.
    def __init__(self, valor: float, moneda: str = "MXN"):
        if not moneda or not str(moneda).strip():
            raise ValueError("La moneda no puede estar vacía.")
        self._moneda = str(moneda).strip().upper()
        self.valor = valor  # Invoca al setter para validar desde __init__

    # Devuelve el monto numérico del precio.
    @property
    def valor(self) -> float:
        return self._valor

    # Asigna un nuevo monto verificando que sea mayor o igual a cero.
    @valor.setter
    def valor(self, nuevoValor: float):
        valorFloat = float(nuevoValor)
        if valorFloat < 0:
            raise ValueError("El precio no puede ser negativo.")
        self._valor = valorFloat

    # Devuelve el código de moneda (ej. MXN).
    @property
    def moneda(self) -> str:
        return self._moneda

    # Retorna el valor numérico del precio.
    def obtenerValor(self) -> float:
        return self._valor

    # Actualiza el valor del precio pasando por la validación del setter.
    def actualizarValor(self, nuevoValor: float):
        self.valor = nuevoValor

    # Devuelve el precio formateado con símbolo y divisa.
    def __str__(self) -> str:
        return f"${self._valor:.2f} {self._moneda}"


# Representa una categoría de productos dentro de la tienda.
class Categoria:
    # Inicializa la categoría validando su identificador y nombre.
    def __init__(self, idCategoria: int, nombre: str):
        if int(idCategoria) <= 0:
            raise ValueError("El ID de la categoría debe ser mayor a cero.")
        if not nombre or not str(nombre).strip():
            raise ValueError("El nombre de la categoría no puede estar vacío.")
        self._idCategoria = int(idCategoria)
        self._nombre = str(nombre).strip()
        self._listaProductos = []

    # Devuelve el identificador numérico de la categoría.
    @property
    def idCategoria(self) -> int:
        return self._idCategoria

    # Devuelve el nombre de la categoría.
    @property
    def nombre(self) -> str:
        return self._nombre

    # Devuelve una copia de los productos registrados en la categoría.
    @property
    def listaProductos(self) -> list:
        return list(self._listaProductos)

    # Asocia un producto a esta categoría.
    def agregarProducto(self, producto):
        if producto not in self._listaProductos:
            self._listaProductos.append(producto)

    # Retorna la lista de productos pertenecientes a la categoría.
    def listarProductos(self) -> list:
        return list(self._listaProductos)

    # Devuelve el nombre de la categoría.
    def __str__(self) -> str:
        return self._nombre


# Clase base que modela un artículo general del inventario.
class Producto:
    # Inicializa un producto validando que código, nombre y stock sean válidos.
    def __init__(self, codigo: str, nombre: str, stock: int, precio: Precio, categoria: Categoria):
        if not codigo or not str(codigo).strip():
            raise ValueError("El código del producto no puede estar vacío.")
        if not isinstance(precio, Precio):
            raise TypeError("El precio debe ser una instancia de Precio.")

        self._codigo = str(codigo).strip()
        self.nombre = nombre
        self.stock = stock  # Invoca al setter para rechazar stock negativo desde __init__
        self._precio = precio
        self.categoria = categoria

    # Devuelve el código único del producto.
    @property
    def codigo(self) -> str:
        return self._codigo

    # Devuelve el nombre del producto.
    @property
    def nombre(self) -> str:
        return self._nombre

    # Asigna un nuevo nombre validando que no esté vacío.
    @nombre.setter
    def nombre(self, nuevoNombre: str):
        if not nuevoNombre or not str(nuevoNombre).strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
        self._nombre = str(nuevoNombre).strip()

    # Devuelve las existencias actuales del producto.
    @property
    def stock(self) -> int:
        return self._stock

    # Asigna un nuevo valor de stock verificando que no sea negativo.
    @stock.setter
    def stock(self, nuevoStock: int):
        if isinstance(nuevoStock, bool):
            raise TypeError("El stock debe ser un número entero, no booleano.")
        stockInt = int(nuevoStock)
        if stockInt < 0:
            raise ValueError("El stock no puede ser negativo.")
        self._stock = stockInt

    # Devuelve el objeto Precio asociado al producto.
    @property
    def precio(self) -> Precio:
        return self._precio

    # Devuelve el objeto Categoria asociado al producto.
    @property
    def categoria(self) -> Categoria:
        return self._categoria

    # Asigna una nueva categoría validando su tipo.
    @categoria.setter
    def categoria(self, nuevaCategoria: Categoria):
        if not isinstance(nuevaCategoria, Categoria):
            raise TypeError("La categoría debe ser una instancia de Categoria.")
        self._categoria = nuevaCategoria
        self._categoria.agregarProducto(self)

    # Incrementa o decrementa el stock; lanza StockInsuficienteError si no alcanza.
    def actualizarStock(self, cantidad: int):
        cantidadInt = int(cantidad)
        if self._stock + cantidadInt < 0:
            raise StockInsuficienteError(
                f"Stock insuficiente para '{self._nombre}'. Disponible: {self._stock}, solicitado: {abs(cantidadInt)}."
            )
        self._stock += cantidadInt

    # Retorna el objeto Precio del producto.
    def obtenerPrecio(self) -> Precio:
        return self._precio

    # Indica si existe al menos una unidad disponible.
    def estaDisponible(self) -> bool:
        return self._stock > 0

    # Devuelve la representación textual del producto.
    def __str__(self) -> str:
        return (
            f"Código: {self._codigo} | Nombre: {self._nombre} | "
            f"Categoría: {self._categoria.nombre} (ID:{self._categoria.idCategoria}) | "
            f"Stock: {self._stock} | Precio: {self._precio}"
        )


# Subclase de Producto para artículos con fecha de caducidad y control térmico.
class Perecedero(Producto):
    # Inicializa un producto perecedero validando el formato de su fecha de caducidad.
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
        super().__init__(codigo, nombre, stock, precio, categoria)
        self.fechaCaducidad = fechaCaducidad
        self.temperaturaConservacion = temperaturaConservacion

    # Devuelve la fecha de caducidad en texto.
    @property
    def fechaCaducidad(self) -> str:
        return self._fechaCaducidad

    # Actualiza y valida el formato de la fecha de caducidad.
    @fechaCaducidad.setter
    def fechaCaducidad(self, nuevaFecha: str):
        fechaLimpia = str(nuevaFecha).strip()
        for formato in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                datetime.strptime(fechaLimpia, formato)
                self._fechaCaducidad = fechaLimpia
                return
            except ValueError:
                continue
        raise ValueError(
            f"Formato de fecha inválido: '{fechaLimpia}'. Use YYYY-MM-DD."
        )

    # Devuelve la temperatura de conservación en grados Celsius.
    @property
    def temperaturaConservacion(self) -> float:
        return self._temperaturaConservacion

    # Actualiza la temperatura de conservación.
    @temperaturaConservacion.setter
    def temperaturaConservacion(self, nuevaTemp: float):
        self._temperaturaConservacion = float(nuevaTemp)

    # Convierte la fecha de caducidad a objeto date (acepta YYYY-MM-DD o DD/MM/YYYY).
    def _obtenerFechaDate(self):
        for formato in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(self._fechaCaducidad, formato).date()
            except ValueError:
                continue
        raise ValueError(
            f"Formato de fecha inválido: '{self._fechaCaducidad}'. Use YYYY-MM-DD."
        )

    # Evalúa si el producto ya caducó comparando su fecha contra la fecha actual.
    def verificarCaducidad(self) -> bool:
        fechaCad = self._obtenerFechaDate()
        return fechaCad < datetime.now().date()

    # Retorna True si el producto requiere temperatura menor a 10 °C.
    def requiereRefrigeracion(self) -> bool:
        return self._temperaturaConservacion < 10.0

    # Devuelve la descripción del producto perecedero y su estado de caducidad.
    def __str__(self) -> str:
        estado = "CADUCADO" if self.verificarCaducidad() else "Vigente"
        return (
            super().__str__()
            + f" [Perecedero - Caduca: {self._fechaCaducidad} ({estado})]"
        )


# Subclase de Producto para artículos de almacén sin caducidad inmediata.
class NoPerecedero(Producto):
    # Inicializa un producto no perecedero validando su material de empaque.
    def __init__(
        self,
        codigo: str,
        nombre: str,
        stock: int,
        precio: Precio,
        categoria: Categoria,
        materialEmpaque: str,
    ):
        super().__init__(codigo, nombre, stock, precio, categoria)
        self.materialEmpaque = materialEmpaque

    # Devuelve el material de empaque del producto.
    @property
    def materialEmpaque(self) -> str:
        return self._materialEmpaque

    # Actualiza y valida el material de empaque.
    @materialEmpaque.setter
    def materialEmpaque(self, nuevoMaterial: str):
        if not nuevoMaterial or not str(nuevoMaterial).strip():
            raise ValueError("El material de empaque no puede estar vacío.")
        self._materialEmpaque = str(nuevoMaterial).strip()

    # Evalúa si el material de empaque garantiza conservación prolongada.
    def esDeLargaDuracion(self) -> bool:
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

    # Devuelve la descripción del producto no perecedero y su empaque.
    def __str__(self) -> str:
        duracion = "Larga duración" if self.esDeLargaDuracion() else "Duración estándar"
        return (
            super().__str__()
            + f" [No Perecedero - Empaque: {self._materialEmpaque} ({duracion})]"
        )


# Representa un proveedor encargado de suministrar mercancía a la tienda.
class Proveedor:
    # Inicializa un proveedor validando su identificador, nombre y teléfono.
    def __init__(self, idProveedor: int, nombre: str, telefono: str):
        if int(idProveedor) <= 0:
            raise ValueError("El ID del proveedor debe ser mayor a cero.")
        if not nombre or not str(nombre).strip():
            raise ValueError("El nombre del proveedor no puede estar vacío.")
        if not telefono or not str(telefono).strip():
            raise ValueError("El teléfono del proveedor no puede estar vacío.")

        self._idProveedor = int(idProveedor)
        self._nombre = str(nombre).strip()
        self._telefono = str(telefono).strip()

    # Devuelve el identificador del proveedor.
    @property
    def idProveedor(self) -> int:
        return self._idProveedor

    # Devuelve el nombre del proveedor.
    @property
    def nombre(self) -> str:
        return self._nombre

    # Devuelve el teléfono de contacto del proveedor.
    @property
    def telefono(self) -> str:
        return self._telefono

    # Abastece unidades de un producto incrementando su stock.
    def suministrarProducto(self, producto: Producto, cantidad: int):
        if int(cantidad) <= 0:
            raise ValueError("La cantidad suministrada debe ser mayor a cero.")
        producto.actualizarStock(int(cantidad))

    # Actualiza el número telefónico del proveedor.
    def actualizarDatos(self, nuevoTelefono: str):
        if not nuevoTelefono or not str(nuevoTelefono).strip():
            raise ValueError("El teléfono no puede estar vacío.")
        self._telefono = str(nuevoTelefono).strip()

    # Devuelve la representación textual del proveedor.
    def __str__(self) -> str:
        return f"Proveedor #{self._idProveedor}: {self._nombre} (Tel: {self._telefono})"


# Representa una línea de producto y cantidad dentro de una venta.
class DetalleVenta:
    # Inicializa un detalle validando cantidad positiva y existencias disponibles.
    def __init__(self, producto: Producto, cantidad: int):
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

    # Devuelve el producto asociado al detalle.
    @property
    def producto(self) -> Producto:
        return self._producto

    # Devuelve la cantidad de unidades incluidas en el detalle.
    @property
    def cantidad(self) -> int:
        return self._cantidad

    # Devuelve el subtotal calculado del detalle.
    @property
    def subtotal(self) -> float:
        return self._subtotal

    # Calcula el subtotal multiplicando el precio unitario por la cantidad.
    def calcularSubtotal(self) -> float:
        return self._producto.obtenerPrecio().obtenerValor() * self._cantidad

    # Actualiza la cantidad del detalle y recalcula su subtotal.
    def actualizarCantidad(self, nuevaCantidad: int):
        cantidadInt = int(nuevaCantidad)
        if cantidadInt <= 0:
            raise ValueError("La cantidad en el detalle debe ser mayor a cero.")
        if cantidadInt > self._producto.stock:
            raise StockInsuficienteError(
                f"Stock insuficiente para '{self._producto.nombre}' (Disponible: {self._producto.stock})."
            )
        self._cantidad = cantidadInt
        self._subtotal = self.calcularSubtotal()

    # Devuelve la línea formateada del detalle de venta.
    def __str__(self) -> str:
        return f"{self._cantidad}x {self._producto.nombre} - Subtotal: ${self._subtotal:.2f}"


# Representa una transacción de venta con sus detalles y total.
class Venta:
    # Inicializa una venta con número de ticket y fecha.
    def __init__(self, numero: int, fecha: str):
        if int(numero) <= 0:
            raise ValueError("El número de venta debe ser mayor a cero.")
        if not fecha or not str(fecha).strip():
            raise ValueError("La fecha de la venta no puede estar vacía.")

        self._numero = int(numero)
        self._fecha = str(fecha).strip()
        self._listaDetalles = []
        self._total = 0.0

    # Devuelve el número de folio de la venta.
    @property
    def numero(self) -> int:
        return self._numero

    # Devuelve la fecha de la venta.
    @property
    def fecha(self) -> str:
        return self._fecha

    # Devuelve una copia de la lista de detalles de la venta.
    @property
    def listaDetalles(self) -> list:
        return list(self._listaDetalles)

    # Devuelve el total acumulado de la venta.
    @property
    def total(self) -> float:
        return self._total

    # Agrega un detalle, descuenta el stock del producto y actualiza el total.
    def agregarDetalle(self, detalle: DetalleVenta):
        detalle.producto.actualizarStock(-detalle.cantidad)
        self._listaDetalles.append(detalle)
        self._total = self.calcularTotal()

    # Suma los subtotales de todos los detalles mediante su propiedad pública.
    def calcularTotal(self) -> float:
        return sum(d.subtotal for d in self._listaDetalles)

    # Genera el ticket de compra formateado.
    def generarTicket(self) -> str:
        ticket = f"\n--- TICKET DE VENTA #{self._numero} ---\nFecha: {self._fecha}\n"
        for det in self._listaDetalles:
            ticket += f"  - {det}\n"
        ticket += f"TOTAL A PAGAR: ${self._total:.2f}\n--------------------------------------"
        return ticket


# Representa la tienda de abarrotes y administra su catálogo e inventario.
class Tienda:
    # Inicializa la tienda con su nombre, dirección e inventario vacío.
    def __init__(self, nombre: str, direccion: str):
        if not nombre or not str(nombre).strip():
            raise ValueError("El nombre de la tienda no puede estar vacío.")
        if not direccion or not str(direccion).strip():
            raise ValueError("La dirección de la tienda no puede estar vacía.")

        self._nombre = str(nombre).strip()
        self._direccion = str(direccion).strip()
        self._inventario = []
        self._indiceCodigos = {}

    # Devuelve el nombre de la tienda.
    @property
    def nombre(self) -> str:
        return self._nombre

    # Devuelve la dirección de la tienda.
    @property
    def direccion(self) -> str:
        return self._direccion

    # Devuelve una copia de la lista de productos en inventario.
    @property
    def inventario(self) -> list:
        return list(self._inventario)

    # Agrega un producto al inventario y lo indexa por su código.
    def agregarProducto(self, producto: Producto):
        clave = producto.codigo.upper()
        if clave in self._indiceCodigos:
            raise ValueError(f"Ya existe un producto con el código '{producto.codigo}'.")
        self._inventario.append(producto)
        self._indiceCodigos[clave] = producto

    # Busca un producto por código; lanza ProductoNoEncontradoError si no existe.
    def buscarProductoPorCodigo(self, codigo: str) -> Producto:
        clave = str(codigo).strip().upper()
        try:
            return self._indiceCodigos[clave]
        except KeyError as e:
            raise ProductoNoEncontradoError(
                f"No se encontró el producto con código '{codigo}'."
            ) from e

    # Elimina un producto del inventario y de su índice usando su código único.
    def eliminarProducto(self, codigo: str) -> Producto:
        clave = str(codigo).strip().upper()
        productoEliminar = self.buscarProductoPorCodigo(clave)
        self._inventario.remove(productoEliminar)
        del self._indiceCodigos[clave]
        return productoEliminar

    # Reemplaza el inventario actual de forma segura manteniendo el encapsulamiento.
    def reemplazarInventario(self, nuevaLista: list):
        self._inventario = []
        self._indiceCodigos = {}
        for prod in nuevaLista:
            self.agregarProducto(prod)

    # Retorna una copia de los productos registrados en la tienda.
    def consultarInventario(self) -> list:
        return list(self._inventario)

    # Devuelve la descripción general de la tienda.
    def __str__(self) -> str:
        return f"Tienda: {self._nombre} | Dirección: {self._direccion}"
