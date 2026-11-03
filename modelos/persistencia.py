import os
from modelos.producto import Producto, Perecedero, NoPerecedero, Precio, Categoria
from utils.excepciones import registrarError

class GestorArchivos:
    @staticmethod
    def guardarInventario(rutaArchivo: str, listaProductos: list):
        """Guarda la lista de productos en un archivo de texto plano utilizando utf-8."""
        try:
            with open(rutaArchivo, "w", encoding="utf-8") as archivo:
                for p in listaProductos:
                    tipo = "Perecedero" if isinstance(p, Perecedero) else "NoPerecedero"
                    extra = p.fechaCaducidad if isinstance(p, Perecedero) else p.materialEmpaque
                    temp = p._temperaturaConservacion if isinstance(p, Perecedero) else 0.0
                    
                    linea = f"{tipo},{p.codigo},{p.nombre},{p.stock},{p.precio.obtenerValor()},{p._categoria.nombre},{extra},{temp}\n"
                    archivo.write(linea)
            print("✔ Inventario guardado exitosamente en archivo.")
        except Exception as e:
            registrarError(f"Error al guardar archivo: {type(e).__name__} - {e}")

    @staticmethod
    def cargarInventario(rutaArchivo: str) -> list:
        """Carga y reconstruye los objetos desde el archivo de texto plano."""
        listaProductos = []
        if not os.path.exists(rutaArchivo):
            raise FileNotFoundError(f"No se encontró el archivo: {rutaArchivo}")
            
        with open(rutaArchivo, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                partes = linea.strip().split(",")
                if len(partes) < 6:
                    continue
                tipo, codigo, nombre, stock, valorPrecio, nombreCat, extra, temp = partes
                
                cat = Categoria(1, nombreCat)
                precioObj = Precio(float(valorPrecio))
                
                if tipo == "Perecedero":
                    prod = Perecedero(codigo, nombre, int(stock), precioObj, cat, extra, float(temp))
                else:
                    prod = NoPerecedero(codigo, nombre, int(stock), precioObj, cat, extra)
                
                listaProductos.append(prod)
        return listaProductos
