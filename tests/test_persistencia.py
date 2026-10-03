"""
Tests del módulo persistencia
"""
import json
import pytest
import persistencia


def test_rnf06_cargar_datos_archivo_inexistente(tmp_path):
    '''test'''
    ruta = tmp_path / "inventario.json"
    resultado = persistencia.cargar_datos(str(ruta))
    assert resultado == persistencia.ESTRUCTURA_VACIA


def test_rnf06_cargar_datos_archivo_corrupto(tmp_path):
    '''test'''
    ruta = tmp_path / "inventario.json"
    ruta.write_text("esto no es json válido", encoding="utf-8")

    with pytest.raises(persistencia.ErrorArchivoCorrupto):
        persistencia.cargar_datos(str(ruta))


def test_rnf06_cargar_datos_archivo_valido(tmp_path):
    ruta = tmp_path / "inventario.json"
    contenido = {"productos": [], "proveedores": [], "auditoria": []}
    ruta.write_text(json.dumps(contenido), encoding="utf-8")

    resultado = persistencia.cargar_datos(str(ruta))

    assert resultado == contenido


def test_rnf06_guardar_datos_escribe_archivo(tmp_path):
    ruta = tmp_path / "inventario.json"
    datos = {"productos": [{"id": 1, "nombre": "arroz"}],
             "proveedores": [], "auditoria": []}

    persistencia.guardar_datos(str(ruta), datos)
    resultado = persistencia.cargar_datos(str(ruta))

    assert resultado == datos


def test_rnf06_guardar_datos_no_escapa_caracteres(tmp_path):
    ruta = tmp_path / "inventario.json"
    datos = {"productos": [{"id": 1, "nombre": "ñandú"}],
             "proveedores": [], "auditoria": []}

    persistencia.guardar_datos(str(ruta), datos)
    texto_crudo = ruta.read_text(encoding="utf-8")

    assert "ñandú" in texto_crudo
    assert "\\u00f1" not in texto_crudo


def test_rnf06_cargar_datos_sin_permisos_lectura(tmp_path, monkeypatch):
    ruta = tmp_path / "inventario.json"
    ruta.write_text("{}", encoding="utf-8")

    def open_con_error(*args, **kwargs):
        raise PermissionError

    monkeypatch.setattr("builtins.open", open_con_error)

    with pytest.raises(persistencia.ErrorPermisos):
        persistencia.cargar_datos(str(ruta))


def test_rnf06_guardar_datos_sin_permisos_escritura(tmp_path, monkeypatch):
    ruta = tmp_path / "inventario.json"

    def open_con_error(*args, **kwargs):
        raise PermissionError

    monkeypatch.setattr("builtins.open", open_con_error)

    with pytest.raises(persistencia.ErrorPermisos):
        persistencia.guardar_datos(
            str(ruta), {"productos": [], "proveedores": [], "auditoria": []})


if __name__ == "__main__":
    print('Hola mundo')
