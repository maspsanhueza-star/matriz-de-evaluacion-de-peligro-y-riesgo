"""Modelo de datos de una fila (peligro) de la matriz MIPER."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Iterable

from .config import NivelRiesgo, obtener_nivel
from .risk import calcular_mr


@dataclass
class FilaIPER:
    """Representa un peligro evaluado dentro de una actividad o tarea.

    Los campos ``p``/``c`` corresponden al **riesgo inherente** (antes de
    controles) y ``p_res``/``c_res`` al **riesgo residual** (después de
    implementar las medidas de control).
    """

    tarea: str
    peligro: str
    incidente: str = ""
    lesiones: str = ""
    rutinaria: str = "SI"
    control: str = ""
    categorias: list[str] = field(default_factory=list)
    frecuencia: str = "Siempre"
    responsable: str = ""
    p: int = 1
    c: int = 1
    p_res: int = 1
    c_res: int = 1
    numero: int = 0
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:10])

    # -- propiedades derivadas -------------------------------------------
    @property
    def mr(self) -> int:
        """Magnitud del riesgo inherente (P × C)."""
        return calcular_mr(self.p, self.c)

    @property
    def mr_res(self) -> int:
        """Magnitud del riesgo residual (P × C)."""
        return calcular_mr(self.p_res, self.c_res)

    @property
    def nivel(self) -> NivelRiesgo:
        """Clasificación del riesgo inherente."""
        return obtener_nivel(self.mr)

    @property
    def nivel_res(self) -> NivelRiesgo:
        """Clasificación del riesgo residual."""
        return obtener_nivel(self.mr_res)

    @property
    def categorias_texto(self) -> str:
        """Categorías de control como texto (A, C, E, G...)."""
        return ", ".join(self.categorias)

    @property
    def reduccion(self) -> int:
        """Disminución absoluta de la magnitud del riesgo."""
        return self.mr - self.mr_res

    # -- serialización ----------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        """Convierte la fila en un diccionario serializable a JSON."""
        return asdict(self)

    @classmethod
    def from_dict(cls, datos: dict[str, Any]) -> "FilaIPER":
        """Construye una fila tolerando diccionarios incompletos o heredados."""
        campos_validos = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        limpio = {k: v for k, v in datos.items() if k in campos_validos}
        categorias = limpio.get("categorias") or []
        if isinstance(categorias, str):
            categorias = [c.strip() for c in categorias.replace(";", ",").split(",") if c.strip()]
        limpio["categorias"] = list(categorias)
        return cls(**limpio)


def numerar(filas: Iterable[FilaIPER]) -> list[FilaIPER]:
    """Asigna el número de actividad agrupando por tarea en orden de aparición.

    Igual que en el Excel original: todas las filas de una misma tarea
    comparten el mismo número.
    """
    resultado: list[FilaIPER] = []
    orden: dict[str, int] = {}
    for fila in filas:
        clave = fila.tarea.strip().lower()
        if clave not in orden:
            orden[clave] = len(orden) + 1
        resultado.append(fila)
        fila.numero = orden[clave]
    return resultado
