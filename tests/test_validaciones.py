import validaciones


# --- normalizar_texto ---

def test_normalizar_texto_minusculas_sin_espacios():
    resultado = validaciones.normalizar_texto("  ÑANDÚ   Premium ")
    assert resultado == "ñandú premium"


def test_normalizar_texto_ya_normalizado_no_cambia():
    resultado = validaciones.normalizar_texto("arroz premium")
    assert resultado == "arroz premium"


# --- validar_texto ---

def test_validar_texto_vacio_obligatorio_rechazado():
    valido, mensaje = validaciones.validar_texto(
        "", 20, obligatorio=True, nombre_campo="nombre")
    assert valido is False
    assert mensaje == "Nombre: no puede estar vacío."


def test_validar_texto_vacio_no_obligatorio_aceptado():
    valido, mensaje = validaciones.validar_texto(
        "", 50, obligatorio=False, nombre_campo="marca")
    assert valido is True


def test_validar_texto_limite_caracteres_aceptado():
    valido, mensaje = validaciones.validar_texto(
        "a" * 20, 20, nombre_campo="nombre")
    assert valido is True


def test_validar_texto_excede_caracteres_rechazado():
    valido, mensaje = validaciones.validar_texto(
        "a" * 21, 20, nombre_campo="nombre")
    assert valido is False
    assert mensaje == "Nombre: no puede tener más de 20 caracteres."


def test_validar_texto_caracter_invalido_rechazado():
    valido, mensaje = validaciones.validar_texto(
        "arroz1", 20, nombre_campo="nombre")
    assert valido is False
    assert mensaje == "Nombre: solo puede contener letras."


def test_validar_texto_con_enie_tilde_aceptado():
    valido, mensaje = validaciones.validar_texto(
        "ñandú", 20, nombre_campo="nombre")
    assert valido is True


# --- validar_cantidad ---

def test_validar_cantidad_negativa_rechazada():
    valido, mensaje = validaciones.validar_cantidad("-1")
    assert valido is False
    assert mensaje == "La cantidad no puede ser negativa."


def test_validar_cantidad_cero_aceptada():
    valido, mensaje = validaciones.validar_cantidad("0")
    assert valido is True


def test_validar_cantidad_positiva_aceptada():
    valido, mensaje = validaciones.validar_cantidad("50")
    assert valido is True


def test_validar_cantidad_no_entera_rechazada():
    valido, mensaje = validaciones.validar_cantidad("abc")
    assert valido is False
    assert mensaje == "La cantidad debe ser un número entero."


def test_validar_cantidad_vacia_rechazada():
    valido, mensaje = validaciones.validar_cantidad("")
    assert valido is False
    assert mensaje == "La cantidad debe ser un número entero."


# --- validar_celular ---

def test_validar_celular_vacio_rechazado():
    valido, mensaje = validaciones.validar_celular("")
    assert valido is False
    assert mensaje == "El celular no puede estar vacío."


def test_validar_celular_sin_prefijo_rechazado():
    valido, mensaje = validaciones.validar_celular("3001234567")
    assert valido is False
    assert mensaje == "El celular debe tener el formato +57 seguido de 10 dígitos."


def test_validar_celular_con_letras_rechazado():
    valido, mensaje = validaciones.validar_celular("+573001abcd67")
    assert valido is False
    assert mensaje == "El celular debe tener el formato +57 seguido de 10 dígitos."


def test_validar_celular_longitud_incorrecta_rechazado():
    valido, mensaje = validaciones.validar_celular(
        "+57300123456")  # 11 dígitos
    assert valido is False
    assert mensaje == "El celular debe tener el formato +57 seguido de 10 dígitos."


def test_validar_celular_valido_aceptado():
    valido, mensaje = validaciones.validar_celular("+573001234567")
    assert valido is True
