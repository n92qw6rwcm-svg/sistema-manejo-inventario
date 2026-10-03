import validaciones
import persistencia
from datetime import datetime


def _generar_id(datos: dict, entidad: str) -> int:
    ids_creacion = [
        evento["entidad_id"]
        for evento in datos["auditoria"]
        if evento["entidad"] == entidad and evento["operacion"] == "Creación"
    ]
    return max(ids_creacion, default=0) + 1


def _registrar_evento(
    datos: dict, entidad: str, entidad_id: int, operacion: str, descripcion: str
) -> None:
    datos["auditoria"].append({
        "fecha_hora": datetime.now().isoformat(),
        "entidad": entidad,
        "entidad_id": entidad_id,
        "operacion": operacion,
        "descripcion": descripcion,
    })


def registrar_producto(
    datos: dict, nombre: str, cantidad: str, proveedor_id: str, marca: str = None
) -> tuple[bool, str, dict | None]:
    """Registra un nuevo producto tras validar RN-02 y los campos del Anexo A.

    Returns:
        (éxito, mensaje, producto creado o None si falló)
    """
    try:
        proveedor_id = int(proveedor_id)
    except (ValueError, TypeError):
        return False, "El id del proveedor debe ser un número entero.", None

    if not any(p["id"] == proveedor_id for p in datos["proveedores"]):
        return False, "El proveedor indicado no existe.", None

    nombre = validaciones.normalizar_texto(nombre)
    if marca:
        marca = validaciones.normalizar_texto(marca)

    valido, mensaje = validaciones.validar_texto(
        nombre, 20, obligatorio=True, nombre_campo="nombre")
    if not valido:
        return False, mensaje, None

    if marca:
        valido, mensaje = validaciones.validar_texto(
            marca, 50, obligatorio=False, nombre_campo="marca")
        if not valido:
            return False, mensaje, None

    valido, mensaje = validaciones.validar_cantidad(cantidad)
    if not valido:
        return False, mensaje, None
    cantidad = int(cantidad)

    nuevo_id = _generar_id(datos, "Producto")
    producto = {
        "id": nuevo_id,
        "nombre": nombre,
        "cantidad": cantidad,
        "marca": marca if marca else None,
        "proveedor_id": proveedor_id,
    }
    datos["productos"].append(producto)
    _registrar_evento(
        datos, "Producto", nuevo_id, "Creación",
        f"Producto '{nombre}' creado con cantidad {cantidad}."
    )
    return True, f"Producto registrado con id {nuevo_id}.", producto


def listar_productos(datos: dict) -> tuple[bool, str, list]:
    """Devuelve todos los productos registrados."""
    return True, "", datos["productos"]


def actualizar_producto(datos: dict, id: int, cambios: dict) -> tuple[bool, str, dict | None]:
    """Actualiza los campos indicados en `cambios` de un producto existente."""
    producto = next((p for p in datos["productos"] if p["id"] == id), None)
    if producto is None:
        return False, "El producto indicado no existe.", None

    if "proveedor_id" in cambios:
        try:
            cambios["proveedor_id"] = int(cambios["proveedor_id"])
        except (ValueError, TypeError):
            return False, "El id del proveedor debe ser un número entero.", None
        if not any(p["id"] == cambios["proveedor_id"] for p in datos["proveedores"]):
            return False, "El proveedor indicado no existe.", None

    if "nombre" in cambios:
        cambios["nombre"] = validaciones.normalizar_texto(cambios["nombre"])
        valido, mensaje = validaciones.validar_texto(
            cambios["nombre"], 20, obligatorio=True, nombre_campo="nombre")
        if not valido:
            return False, mensaje, None

    if "marca" in cambios and cambios["marca"] != "":
        cambios["marca"] = validaciones.normalizar_texto(cambios["marca"])
        valido, mensaje = validaciones.validar_texto(
            cambios["marca"], 50, obligatorio=False, nombre_campo="marca")
        if not valido:
            return False, mensaje, None

    if "cantidad" in cambios:
        valido, mensaje = validaciones.validar_cantidad(cambios["cantidad"])
        if not valido:
            return False, mensaje, None
        cambios["cantidad"] = int(cambios["cantidad"])

    descripciones = []
    for campo, valor_nuevo in cambios.items():
        descripciones.append(f"{campo}: {producto[campo]} → {valor_nuevo}")
        producto[campo] = valor_nuevo

    _registrar_evento(datos, "Producto", id, "Actualización",
                      "; ".join(descripciones))
    return True, "Producto actualizado.", producto


def eliminar_producto(datos: dict, id: int) -> tuple[bool, str, dict | None]:
    """Elimina un producto existente, si su cantidad es 0 (RN-03)."""
    producto = next((p for p in datos["productos"] if p["id"] == id), None)
    if producto is None:
        return False, "El producto indicado no existe.", None

    if producto["cantidad"] > 0:
        return False, "No se puede eliminar un producto con cantidad mayor a 0.", None

    datos["productos"].remove(producto)
    _registrar_evento(
        datos, "Producto", id, "Eliminación",
        f"Producto '{producto['nombre']}' (id {id}) eliminado."
    )
    return True, "Producto eliminado.", producto


def registrar_proveedor(
    datos: dict, nombre: str, apellido: str, celular: str
) -> tuple[bool, str, dict | None]:
    """Registra un nuevo proveedor tras validar RN-04 y los campos del Anexo A."""
    valido, mensaje = validaciones.validar_celular(celular)
    if not valido:
        return False, mensaje, None

    if any(p["celular"] == celular for p in datos["proveedores"]):
        return False, "Ya existe un proveedor registrado con ese celular.", None

    nombre = validaciones.normalizar_texto(nombre)
    apellido = validaciones.normalizar_texto(apellido)

    valido, mensaje = validaciones.validar_texto(
        nombre, 20, obligatorio=True, nombre_campo="nombre")
    if not valido:
        return False, mensaje, None

    valido, mensaje = validaciones.validar_texto(
        apellido, 20, obligatorio=True, nombre_campo="apellido")
    if not valido:
        return False, mensaje, None

    nuevo_id = _generar_id(datos, "Proveedor")
    proveedor = {"id": nuevo_id, "nombre": nombre,
                 "apellido": apellido, "celular": celular}
    datos["proveedores"].append(proveedor)
    _registrar_evento(
        datos, "Proveedor", nuevo_id, "Creación",
        f"Proveedor '{nombre} {apellido}' creado."
    )
    return True, f"Proveedor registrado con id {nuevo_id}.", proveedor


def listar_proveedores(datos: dict) -> tuple[bool, str, list]:
    """Devuelve todos los proveedores registrados."""
    return True, "", datos["proveedores"]


def actualizar_proveedor(datos: dict, id: int, cambios: dict) -> tuple[bool, str, dict | None]:
    """Actualiza los campos indicados en `cambios` de un proveedor existente."""
    proveedor = next((p for p in datos["proveedores"] if p["id"] == id), None)
    if proveedor is None:
        return False, "El proveedor indicado no existe.", None

    if "celular" in cambios:
        valido, mensaje = validaciones.validar_celular(cambios["celular"])
        if not valido:
            return False, mensaje, None
        if any(p["celular"] == cambios["celular"] and p["id"] != id for p in datos["proveedores"]):
            return False, "Ya existe otro proveedor registrado con ese celular.", None

    if "nombre" in cambios:
        cambios["nombre"] = validaciones.normalizar_texto(cambios["nombre"])
        valido, mensaje = validaciones.validar_texto(
            cambios["nombre"], 20, obligatorio=True, nombre_campo="nombre")
        if not valido:
            return False, mensaje, None

    if "apellido" in cambios:
        cambios["apellido"] = validaciones.normalizar_texto(
            cambios["apellido"])
        valido, mensaje = validaciones.validar_texto(
            cambios["apellido"], 20, obligatorio=True, nombre_campo="apellido")
        if not valido:
            return False, mensaje, None

    descripciones = []
    for campo, valor_nuevo in cambios.items():
        descripciones.append(f"{campo}: {proveedor[campo]} → {valor_nuevo}")
        proveedor[campo] = valor_nuevo

    _registrar_evento(datos, "Proveedor", id,
                      "Actualización", "; ".join(descripciones))
    return True, "Proveedor actualizado.", proveedor


def eliminar_proveedor(datos: dict, id: int) -> tuple[bool, str, dict | None]:
    """Elimina un proveedor existente, si no tiene productos asociados (RN-01)."""
    proveedor = next((p for p in datos["proveedores"] if p["id"] == id), None)
    if proveedor is None:
        return False, "El proveedor indicado no existe.", None

    if any(p["proveedor_id"] == id for p in datos["productos"]):
        return False, "No se puede eliminar un proveedor con productos asociados.", None

    datos["proveedores"].remove(proveedor)
    _registrar_evento(
        datos, "Proveedor", id, "Eliminación",
        f"Proveedor '{proveedor['nombre']} {proveedor['apellido']}' (id {id}) eliminado."
    )
    return True, "Proveedor eliminado.", proveedor


def listar_auditoria(datos: dict) -> tuple[bool, str, list]:
    """Devuelve el historial de auditoría, del más reciente al más antiguo."""
    eventos_ordenados = sorted(
        datos["auditoria"], key=lambda e: e["fecha_hora"], reverse=True)
    return True, "", eventos_ordenados
