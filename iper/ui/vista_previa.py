"""Vista previa interactiva de la matriz con filtros en tiempo real."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ..config import NIVELES_RIESGO
from ..models import FilaIPER
from ..storage import duplicar, eliminar, mover
from .estilos import estilizar_riesgos

_COLUMNAS_VISTA = {
    "numero": "Nº",
    "tarea": "Tarea / Actividad",
    "rutinaria": "Rutinaria",
    "peligro": "Peligro",
    "incidente": "Incidente potencial",
    "lesiones": "Lesiones / Enf. profesional",
    "p": "P",
    "c": "C",
    "mr": "MR",
    "nivel": "Clasificación",
    "categorias": "Control",
    "frecuencia": "Frecuencia",
    "responsable": "Responsable",
    "mr_res": "MR res.",
    "nivel_res": "Clasificación res.",
    "control": "Medidas de control",
}


def construir_dataframe(filas: list[FilaIPER]) -> pd.DataFrame:
    """Convierte las filas en un DataFrame listo para mostrar y filtrar."""
    registros = [
        {
            "id": f.id,
            "numero": f.numero,
            "tarea": f.tarea,
            "rutinaria": f.rutinaria,
            "peligro": f.peligro,
            "incidente": f.incidente,
            "lesiones": f.lesiones,
            "p": f.p,
            "c": f.c,
            "mr": f.mr,
            "nivel": f.nivel.etiqueta,
            "categorias": f.categorias_texto,
            "frecuencia": f.frecuencia,
            "responsable": f.responsable,
            "control": f.control,
            "p_res": f.p_res,
            "c_res": f.c_res,
            "mr_res": f.mr_res,
            "nivel_res": f.nivel_res.etiqueta,
        }
        for f in filas
    ]
    return pd.DataFrame(registros)


def _filtros(df: pd.DataFrame) -> pd.DataFrame:
    """Controles de filtrado que se aplican en tiempo real sobre el DataFrame."""
    st.markdown("##### 🔎 Filtros")
    col1, col2, col3 = st.columns([1.4, 1, 1])
    with col1:
        texto = st.text_input(
            "Buscar texto (tarea, peligro, incidente, control)",
            key="filtro_texto",
            placeholder="Ej.: altura, ruido, eléctrico…",
        )
    with col2:
        niveles = st.multiselect(
            "Clasificación inherente",
            options=[n.etiqueta for n in NIVELES_RIESGO],
            default=[n.etiqueta for n in NIVELES_RIESGO],
            key="filtro_nivel",
        )
    with col3:
        tareas = st.multiselect(
            "Tarea / Actividad",
            options=sorted(df["tarea"].unique().tolist()),
            default=[],
            key="filtro_tarea",
            placeholder="Todas",
        )

    col4, col5 = st.columns([1, 1])
    with col4:
        solo_criticos = st.checkbox(
            "Mostrar solo riesgos moderados y críticos", key="filtro_criticos"
        )
    with col5:
        niveles_res = st.multiselect(
            "Clasificación residual",
            options=[n.etiqueta for n in NIVELES_RIESGO],
            default=[n.etiqueta for n in NIVELES_RIESGO],
            key="filtro_nivel_res",
        )

    filtrado = df.copy()
    if texto:
        patron = texto.strip().lower()
        mascara = (
            filtrado["tarea"].str.lower().str.contains(patron, na=False)
            | filtrado["peligro"].str.lower().str.contains(patron, na=False)
            | filtrado["incidente"].str.lower().str.contains(patron, na=False)
            | filtrado["control"].str.lower().str.contains(patron, na=False)
        )
        filtrado = filtrado[mascara]
    if niveles:
        filtrado = filtrado[filtrado["nivel"].isin(niveles)]
    if niveles_res:
        filtrado = filtrado[filtrado["nivel_res"].isin(niveles_res)]
    if tareas:
        filtrado = filtrado[filtrado["tarea"].isin(tareas)]
    if solo_criticos:
        filtrado = filtrado[
            filtrado["nivel"].isin(["Riesgo Crítico / Elevado", "Riesgo Moderado"])
        ]
    return filtrado


def _gestion_registros(filas: list[FilaIPER]) -> None:
    """Acciones de edición, duplicado, orden y eliminación de registros."""
    if not filas:
        return

    with st.expander("🛠️ Gestionar registros (editar · duplicar · eliminar)"):
        etiquetas = {
            f.id: f"{f.numero}. {f.peligro[:70]} — {f.tarea[:45]}" for f in filas
        }
        seleccionado = st.selectbox(
            "Selecciona un registro",
            options=list(etiquetas.keys()),
            format_func=lambda i: etiquetas[i],
            key="gestion_id",
        )
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("✏️ Editar", use_container_width=True):
                st.session_state["editando_id"] = seleccionado
                st.session_state["form_version"] += 1
                st.session_state["nav_pendiente"] = "📝 Registro"
                st.rerun()
        with col2:
            if st.button("📄 Duplicar", use_container_width=True):
                duplicar(seleccionado)
                st.toast("Registro duplicado.", icon="📄")
                st.rerun()
        with col3:
            if st.button("⬆️ Subir", use_container_width=True):
                mover(seleccionado, -1)
                st.rerun()
        with col4:
            if st.button("⬇️ Bajar", use_container_width=True):
                mover(seleccionado, 1)
                st.rerun()
        with col5:
            confirmar = st.checkbox("Confirmar", key="confirmar_eliminar")
            if st.button(
                "🗑️ Eliminar",
                use_container_width=True,
                disabled=not confirmar,
                help="Marca 'Confirmar' para habilitar la eliminación.",
            ):
                eliminar(seleccionado)
                st.toast("Registro eliminado.", icon="🗑️")
                st.rerun()


def render(filas: list[FilaIPER]) -> pd.DataFrame:
    """Dibuja la vista previa y devuelve el DataFrame filtrado."""
    if not filas:
        st.info(
            "Aún no hay peligros registrados. Usa la pestaña **Registro** o carga los "
            "datos de ejemplo desde la barra lateral."
        )
        return pd.DataFrame()

    df = construir_dataframe(filas)
    filtrado = _filtros(df)

    criticos = int((df["nivel"] == "Riesgo Crítico / Elevado").sum())
    moderados = int((df["nivel"] == "Riesgo Moderado").sum())
    aceptables = int((df["nivel"] == "Riesgo Aceptable / Leve").sum())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Peligros registrados", len(df))
    col2.metric("🔴 Críticos", criticos)
    col3.metric("🟡 Moderados", moderados)
    col4.metric("🟢 Aceptables", aceptables)

    st.caption(
        f"Mostrando **{len(filtrado)}** de **{len(df)}** registros "
        f"(filtros activos: {'sí' if len(filtrado) != len(df) else 'no'})."
    )

    vista = filtrado[list(_COLUMNAS_VISTA.keys())].rename(columns=_COLUMNAS_VISTA)
    if vista.empty:
        st.warning("Ningún registro coincide con los filtros seleccionados.")
    else:
        estilizado = estilizar_riesgos(vista, ["Clasificación", "Clasificación res."])
        st.dataframe(
            estilizado,
            hide_index=True,
            height=min(620, 120 + 36 * len(vista)),
            column_config={
                "P": st.column_config.NumberColumn(width="small"),
                "C": st.column_config.NumberColumn(width="small"),
                "MR": st.column_config.NumberColumn(width="small"),
                "MR res.": st.column_config.NumberColumn(width="small"),
                "Medidas de control": st.column_config.TextColumn(width="large"),
                "Peligro": st.column_config.TextColumn(width="medium"),
                "Incidente potencial": st.column_config.TextColumn(width="medium"),
            },
        )

    st.divider()
    _gestion_registros(filas)
    return filtrado
