"""Pestaña de exportación: metadatos del encabezado y descarga del Excel."""

from __future__ import annotations

from datetime import date

import streamlit as st

from ..config import META_POR_DEFECTO  # noqa: F401  (documenta valores por defecto)
from ..excel_export import construir_libro, construir_plantilla_vacia, nombre_archivo
from ..models import FilaIPER
from ..storage import exportar_json, guardar_meta, meta as meta_actual

_MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _formulario_metadatos() -> None:
    """Encabezado corporativo del registro (obra, contrato, responsable...)."""
    meta = meta_actual()

    with st.form("form_metadatos", border=True):
        st.markdown("##### 🏷️ Encabezado del registro")
        col1, col2 = st.columns(2)
        with col1:
            obra = st.text_input("Obra / Lugar", value=meta.get("obra", ""))
            actividad = st.text_input("Actividad", value=meta.get("actividad", ""))
            realizado_por = st.text_input(
                "Realizado por", value=meta.get("realizado_por", "")
            )
            codigo = st.text_input("Código del documento", value=meta.get("codigo", ""))
        with col2:
            contrato = st.text_input("Contrato", value=meta.get("contrato", ""))
            aprobado_por = st.text_input(
                "Aprobado por", value=meta.get("aprobado_por", "")
            )
            marco = st.text_input(
                "Marco normativo", value=meta.get("marco_normativo", "")
            )
            revision = st.text_input("Revisión", value=meta.get("revision", ""))

        guardar = st.form_submit_button("💾 Guardar encabezado", type="primary")
        if guardar:
            guardar_meta(
                {
                    "obra": obra,
                    "contrato": contrato,
                    "actividad": actividad,
                    "realizado_por": realizado_por,
                    "aprobado_por": aprobado_por,
                    "marco_normativo": marco,
                    "codigo": codigo,
                    "revision": revision,
                }
            )
            st.toast("Encabezado guardado.", icon="✅")
            st.rerun()


def render(filas: list[FilaIPER], filtradas: list[FilaIPER] | None = None) -> None:
    """Genera y ofrece la descarga del libro Excel (completo o filtrado)."""
    _formulario_metadatos()
    st.divider()

    meta = meta_actual()
    completo = construir_libro(filas, meta)

    st.markdown("##### ⬇️ Descarga")
    if not filas:
        st.warning(
            "La matriz está vacía. Puedes descargar una **plantilla en blanco** con "
            "los criterios y el formato listos para completar en terreno."
        )
        st.download_button(
            "📄 Descargar plantilla vacía (.xlsx)",
            data=construir_plantilla_vacia(meta),
            file_name="MIPER_plantilla.xlsx",
            mime=_MIME_XLSX,
            type="primary",
        )
        return

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ Descargar matriz completa (.xlsx)",
            data=completo,
            file_name=nombre_archivo(meta),
            mime=_MIME_XLSX,
            type="primary",
            use_container_width=True,
        )
        st.caption(
            f"{len(filas)} peligros · hojas **Matriz IPER**, **Criterios** y **Resumen**."
        )
    with col2:
        if filtradas is not None and len(filtradas) and len(filtradas) != len(filas):
            st.download_button(
                "⬇️ Descargar solo los filtrados (.xlsx)",
                data=construir_libro(filtradas, meta),
                file_name=nombre_archivo(meta).replace(".xlsx", "_filtrado.xlsx"),
                mime=_MIME_XLSX,
                use_container_width=True,
            )
            st.caption(f"{len(filtradas)} peligros según los filtros aplicados.")
        else:
            st.button(
                "⬇️ Descargar solo los filtrados (.xlsx)",
                disabled=True,
                use_container_width=True,
                help="Aplica filtros en la pestaña Vista previa para habilitar esta opción.",
            )

    st.divider()
    st.markdown("##### 💾 Respaldo de trabajo (.json)")
    st.caption(
        "Guarda una copia editable de la matriz para continuar después o traspasarla "
        "a otro equipo."
    )
    col3, col4 = st.columns(2)
    with col3:
        st.download_button(
            "⬇️ Descargar respaldo JSON",
            data=exportar_json(),
            file_name=f"mipre_respaldo_{date.today():%Y%m%d}.json",
            mime="application/json",
            use_container_width=True,
        )
    with col4:
        archivo = st.file_uploader("Restaurar respaldo JSON", type=["json"])
        if archivo is not None:
            from ..storage import importar_json

            try:
                cantidad = importar_json(archivo.getvalue())
                st.success(f"Respaldo restaurado: {cantidad} registros.")
                st.rerun()
            except Exception as exc:  # noqa: BLE001 - se muestra al usuario
                st.error(f"No se pudo leer el respaldo: {exc}")

    st.divider()
    st.info(
        "**Metodología aplicada:** MR = P × C, con P y C en escala de 4 niveles "
        "(1-2-4-8). Crítico ≥ 24 · Moderado 8 a 16 · Aceptable < 8. "
        "El formato condicional del Excel se mantiene al editar el archivo."
    )
