"""Pruebas de humo de la interfaz Streamlit con ``AppTest``.

Verifican el flujo completo sin navegador: cargar datos demo, guardar un
registro desde el formulario y navegar entre secciones.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from streamlit.testing.v1 import AppTest

from iper import storage

APP = str(Path(__file__).resolve().parent.parent / "app.py")

SECCIONES = (
    "📝 Registro",
    "📋 Vista previa",
    "📊 Resumen",
    "⬇️ Exportar",
    "📚 Criterios",
)


@pytest.fixture()
def app(tmp_path, monkeypatch) -> AppTest:
    """AppTest aislado del respaldo en disco (``data/sesion_iper.json``)."""
    monkeypatch.setattr(storage, "RUTA_DATOS", tmp_path / "sesion_iper.json")
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    return at


def _boton(at: AppTest, texto: str):
    for boton in at.button:
        if texto.lower() in (boton.label or "").lower():
            return boton
    raise AssertionError(f"No se encontró el botón: {texto}")


def test_arranca_sin_excepciones(app: AppTest) -> None:
    assert not app.exception
    assert app.session_state["iper_filas"] == []


def test_carga_datos_de_ejemplo(app: AppTest) -> None:
    _boton(app, "Cargar datos de ejemplo").click().run()
    assert not app.exception
    assert len(app.session_state["iper_filas"]) == 15

    metricas = {m.label: m.value for m in app.metric}
    assert metricas["Peligros en la matriz"] == "15"


def test_guardar_registro_desde_el_formulario(app: AppTest) -> None:
    # Orden de los selectbox del formulario:
    # 0 tarea · 1 peligro · 2 P · 3 C · 4 frecuencia · 5 responsable ·
    # 6 P' · 7 C'
    app.selectbox[0].set_value("Movimiento de tierras y excavaciones")
    app.selectbox[1].set_value("Ruido (exposición a niveles sobre 85 dB(A))")
    app.text_area[0].set_value("Exposición a ruido continuo de maquinaria")
    app.text_area[1].set_value("Hipoacusia neurosensorial")
    app.selectbox[2].set_value(4)          # probabilidad (P)
    app.selectbox[3].set_value(4)          # consecuencia (C)
    app.selectbox[4].set_value("Diario")   # frecuencia del control
    app.multiselect[0].set_value(["C", "G"])
    app.text_area[2].set_value("• C1: Encerramiento acústico.\n• G1: Protección auditiva.")
    _boton(app, "Guardar registro").click().run()

    assert not app.exception
    filas = app.session_state["iper_filas"]
    assert len(filas) == 1
    assert filas[0].mr == 16
    assert filas[0].nivel.clave == "moderado"
    assert filas[0].categorias == ["C", "G"]


def test_navegacion_entre_secciones(app: AppTest) -> None:
    _boton(app, "Cargar datos de ejemplo").click().run()

    for seccion in SECCIONES:
        app.radio[0].set_value(seccion).run()
        assert not app.exception, f"La sección {seccion} lanzó una excepción"
