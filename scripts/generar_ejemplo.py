"""Genera un Excel de ejemplo con los datos demo, sin abrir Streamlit.

Uso:
    python scripts/generar_ejemplo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from iper.config import META_POR_DEFECTO  # noqa: E402
from iper.demo_data import filas_demo  # noqa: E402
from iper.excel_export import construir_libro, nombre_archivo  # noqa: E402


def main() -> None:
    salida = RAIZ / "salida"
    salida.mkdir(exist_ok=True)
    meta = dict(META_POR_DEFECTO)
    destino = salida / nombre_archivo(meta)
    destino.write_bytes(construir_libro(filas_demo(), meta))
    print(f"Archivo generado: {destino}")


if __name__ == "__main__":
    main()
