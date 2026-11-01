"""Exportación a Excel (.xlsx) con formato profesional usando openpyxl.

El libro generado replica el diseño del Excel de referencia:

* Hoja **Matriz IPER**  → encabezado corporativo, cabecera agrupada de dos
  filas, colores por criticidad (inherente y residual), autofiltro y registro
  de difusión al pie.
* Hoja **Criterios**    → escalas de P y C, semáforo de la matriz y jerarquía
  de controles.
* Hoja **Resumen**      → indicadores y gráfico de torta/barras por criticidad.
"""

from __future__ import annotations

import math
from datetime import date
from io import BytesIO
from typing import Sequence

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from .config import (
    CATEGORIAS_CONTROL,
    COLOR_SUAVE,
    ESCALA_CONSECUENCIA,
    ESCALA_PROBABILIDAD,
    NIVELES_RIESGO,
    obtener_nivel,
)
from .models import FilaIPER, numerar

# ---------------------------------------------------------------------------
# Paleta y estilos base
# ---------------------------------------------------------------------------

AZUL = "1F3864"
AZUL_MEDIO = "2F5597"
AZUL_CLARO = "D9E2F3"
GRIS_CLARO = "F2F2F2"
GRIS_BORDE = "B4C6E7"
BLANCO = "FFFFFF"

FUENTE = "Calibri"
BORDE_FINO = Border(
    left=Side(style="thin", color=GRIS_BORDE),
    right=Side(style="thin", color=GRIS_BORDE),
    top=Side(style="thin", color=GRIS_BORDE),
    bottom=Side(style="thin", color=GRIS_BORDE),
)

#: (encabezado, ancho de columna) en el orden A..R
COLUMNAS: tuple[tuple[str, float], ...] = (
    ("Nº", 5),
    ("SECUENCIA DE TAREAS PRINCIPALES", 30),
    ("RUTINARIA\n(SI/NO)", 10),
    ("PELIGRO POTENCIAL", 30),
    ("RIESGO POTENCIAL / INCIDENTE", 32),
    ("LESIONES O ENFERMEDADES PROFESIONALES ASOCIADAS", 30),
    ("PROB.\n(P)", 8),
    ("CONSEC.\n(C)", 8),
    ("MAGNITUD\n(MR)", 10),
    ("CLASIFICACIÓN DEL RIESGO", 19),
    ("DESCRIPCIÓN DE LAS MEDIDAS DE CONTROL Y EXIGENCIA NORMATIVA", 62),
    ("CATEGORÍA DE CONTROL\n(A/B/C/D/E/F/G)", 16),
    ("FRECUENCIA", 13),
    ("RESPONSABLE", 22),
    ("PROB. RES.\n(P)", 9),
    ("CONSEC. RES.\n(C)", 9),
    ("MAGNITUD RES.\n(MR)", 11),
    ("CLASIFICACIÓN RESIDUAL", 19),
)

#: Bloques de cabecera agrupada: (título, columna inicial, columna final)
GRUPOS_CABECERA: tuple[tuple[str, int, int], ...] = (
    ("EVALUACIÓN DEL RIESGO INHERENTE (RIESGO PURO)", 7, 10),
    ("MEDIDAS DE CONTROL Y PREVENCIÓN (JERARQUÍA Y NORMATIVA)", 11, 14),
    ("EVALUACIÓN DEL RIESGO RESIDUAL", 15, 18),
)

FILA_TITULO = 1
FILA_META_INICIO = 3
FILA_CABECERA = 7          # cabecera agrupada
FILA_SUBCABECERA = 8       # nombres de columna
FILA_DATOS = 9             # primer registro


# ---------------------------------------------------------------------------
# Utilidades de estilo
# ---------------------------------------------------------------------------


def _fill(color: str) -> PatternFill:
    """Relleno sólido a partir de un color HEX sin '#'."""
    return PatternFill(fill_type="solid", start_color=color, end_color=color)


def _fuente(tamano: int = 10, negrita: bool = False, color: str = "000000") -> Font:
    return Font(name=FUENTE, size=tamano, bold=negrita, color=color)


def _centro(wrap: bool = True) -> Alignment:
    return Alignment(horizontal="center", vertical="center", wrap_text=wrap)


def _izquierda(wrap: bool = True) -> Alignment:
    return Alignment(horizontal="left", vertical="top", wrap_text=wrap)


def _alto_fila(valores: Sequence[str], anchos: Sequence[float], minimo: float = 45) -> float:
    """Estima la altura necesaria según el texto más largo de la fila."""
    lineas = 1
    for texto, ancho in zip(valores, anchos):
        if not texto:
            continue
        for parrafo in str(texto).split("\n"):
            caracteres_por_linea = max(ancho - 2, 8)
            lineas = max(lineas, math.ceil(max(len(parrafo), 1) / caracteres_por_linea))
    return max(minimo, min(lineas * 13.5, 260))


def _pintar_nivel(celda, nivel) -> None:
    """Aplica el código de color del nivel de riesgo a una celda."""
    celda.fill = _fill(nivel.color_fondo)
    celda.font = _fuente(10, negrita=True, color=nivel.color_texto)


# ---------------------------------------------------------------------------
# Hoja 1: Matriz IPER
# ---------------------------------------------------------------------------


def _hoja_matriz(ws: Worksheet, filas: list[FilaIPER], meta: dict[str, str]) -> int:
    """Escribe la matriz y devuelve la última fila usada."""
    anchos = [ancho for _, ancho in COLUMNAS]
    total_columnas = len(COLUMNAS)
    ultima_columna = get_column_letter(total_columnas)

    # --- anchos de columna -------------------------------------------------
    for indice, ancho in enumerate(anchos, start=1):
        ws.column_dimensions[get_column_letter(indice)].width = ancho

    # --- título ------------------------------------------------------------
    ws.merge_cells(f"A{FILA_TITULO}:{ultima_columna}{FILA_TITULO}")
    titulo = ws.cell(
        row=FILA_TITULO,
        column=1,
        value=(
            "REGISTRO: IDENTIFICACIÓN DE PELIGROS, EVALUACIÓN DE RIESGOS Y "
            "DETERMINACIÓN DE CONTROLES (MIPER)"
        ),
    )
    titulo.font = _fuente(13, negrita=True, color=BLANCO)
    titulo.fill = _fill(AZUL)
    titulo.alignment = _centro()
    ws.row_dimensions[FILA_TITULO].height = 30

    # --- bloque de metadatos (3 filas) ------------------------------------
    filas_meta = (
        ("OBRA / LUGAR:", meta.get("obra", ""), "REALIZADO POR:", meta.get("realizado_por", ""), "FECHA:", meta.get("fecha", date.today().strftime("%d/%m/%Y"))),
        ("CONTRATO:", meta.get("contrato", ""), "APROBADO POR:", meta.get("aprobado_por", ""), "CÓDIGO:", meta.get("codigo", "")),
        ("ACTIVIDAD:", meta.get("actividad", ""), "MARCO NORMATIVO:", meta.get("marco_normativo", ""), "REVISIÓN:", meta.get("revision", "")),
    )
    for i, (etiq1, val1, etiq2, val2, etiq3, val3) in enumerate(filas_meta):
        fila = FILA_META_INICIO + i
        ws.row_dimensions[fila].height = 20
        # etiqueta 1 + valor (B:E)
        ws.cell(row=fila, column=1, value=etiq1).font = _fuente(9, negrita=True)
        ws.cell(row=fila, column=1).alignment = _izquierda()
        ws.merge_cells(start_row=fila, start_column=2, end_row=fila, end_column=5)
        ws.cell(row=fila, column=2, value=val1).alignment = _izquierda(wrap=False)
        ws.cell(row=fila, column=2).font = _fuente(9)
        # etiqueta 2 + valor (G:M)
        ws.cell(row=fila, column=6, value=etiq2).font = _fuente(9, negrita=True)
        ws.merge_cells(start_row=fila, start_column=7, end_row=fila, end_column=13)
        ws.cell(row=fila, column=7, value=val2).alignment = _izquierda(wrap=False)
        ws.cell(row=fila, column=7).font = _fuente(9)
        # etiqueta 3 + valor (O:R)
        ws.cell(row=fila, column=14, value=etiq3).font = _fuente(9, negrita=True)
        ws.merge_cells(start_row=fila, start_column=15, end_row=fila, end_column=18)
        ws.cell(row=fila, column=15, value=val3).alignment = _izquierda(wrap=False)
        ws.cell(row=fila, column=15).font = _fuente(9)
        for col in (1, 6, 14):
            ws.cell(row=fila, column=col).fill = _fill(GRIS_CLARO)

    # --- cabecera agrupada -------------------------------------------------
    ws.row_dimensions[FILA_CABECERA].height = 28
    ws.row_dimensions[FILA_SUBCABECERA].height = 42

    # columnas simples: combinadas verticalmente entre 7 y 8
    for col in range(1, 7):
        ws.merge_cells(
            start_row=FILA_CABECERA, start_column=col,
            end_row=FILA_SUBCABECERA, end_column=col,
        )
        celda = ws.cell(row=FILA_CABECERA, column=col, value=COLUMNAS[col - 1][0])
        celda.font = _fuente(8, negrita=True, color=BLANCO)
        celda.fill = _fill(AZUL)
        celda.alignment = _centro()
        celda.border = BORDE_FINO
        ws.cell(row=FILA_SUBCABECERA, column=col).border = BORDE_FINO

    # columnas agrupadas con subtítulo en la fila 8
    for titulo_grupo, col_ini, col_fin in GRUPOS_CABECERA:
        ws.merge_cells(
            start_row=FILA_CABECERA, start_column=col_ini,
            end_row=FILA_CABECERA, end_column=col_fin,
        )
        celda = ws.cell(row=FILA_CABECERA, column=col_ini, value=titulo_grupo)
        celda.font = _fuente(8, negrita=True, color=BLANCO)
        celda.fill = _fill(AZUL_MEDIO)
        celda.alignment = _centro()
        for col in range(col_ini, col_fin + 1):
            ws.cell(row=FILA_CABECERA, column=col).border = BORDE_FINO
            sub = ws.cell(row=FILA_SUBCABECERA, column=col, value=COLUMNAS[col - 1][0])
            sub.font = _fuente(8, negrita=True, color=BLANCO)
            sub.fill = _fill(AZUL_MEDIO)
            sub.alignment = _centro()
            sub.border = BORDE_FINO

    # --- datos -------------------------------------------------------------
    filas_ordenadas = numerar(filas)
    fila_actual = FILA_DATOS

    for fila in filas_ordenadas:
        valores = (
            fila.numero,
            fila.tarea,
            fila.rutinaria,
            fila.peligro,
            fila.incidente,
            fila.lesiones,
            fila.p,
            fila.c,
            fila.mr,
            fila.nivel.etiqueta,
            fila.control,
            fila.categorias_texto,
            fila.frecuencia,
            fila.responsable,
            fila.p_res,
            fila.c_res,
            fila.mr_res,
            fila.nivel_res.etiqueta,
        )
        for col, valor in enumerate(valores, start=1):
            celda = ws.cell(row=fila_actual, column=col, value=valor)
            celda.border = BORDE_FINO
            celda.font = _fuente(9)
            if col in (1, 3, 7, 8, 9, 12, 13, 15, 16, 17):
                celda.alignment = _centro()
            else:
                celda.alignment = _izquierda()

        # colores de criticidad (inherente y residual)
        _pintar_nivel(ws.cell(row=fila_actual, column=9), fila.nivel)
        _pintar_nivel(ws.cell(row=fila_actual, column=10), fila.nivel)
        _pintar_nivel(ws.cell(row=fila_actual, column=17), fila.nivel_res)
        _pintar_nivel(ws.cell(row=fila_actual, column=18), fila.nivel_res)

        ws.row_dimensions[fila_actual].height = _alto_fila(
            [v for v in valores if isinstance(v, str)], anchos
        )
        fila_actual += 1

    ultima_fila_datos = max(fila_actual - 1, FILA_DATOS)

    # --- formato condicional (se mantiene al editar el archivo) -----------
    for celda_mr, rango in (("$I", f"I{FILA_DATOS}:J{ultima_fila_datos}"),
                            ("$Q", f"Q{FILA_DATOS}:R{ultima_fila_datos}")):
        for nivel in NIVELES_RIESGO:
            if nivel.clave == "critico":
                formula = f"{celda_mr}{FILA_DATOS}>=24"
            elif nivel.clave == "moderado":
                formula = f"AND({celda_mr}{FILA_DATOS}>=8,{celda_mr}{FILA_DATOS}<24)"
            else:
                formula = f"{celda_mr}{FILA_DATOS}<8"
            ws.conditional_formatting.add(
                rango,
                FormulaRule(
                    formula=[formula],
                    fill=_fill(nivel.color_fondo),
                    font=Font(bold=True, color=nivel.color_texto),
                    stopIfTrue=False,
                ),
            )

    # filas intercaladas en gris muy suave para legibilidad
    for i, fila in enumerate(range(FILA_DATOS, ultima_fila_datos + 1)):
        if i % 2 == 1:
            for col in (1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 15, 16, 17, 18):
                ws.cell(row=fila, column=col).fill = _fill("FAFAFA")
            # se repintan las celdas de criticidad
            nivel = filas_ordenadas[i].nivel
            nivel_res = filas_ordenadas[i].nivel_res
            _pintar_nivel(ws.cell(row=fila, column=9), nivel)
            _pintar_nivel(ws.cell(row=fila, column=10), nivel)
            _pintar_nivel(ws.cell(row=fila, column=17), nivel_res)
            _pintar_nivel(ws.cell(row=fila, column=18), nivel_res)

    # --- pie: toma de conocimiento ----------------------------------------
    fila_pie = ultima_fila_datos + 2
    ws.merge_cells(
        start_row=fila_pie, start_column=1, end_row=fila_pie, end_column=total_columnas
    )
    pie = ws.cell(
        row=fila_pie,
        column=1,
        value=(
            "TOMA DE CONOCIMIENTO Y REGISTRO DE DIFUSIÓN DE MATRIZ Y NORMATIVA "
            "VIGENTE (Ley 16.744 · DS 40 · DS 44 · DS 594)"
        ),
    )
    pie.font = _fuente(9, negrita=True, color=BLANCO)
    pie.fill = _fill(AZUL)
    pie.alignment = _centro()

    # firma: 3 cajas de 6 columnas
    fila_firma = fila_pie + 1
    ws.row_dimensions[fila_firma].height = 26
    firmas = (("NOMBRE COMPLETO", 1, 6), ("RUN / CÉDULA", 7, 12), ("FIRMA / FECHA", 13, 18))
    for etiqueta, ini, fin in firmas:
        ws.merge_cells(start_row=fila_firma, start_column=ini, end_row=fila_firma, end_column=fin)
        celda = ws.cell(row=fila_firma, column=ini, value=etiqueta)
        celda.font = _fuente(9, negrita=True)
        celda.fill = _fill(AZUL_CLARO)
        celda.alignment = _centro()
        for col in range(ini, fin + 1):
            ws.cell(row=fila_firma, column=col).border = BORDE_FINO

    for offset in (1, 2):
        fila_vacia = fila_firma + offset
        ws.row_dimensions[fila_vacia].height = 22
        for etiqueta, ini, fin in firmas:
            ws.merge_cells(
                start_row=fila_vacia, start_column=ini, end_row=fila_vacia, end_column=fin
            )
            for col in range(ini, fin + 1):
                ws.cell(row=fila_vacia, column=col).border = BORDE_FINO

    # --- configuración de impresión ---------------------------------------
    ws.freeze_panes = f"C{FILA_DATOS}"
    ws.auto_filter.ref = f"A{FILA_SUBCABECERA}:{ultima_columna}{ultima_fila_datos}"
    ws.print_title_rows = f"{FILA_CABECERA}:{FILA_SUBCABECERA}"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A3
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_area = f"A{FILA_TITULO}:{ultima_columna}{fila_firma + 2}"

    return fila_firma + 2


# ---------------------------------------------------------------------------
# Hoja 2: Criterios y matriz de colores
# ---------------------------------------------------------------------------


def _hoja_criterios(ws: Worksheet) -> None:
    """Escalas de P/C, semáforo y jerarquía de controles."""
    for col, ancho in zip("ABCDE", (22, 26, 62, 18, 24)):
        ws.column_dimensions[col].width = ancho

    def titulo_bloque(fila: int, texto: str) -> None:
        ws.merge_cells(start_row=fila, start_column=1, end_row=fila, end_column=5)
        celda = ws.cell(row=fila, column=1, value=texto)
        celda.font = _fuente(11, negrita=True, color=BLANCO)
        celda.fill = _fill(AZUL)
        celda.alignment = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[fila].height = 22

    def cabecera(fila: int, textos: tuple[str, ...]) -> None:
        for col, texto in enumerate(textos, start=1):
            celda = ws.cell(row=fila, column=col, value=texto)
            celda.font = _fuente(9, negrita=True)
            celda.fill = _fill(AZUL_CLARO)
            celda.alignment = _centro()
            celda.border = BORDE_FINO
        ws.row_dimensions[fila].height = 22

    # Título general
    ws.merge_cells("A1:E1")
    t = ws.cell(
        row=1,
        column=1,
        value="CRITERIOS DE EVALUACIÓN DE RIESGOS Y CÓDIGO DE COLORES (METODOLOGÍA MIPER)",
    )
    t.font = _fuente(13, negrita=True, color=BLANCO)
    t.fill = _fill(AZUL)
    t.alignment = _centro()
    ws.row_dimensions[1].height = 28

    # Bloque 1: probabilidad
    titulo_bloque(3, "1. CRITERIO DE PROBABILIDAD / EXPOSICIÓN (P)")
    cabecera(4, ("NIVEL", "PROBABILIDAD / EXPOSICIÓN", "DESCRIPCIÓN OPERACIONAL / FRECUENCIA", "VALOR (P)", ""))
    for i, item in enumerate(ESCALA_PROBABILIDAD):
        fila = 5 + i
        ws.cell(row=fila, column=1, value=item["nivel"]).font = _fuente(9)
        ws.cell(row=fila, column=2, value=item["alias"]).font = _fuente(9)
        ws.cell(row=fila, column=3, value=item["descripcion"]).font = _fuente(9)
        valor = ws.cell(row=fila, column=4, value=item["valor"])
        valor.font = _fuente(10, negrita=True)
        valor.alignment = _centro()
        for col in range(1, 5):
            ws.cell(row=fila, column=col).border = BORDE_FINO
            ws.cell(row=fila, column=col).alignment = (
                _centro() if col in (1, 2, 4) else _izquierda()
            )
        ws.row_dimensions[fila].height = 30

    # Bloque 2: consecuencia
    titulo_bloque(10, "2. CRITERIO DE CONSECUENCIA / SEVERIDAD (C)")
    cabecera(11, ("NIVEL", "SEVERIDAD DEL DAÑO", "IMPACTO EN LA SALUD / SEGURIDAD / PATRIMONIO", "VALOR (C)", ""))
    for i, item in enumerate(ESCALA_CONSECUENCIA):
        fila = 12 + i
        ws.cell(row=fila, column=1, value=item["nivel"]).font = _fuente(9)
        ws.cell(row=fila, column=2, value=item["alias"]).font = _fuente(9)
        ws.cell(row=fila, column=3, value=item["descripcion"]).font = _fuente(9)
        valor = ws.cell(row=fila, column=4, value=item["valor"])
        valor.font = _fuente(10, negrita=True)
        valor.alignment = _centro()
        for col in range(1, 5):
            ws.cell(row=fila, column=col).border = BORDE_FINO
            ws.cell(row=fila, column=col).alignment = (
                _centro() if col in (1, 2, 4) else _izquierda()
            )
        ws.row_dimensions[fila].height = 30

    # Bloque 3: clasificación
    titulo_bloque(17, "3. MATRIZ DE EVALUACIÓN DE RIESGOS Y CÓDIGO DE COLORES (MR = P × C)")
    cabecera(18, ("CLASIFICACIÓN DEL RIESGO", "RANGO DE MAGNITUD (MR)", "ACCIÓN REQUERIDA / PLAZO DE CONTROL", "CÓDIGO DE COLOR", "COLOR"))
    for i, nivel in enumerate(NIVELES_RIESGO):
        fila = 19 + i
        ws.cell(row=fila, column=1, value=nivel.etiqueta).font = _fuente(9, negrita=True)
        ws.cell(row=fila, column=2, value=nivel.rango).font = _fuente(9)
        ws.cell(row=fila, column=3, value=nivel.accion).font = _fuente(9)
        codigo = ws.cell(row=fila, column=4, value=nivel.clave.capitalize())
        codigo.alignment = _centro()
        codigo.font = _fuente(9, negrita=True, color=nivel.color_texto)
        codigo.fill = _fill(nivel.color_fondo)
        ws.cell(row=fila, column=5).fill = _fill(nivel.color_fondo)
        for col in range(1, 6):
            ws.cell(row=fila, column=col).border = BORDE_FINO
            if col not in (4, 5):
                ws.cell(row=fila, column=col).alignment = _izquierda()
        ws.row_dimensions[fila].height = 44

    # Bloque 4: jerarquía de controles
    titulo_bloque(23, "4. JERARQUÍA DE CONTROLES DE PREVENCIÓN (NCh / ISO 45001 / DS 44)")
    cabecera(24, ("CÓDIGO", "CATEGORÍA DE CONTROL", "DESCRIPCIÓN Y EJEMPLO APLICADO", "EFECTIVIDAD", ""))
    for i, cat in enumerate(CATEGORIAS_CONTROL):
        fila = 25 + i
        ws.cell(row=fila, column=1, value=cat["codigo"]).font = _fuente(10, negrita=True)
        ws.cell(row=fila, column=2, value=cat["nombre"]).font = _fuente(9, negrita=True)
        ws.cell(row=fila, column=3, value=cat["descripcion"]).font = _fuente(9)
        ws.cell(row=fila, column=4, value=cat["efectividad"]).font = _fuente(9)
        for col in range(1, 5):
            ws.cell(row=fila, column=col).border = BORDE_FINO
            ws.cell(row=fila, column=col).alignment = (
                _centro() if col in (1, 4) else _izquierda()
            )
        ws.row_dimensions[fila].height = 32

    # Bloque 5: grilla 4x4 coloreada
    fila_grid = 34
    titulo_bloque(fila_grid, "5. GRILLA DE CRITICIDAD (P × C) – MATRIZ 4 × 4")
    ws.cell(row=fila_grid + 1, column=1, value="P \\ C").font = _fuente(9, negrita=True)
    ws.cell(row=fila_grid + 1, column=1).fill = _fill(GRIS_CLARO)
    ws.cell(row=fila_grid + 1, column=1).alignment = _centro()
    ws.cell(row=fila_grid + 1, column=1).border = BORDE_FINO
    for j, cons in enumerate(ESCALA_CONSECUENCIA):
        celda = ws.cell(row=fila_grid + 1, column=2 + j, value=f"C = {cons['valor']}")
        celda.font = _fuente(9, negrita=True)
        celda.fill = _fill(AZUL_CLARO)
        celda.alignment = _centro()
        celda.border = BORDE_FINO

    for i, prob in enumerate(reversed(ESCALA_PROBABILIDAD)):
        fila = fila_grid + 2 + i
        etiqueta = ws.cell(row=fila, column=1, value=f"P = {prob['valor']}")
        etiqueta.font = _fuente(9, negrita=True)
        etiqueta.fill = _fill(AZUL_CLARO)
        etiqueta.alignment = _centro()
        etiqueta.border = BORDE_FINO
        for j, cons in enumerate(ESCALA_CONSECUENCIA):
            mr = prob["valor"] * cons["valor"]
            nivel = obtener_nivel(mr)
            celda = ws.cell(row=fila, column=2 + j, value=mr)
            celda.font = _fuente(11, negrita=True, color=nivel.color_texto)
            celda.fill = _fill(nivel.color_fondo)
            celda.alignment = _centro()
            celda.border = BORDE_FINO
        ws.row_dimensions[fila].height = 26

    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True


# ---------------------------------------------------------------------------
# Hoja 3: Resumen ejecutivo
# ---------------------------------------------------------------------------


def _hoja_resumen(ws: Worksheet, filas: list[FilaIPER]) -> None:
    """Indicadores, distribución de criticidad y gráfico de barras."""
    for col, ancho in zip("ABCDEF", (32, 14, 14, 18, 18, 18)):
        ws.column_dimensions[col].width = ancho

    ws.merge_cells("A1:F1")
    t = ws.cell(row=1, column=1, value="RESUMEN EJECUTIVO DE LA MATRIZ MIPER")
    t.font = _fuente(13, negrita=True, color=BLANCO)
    t.fill = _fill(AZUL)
    t.alignment = _centro()
    ws.row_dimensions[1].height = 28

    total = len(filas)
    conteo = {nivel.clave: 0 for nivel in NIVELES_RIESGO}
    conteo_res = {nivel.clave: 0 for nivel in NIVELES_RIESGO}
    for fila in filas:
        conteo[fila.nivel.clave] += 1
        conteo_res[fila.nivel_res.clave] += 1

    promedio = round(sum(f.mr for f in filas) / total, 1) if total else 0
    promedio_res = round(sum(f.mr_res for f in filas) / total, 1) if total else 0
    reduccion = round((1 - promedio_res / promedio) * 100, 1) if promedio else 0

    indicadores = (
        ("Total de peligros identificados", total),
        ("Total de actividades / tareas", len({f.tarea for f in filas})),
        ("Magnitud promedio del riesgo inherente", promedio),
        ("Magnitud promedio del riesgo residual", promedio_res),
        ("Reducción promedio de la magnitud (%)", reduccion),
        ("Peligros críticos remanentes (residual)", conteo_res["critico"]),
    )
    for i, (etiqueta, valor) in enumerate(indicadores):
        fila = 3 + i
        ws.cell(row=fila, column=1, value=etiqueta).font = _fuente(10, negrita=True)
        ws.cell(row=fila, column=1).fill = _fill(GRIS_CLARO)
        celda = ws.cell(row=fila, column=2, value=valor)
        celda.font = _fuente(11, negrita=True)
        celda.alignment = _centro()
        for col in (1, 2):
            ws.cell(row=fila, column=col).border = BORDE_FINO
        ws.row_dimensions[fila].height = 20

    # Tabla de distribución
    fila_tabla = 11
    encabezados = ("CLASIFICACIÓN", "INHERENTE", "RESIDUAL", "ACCIÓN")
    for col, texto in enumerate(encabezados, start=1):
        celda = ws.cell(row=fila_tabla, column=col, value=texto)
        celda.font = _fuente(9, negrita=True, color=BLANCO)
        celda.fill = _fill(AZUL_MEDIO)
        celda.alignment = _centro()
        celda.border = BORDE_FINO

    for i, nivel in enumerate(NIVELES_RIESGO):
        fila = fila_tabla + 1 + i
        c1 = ws.cell(row=fila, column=1, value=nivel.etiqueta)
        c1.fill = _fill(COLOR_SUAVE[nivel.clave])
        c1.font = _fuente(9, negrita=True)
        ws.cell(row=fila, column=2, value=conteo[nivel.clave]).alignment = _centro()
        ws.cell(row=fila, column=3, value=conteo_res[nivel.clave]).alignment = _centro()
        ws.cell(row=fila, column=4, value=nivel.rango)
        for col in range(1, 5):
            ws.cell(row=fila, column=col).border = BORDE_FINO
        ws.row_dimensions[fila].height = 26

    # gráfico de barras con la distribución
    datos = Reference(ws, min_col=2, max_col=3, min_row=fila_tabla, max_row=fila_tabla + 3)
    categorias = Reference(ws, min_col=1, min_row=fila_tabla + 1, max_row=fila_tabla + 3)
    grafico = BarChart()
    grafico.type = "col"
    grafico.style = 10
    grafico.title = "Distribución del riesgo: inherente vs. residual"
    grafico.y_axis.title = "N° de peligros"
    grafico.x_axis.title = "Clasificación"
    grafico.add_data(datos, titles_from_data=True)
    grafico.set_categories(categorias)
    grafico.height = 8
    grafico.width = 16
    ws.add_chart(grafico, "F11")

    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr.fitToPage = True


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------


def construir_libro(
    filas: list[FilaIPER], meta: dict[str, str] | None = None
) -> bytes:
    """Genera el archivo .xlsx en memoria y devuelve sus bytes."""
    meta = dict(meta or {})
    meta.setdefault("fecha", date.today().strftime("%d/%m/%Y"))

    libro = Workbook()
    ws_matriz = libro.active
    ws_matriz.title = "Matriz IPER"
    _hoja_matriz(ws_matriz, filas, meta)

    _hoja_criterios(libro.create_sheet("Criterios"))
    _hoja_resumen(libro.create_sheet("Resumen"), filas)

    destino = BytesIO()
    libro.save(destino)
    return destino.getvalue()


def nombre_archivo(meta: dict[str, str] | None = None) -> str:
    """Nombre sugerido para la descarga, con fecha y código del registro."""
    meta = meta or {}
    codigo = (meta.get("codigo") or "MIPER").replace("/", "-").replace(" ", "-")
    return f"{codigo}_{date.today().strftime('%Y%m%d')}.xlsx"


def construir_plantilla_vacia(meta: dict[str, str] | None = None) -> bytes:
    """Libro sin registros, útil como plantilla en blanco para terreno."""
    return construir_libro([], meta)
