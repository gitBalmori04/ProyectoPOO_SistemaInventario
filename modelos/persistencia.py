# Módulo encargado de la persistencia del inventario en archivos de texto plano.

import csv
import os
from modelos.producto import Perecedero, NoPerecedero, Precio, Categoria
from utils.excepciones import registrarError


# Administra el guardado y la reconstrucción de productos en formato CSV/TXT.
class GestorArchivos:
    # Guarda la lista de productos en UTF-8 escapando comas mediante csv.writer.
    @staticmethod
    def guardarInventario(rutaArchivo: str, listaProductos: list) -> bool:
        try:
            with open(rutaArchivo, "w", encoding="utf-8", newline="") as archivo:
                escritor = csv.writer(archivo)
                for p in listaProductos:
                    esPerecedero = isinstance(p, Perecedero)
                    tipo = "Perecedero" if esPerecedero else "NoPerecedero"
                    extra = p.fechaCaducidad if esPerecedero else p.materialEmpaque
                    temp = p.temperaturaConservacion if esPerecedero else 0.0

                    escritor.writerow([
                        tipo,
                        p.codigo,
                        p.nombre,
                        p.stock,
                        p.precio.obtenerValor(),
                        p.categoria.idCategoria,
                        p.categoria.nombre,
                        extra,
                        temp,
                    ])
            print("Inventario guardado exitosamente en archivo.")
            return True
        except PermissionError as e:
            registrarError(f"PermissionError al guardar '{rutaArchivo}': {e}")
            print(f"Sin permisos para escribir en '{rutaArchivo}': {e}")
            return False
        except OSError as e:
            registrarError(f"OSError al guardar '{rutaArchivo}': {e}")
            print(f"Error de entrada/salida al guardar: {e}")
            return False

    # Carga productos desde el archivo; si no existe, registra el evento y lo crea vacío.
    @staticmethod
    def cargarInventario(rutaArchivo: str) -> list:
        listaProductos = []

        if not os.path.exists(rutaArchivo):
            try:
                raise FileNotFoundError(
                    f"No se encontró el archivo '{rutaArchivo}'. Se creará automáticamente."
                )
            except FileNotFoundError as e:
                registrarError(f"FileNotFoundError en GestorArchivos.cargarInventario: {e}")
                try:
                    with open(rutaArchivo, "w", encoding="utf-8", newline=""):
                        pass
                    print(f"ℹ Archivo '{rutaArchivo}' no existía y fue creado vacío.")
                except PermissionError as permErr:
                    registrarError(f"PermissionError al crear '{rutaArchivo}': {permErr}")
                    raise
                return listaProductos

        try:
            with open(rutaArchivo, "r", encoding="utf-8", newline="") as archivo:
                lector = csv.reader(archivo)
                for numLinea, partes in enumerate(lector, 1):
                    if not partes:
                        continue
                    try:
                        if len(partes) == 9:
                            (
                                tipo,
                                codigo,
                                nombre,
                                stock,
                                valorPrecio,
                                idCat,
                                nombreCat,
                                extra,
                                temp,
                            ) = partes
                            cat = Categoria(int(idCat), nombreCat)
                        elif len(partes) == 8:
                            (
                                tipo,
                                codigo,
                                nombre,
                                stock,
                                valorPrecio,
                                nombreCat,
                                extra,
                                temp,
                            ) = partes
                            cat = Categoria(1, nombreCat)
                        else:
                            raise ValueError(
                                f"Línea {numLinea} inválida: se esperaban 9 campos y se recibieron {len(partes)}."
                            )

                        precioObj = Precio(float(valorPrecio))

                        if tipo == "Perecedero":
                            prod = Perecedero(
                                codigo,
                                nombre,
                                int(stock),
                                precioObj,
                                cat,
                                extra,
                                float(temp),
                            )
                        else:
                            prod = NoPerecedero(
                                codigo,
                                nombre,
                                int(stock),
                                precioObj,
                                cat,
                                extra,
                            )

                        listaProductos.append(prod)
                    except (ValueError, TypeError) as e:
                        registrarError(
                            f"Error al reconstruir producto en línea {numLinea} de '{rutaArchivo}': {type(e).__name__} - {e}"
                        )
        except PermissionError as e:
            registrarError(f"PermissionError al leer '{rutaArchivo}': {e}")
            raise
        except OSError as e:
            registrarError(f"OSError al leer '{rutaArchivo}': {e}")
            raise

        return listaProductos
