"""Componentes visuales reutilizables (tarjetas de riesgo y estilos de tabla)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ..config import NivelRiesgo


def tarjeta_riesgo(mr: int, nivel: NivelRiesgo, titulo: str = "Magnitud del riesgo") -> None:
    """Muestra una tarjeta con el valor de MR y su clasificación por color."""
    st.markdown(
        f"""
        <div style="
            border-left: 8px solid #{nivel.color_fondo};
            background: #{nivel.color_fondo}22;
            border-radius: 8px;
            padding: 10px 16px;
            margin: 4px 0 12px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
        ">
            <span style="font-size: 0.80rem; letter-spacing: .04em; text-transform: uppercase;
                         color: #555;">{titulo}</span>
            <span style="font-size: 1.05rem; font-weight: 600;">
                MR = <b>{mr}</b> &nbsp;·&nbsp;
                <span style="background:#{nivel.color_fondo}; color:#{nivel.color_texto};
                             padding: 3px 12px; border-radius: 999px; font-size: .95rem;">
                    {nivel.etiqueta}
                </span>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _aplicar_estilo(styler, funcion, columnas: list[str]):
    """Compatibilidad entre pandas 2.0 (applymap) y 2.1+ (map)."""
    if hasattr(styler, "map"):
        return styler.map(funcion, subset=columnas)
    return styler.applymap(funcion, subset=columnas)  # pragma: no cover


def estilizar_riesgos(df: pd.DataFrame, columnas_nivel: list[str]):
    """Colorea las columnas de criticidad usando el semáforo de la matriz."""

    colores = {
        "Riesgo Crítico / Elevado": ("#C00000", "#FFFFFF"),
        "Riesgo Moderado": ("#FFC000", "#3F2A00"),
        "Riesgo Aceptable / Leve": ("#00B050", "#FFFFFF"),
    }

    def color(valor: str) -> str:
        fondo, texto = colores.get(str(valor), ("", ""))
        if not fondo:
            return ""
        return f"background-color: {fondo}; color: {texto}; font-weight: 600;"

    return _aplicar_estilo(df.style, color, columnas_nivel)
