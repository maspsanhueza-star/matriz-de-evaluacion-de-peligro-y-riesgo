"""Pestaña de criterios metodológicos y marco legal."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ..config import (
    CATEGORIAS_CONTROL,
    ESCALA_CONSECUENCIA,
    ESCALA_PROBABILIDAD,
    MARCO_NORMATIVO,
    NIVELES_RIESGO,
    obtener_nivel,
)
from .estilos import _aplicar_estilo


def render() -> None:
    """Muestra las escalas, el semáforo, la grilla 4×4 y la jerarquía de controles."""
    st.markdown(
        """
        La **magnitud del riesgo (MR)** se obtiene multiplicando la probabilidad de
        ocurrencia por la consecuencia esperada:

        **MR = P × C** — ambas variables en escala de 4 niveles con valores
        **1, 2, 4 y 8** (progresión geométrica), lo que arroja magnitudes entre 1 y 64.
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 1 · Probabilidad / Exposición (P)")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Nivel": i["nivel"],
                        "Valor (P)": i["valor"],
                        "Descripción operacional": i["descripcion"],
                    }
                    for i in ESCALA_PROBABILIDAD
                ]
            ),
            hide_index=True,
            use_container_width=True,
        )

    with col2:
        st.markdown("##### 2 · Consecuencia / Severidad (C)")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Nivel": i["nivel"],
                        "Valor (C)": i["valor"],
                        "Impacto en salud / seguridad": i["descripcion"],
                    }
                    for i in ESCALA_CONSECUENCIA
                ]
            ),
            hide_index=True,
            use_container_width=True,
        )

    st.divider()

    # -- Semáforo ----------------------------------------------------------
    st.markdown("##### 3 · Clasificación del riesgo y código de colores")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Clasificación": n.etiqueta,
                    "Equivalencia": n.alias,
                    "Rango de MR": n.rango,
                    "Color": n.clave.upper(),
                    "Acción requerida": n.accion,
                }
                for n in NIVELES_RIESGO
            ]
        ),
        hide_index=True,
        use_container_width=True,
    )

    # -- Grilla 4x4 --------------------------------------------------------
    st.markdown("##### 4 · Grilla de criticidad (P × C)")
    filas_grid = []
    for prob in reversed(ESCALA_PROBABILIDAD):
        fila = {"P \\ C": f"P = {prob['valor']}"}
        for cons in ESCALA_CONSECUENCIA:
            fila[f"C = {cons['valor']}"] = prob["valor"] * cons["valor"]
        filas_grid.append(fila)
    grid = pd.DataFrame(filas_grid).set_index("P \\ C")

    def _color_mr(valor: int) -> str:
        nivel = obtener_nivel(valor)
        return (
            f"background-color: #{nivel.color_fondo}; color: #{nivel.color_texto}; "
            "font-weight: 700; text-align: center;"
        )

    colores_grid = ["C = 1", "C = 2", "C = 4", "C = 8"]
    st.dataframe(
        _aplicar_estilo(grid.style, _color_mr, colores_grid).format("{:.0f}"),
        use_container_width=True,
    )
    st.caption(
        "Verde: aceptable (< 8) · Ámbar: moderado (8 a 16) · Rojo: crítico (≥ 24)."
    )

    st.divider()

    # -- Jerarquía de controles -------------------------------------------
    st.markdown("##### 5 · Jerarquía de controles de prevención")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Código": c["codigo"],
                    "Categoría": c["nombre"],
                    "Descripción y ejemplo": c["descripcion"],
                    "Efectividad": c["efectividad"],
                }
                for c in CATEGORIAS_CONTROL
            ]
        ),
        hide_index=True,
        use_container_width=True,
    )
    st.info(
        "La jerarquía debe aplicarse **de arriba hacia abajo**: primero eliminar el "
        "peligro, luego sustituirlo, después aplicar controles de ingeniería, "
        "señalización y medidas administrativas. El EPP es siempre la **última "
        "barrera** de protección (Ley 16.744, DS 44, ISO 45001)."
    )

    with st.expander("📚 Marco normativo de referencia (Chile)"):
        for norma in MARCO_NORMATIVO:
            st.markdown(f"- {norma}")
        st.caption(
            "Esta aplicación es una herramienta de apoyo metodológico y no reemplaza "
            "la evaluación de un experto en prevención de riesgos acreditado, ni el "
            "cumplimiento de las obligaciones legales del empleador."
        )
