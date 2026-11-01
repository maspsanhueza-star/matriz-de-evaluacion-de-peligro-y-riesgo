"""Panel de indicadores y gráficos de la matriz."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ..config import CATEGORIAS_POR_CODIGO, NIVELES_RIESGO
from ..models import FilaIPER


def render(filas: list[FilaIPER]) -> None:
    """Muestra KPIs, distribución de criticidad y focos de atención."""
    if not filas:
        st.info("Registra peligros para ver el resumen ejecutivo.")
        return

    total = len(filas)
    promedio = sum(f.mr for f in filas) / total
    promedio_res = sum(f.mr_res for f in filas) / total
    reduccion = (1 - promedio_res / promedio) * 100 if promedio else 0
    criticos_res = sum(1 for f in filas if f.nivel_res.clave == "critico")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Peligros evaluados", total)
    col2.metric("MR promedio inherente", f"{promedio:.1f}")
    col3.metric(
        "MR promedio residual",
        f"{promedio_res:.1f}",
        delta=f"-{promedio - promedio_res:.1f}",
        delta_color="normal",
    )
    col4.metric("Reducción del riesgo", f"{reduccion:.0f}%")

    st.divider()

    # -- Distribución inherente vs residual --------------------------------
    etiquetas = [n.etiqueta for n in NIVELES_RIESGO]
    conteo = pd.DataFrame(
        {
            "Inherente": [sum(1 for f in filas if f.nivel.etiqueta == e) for e in etiquetas],
            "Residual": [sum(1 for f in filas if f.nivel_res.etiqueta == e) for e in etiquetas],
        },
        index=etiquetas,
    )

    col_a, col_b = st.columns([1.3, 1])
    with col_a:
        st.markdown("##### Distribución del riesgo (n.º de peligros)")
        st.bar_chart(conteo, color=["#C00000", "#2F5597"], height=320)
    with col_b:
        st.markdown("##### Tabla de distribución")
        tabla = conteo.copy()
        tabla["Variación"] = tabla["Residual"] - tabla["Inherente"]
        st.dataframe(tabla, use_container_width=True)

    # -- Focos de atención --------------------------------------------------
    st.divider()
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("##### 🔴 Peligros críticos que requieren control inmediato")
        criticos = [f for f in filas if f.nivel.clave == "critico"]
        if criticos:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Nº": f.numero,
                            "Tarea": f.tarea,
                            "Peligro": f.peligro,
                            "MR": f.mr,
                        }
                        for f in criticos
                    ]
                ),
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.success("No hay peligros con clasificación crítica.")

    with col_d:
        st.markdown("##### 🧭 Uso de la jerarquía de controles")
        uso: dict[str, int] = {codigo: 0 for codigo in CATEGORIAS_POR_CODIGO}
        for f in filas:
            for codigo in f.categorias:
                if codigo in uso:
                    uso[codigo] += 1
        df_uso = pd.DataFrame(
            [
                {
                    "Código": codigo,
                    "Categoría": CATEGORIAS_POR_CODIGO[codigo]["nombre"],
                    "N.º de controles": cantidad,
                }
                for codigo, cantidad in uso.items()
            ]
        ).set_index("Categoría")
        st.bar_chart(df_uso["N.º de controles"], color="#2F5597", height=280)

        eliminan = uso.get("A", 0) + uso.get("B", 0)
        epp = uso.get("G", 0)
        if epp > eliminan:
            st.warning(
                "Predominan los controles de **EPP** por sobre eliminación/sustitución. "
                "La jerarquía de la Ley 16.744 y el DS 44 prioriza los controles en la "
                "fuente del riesgo."
            )
