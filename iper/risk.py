"""Cálculos de la metodología MIPER (magnitud y clasificación del riesgo)."""

from __future__ import annotations

from .config import ESCALA_CONSECUENCIA, ESCALA_PROBABILIDAD, NivelRiesgo, obtener_nivel

VALORES_P: tuple[int, ...] = tuple(item["valor"] for item in ESCALA_PROBABILIDAD)
VALORES_C: tuple[int, ...] = tuple(item["valor"] for item in ESCALA_CONSECUENCIA)


def calcular_mr(probabilidad: int, consecuencia: int) -> int:
    """Magnitud del riesgo = Probabilidad × Consecuencia.

    >>> calcular_mr(4, 8)
    32
    """
    return int(probabilidad) * int(consecuencia)


def clasificar(mr: int) -> NivelRiesgo:
    """Clasifica la magnitud del riesgo en Crítico / Moderado / Aceptable."""
    return obtener_nivel(mr)


def evaluar(probabilidad: int, consecuencia: int) -> tuple[int, NivelRiesgo]:
    """Atajo que devuelve (magnitud, nivel) para un par P/C."""
    mr = calcular_mr(probabilidad, consecuencia)
    return mr, clasificar(mr)


def residual_empeora(
    p: int, c: int, p_res: int, c_res: int
) -> bool:
    """Indica si el riesgo residual quedó por sobre el riesgo inherente.

    Un control operacional nunca debería aumentar el riesgo: si esto ocurre,
    la app lo advierte para evitar errores de digitación.
    """
    return calcular_mr(p_res, c_res) > calcular_mr(p, c)


def validar_valores(probabilidad: int, consecuencia: int) -> bool:
    """Verifica que P y C pertenezcan a la escala metodológica (1, 2, 4, 8)."""
    return probabilidad in VALORES_P and consecuencia in VALORES_C
