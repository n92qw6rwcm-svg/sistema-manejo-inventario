"""
Responsabilidad:leer y escribir el archivo JSON único (RNF-01), 
y manejar los errores de archivo descritos en RNF-06.
"""
import json

ESTRUCTURA_VACIA = {
    "productos": [],
    "proveedores": [],
    "auditoria": []
}


class ErrorArchivoCorrupto(Exception):
    """El archivo existe pero no es JSON válido, o no tiene la estructura esperada."""


class ErrorPermisos(Exception):
    """No hay permisos de lectura o escritura sobre el archivo/carpeta de datos."""


def cargar_datos(ruta: str) -> dict:
    """Carga los datos del sistema desde el archivo JSON indicado.

    Si el archivo no existe, devuelve la estructura vacía sin tocar el disco.

    Raises:
        ErrorArchivoCorrupto: si el archivo existe pero no es JSON válido.
        ErrorPermisos: si no hay permisos de lectura sobre el archivo.
    """
    try:
        with open(ruta, 'r', encoding="utf-8") as f:

            try:
                return json.load(f)
            except json.JSONDecodeError:
                raise ErrorArchivoCorrupto(
                    "El archivo de datos no es un JSON válido."
                )

    except FileNotFoundError:
        return ESTRUCTURA_VACIA
    except PermissionError:
        raise ErrorPermisos(
            "No se pudo leer: sin permisos de lectura."
            "Verifique los permisos e intente nuevamente."
        )


# Se debe agregar el uso de la librería json para que el type hint de la firma no arroje error.
# Pues al utilizar contenido = f.read() y retornar contenido lo que devolvería sería un str
# no un dict.
# Mientras que con json se escribre json.load(f) y el retorno si es un dict.

def guardar_datos(ruta: str, datos: dict) -> None:
    """Guarda los datos del sistema en el archivo JSON indicado.

    Escribe en UTF-8, con indentado y sin escapar caracteres no-ASCII,
    para que ñ y tildes queden legibles en el archivo (RNF-01).

    Raises:
        ErrorPermisos: si no hay permisos de escritura sobre el archivo.
    """
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
    except PermissionError:
        raise ErrorPermisos(
            "No se pudo guardar: sin permisos de escritura. "
            "Verifique los permisos e intente nuevamente."
        )
