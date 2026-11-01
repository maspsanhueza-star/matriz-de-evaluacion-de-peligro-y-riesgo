"""Pruebas de la exportación a Excel (openpyxl, sin Streamlit)."""

from __future__ import annotations

from io import BytesIO

from openpyxl import load_workbook

from iper.demo_data import filas_demo
from iper.excel_export import construir_libro, construir_plantilla_vacia, nombre_archivo


def _cargar(datos: bytes):
    return load_workbook(BytesIO(datos))


def test_genera_libro_con_tres_hojas() -> None:
    libro = _cargar(construir_libro(filas_demo(), {"codigo": "SSO-001"}))
    assert libro.sheetnames == ["Matriz IPER", "Criterios", "Resumen"]


def test_escribe_todas_las_filas() -> None:
    libro = _cargar(construir_libro(filas_demo()))
    hoja = libro["Matriz IPER"]
    # La primera fila de datos parte en la fila 9
    primera = hoja.cell(row=9, column=4).value
    assert primera == "Estructuras o planchas deterioradas, traslúcidas o frágiles"
    # 15 filas de datos → última fila de datos = 23
    assert hoja.cell(row=23, column=1).value == 8


def test_aplica_color_de_criticidad() -> None:
    libro = _cargar(construir_libro(filas_demo()))
    hoja = libro["Matriz IPER"]
    celda_mr = hoja.cell(row=9, column=9)
    assert celda_mr.value == 32
    assert celda_mr.fill.start_color.rgb.endswith("C00000")


def test_plantilla_vacia_no_tiene_datos() -> None:
    libro = _cargar(construir_plantilla_vacia())
    hoja = libro["Matriz IPER"]
    assert hoja.cell(row=9, column=2).value is None
    assert hoja.max_row >= 9


def test_nombre_archivo_incluye_codigo_y_fecha() -> None:
    nombre = nombre_archivo({"codigo": "SSO-P01/01-MTZ-0002"})
    assert nombre.startswith("SSO-P01-01-MTZ-0002_")
    assert nombre.endswith(".xlsx")
