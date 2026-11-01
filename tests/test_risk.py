"""Pruebas unitarias de la metodología MIPER (sin dependencias de Streamlit)."""

from __future__ import annotations

import pytest

from iper.config import NIVELES_RIESGO, obtener_nivel
from iper.models import FilaIPER, numerar
from iper.risk import calcular_mr, clasificar, evaluar, residual_empeora, validar_valores


@pytest.mark.parametrize(
    "p,c,esperado",
    [
        (1, 1, 1),
        (1, 8, 8),
        (2, 4, 8),
        (4, 4, 16),
        (4, 8, 32),
        (8, 8, 64),
    ],
)
def test_magnitud(p: int, c: int, esperado: int) -> None:
    assert calcular_mr(p, c) == esperado


@pytest.mark.parametrize(
    "mr,clave",
    [
        (1, "aceptable"),
        (2, "aceptable"),
        (4, "aceptable"),
        (7, "aceptable"),
        (8, "moderado"),
        (16, "moderado"),
        (23, "moderado"),
        (24, "critico"),
        (32, "critico"),
        (64, "critico"),
    ],
)
def test_clasificacion(mr: int, clave: str) -> None:
    assert clasificar(mr).clave == clave


def test_clasificacion_cubre_toda_la_escala() -> None:
    """Todo MR posible (P×C) debe tener exactamente una clasificación."""
    posibles = {p * c for p in (1, 2, 4, 8) for c in (1, 2, 4, 8)}
    for mr in posibles:
        niveles = [n for n in NIVELES_RIESGO if n.mr_min <= mr <= n.mr_max]
        assert len(niveles) == 1, f"MR={mr} tiene {len(niveles)} clasificaciones"


def test_formato_etiquetas() -> None:
    mr, nivel = evaluar(4, 8)
    assert mr == 32
    assert "Crítico" in nivel.etiqueta


def test_residual_no_debe_empeorar() -> None:
    assert residual_empeora(4, 8, 2, 4) is False
    assert residual_empeora(2, 4, 4, 8) is True


def test_validar_valores_de_escala() -> None:
    assert validar_valores(1, 8) is True
    assert validar_valores(3, 4) is False


def test_fila_calcula_magnitudes() -> None:
    fila = FilaIPER(tarea="Techumbre", peligro="Caída de altura", p=4, c=8, p_res=2, c_res=4)
    assert fila.mr == 32
    assert fila.mr_res == 8
    assert fila.nivel.clave == "critico"
    assert fila.nivel_res.clave == "moderado"
    assert fila.reduccion == 24


def test_fila_serializa_y_recupera() -> None:
    original = FilaIPER(
        tarea="Tarea",
        peligro="Peligro",
        categorias=["C", "G"],
        p=2,
        c=4,
    )
    copia = FilaIPER.from_dict(original.to_dict())
    assert copia.to_dict() == original.to_dict()


def test_numerar_agrupa_por_tarea() -> None:
    filas = [
        FilaIPER(tarea="A", peligro="p1"),
        FilaIPER(tarea="B", peligro="p2"),
        FilaIPER(tarea="A", peligro="p3"),
        FilaIPER(tarea="C", peligro="p4"),
    ]
    numeradas = numerar(filas)
    assert [f.numero for f in numeradas] == [1, 2, 1, 3]


def test_datos_demo_coherentes() -> None:
    from iper.demo_data import filas_demo

    filas = filas_demo()
    assert len(filas) == 15
    for fila in filas:
        assert validar_valores(fila.p, fila.c)
        assert fila.mr_res <= fila.mr, f"El residual empeora en: {fila.peligro}"
        assert fila.categorias, "Toda fila de ejemplo debe tener controles"
