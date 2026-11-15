#Módulo que define la clase Precio para representar valores monetarios

class Precio:
    #Representa el precio unitario de un producto con validación de monto y moneda
    def __init__(self, valor: float, moneda: str = "MXN"):
        self._valor = float(valor)
        self._moneda = moneda

    @property
    def valor(self):
        return self._valor

    @valor.setter
    def valor(self, nuevoValor):
        if nuevoValor < 0:
            raise ValueError("El precio no puede ser negativo.")
        self._valor = float(nuevoValor)

    @property
    def moneda(self):
        return self._moneda

    def obtenerValor(self) -> float:
        return self._valor

    def actualizarValor(self, nuevoValor: float):
        self.valor = nuevoValor

    def __str__(self):
        return f"${self._valor:.2f} {self._moneda}"


class Categoria:
    def __init__(self, idCategoria: int, nombre: str):
        self._idCategoria = idCategoria
        self._nombre = nombre
        self._listaProductos = []

    @property
    def nombre(self):
        return self._nombre

    def agregarProducto(self, producto):
        self._listaProductos.append(producto)

    def listarProductos(self):
        return self._listaProductos

    def __str__(self):
        return self._nombre


class Producto:
    def __init__(self, codigo: str, nombre: str, stock: int, precio: Precio, categoria: Categoria):
        self._codigo = codigo
        self._nombre = nombre
        self._stock = int(stock)
        self._precio = precio
        self._categoria = categoria

    @property
    def codigo(self):
        return self._codigo

    @property
    def nombre(self):
        return self._nombre

    @property
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, nuevoStock):
        if nuevoStock < 0:
            raise ValueError("El stock no puede ser negativo.")
        self._stock = int(nuevoStock)

    @property
    def precio(self):
        return self._precio

    def actualizarStock(self, cantidad: int):
        self.stock = self._stock + cantidad

    def obtenerPrecio(self) -> Precio:
        return self._precio

    def estaDisponible(self) -> bool:
        return self._stock > 0

    def __str__(self):
        return f"Código: {self._codigo} | Nombre: {self._nombre} | Stock: {self._stock} | Precio: {self._precio}"


class Perecedero(Producto):
    def __init__(self, codigo: str, nombre: str, stock: int, precio: Precio, categoria: Categoria, fechaCaducidad: str, temperaturaConservacion: float):
        super().__init__(codigo, nombre, stock, precio, categoria)
        self._fechaCaducidad = fechaCaducidad
        self._temperaturaConservacion = float(temperaturaConservacion)

    @property
    def fechaCaducidad(self):
        return self._fechaCaducidad

    def verificarCaducidad(self) -> bool:
        return True

    def requiereRefrigeracion(self) -> bool:
        return self._temperaturaConservacion < 10.0

    def __str__(self):
        return super().__str__() + f" [Perecedero - Caduca: {self._fechaCaducidad}]"


class NoPerecedero(Producto):
    def __init__(self, codigo: str, nombre: str, stock: int, precio: Precio, categoria: Categoria, materialEmpaque: str):
        super().__init__(codigo, nombre, stock, precio, categoria)
        self._materialEmpaque = materialEmpaque

    @property
    def materialEmpaque(self):
        return self._materialEmpaque

    def esDeLargaDuracion(self) -> bool:
        return True

    def __str__(self):
        return super().__str__() + f" [No Perecedero - Empaque: {self._materialEmpaque}]"


class Proveedor:
    def __init__(self, idProveedor: int, nombre: str, telefono: str):
        self._idProveedor = idProveedor
        self._nombre = nombre
        self._telefono = telefono

    @property
    def nombre(self):
        return self._nombre

    def suministrarProducto(self, producto: Producto, cantidad: int):
        producto.actualizarStock(cantidad)

    def actualizarDatos(self, nuevoTelefono: str):
        self._telefono = nuevoTelefono

    def __str__(self):
        return f"Proveedor: {self._nombre} (Tel: {self._telefono})"


class DetalleVenta:
    def __init__(self, producto: Producto, cantidad: int):
        self._producto = producto
        self._cantidad = int(cantidad)
        self._subtotal = self.calcularSubtotal()

    @property
    def cantidad(self):
        return self._cantidad

    def calcularSubtotal(self) -> float:
        return self._producto.obtenerPrecio().obtenerValor() * self._cantidad

    def actualizarCantidad(self, nuevaCantidad: int):
        if nuevaCantidad <= 0:
            raise ValueError("La cantidad en el detalle debe ser mayor a cero.")
        self._cantidad = nuevaCantidad
        self._subtotal = self.calcularSubtotal()

    def __str__(self):
        return f"{self._cantidad}x {self._producto.nombre} - Subtotal: ${self._subtotal:.2f}"


class Venta:
    def __init__(self, numero: int, fecha: str):
        self._numero = int(numero)
        self._fecha = fecha
        self._listaDetalles = []
        self._total = 0.0

    def agregarDetalle(self, detalle: DetalleVenta):
        self._listaDetalles.append(detalle)
        self._total = self.calcularTotal()

    def calcularTotal(self) -> float:
        return sum(d._subtotal for d in self._listaDetalles)

    def generarTicket(self) -> str:
        ticket = f"\n--- TICKET DE VENTA #{self._numero} ---\nFecha: {self._fecha}\n"
        for det in self._listaDetalles:
            ticket += f"  - {det}\n"
        ticket += f"TOTAL A PAGAR: ${self._total:.2f}\n--------------------------------------"
        return ticket


class Tienda:
    def __init__(self, nombre: str, direccion: str):
        self._nombre = nombre
        self._direccion = direccion
        self._inventario = []

    def agregarProducto(self, producto: Producto):
        self._inventario.append(producto)

    def consultarInventario(self):
        return self._inventario

    def __str__(self):
        return f"Tienda: {self._nombre} | Dirección: {self._direccion}"
