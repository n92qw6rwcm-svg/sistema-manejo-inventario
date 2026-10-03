import pytest
import main
import persistencia


# --- RF-01: registrar producto ---

def test_rf01_registro_exitoso(tmp_path, monkeypatch, capsys):
    ruta = str(tmp_path / "inventario.json")
    datos = {
        "productos": [],
        "proveedores": [{"id": 1, "nombre": "diana", "apellido": "gomez", "celular": "+573001234567"}],
        "auditoria": [],
    }
    respuestas = iter(["arroz", "50", "1", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(respuestas))

    main._registrar_producto_cli(datos, ruta)

    salida = capsys.readouterr().out
    assert "[OK]" in salida
    assert len(datos["productos"]) == 1


def test_rf01_guardado_fallido_revierte_datos(tmp_path, monkeypatch, capsys):
    ruta = str(tmp_path / "inventario.json")
    datos = {
        "productos": [],
        "proveedores": [{"id": 1, "nombre": "diana", "apellido": "gomez", "celular": "+573001234567"}],
        "auditoria": [],
    }
    respuestas = iter(["arroz", "50", "1", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(respuestas))

    def guardar_con_error(ruta_archivo, datos_a_guardar):
        raise persistencia.ErrorPermisos("sin permisos")

    monkeypatch.setattr(persistencia, "guardar_datos", guardar_con_error)

    main._registrar_producto_cli(datos, ruta)

    salida = capsys.readouterr().out
    assert "[ERROR]" in salida
    assert datos["productos"] == []
    assert datos["auditoria"] == []


# --- RF-02: listar productos ---

def test_rf02_mensaje_inventario_vacio(capsys):
    datos = {"productos": [], "proveedores": [], "auditoria": []}

    main.mostrar_productos(datos)

    salida = capsys.readouterr().out
    assert "El inventario no tiene productos registrados." in salida
    assert "[OK]" not in salida
    assert "[ERROR]" not in salida


# --- RF-03: actualizar producto ---

def test_rf03_sin_cambios_no_llama_a_negocio(monkeypatch, capsys):
    datos = {
        "productos": [{"id": 1, "nombre": "arroz", "cantidad": 50, "marca": None, "proveedor_id": 1}],
        "proveedores": [],
        "auditoria": [],
    }
    respuestas = iter(["1", "", "", "n", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(respuestas))

    main._actualizar_producto_cli(datos, "ruta_no_usada.json")

    salida = capsys.readouterr().out
    assert "No se indicó ningún cambio." in salida
    assert datos["productos"][0]["cantidad"] == 50


# --- RF-06: listar proveedores ---

def test_rf06_mensaje_sin_proveedores(capsys):
    datos = {"productos": [], "proveedores": [], "auditoria": []}

    main.mostrar_proveedores(datos)

    salida = capsys.readouterr().out
    assert "No hay proveedores registrados." in salida


# --- Menús ---

def test_opcion_invalida_en_menu_principal(monkeypatch, capsys):
    datos = {"productos": [], "proveedores": [], "auditoria": []}
    respuestas = iter(["9", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(respuestas))

    main.menu_principal(datos, "ruta_no_usada.json")

    salida = capsys.readouterr().out
    assert "[ERROR] Opción no válida." in salida


# --- Arranque con archivo corrupto ---

def test_iniciar_archivo_corrupto_no_muestra_menu(tmp_path, monkeypatch, capsys):
    ruta = tmp_path / "inventario.json"
    ruta.write_text("esto no es json válido", encoding="utf-8")
    monkeypatch.setattr(main, "RUTA_ARCHIVO", str(ruta))
    monkeypatch.setattr(main, "menu_principal", lambda *a,
                        **k: pytest.fail("no debería llamarse"))

    main.iniciar()

    salida = capsys.readouterr().out
    assert "[ERROR]" in salida
