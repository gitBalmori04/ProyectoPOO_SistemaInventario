import datetime
import os

class ErrorInventario(Exception):
    """Excepción base para errores propios del sistema de abarrotes."""
    pass

class ProductoNoEncontradoError(ErrorInventario):
    """Se lanza cuando se busca un producto que no existe en el inventario."""
    pass

class StockInsuficienteError(ErrorInventario):
    """Se lanza cuando se intenta vender más stock del disponible."""
    pass

def registrarError(mensajeError: str):
    """
    Método reutilizable para registrar errores en 'log_errores.txt' 
    en modo append ('a'), incluyendo fecha y hora actuales.
    """
    rutaLog = "log_errores.txt"
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lineaLog = f"{ahora} | ERROR | {mensajeError}\n"
    
    try:
        with open(rutaLog, "a", encoding="utf-8") as archivo:
            archivo.write(lineaLog)
    except Exception as e:
        print(f"Error crítico al escribir en el log: {e}")
