"""
Módulo de validaciones
Contiene las funciones para validar:
normalizar_texto
validar_texto
validar_cantidad
validar_celular
"""


def normalizar_texto(valor: str) -> str:
    """Normaliza un texto: minúsculas, sin espacios extremos, un solo espacio intermedio."""
    return " ".join(valor.lower().split())


def validar_texto(valor: str, max_len: int, obligatorio: bool = True, nombre_campo: str = "El campo"
                  ) -> tuple[bool, str]:
    """Valida un texto según las reglas del Anexo A: solo letras y espacios, longitud máxima."""
    if obligatorio and valor == "":
        return False, f"{nombre_campo.capitalize()}: no puede estar vacío."

    if len(valor) > max_len:
        return False, f"{nombre_campo.capitalize()}: no puede tener más de {max_len} caracteres."

    if not all(c.isalpha() or c == " " for c in valor):
        return False, f"{nombre_campo.capitalize()}: solo puede contener letras."

    return True, ""


def validar_cantidad(valor: str) -> tuple[bool, str]:
    """Valida que la cantidad sea un entero mayor o igual a cero."""
    try:
        cantidad = int(valor)
    except (ValueError, TypeError):
        return False, "La cantidad debe ser un número entero."

    if cantidad < 0:
        return False, "La cantidad no puede ser negativa."

    return True, ""


def validar_celular(valor: str) -> tuple[bool, str]:
    """Valida que el celular tenga el formato E.164 Colombia (+57 + 10 dígitos)."""
    if valor == "":
        return False, "El celular no puede estar vacío."

    if not valor.startswith("+57"):
        return False, "El celular debe tener el formato +57 seguido de 10 dígitos."

    resto = valor[3:]
    if not resto.isdigit() or len(resto) != 10:
        return False, "El celular debe tener el formato +57 seguido de 10 dígitos."

    return True, ""


if __name__ == '__main__':
    print('hola mundo')
