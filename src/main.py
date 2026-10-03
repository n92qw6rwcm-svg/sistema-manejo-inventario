import negocio
import persistencia


RUTA_ARCHIVO = "inventario.json"


def iniciar():
    try:
        datos = persistencia.cargar_datos(RUTA_ARCHIVO)
    except persistencia.ErrorArchivoCorrupto as e:
        print(f"[ERROR] {e}")
        return
    except persistencia.ErrorPermisos as e:
        print(f"[ERROR] {e}")
        return

    menu_principal(datos, RUTA_ARCHIVO)


def menu_principal(datos, ruta_archivo):
    while True:
        print("1. Gestionar productos")
        print("2. Gestionar proveedores")
        print("3. Ver historial de auditoría")
        print("0. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            menu_productos(datos, ruta_archivo)
        elif opcion == "2":
            menu_proveedores(datos, ruta_archivo)
        elif opcion == "3":
            mostrar_auditoria(datos)
        elif opcion == "0":
            break
        else:
            print("[ERROR] Opción no válida.")


def menu_productos(datos, ruta_archivo):
    while True:
        print("1. Registrar producto")
        print("2. Listar productos")
        print("3. Actualizar producto")
        print("4. Eliminar producto")
        print("0. Volver")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            _registrar_producto_cli(datos, ruta_archivo)
        elif opcion == "2":
            mostrar_productos(datos)
        elif opcion == "3":
            _actualizar_producto_cli(datos, ruta_archivo)
        elif opcion == "4":
            _eliminar_producto_cli(datos, ruta_archivo)
        elif opcion == "0":
            break
        else:
            print("[ERROR] Opción no válida.")


def menu_proveedores(datos, ruta_archivo):
    while True:
        print("1. Registrar proveedor")
        print("2. Listar proveedores")
        print("3. Actualizar proveedor")
        print("4. Eliminar proveedor")
        print("0. Volver")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            _registrar_proveedor_cli(datos, ruta_archivo)
        elif opcion == "2":
            mostrar_proveedores(datos)
        elif opcion == "3":
            _actualizar_proveedor_cli(datos, ruta_archivo)
        elif opcion == "4":
            _eliminar_proveedor_cli(datos, ruta_archivo)
        elif opcion == "0":
            break
        else:
            print("[ERROR] Opción no válida.")


def _respaldar(datos):
    return {
        "productos": [dict(p) for p in datos["productos"]],
        "proveedores": [dict(p) for p in datos["proveedores"]],
        "auditoria": [dict(a) for a in datos["auditoria"]],
    }


def mostrar_productos(datos):
    _, _, productos = negocio.listar_productos(datos)

    if not productos:
        print("El inventario no tiene productos registrados.")
        return

    for p in productos:
        marca = p["marca"] if p["marca"] else "—"
        print(f"[{p['id']}] {p['nombre']} | Cantidad: {p['cantidad']} | Marca: {marca} | Proveedor: {p['proveedor_id']}")


def mostrar_proveedores(datos):
    _, _, proveedores = negocio.listar_proveedores(datos)

    if not proveedores:
        print("No hay proveedores registrados.")
        return

    for p in proveedores:
        print(f"[{p['id']}] {p['nombre']} {p['apellido']} | Celular: {p['celular']}")


def mostrar_auditoria(datos):
    _, _, eventos = negocio.listar_auditoria(datos)

    if not eventos:
        print("El historial de auditoría está vacío.")
        return

    for e in eventos:
        print(
            f"[{e['fecha_hora']}] {e['entidad']} #{e['entidad_id']} — {e['operacion']}: {e['descripcion']}")


def _registrar_producto_cli(datos, ruta_archivo):
    nombre = input("Nombre: ")
    cantidad = input("Cantidad: ")
    proveedor_id = input("Id del proveedor: ")
    marca = input("Marca (opcional, Enter para omitir): ")

    respaldo = _respaldar(datos)
    exito, mensaje, producto = negocio.registrar_producto(
        datos, nombre, cantidad, proveedor_id, marca if marca != "" else None
    )

    if not exito:
        print(f"[ERROR] {mensaje}")
        return

    try:
        persistencia.guardar_datos(ruta_archivo, datos)
        print(f"[OK] {mensaje}")
    except persistencia.ErrorPermisos as e:
        datos.clear()
        datos.update(respaldo)
        print(f"[ERROR] {e}")


def _actualizar_producto_cli(datos, ruta_archivo):
    id_texto = input("Id del producto a actualizar: ")
    try:
        id_producto = int(id_texto)
    except ValueError:
        print("[ERROR] El id debe ser un número entero.")
        return

    cambios = {}

    nombre = input("Nuevo nombre (Enter para no modificar): ")
    if nombre != "":
        cambios["nombre"] = nombre

    cantidad = input("Nueva cantidad (Enter para no modificar): ")
    if cantidad != "":
        try:
            cambios["cantidad"] = int(cantidad)
        except ValueError:
            print("[ERROR] La cantidad debe ser un número entero.")
            return

    respuesta_marca = input("¿Modificar la marca? (s/n): ")
    if respuesta_marca.lower() == "s":
        cambios["marca"] = input("Nueva marca (Enter para dejarla vacía): ")

    proveedor_id = input("Nuevo id de proveedor (Enter para no modificar): ")
    if proveedor_id != "":
        cambios["proveedor_id"] = proveedor_id

    if not cambios:
        print("No se indicó ningún cambio.")
        return

    respaldo = _respaldar(datos)
    exito, mensaje, producto = negocio.actualizar_producto(
        datos, id_producto, cambios)

    if not exito:
        print(f"[ERROR] {mensaje}")
        return

    try:
        persistencia.guardar_datos(ruta_archivo, datos)
        print(f"[OK] {mensaje}")
    except persistencia.ErrorPermisos as e:
        datos.clear()
        datos.update(respaldo)
        print(f"[ERROR] {e}")


def _eliminar_producto_cli(datos, ruta_archivo):
    id_texto = input("Id del producto a eliminar: ")
    try:
        id_producto = int(id_texto)
    except ValueError:
        print("[ERROR] El id debe ser un número entero.")
        return

    respaldo = _respaldar(datos)
    exito, mensaje, producto = negocio.eliminar_producto(datos, id_producto)

    if not exito:
        print(f"[ERROR] {mensaje}")
        return

    try:
        persistencia.guardar_datos(ruta_archivo, datos)
        print(f"[OK] {mensaje}")
    except persistencia.ErrorPermisos as e:
        datos.clear()
        datos.update(respaldo)
        print(f"[ERROR] {e}")


def _registrar_proveedor_cli(datos, ruta_archivo):
    nombre = input("Nombre: ")
    apellido = input("Apellido: ")
    celular = input("Celular (+57 seguido de 10 dígitos): ")

    respaldo = _respaldar(datos)
    exito, mensaje, proveedor = negocio.registrar_proveedor(
        datos, nombre, apellido, celular)

    if not exito:
        print(f"[ERROR] {mensaje}")
        return

    try:
        persistencia.guardar_datos(ruta_archivo, datos)
        print(f"[OK] {mensaje}")
    except persistencia.ErrorPermisos as e:
        datos.clear()
        datos.update(respaldo)
        print(f"[ERROR] {e}")


def _actualizar_proveedor_cli(datos, ruta_archivo):
    id_texto = input("Id del proveedor a actualizar: ")
    try:
        id_proveedor = int(id_texto)
    except ValueError:
        print("[ERROR] El id debe ser un número entero.")
        return

    cambios = {}

    nombre = input("Nuevo nombre (Enter para no modificar): ")
    if nombre != "":
        cambios["nombre"] = nombre

    apellido = input("Nuevo apellido (Enter para no modificar): ")
    if apellido != "":
        cambios["apellido"] = apellido

    celular = input("Nuevo celular (Enter para no modificar): ")
    if celular != "":
        cambios["celular"] = celular

    if not cambios:
        print("No se indicó ningún cambio.")
        return

    respaldo = _respaldar(datos)
    exito, mensaje, proveedor = negocio.actualizar_proveedor(
        datos, id_proveedor, cambios)

    if not exito:
        print(f"[ERROR] {mensaje}")
        return

    try:
        persistencia.guardar_datos(ruta_archivo, datos)
        print(f"[OK] {mensaje}")
    except persistencia.ErrorPermisos as e:
        datos.clear()
        datos.update(respaldo)
        print(f"[ERROR] {e}")


def _eliminar_proveedor_cli(datos, ruta_archivo):
    id_texto = input("Id del proveedor a eliminar: ")
    try:
        id_proveedor = int(id_texto)
    except ValueError:
        print("[ERROR] El id debe ser un número entero.")
        return

    respaldo = _respaldar(datos)
    exito, mensaje, proveedor = negocio.eliminar_proveedor(datos, id_proveedor)

    if not exito:
        print(f"[ERROR] {mensaje}")
        return

    try:
        persistencia.guardar_datos(ruta_archivo, datos)
        print(f"[OK] {mensaje}")
    except persistencia.ErrorPermisos as e:
        datos.clear()
        datos.update(respaldo)
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    iniciar()
