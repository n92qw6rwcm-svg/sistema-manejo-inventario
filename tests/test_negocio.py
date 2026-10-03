import pytest
import validaciones
import negocio


def _datos_base():
    return {
        "productos": [],
        "proveedores": [{"id": 1, "nombre": "diana", "apellido": "gomez", "celular": "+573001234567"}],
        "auditoria": [],
    }


def test_rf01_nombre_vacio_rechazado(monkeypatch):
    datos = _datos_base()
    monkeypatch.setattr(validaciones, "validar_texto", lambda *a,
                        **k: (False, "Nombre: no puede estar vacío."))

    exito, mensaje, producto = negocio.registrar_producto(datos, "", 50, 1)

    assert exito is False
    assert mensaje == "Nombre: no puede estar vacío."
    assert producto is None
    assert datos["productos"] == []


def test_rf01_marca_invalida_rechazada(monkeypatch):
    datos = _datos_base()

    def validar_texto_falso(valor, max_len, obligatorio=True, nombre_campo="El campo"):
        if nombre_campo == "marca":
            return False, "Marca: no puede tener más de 50 caracteres."
        return True, ""

    monkeypatch.setattr(validaciones, "validar_texto", validar_texto_falso)

    exito, mensaje, producto = negocio.registrar_producto(
        datos, "arroz", 50, 1, marca="a" * 51)

    assert exito is False
    assert mensaje == "Marca: no puede tener más de 50 caracteres."


def test_rf01_cantidad_invalida_rechazada(monkeypatch):
    datos = _datos_base()
    monkeypatch.setattr(validaciones, "validar_texto",
                        lambda *a, **k: (True, ""))
    monkeypatch.setattr(validaciones, "validar_cantidad", lambda *a,
                        **k: (False, "La cantidad no puede ser negativa."))

    exito, mensaje, producto = negocio.registrar_producto(
        datos, "arroz", -1, 1)

    assert exito is False
    assert mensaje == "La cantidad no puede ser negativa."


def test_rf01_proveedor_id_no_entero_rechazado():
    datos = _datos_base()

    exito, mensaje, producto = negocio.registrar_producto(
        datos, "arroz", 50, "abc")

    assert exito is False
    assert mensaje == "El id del proveedor debe ser un número entero."


def test_rf01_proveedor_inexistente_rechazado():
    datos = _datos_base()

    exito, mensaje, producto = negocio.registrar_producto(
        datos, "arroz", 50, 99)

    assert exito is False
    assert mensaje == "El proveedor indicado no existe."


def test_rf01_orden_proveedor_antes_que_nombre():
    datos = _datos_base()

    exito, mensaje, producto = negocio.registrar_producto(datos, "", 50, "abc")

    assert mensaje == "El id del proveedor debe ser un número entero."


def test_rf01_registro_exitoso_genera_auditoria(monkeypatch):
    datos = _datos_base()
    monkeypatch.setattr(validaciones, "validar_texto",
                        lambda *a, **k: (True, ""))
    monkeypatch.setattr(validaciones, "validar_cantidad",
                        lambda *a, **k: (True, ""))

    exito, mensaje, producto = negocio.registrar_producto(
        datos, "arroz", 50, 1)

    assert exito is True
    assert mensaje == "Producto registrado con id 1."
    assert len(datos["auditoria"]) == 1
    assert datos["auditoria"][0]["operacion"] == "Creación"


# --- RF-02: listar_productos ---

def test_rf02_listar_productos_vacio():
    datos = _datos_base()
    exito, mensaje, productos = negocio.listar_productos(datos)
    assert exito is True
    assert productos == []


def test_rf02_listar_productos_con_datos():
    datos = _datos_base()
    datos["productos"] = [{"id": 1, "nombre": "arroz"},
                          {"id": 2, "nombre": "frijol"}]
    exito, mensaje, productos = negocio.listar_productos(datos)
    assert len(productos) == 2


# --- RF-03: actualizar_producto ---

def test_rf03_id_inexistente_rechazado():
    datos = _datos_base()
    exito, mensaje, producto = negocio.actualizar_producto(
        datos, 99, {"cantidad": 10})
    assert exito is False
    assert mensaje == "El producto indicado no existe."


def test_rf03_nombre_invalido_en_cambios_rechazado(monkeypatch):
    datos = _datos_base()
    datos["productos"] = [{"id": 1, "nombre": "arroz",
                           "cantidad": 50, "marca": None, "proveedor_id": 1}]
    monkeypatch.setattr(validaciones, "validar_texto", lambda *a,
                        **k: (False, "Nombre: no puede estar vacío."))

    exito, mensaje, producto = negocio.actualizar_producto(datos, 1, {
                                                           "nombre": ""})

    assert exito is False
    assert mensaje == "Nombre: no puede estar vacío."


def test_rf03_marca_vaciada_aceptada(monkeypatch):
    datos = _datos_base()
    datos["productos"] = [{"id": 1, "nombre": "arroz",
                           "cantidad": 50, "marca": "diana", "proveedor_id": 1}]

    exito, mensaje, producto = negocio.actualizar_producto(datos, 1, {
                                                           "marca": ""})

    assert exito is True
    assert producto["marca"] == ""


def test_rf03_cantidad_negativa_en_cambios_rechazada(monkeypatch):
    datos = _datos_base()
    datos["productos"] = [{"id": 1, "nombre": "arroz",
                           "cantidad": 50, "marca": None, "proveedor_id": 1}]
    monkeypatch.setattr(validaciones, "validar_cantidad", lambda *a,
                        **k: (False, "La cantidad no puede ser negativa."))

    exito, mensaje, producto = negocio.actualizar_producto(
        datos, 1, {"cantidad": -1})

    assert exito is False
    assert mensaje == "La cantidad no puede ser negativa."


def test_rf03_proveedor_id_inexistente_en_cambios_rechazado():
    datos = _datos_base()
    datos["productos"] = [{"id": 1, "nombre": "arroz",
                           "cantidad": 50, "marca": None, "proveedor_id": 1}]

    exito, mensaje, producto = negocio.actualizar_producto(
        datos, 1, {"proveedor_id": 99})

    assert exito is False
    assert mensaje == "El proveedor indicado no existe."


def test_rf03_actualizacion_exitosa_registra_auditoria():
    datos = _datos_base()
    datos["productos"] = [{"id": 1, "nombre": "arroz",
                           "cantidad": 50, "marca": None, "proveedor_id": 1}]

    exito, mensaje, producto = negocio.actualizar_producto(
        datos, 1, {"cantidad": 30})

    assert exito is True
    assert producto["cantidad"] == 30
    assert len(datos["auditoria"]) == 1
    assert "cantidad: 50 → 30" in datos["auditoria"][0]["descripcion"]


# --- RF-04: eliminar_producto ---

def test_rf04_id_inexistente_rechazado():
    datos = _datos_base()
    exito, mensaje, producto = negocio.eliminar_producto(datos, 99)
    assert exito is False
    assert mensaje == "El producto indicado no existe."


def test_rf04_cantidad_mayor_a_cero_rechazado():
    datos = _datos_base()
    datos["productos"] = [{"id": 1, "nombre": "arroz",
                           "cantidad": 5, "marca": None, "proveedor_id": 1}]

    exito, mensaje, producto = negocio.eliminar_producto(datos, 1)

    assert exito is False
    assert mensaje == "No se puede eliminar un producto con cantidad mayor a 0."


def test_rf04_cantidad_cero_eliminado():
    datos = _datos_base()
    datos["productos"] = [{"id": 1, "nombre": "arroz",
                           "cantidad": 0, "marca": None, "proveedor_id": 1}]

    exito, mensaje, producto = negocio.eliminar_producto(datos, 1)

    assert exito is True
    assert datos["productos"] == []


# --- RF-05: registrar_proveedor ---

def test_rf05_nombre_vacio_rechazado(monkeypatch):
    datos = _datos_base()
    datos["proveedores"] = []
    monkeypatch.setattr(validaciones, "validar_texto", lambda *a,
                        **k: (False, "Nombre: no puede estar vacío."))

    exito, mensaje, proveedor = negocio.registrar_proveedor(
        datos, "", "gomez", "+573009999999")

    assert exito is False
    assert mensaje == "Nombre: no puede estar vacío."


def test_rf05_celular_vacio_rechazado():
    datos = _datos_base()
    datos["proveedores"] = []

    exito, mensaje, proveedor = negocio.registrar_proveedor(
        datos, "carlos", "perez", "")

    assert exito is False
    assert mensaje == "El celular no puede estar vacío."


def test_rf05_celular_formato_invalido_rechazado():
    datos = _datos_base()
    datos["proveedores"] = []

    exito, mensaje, proveedor = negocio.registrar_proveedor(
        datos, "carlos", "perez", "3001234567")

    assert exito is False
    assert mensaje == "El celular debe tener el formato +57 seguido de 10 dígitos."


def test_rf05_celular_duplicado_rechazado():
    datos = _datos_base()  # ya tiene un proveedor con +573001234567

    exito, mensaje, proveedor = negocio.registrar_proveedor(
        datos, "carlos", "perez", "+573001234567")

    assert exito is False
    assert mensaje == "Ya existe un proveedor registrado con ese celular."


def test_rf05_registro_exitoso_normaliza_y_registra():
    datos = _datos_base()

    exito, mensaje, proveedor = negocio.registrar_proveedor(
        datos, "  Carlos  Andres ", "Pérez", "+573009999999"
    )

    assert exito is True
    assert proveedor["nombre"] == "carlos andres"
    assert len(datos["auditoria"]) == 1


# --- RF-06: listar_proveedores ---

def test_rf06_listar_proveedores_vacio():
    datos = _datos_base()
    datos["proveedores"] = []
    exito, mensaje, proveedores = negocio.listar_proveedores(datos)
    assert proveedores == []


def test_rf06_listar_proveedores_con_datos():
    datos = _datos_base()
    exito, mensaje, proveedores = negocio.listar_proveedores(datos)
    assert len(proveedores) == 1


# --- RF-07: actualizar_proveedor ---

def test_rf07_id_inexistente_rechazado():
    datos = _datos_base()
    exito, mensaje, proveedor = negocio.actualizar_proveedor(
        datos, 99, {"celular": "+573009999999"})
    assert exito is False
    assert mensaje == "El proveedor indicado no existe."


def test_rf07_celular_duplicado_con_otro_rechazado():
    datos = _datos_base()
    datos["proveedores"].append(
        {"id": 2, "nombre": "ana", "apellido": "lopez", "celular": "+573009876543"}
    )

    exito, mensaje, proveedor = negocio.actualizar_proveedor(
        datos, 1, {"celular": "+573009876543"})

    assert exito is False
    assert mensaje == "Ya existe otro proveedor registrado con ese celular."


def test_rf07_celular_propio_reenviado_aceptado():
    datos = _datos_base()  # proveedor id=1 ya tiene +573001234567

    exito, mensaje, proveedor = negocio.actualizar_proveedor(
        datos, 1, {"celular": "+573001234567"})

    assert exito is True


def test_rf07_nombre_vacio_en_cambios_rechazado(monkeypatch):
    datos = _datos_base()
    monkeypatch.setattr(validaciones, "validar_texto", lambda *a,
                        **k: (False, "Nombre: no puede estar vacío."))

    exito, mensaje, proveedor = negocio.actualizar_proveedor(datos, 1, {
                                                             "nombre": ""})

    assert exito is False
    assert mensaje == "Nombre: no puede estar vacío."


def test_rf07_actualizacion_exitosa_registra_auditoria():
    datos = _datos_base()

    exito, mensaje, proveedor = negocio.actualizar_proveedor(
        datos, 1, {"celular": "+573001112222"})
