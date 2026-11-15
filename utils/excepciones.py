# Módulo de excepciones personalizadas y bitácora de errores del sistema.

import datetime
import sys


# Excepción base para errores propios del sistema de abarrotes.
class ErrorInventario(Exception):
    pass


# Se lanza cuando se busca un producto que no existe en el inventario.
class ProductoNoEncontradoError(ErrorInventario):
    pass


# Se lanza cuando se intenta vender o descontar más stock del disponible.
class StockInsuficienteError(ErrorInventario):
    pass


# Registra errores en 'log_errores.txt' en modo append ('a') con fecha y hora.
def registrarError(mensajeError: str):
    rutaLog = "log_errores.txt"
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lineaLog = f"{ahora} | ERROR | {mensajeError}\n"

    try:
        with open(rutaLog, "a", encoding="utf-8") as archivo:
            archivo.write(lineaLog)
    except (PermissionError, OSError) as e:
        sys.stderr.write(f"Error crítico al escribir en el log: {e}\n")
