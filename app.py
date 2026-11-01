"""Punto de entrada de la aplicación Streamlit: Matriz MIPER (Chile).

Ejecutar con:

    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from iper import storage
from iper.config import META_POR_DEFECTO
from iper.ui import criterios, exportacion, formulario, resumen, vista_previa

# ---------------------------------------------------------------------------
# Configuración de página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="MIPER · Matriz de Peligros y Riesgos",
    page_icon="🦺",
    layout="wide",
    initial_sidebar_state="expanded",
)

storage.inicializar()

SECCIONES = (
    "📝 Registro",
    "📋 Vista previa",
    "📊 Resumen",
    "⬇️ Exportar",
    "📚 Criterios",
)

st.markdown(
    """
    <style>
        .block-container { padding-top: 1.6rem; }
        [data-testid="stMetricValue"] { font-size: 1.6rem; }
        h1, h2, h3 { letter-spacing: -0.01em; }
        .cabecera-miper {
            border-left: 6px solid #1F3864;
            padding-left: 14px;
            margin-bottom: 6px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="cabecera-miper">
        <h1 style="margin-bottom:0;">🦺 MIPER — Matriz de Identificación de Peligros
        y Evaluación de Riesgos</h1>
        <p style="color:#666; margin-top:4px;">
            Metodología P × C de 4 niveles · Ley 16.744 · D.S. 40 · D.S. 44 · D.S. 594
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

filas = storage.filas()
meta = storage.meta()

# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### ⚙️ Panel de control")
    st.metric("Peligros en la matriz", len(filas))
    st.caption(
        f"Actividades: {len({f.tarea for f in filas})} · "
        f"Críticos residuales: {sum(1 for f in filas if f.nivel_res.clave == 'critico')}"
    )

    st.divider()
    if st.button("📥 Cargar datos de ejemplo", use_container_width=True):
        storage.cargar_demo()
        st.session_state["form_version"] = st.session_state.get("form_version", 1) + 1
        st.toast("Matriz de ejemplo cargada (15 peligros).", icon="📥")
        st.rerun()

    if st.button("🧹 Vaciar matriz", use_container_width=True):
        storage.limpiar()
        st.toast("Matriz vaciada.", icon="🧹")
        st.rerun()

    st.divider()
    with st.expander("ℹ️ Acerca de esta herramienta"):
        st.markdown(
            f"""
            **{META_POR_DEFECTO['codigo']} · Rev. {META_POR_DEFECTO['revision']}**

            Aplicación de apoyo para construir la matriz IPER/MIPER y exportarla a
            Excel con formato condicional por criticidad.

            - Escala **P × C**: 1, 2, 4, 8 → MR de 1 a 64.
            - **Crítico** ≥ 24 · **Moderado** 8–16 · **Aceptable** < 8.
            - Jerarquía de controles A→G.

            *No reemplaza la evaluación de un experto en prevención de riesgos.*
            """
        )

# ---------------------------------------------------------------------------
# Navegación
# ---------------------------------------------------------------------------

destino = st.session_state.pop("nav_pendiente", None)
if destino:
    st.session_state["nav"] = destino

seccion = st.radio(
    "Sección",
    options=SECCIONES,
    horizontal=True,
    label_visibility="collapsed",
    key="nav",
)

st.divider()

# ---------------------------------------------------------------------------
# Contenido por sección
# ---------------------------------------------------------------------------

if seccion == "📝 Registro":
    editar_id = st.session_state.get("editando_id")
    datos_edicion = next((f.to_dict() for f in filas if f.id == editar_id), None)
    formulario.render(datos_edicion)

elif seccion == "📋 Vista previa":
    filtrado = vista_previa.render(filas)
    if not filtrado.empty:
        st.session_state["ids_filtrados"] = filtrado["id"].tolist()

elif seccion == "📊 Resumen":
    resumen.render(filas)

elif seccion == "⬇️ Exportar":
    ids = st.session_state.get("ids_filtrados")
    filtradas = [f for f in filas if f.id in ids] if ids else filas
    exportacion.render(filas, filtradas)

else:
    criterios.render()

# ---------------------------------------------------------------------------
# Pie
# ---------------------------------------------------------------------------

st.divider()
st.caption(
    "MIPER · Herramienta de apoyo metodológico. El empleador es responsable de la "
    "identificación de peligros, la evaluación de riesgos y la implementación de "
    "controles conforme a la Ley 16.744 y el D.S. N° 44."
)
