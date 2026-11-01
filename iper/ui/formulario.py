"""Formulario de ingreso / edición de un peligro con su evaluación de riesgo."""

from __future__ import annotations

import streamlit as st

from ..config import (
    ACTIVIDADES_SUGERIDAS,
    CATEGORIAS_CONTROL,
    CATEGORIAS_POR_CODIGO,
    ESCALA_CONSECUENCIA,
    ESCALA_PROBABILIDAD,
    FRECUENCIAS,
    PELIGROS_SUGERIDOS,
    RESPONSABLES_SUGERIDOS,
    etiqueta_consecuencia,
    etiqueta_probabilidad,
)
from ..models import FilaIPER
from ..risk import evaluar, residual_empeora
from ..storage import actualizar, agregar
from .estilos import tarjeta_riesgo

OTRA_TAREA = "➕ Otra actividad / tarea…"
OTRO_PELIGRO = "➕ Otro peligro (describir)…"
OTRO_RESPONSABLE = "➕ Otro responsable…"

_VALORES_P = [item["valor"] for item in ESCALA_PROBABILIDAD]
_VALORES_C = [item["valor"] for item in ESCALA_CONSECUENCIA]
_CODIGOS = [cat["codigo"] for cat in CATEGORIAS_CONTROL]


def _indice(opciones: list[str], valor: str | None) -> int:
    """Índice seguro para un selectbox, agregando el valor si no está en la lista."""
    if valor and valor in opciones:
        return opciones.index(valor)
    return 0


def _opciones_con(valor: str | None, base: tuple[str, ...]) -> list[str]:
    """Devuelve la lista base asegurando que el valor actual esté presente."""
    opciones = list(base)
    if valor and valor not in opciones:
        opciones.insert(0, valor)
    return opciones


def render(datos: dict | None = None) -> None:
    """Dibuja el formulario completo.

    ``datos`` es la fila a editar (diccionario) o ``None`` para crear una nueva.
    """
    editando = datos is not None
    d = datos or {}
    version = st.session_state.get("form_version", 1)

    def clave(nombre: str) -> str:
        # Las claves incluyen la versión para que al abrir una fila distinta los
        # widgets se reinicien con los valores correctos.
        return f"f{version}_{nombre}"

    st.subheader("✏️ Editar peligro" if editando else "➕ Nuevo peligro")
    if editando:
        st.info(
            "Estás modificando un registro existente. Al guardar se reemplaza en "
            "su misma posición de la matriz."
        )

    # =====================================================================
    # 1. Identificación de la actividad, el peligro y sus consecuencias
    # =====================================================================
    st.markdown("#### 1 · Identificación del peligro")
    with st.container(border=True):
        col_a, col_b = st.columns([1.1, 1])

        with col_a:
            opciones_tarea = _opciones_con(d.get("tarea"), ACTIVIDADES_SUGERIDAS) + [OTRA_TAREA]
            indice_tarea = (
                _indice(opciones_tarea, d.get("tarea")) if d.get("tarea") else 0
            )
            seleccion_tarea = st.selectbox(
                "Actividad / Tarea *",
                options=opciones_tarea,
                index=indice_tarea,
                key=clave("tarea"),
                help="Elige una tarea del catálogo o crea una nueva.",
            )
            tarea = seleccion_tarea
            if seleccion_tarea == OTRA_TAREA:
                tarea = st.text_input(
                    "Nombre de la nueva actividad / tarea *",
                    value=d.get("tarea", "") if editando else "",
                    key=clave("tarea_nueva"),
                    placeholder="Ej.: Instalación de canaletas y bajadas de aguas lluvia",
                )

        with col_b:
            opciones_rutina = ["SI", "NO"]
            rutinaria = st.radio(
                "¿Tarea rutinaria?",
                options=opciones_rutina,
                index=opciones_rutina.index(d.get("rutinaria", "SI")),
                horizontal=True,
                key=clave("rutinaria"),
            )

        col_c, col_d = st.columns([1, 1])
        with col_c:
            opciones_peligro = _opciones_con(d.get("peligro"), PELIGROS_SUGERIDOS) + [OTRO_PELIGRO]
            indice_peligro = (
                _indice(opciones_peligro, d.get("peligro")) if d.get("peligro") else 0
            )
            seleccion_peligro = st.selectbox(
                "Peligro potencial *",
                options=opciones_peligro,
                index=indice_peligro,
                key=clave("peligro"),
            )
            peligro = seleccion_peligro
            if seleccion_peligro == OTRO_PELIGRO:
                peligro = st.text_input(
                    "Describe el peligro *",
                    value=d.get("peligro", "") if editando else "",
                    key=clave("peligro_nuevo"),
                    placeholder="Ej.: Caída de herramientas desde altura",
                )

        with col_d:
            incidente = st.text_area(
                "Incidente potencial *",
                value=d.get("incidente", ""),
                key=clave("incidente"),
                height=100,
                placeholder="Ej.: Caída a distinto nivel por pérdida de equilibrio",
            )
            lesiones = st.text_area(
                "Lesiones o enfermedades profesionales asociadas",
                value=d.get("lesiones", ""),
                key=clave("lesiones"),
                height=100,
                placeholder="Ej.: Fracturas, contusiones graves, muerte",
            )

    # =====================================================================
    # 2. Evaluación del riesgo puro (inherente)
    # =====================================================================
    st.markdown("#### 2 · Evaluación del riesgo inherente (riesgo puro)")
    with st.container(border=True):
        col_p, col_c, col_res = st.columns([1, 1, 1.3])
        with col_p:
            p = st.selectbox(
                "Probabilidad (P)",
                options=_VALORES_P,
                index=_VALORES_P.index(d.get("p", 1)) if d.get("p") in _VALORES_P else 0,
                format_func=etiqueta_probabilidad,
                key=clave("p"),
            )
        with col_c:
            c = st.selectbox(
                "Consecuencia (C)",
                options=_VALORES_C,
                index=_VALORES_C.index(d.get("c", 1)) if d.get("c") in _VALORES_C else 0,
                format_func=etiqueta_consecuencia,
                key=clave("c"),
            )
        with col_res:
            mr, nivel = evaluar(p, c)
            tarjeta_riesgo(mr, nivel, "Riesgo inherente")

        st.caption(
            f"**Criterio P:** {next(i['descripcion'] for i in ESCALA_PROBABILIDAD if i['valor'] == p)}"
        )
        st.caption(
            f"**Criterio C:** {next(i['descripcion'] for i in ESCALA_CONSECUENCIA if i['valor'] == c)}"
        )

    # =====================================================================
    # 3. Controles operacionales y riesgo residual
    # =====================================================================
    st.markdown("#### 3 · Controles operacionales y riesgo residual")
    with st.container(border=True):
        categorias = st.multiselect(
            "Categorías de control aplicadas (jerarquía de prevención)",
            options=_CODIGOS,
            default=[c for c in (d.get("categorias") or []) if c in _CODIGOS],
            format_func=lambda cod: (
                f"{cod} · {CATEGORIAS_POR_CODIGO[cod]['nombre']} "
                f"({CATEGORIAS_POR_CODIGO[cod]['efectividad']})"
            ),
            key=clave("categorias"),
            help="A = Eliminación · B = Sustitución · C = Ingeniería · D = Señalización "
                 "· E = Administrativo · F = Legal · G = EPP",
        )

        control = st.text_area(
            "Descripción de las medidas de control y exigencia normativa",
            value=d.get("control", ""),
            key=clave("control"),
            height=170,
            placeholder=(
                "• C1: Barandillas perimetrales rígidas o mallas anticaídas.\n"
                "• E1: Procedimiento de Trabajo Seguro (PTS) y AST previo.\n"
                "• F1: Cumplimiento DS 594 Art. 7 y 8.\n"
                "• G1: Arnés de cuerpo entero de doble cabo."
            ),
        )

        col_frec, col_resp = st.columns([1, 1])
        with col_frec:
            frecuencia = st.selectbox(
                "Frecuencia del control",
                options=_opciones_con(d.get("frecuencia"), FRECUENCIAS),
                index=_indice(_opciones_con(d.get("frecuencia"), FRECUENCIAS), d.get("frecuencia")),
                key=clave("frecuencia_control"),
            )
        with col_resp:
            opciones_resp = _opciones_con(d.get("responsable"), RESPONSABLES_SUGERIDOS) + [OTRO_RESPONSABLE]
            seleccion_resp = st.selectbox(
                "Responsable del control",
                options=opciones_resp,
                index=_indice(opciones_resp, d.get("responsable")),
                key=clave("responsable"),
            )
            responsable = seleccion_resp
            if seleccion_resp == OTRO_RESPONSABLE:
                responsable = st.text_input(
                    "Nombre / cargo del responsable",
                    value=d.get("responsable", "") if editando else "",
                    key=clave("responsable_nuevo"),
                )

        st.divider()
        col_pr, col_cr, col_rr = st.columns([1, 1, 1.3])
        with col_pr:
            p_res = st.selectbox(
                "Probabilidad residual (P')",
                options=_VALORES_P,
                index=_VALORES_P.index(d.get("p_res", 1)) if d.get("p_res") in _VALORES_P else 0,
                format_func=etiqueta_probabilidad,
                key=clave("p_res"),
            )
        with col_cr:
            c_res = st.selectbox(
                "Consecuencia residual (C')",
                options=_VALORES_C,
                index=_VALORES_C.index(d.get("c_res", 1)) if d.get("c_res") in _VALORES_C else 0,
                format_func=etiqueta_consecuencia,
                key=clave("c_res_val"),
            )
        with col_rr:
            mr_res, nivel_res = evaluar(p_res, c_res)
            tarjeta_riesgo(mr_res, nivel_res, "Riesgo residual")

        if residual_empeora(p, c, p_res, c_res):
            st.warning(
                "⚠️ El riesgo residual quedó **por sobre** el riesgo inherente. "
                "Revisa las medidas de control o los valores de P' y C': un control "
                "nunca debe aumentar el riesgo."
            )
        elif categorias:
            st.success(
                f"Reducción de la magnitud del riesgo: **{mr - mr_res} punto(s)** "
                f"({mr} → {mr_res})."
            )

    # =====================================================================
    # Acciones
    # =====================================================================
    col_guardar, col_cancelar, _ = st.columns([1, 1, 3])
    with col_guardar:
        guardar = st.button(
            "💾 Guardar registro" if not editando else "💾 Guardar cambios",
            type="primary",
            use_container_width=True,
        )
    with col_cancelar:
        cancelar = st.button("✖ Cancelar", use_container_width=True) if editando else False

    if cancelar:
        st.session_state["editando_id"] = None
        st.session_state["form_version"] += 1
        st.rerun()

    if guardar:
        errores = []
        if not tarea or not tarea.strip():
            errores.append("La **actividad / tarea** es obligatoria.")
        if not peligro or not peligro.strip():
            errores.append("El **peligro potencial** es obligatorio.")
        if not incidente or not incidente.strip():
            errores.append("El **incidente potencial** es obligatorio.")
        if not categorias:
            errores.append("Selecciona al menos una **categoría de control**.")
        if not control or not control.strip():
            errores.append("Describe al menos una **medida de control**.")

        if errores:
            for error in errores:
                st.error(error)
            return

        nueva = FilaIPER(
            tarea=tarea.strip(),
            peligro=peligro.strip(),
            incidente=incidente.strip(),
            lesiones=lesiones.strip(),
            rutinaria=rutinaria,
            control=control.strip(),
            categorias=list(categorias),
            frecuencia=frecuencia,
            responsable=responsable,
            p=p,
            c=c,
            p_res=p_res,
            c_res=c_res,
        )

        if editando:
            actualizar(d["id"], nueva)
            st.toast("Registro actualizado correctamente.", icon="✅")
        else:
            agregar(nueva)
            st.toast("Peligro agregado a la matriz.", icon="✅")

        st.session_state["editando_id"] = None
        st.session_state["form_version"] += 1
        st.rerun()
