import os
from modelos.producto import Precio, Categoria, Perecedero, NoPerecedero, Proveedor, Venta, DetalleVenta, Tienda
from modelos.persistencia import GestorArchivos
from utils.excepciones import registrarError

if __name__ == "__main__":
    # Inicialización de la tienda principal del sistema
    miTienda = Tienda("Abarrotes Don Beto", "Av. 5 de Febrero #76118, Querétaro")
    archivoDatos = "inventario.txt"

    # Intentar cargar datos guardados de sesiones previas si el archivo existe
    if os.path.exists(archivoDatos):
        try:
            productosCargados = GestorArchivos.cargarInventario(archivoDatos)
            for p in productosCargados:
                miTienda.agregarProducto(p)
            print("Se cargó el inventario previo desde 'inventario.txt'.")
        except Exception as e:
            registrarError(f"Error al cargar archivo inicial: {e}")

    # ==================================================
    # MENÚ INTERACTIVO COMPLETO CON EL USUARIO
    # ==================================================
    while True:
        print("\n==========================================")
        print(f"   Sistema de control de abarrotes")
        print(f"   ({miTienda._nombre})")
        print("==========================================")
        print("1. Consultar inventario completo")
        print("2. Registrar nuevo producto al catálogo")
        print("3. Registrar venta de productos")
        print("4. Guardar inventario actual en archivo (.txt)")
        print("5. Cargar / Recargar inventario desde archivo (.txt)")
        print("6. Registrar errores en la bitácora (log_errores.txt)")
        print("7. Salir del programa")
        
        opcion = input("\nSeleccione una opción (1-7): ").strip()

        if opcion == "1":
            print("\n--- Consulta De Inventario ---")
            inventario = miTienda.consultarInventario()
            if not inventario:
                print("El inventario está vacío. Registre un nuevo producto en la opción 2.")
            else:
                for idx, prod in enumerate(inventario, 1):
                    print(f"{idx}. {prod}")

        elif opcion == "2":
            print("\n--- Registrar Nuevo Producto Al Catálogo ---")
            try:
                tipoProd = input("¿El producto es perecedero? (s/n): ").strip().lower()
                codigo = input("Código único del producto (ej. P001): ").strip()
                nombre = input("Nombre del producto (ej. Leche Entera): ").strip()
                stock = int(input("Stock inicial (cantidad en existencias): "))
                valorPrecio = float(input("Precio unitario ($): "))
                nombreCat = input("Categoría (ej. Lácteos, Abarrotes): ").strip()
                
                cat = Categoria(1, nombreCat)
                precio = Precio(valorPrecio)

                if tipoProd == 's':
                    caducidad = input("Fecha de caducidad (YYYY-MM-DD): ").strip()
                    temp = float(input("Temperatura de conservación (°C): "))
                    nuevoProd = Perecedero(codigo, nombre, stock, precio, cat, caducidad, temp)
                else:
                    empaque = input("Material de empaque (ej. Plástico, Lata): ").strip()
                    nuevoProd = NoPerecedero(codigo, nombre, stock, precio, cat, empaque)

                miTienda.agregarProducto(nuevoProd)
                print("¡Producto registrado exitosamente por el usuario!")
            except ValueError as e:
                errorMsg = f"ValueError en registro interactivo de producto: {e}"
                print(f"Error de entrada: {e}")
                registrarError(errorMsg)

        elif opcion == "3":
            print("\n--- Registrar Venta De Productos ---")
            inventario = miTienda.consultarInventario()
            if not inventario:
                print("No hay productos disponibles en el inventario para vender.")
                continue
            
            print("\nProductos disponibles:")
            for idx, p in enumerate(inventario, 1):
                print(f"{idx}. {p}")
            
            try:
                numVenta = int(input("\nNúmero de ticket/venta: "))
                fechaVenta = input("Fecha de venta (YYYY-MM-DD): ").strip()
                venta = Venta(numVenta, fechaVenta)

                while True:
                    sel = int(input("Número del producto a vender (0 para finalizar ticket): "))
                    if sel == 0:
                        break
                    if sel < 1 or sel > len(inventario):
                        raise IndexError("El número de producto seleccionado no existe en la lista.")
                    
                    prodSeleccionado = inventario[sel - 1]
                    cant = int(input(f"Cantidad a vender de '{prodSeleccionado.nombre}': "))
                    
                    if cant > prodSeleccionado.stock:
                        raise ValueError(f"Stock insuficiente. Disponible: {prodSeleccionado.stock}")

                    prodSeleccionado.stock -= cant
                    detalle = DetalleVenta(prodSeleccionado, cant)
                    venta.agregarDetalle(detalle)

                if len(venta._listaDetalles) > 0:
                    print(venta.generarTicket())
                else:
                    print("Venta cancelada (no se agregaron artículos).")

            except (ValueError, IndexError) as e:
                errorMsg = f"{type(e).__name__} en proceso interactivo de venta: {e}"
                print(f"Error durante la venta: {e}")
                registrarError(errorMsg)

        elif opcion == "4":
            print("\n--- Guardando Cambios En Archivo ---")
            GestorArchivos.guardarInventario(archivoDatos, miTienda.consultarInventario())

        elif opcion == "5":
            print("\n--- Recargando Datos Desde Archivo ---")
            try:
                cargados = GestorArchivos.cargarInventario(archivoDatos)
                miTienda._inventario = cargados
                print(f"Se cargaron {len(cargados)} productos desde 'inventario.txt'.")
            except FileNotFoundError as e:
                print(f"❌ {e}")
                registrarError(f"FileNotFoundError al recargar: {e}")

        elif opcion == "6":
            print("\n---Registrando Errores Para La Bitácora ---")
            # Error 1: FileNotFoundError
            try:
                GestorArchivos.cargarInventario("archivo_inexistente.txt")
            except FileNotFoundError as e:
                err = f"FileNotFoundError: No se encontró el archivo 'archivo_inexistente.txt' -> {e}"
                registrarError(err)
                print(f"   1. Capturado y registrado: FileNotFoundError")

            # Error 2: ValueError (precio negativo)
            try:
                precioPrueba = Precio(10.0)
                precioPrueba.valor = -25.0
            except ValueError as e:
                err = f"ValueError: El precio ingresado no puede ser negativo -> {e}"
                registrarError(err)
                print(f"   2. Capturado y registrado: ValueError (precio negativo)")

            # Error 3: TypeError / ValueError en tipo de dato
            try:
                if miTienda.consultarInventario():
                    miTienda.consultarInventario()[0].stock = "texto_invalido"
                else:
                    raise TypeError("Se asignó una cadena de texto en lugar de un entero al stock.")
            except (ValueError, TypeError) as e:
                err = f"TypeError/ValueError: Asignación de tipo de dato inválido al stock -> {e}"
                registrarError(err)
                print(f"   3. Capturado y registrado: TypeError/ValueError (tipo de dato en stock)")

            print("¡Los errores han sido guardados en 'log_errores.txt'!")

        elif opcion == "7":
            print("\nCerrando el sistema de abarrotes. ¡Hasta luego!")
            break
        else:
            print("Opción inválida. Ingrese un número del 1 al 7.")
