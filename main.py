# Módulo principal con menú interactivo para el Sistema de Control de Abarrotes.

from modelos.producto import (
    Precio,
    Categoria,
    Producto,
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


# Compara los objetos en memoria antes de guardar contra los reconstruidos desde archivo.
def compararGuardadoVsCargado(guardados: list, cargados: list) -> bool:
    print("\n--- Verificación de Integridad (Guardado vs. Cargado) ---")
    if len(guardados) != len(cargados):
        print(
            f"Diferencia en cantidad: guardados={len(guardados)}, cargados={len(cargados)}"
        )
        return False

    coincideTodo = True
    for orig, rec in zip(guardados, cargados):
        mismoCodigo = orig.codigo == rec.codigo
        mismoNombre = orig.nombre == rec.nombre
        mismoStock = orig.stock == rec.stock
        mismoPrecio = abs(orig.precio.valor - rec.precio.valor) < 1e-6
        mismaCat = (
            orig.categoria.idCategoria == rec.categoria.idCategoria
            and orig.categoria.nombre == rec.categoria.nombre
        )

        if not (mismoCodigo and mismoNombre and mismoStock and mismoPrecio and mismaCat):
            print(f"Discrepancia detectada en producto '{orig.codigo}'.")
            coincideTodo = False

    if coincideTodo:
        print(
            f"✔ Verificación exitosa: {len(cargados)} producto(s) cargados coinciden exactamente con los guardados."
        )
    return coincideTodo


if __name__ == "__main__":
    # Inicialización de la tienda y proveedor principal
    miTienda = Tienda("Abarrotes Don Beto", "Av. 5 de Febrero #76118, Querétaro")
    proveedorPrincipal = Proveedor(1, "Distribuidora Mayorista del Centro", "442-215-8890")
    archivoDatos = "inventario.txt"

    # Carga inicial (si inventario.txt no existe, GestorArchivos registra el evento y lo crea)
    try:
        productosCargados = GestorArchivos.cargarInventario(archivoDatos)
        miTienda.reemplazarInventario(productosCargados)
        if productosCargados:
            print(f"Se cargaron {len(productosCargados)} productos previos desde '{archivoDatos}'.")
    except (PermissionError, OSError, ValueError) as e:
        registrarError(f"Error al cargar archivo inicial: {type(e).__name__} - {e}")
        print(f"No se pudo cargar el inventario inicial: {e}")

    # ==================================================
    # MENÚ INTERACTIVO CON EL USUARIO
    # ==================================================
    while True:
        print("\n==========================================")
        print("   Sistema de control de abarrotes")
        print(f"   ({miTienda.nombre})")
        print(f"   {proveedorPrincipal}")
        print("==========================================")
        print("1. Consultar inventario completo")
        print("2. Registrar nuevo producto al catálogo")
        print("3. Reabastecer existencias con Proveedor")
        print("4. Registrar venta de productos")
        print("5. Guardar inventario y verificar contra archivo (.txt)")
        print("6. Cargar / Recargar inventario desde archivo (.txt)")
        print("7. Ejecutar pruebas de excepciones y bitácora (log_errores.txt)")
        print("8. Salir del programa")

        opcion = input("\nSeleccione una opción (1-8): ").strip()

        if opcion == "1":
            print("\n--- Consulta De Inventario ---")
            inventario = miTienda.consultarInventario()
            if not inventario:
                print("El inventario está vacío. Registre un producto en la opción 2.")
            else:
                for idx, prod in enumerate(inventario, 1):
                    print(f"{idx}. {prod}")

        elif opcion == "2":
            print("\n--- Registrar Nuevo Producto Al Catálogo ---")
            try:
                tipoProd = input("¿El producto es perecedero? (s/n): ").strip().lower()
                codigo = input("Código único del producto (ej. P001): ").strip()
                nombre = input("Nombre del producto (ej. Leche, entera): ").strip()
                stock = int(input("Stock inicial (cantidad en existencias): "))
                valorPrecio = float(input("Precio unitario ($): "))
                idCat = int(input("ID numérico de la categoría (ej. 1, 2, 3): "))
                nombreCat = input("Nombre de la categoría (ej. Lácteos, Abarrotes): ").strip()

                cat = Categoria(idCat, nombreCat)
                precio = Precio(valorPrecio)

                if tipoProd == "s":
                    caducidad = input("Fecha de caducidad (YYYY-MM-DD): ").strip()
                    temp = float(input("Temperatura de conservación (°C): "))
                    nuevoProd = Perecedero(codigo, nombre, stock, precio, cat, caducidad, temp)
                else:
                    empaque = input("Material de empaque (ej. Lata, Vidrio, Plástico): ").strip()
                    nuevoProd = NoPerecedero(codigo, nombre, stock, precio, cat, empaque)

                miTienda.agregarProducto(nuevoProd)
                print("✔ ¡Producto registrado exitosamente!")
            except (ValueError, TypeError) as e:
                errorMsg = f"{type(e).__name__} en registro interactivo de producto: {e}"
                print(f"Error de entrada: {e}")
                registrarError(errorMsg)

        elif opcion == "3":
            print("\n--- Reabastecer Existencias Con Proveedor ---")
            inventario = miTienda.consultarInventario()
            if not inventario:
                print("No hay productos registrados para reabastecer.")
                continue

            for idx, p in enumerate(inventario, 1):
                print(f"{idx}. {p}")

            try:
                codigoBuscar = input("\nIngrese el código del producto a suministrar: ").strip()
                prodObjetivo = miTienda.buscarProductoPorCodigo(codigoBuscar)
                cantidadSuministro = int(
                    input(f"Cantidad entregada por {proveedorPrincipal.nombre}: ")
                )
                proveedorPrincipal.suministrarProducto(prodObjetivo, cantidadSuministro)
                print(
                    f"✔ Abastecimiento completado. Nuevo stock de '{prodObjetivo.nombre}': {prodObjetivo.stock}"
                )
            except (ProductoNoEncontradoError, ValueError) as e:
                errorMsg = f"{type(e).__name__} en abastecimiento de proveedor: {e}"
                print(f"Error al abastecer: {e}")
                registrarError(errorMsg)

        elif opcion == "4":
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
                    codigoVenta = input(
                        "Código del producto a vender (0 para finalizar ticket): "
                    ).strip()
                    if codigoVenta == "0":
                        break

                    prodSeleccionado = miTienda.buscarProductoPorCodigo(codigoVenta)
                    cant = int(input(f"Cantidad a vender de '{prodSeleccionado.nombre}': "))

                    detalle = DetalleVenta(prodSeleccionado, cant)
                    venta.agregarDetalle(detalle)
                    print(f"Agregado: {detalle}")

                if len(venta.listaDetalles) > 0:
                    print(venta.generarTicket())
                else:
                    print("Venta cancelada (no se agregaron artículos).")

            except (ProductoNoEncontradoError, StockInsuficienteError, ValueError) as e:
                errorMsg = f"{type(e).__name__} en proceso interactivo de venta: {e}"
                print(f"Error durante la venta: {e}")
                registrarError(errorMsg)

        elif opcion == "5":
            print("\n--- Guardando Cambios Y Verificando Archivo ---")
            inventarioActual = miTienda.consultarInventario()
            if GestorArchivos.guardarInventario(archivoDatos, inventarioActual):
                try:
                    cargadosVerificacion = GestorArchivos.cargarInventario(archivoDatos)
                    compararGuardadoVsCargado(inventarioActual, cargadosVerificacion)
                except (PermissionError, OSError, ValueError) as e:
                    print(f"Error al verificar el archivo guardado: {e}")
                    registrarError(f"{type(e).__name__} al verificar guardado: {e}")

        elif opcion == "6":
            print("\n--- Recargando Datos Desde Archivo ---")
            try:
                previos = miTienda.consultarInventario()
                cargados = GestorArchivos.cargarInventario(archivoDatos)
                miTienda.reemplazarInventario(cargados)
                print(f"Se cargaron {len(cargados)} productos desde '{archivoDatos}'.")
                if previos:
                    compararGuardadoVsCargado(previos, cargados)
            except (FileNotFoundError, PermissionError, ValueError, OSError) as e:
                print(f"Error al recargar inventario: {e}")
                registrarError(f"{type(e).__name__} al recargar: {e}")

        elif opcion == "7":
            print("\n--- Ejecutando Pruebas De Excepciones Para La Bitácora ---")

            # 1. FileNotFoundError (crea archivo si no existe y registra en log)
            try:
                GestorArchivos.cargarInventario("archivo_prueba_inexistente.txt")
                print("   1. Capturado y registrado: FileNotFoundError (archivo creado automáticamente)")
            except OSError as e:
                registrarError(f"OSError en prueba 1: {e}")

            # 2. ValueError en constructor de Precio y Producto
            try:
                Precio(-25.0)
            except ValueError as e:
                registrarError(f"ValueError en constructor Precio(-25.0): {e}")
                print("   2. Capturado y registrado: ValueError (precio negativo en constructor)")

            # 3. StockInsuficienteError al vender más de lo disponible
            try:
                catPrueba = Categoria(99, "Pruebas")
                prodPrueba = Producto("TEST-01", "Producto Prueba", 2, Precio(15.0), catPrueba)
                DetalleVenta(prodPrueba, 10)
            except StockInsuficienteError as e:
                registrarError(f"StockInsuficienteError: {e}")
                print("   3. Capturado y registrado: StockInsuficienteError")

            # 4. ProductoNoEncontradoError y KeyError al buscar código inexistente
            try:
                miTienda.buscarProductoPorCodigo("CODIGO-NO-EXISTE")
            except ProductoNoEncontradoError as e:
                registrarError(f"ProductoNoEncontradoError (origen KeyError): {e}")
                print("   4. Capturado y registrado: ProductoNoEncontradoError / KeyError")

            # 5. PermissionError simulado al intentar abrir ruta protegida/inválida
            try:
                raise PermissionError("Acceso denegado simulado sobre archivo protegido.")
            except PermissionError as e:
                registrarError(f"PermissionError: {e}")
                print("   5. Capturado y registrado: PermissionError")

            print("✔ ¡Todas las excepciones fueron registradas en 'log_errores.txt'!")

        elif opcion == "8":
            print("\nCerrando el sistema de abarrotes. ¡Hasta luego!")
            break
        else:
            print("Opción inválida. Ingrese un número del 1 al 8.")
