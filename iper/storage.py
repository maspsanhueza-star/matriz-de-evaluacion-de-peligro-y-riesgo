"""Persistencia de la matriz (sesión de Streamlit + respaldo en disco).

La fuente de verdad es ``st.session_state``. Además se guarda una copia JSON en
``data/sesion_iper.json`` para no perder el trabajo al recargar la página
(en Streamlit Cloud el disco es efímero: allí el respaldo es solo temporal).
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import streamlit as st

from .config import META_POR_DEFECTO
from .demo_data import filas_demo
from .models import FilaIPER, numerar

_K_FILAS = "iper_filas"
_K_META = "iper_meta"
_K_CARGADO = "iper_cargado"

RUTA_DATOS = Path(__file__).resolve().parent.parent / "data" / "sesion_iper.json"


# ---------------------------------------------------------------------------
# Inicialización
# ---------------------------------------------------------------------------


def inicializar() -> None:
    """Crea el estado base de la aplicación la primera vez que se ejecuta."""
    if _K_FILAS not in st.session_state:
        filas, meta = _leer_disco()
        st.session_state[_K_FILAS] = filas
        st.session_state[_K_META] = meta or dict(META_POR_DEFECTO)
    if _K_META not in st.session_state:
        st.session_state[_K_META] = dict(META_POR_DEFECTO)
    st.session_state.setdefault("form_version", 1)
    st.session_state.setdefault("editando_id", None)


# ---------------------------------------------------------------------------
# Lectura / escritura
# ---------------------------------------------------------------------------


def filas() -> list[FilaIPER]:
    """Filas actuales de la matriz, numeradas por actividad."""
    return numerar(st.session_state[_K_FILAS])


def meta() -> dict[str, str]:
    """Metadatos del encabezado (obra, contrato, código, revisión...)."""
    return st.session_state[_K_META]


def guardar_meta(datos: dict[str, str]) -> None:
    """Reemplaza los metadatos del encabezado y persiste."""
    st.session_state[_K_META] = {**META_POR_DEFECTO, **datos}
    _guardar_disco()


def agregar(fila: FilaIPER) -> None:
    """Añade un peligro al final de la matriz."""
    st.session_state[_K_FILAS].append(fila)
    _guardar_disco()


def actualizar(fila_id: str, fila: FilaIPER) -> None:
    """Reemplaza una fila existente conservando su posición."""
    actuales: list[FilaIPER] = st.session_state[_K_FILAS]
    for i, existente in enumerate(actuales):
        if existente.id == fila_id:
            fila.id = fila_id
            actuales[i] = fila
            break
    _guardar_disco()


def eliminar(fila_id: str) -> None:
    """Elimina un peligro por su identificador."""
    st.session_state[_K_FILAS] = [
        f for f in st.session_state[_K_FILAS] if f.id != fila_id
    ]
    _guardar_disco()


def duplicar(fila_id: str) -> None:
    """Duplica una fila justo después de la original (nuevo id)."""
    actuales: list[FilaIPER] = st.session_state[_K_FILAS]
    for i, existente in enumerate(actuales):
        if existente.id == fila_id:
            copia = FilaIPER.from_dict(existente.to_dict())
            copia.id = uuid.uuid4().hex[:10]
            actuales.insert(i + 1, copia)
            break
    _guardar_disco()


def mover(fila_id: str, direccion: int) -> None:
    """Mueve una fila una posición arriba (-1) o abajo (+1)."""
    actuales: list[FilaIPER] = st.session_state[_K_FILAS]
    for i, existente in enumerate(actuales):
        if existente.id == fila_id:
            destino = i + direccion
            if 0 <= destino < len(actuales):
                actuales.insert(destino, actuales.pop(i))
            break
    _guardar_disco()


def cargar_demo() -> None:
    """Reemplaza la matriz con los 15 peligros del Excel de ejemplo."""
    st.session_state[_K_FILAS] = filas_demo()
    _guardar_disco()


def limpiar() -> None:
    """Vacía la matriz manteniendo los metadatos del encabezado."""
    st.session_state[_K_FILAS] = []
    st.session_state["editando_id"] = None
    st.session_state["form_version"] += 1
    _guardar_disco()


def reemplazar_todo(nuevas: list[FilaIPER]) -> None:
    """Sustituye la matriz completa (usado al importar un respaldo JSON)."""
    st.session_state[_K_FILAS] = nuevas
    _guardar_disco()


# ---------------------------------------------------------------------------
# Respaldo en disco
# ---------------------------------------------------------------------------


def _guardar_disco() -> None:
    """Escribe el respaldo JSON; falla en silencio si el disco no es escribible."""
    try:
        RUTA_DATOS.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {
            "meta": st.session_state.get(_K_META, {}),
            "filas": [f.to_dict() for f in st.session_state.get(_K_FILAS, [])],
        }
        RUTA_DATOS.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError:  # pragma: no cover - entorno de solo lectura
        pass


def _leer_disco() -> tuple[list[FilaIPER], dict[str, str] | None]:
    """Recupera el respaldo JSON si existe y es válido."""
    if not RUTA_DATOS.exists():
        return [], None
    try:
        payload = json.loads(RUTA_DATOS.read_text(encoding="utf-8"))
        filas_json = payload.get("filas", [])
        return [FilaIPER.from_dict(f) for f in filas_json], payload.get("meta")
    except (OSError, ValueError, TypeError):  # pragma: no cover
        return [], None


def exportar_json() -> bytes:
    """Respaldo completo (metadatos + filas) para descargar como .json."""
    payload = {
        "meta": meta(),
        "filas": [f.to_dict() for f in filas()],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def importar_json(contenido: bytes) -> int:
    """Carga un respaldo descargado previamente. Devuelve el n.º de filas."""
    payload = json.loads(contenido.decode("utf-8"))
    nuevas = [FilaIPER.from_dict(f) for f in payload.get("filas", [])]
    reemplazar_todo(nuevas)
    if payload.get("meta"):
        guardar_meta(payload["meta"])
    return len(nuevas)
