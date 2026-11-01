# MIPER — Matriz de Identificación de Peligros y Evaluación de Riesgos

Aplicación web interactiva en **Python + Streamlit + Pandas** para construir la
**Matriz de Identificación de Peligros y Evaluación de Riesgos (MIPER/IPER)** de
una faena y exportarla a **Excel (.xlsx)** con formato condicional por criticidad.

Desarrollada para el contexto normativo chileno: **Ley 16.744**, **D.S. N° 40**,
**D.S. N° 44**, **D.S. N° 594**, **NCh 1258** y **OGUC Art. 4.1.10**.

El formato de salida replica el libro de referencia
`MATRIZ_DE_RIESGO_TECHUMBRES_CON_CRITERIOS_v4.xlsx` (techumbres y habitabilidad).

---

## 1. Características

| Módulo | Qué hace |
|---|---|
| **Registro** | Ingreso de actividad/tarea, peligro, incidente potencial y lesiones o enfermedades profesionales asociadas. Catálogos de apoyo + campos libres. |
| **Evaluación inherente** | Probabilidad (P) y Consecuencia (C) en escala de 4 niveles (1, 2, 4, 8). Cálculo automático de **MR = P × C** y clasificación con semáforo. |
| **Controles** | Jerarquía de prevención A–G (Eliminación → EPP), descripción de medidas, frecuencia y responsable. Reevaluación de **P' y C'** para el **riesgo residual**, con alerta si el residual empeora. |
| **Vista previa** | Tabla interactiva con filtros en tiempo real (texto, clasificación, tarea, solo críticos), métricas y gestión de registros (editar, duplicar, reordenar, eliminar). |
| **Resumen** | KPIs, reducción promedio del riesgo, distribución inherente vs. residual y detector de dependencia excesiva del EPP. |
| **Exportar** | Excel con 3 hojas, colores por criticidad, formato condicional, autofiltro, impresión configurada y respaldo/restauración JSON. |
| **Criterios** | Escalas P y C, semáforo, grilla 4×4 y jerarquía de controles, tal como en la hoja de criterios del Excel original. |

---

## 2. Metodología

La magnitud del riesgo se calcula como:

```
MR = P × C
```

con **P ∈ {1, 2, 4, 8}** y **C ∈ {1, 2, 4, 8}** (escala geométrica de 4 niveles,
idéntica al Excel de referencia), lo que produce magnitudes entre **1 y 64**.

| Clasificación | Rango | Color | Acción |
|---|---|---|---|
| Riesgo Crítico / Elevado | MR ≥ 24 (24–64) | 🔴 Rojo | No iniciar la tarea sin controles inmediatos y PTSA |
| Riesgo Moderado | 8 ≤ MR < 24 (8–16) | 🟡 Ámbar | Controles específicos, AST y supervisión regular |
| Riesgo Aceptable / Leve | MR < 8 (1–4) | 🟢 Verde | Procedimientos estándar y EPP básico |

> **Nota sobre la nomenclatura:** el Excel de referencia usa tres niveles
> (Crítico/Moderado/Aceptable). La aplicación muestra además la equivalencia con
> la nomenclatura de cuatro niveles (**Inaceptable · Alto · Medio · Bajo**), para
> facilitar la homologación con otros instrumentos de la empresa. Los umbrales se
> configuran en un solo lugar: `iper/config.py` → `NIVELES_RIESGO`.

---

## 3. Estructura del proyecto

```
.
├── app.py                     # Punto de entrada Streamlit (navegación y layout)
├── requirements.txt           # Dependencias de ejecución
├── requirements-dev.txt       # Dependencias de pruebas (pytest)
├── .streamlit/config.toml     # Tema visual
├── iper/
│   ├── config.py              # Escalas P/C, clasificación, catálogos, jerarquía, meta
│   ├── models.py              # Dataclass FilaIPER + numeración por actividad
│   ├── risk.py                # Cálculo de MR, clasificación y validaciones
│   ├── storage.py             # Estado de sesión + respaldo JSON en data/
│   ├── demo_data.py           # Los 15 peligros del Excel de ejemplo
│   ├── excel_export.py        # Libro .xlsx con openpyxl (3 hojas + formato)
│   └── ui/
│       ├── formulario.py      # Módulo de ingreso/edición
│       ├── vista_previa.py    # Tabla con filtros y gestión de registros
│       ├── resumen.py         # Indicadores y gráficos
│       ├── exportacion.py     # Encabezado y descargas
│       ├── criterios.py       # Criterios metodológicos y marco legal
│       └── estilos.py         # Tarjetas de riesgo y estilos de tabla
├── tests/
│   ├── test_risk.py           # Metodología y modelo de datos
│   └── test_excel.py          # Exportación openpyxl
└── data/                      # Respaldos locales (excluidos de git)
```

---

## 4. Instalación y ejecución

```bash
# 1. Crear y activar el entorno virtual
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
streamlit run app.py
```

Se abre en `http://localhost:8501`.

### Pruebas

```bash
pip install -r requirements-dev.txt
pytest -q
```

---

## 5. Uso

1. **Cargar datos de ejemplo** (barra lateral) para ver la matriz del Excel
   original, o comenzar en blanco.
2. En **📝 Registro** completa: actividad/tarea, peligro, incidente potencial y
   lesiones. Elige **P** y **C**: la magnitud y la clasificación se calculan al
   instante.
3. Describe los **controles** con su categoría (A–G), frecuencia y responsable;
   luego fija **P' y C'** para obtener el **riesgo residual**. Si el residual
   supera al inherente, la app lo advierte.
4. En **📋 Vista previa** filtra, revisa y administra los registros.
5. En **⬇️ Exportar** ajusta el encabezado del documento (obra, contrato,
   responsable, código, revisión) y descarga el `.xlsx`.

### Contenido del Excel exportado

| Hoja | Contenido |
|---|---|
| **Matriz IPER** | Encabezado corporativo, cabecera agrupada de dos filas, 18 columnas, colores por criticidad inherente y residual, autofiltro, filas repetidas de título al imprimir y bloque de toma de conocimiento con firmas. |
| **Criterios** | Escalas P y C, clasificación con acción requerida, jerarquía de controles A–G y grilla 4×4 coloreada. |
| **Resumen** | Indicadores (total de peligros, MR promedio inherente/residual, % de reducción) y gráfico comparativo. |

El color de las celdas de criticidad se aplica de dos formas: **relleno estático**
para que se vea igual en cualquier visor y **formato condicional de Excel** para
que se actualice si alguien edita la planilla.

---

## 6. Datos y privacidad

* La matriz vive en la sesión de Streamlit y se respalda en
  `data/sesion_iper.json` (ignorado por git).
* El respaldo JSON se puede descargar/restaurar desde **⬇️ Exportar** para mover
  el trabajo entre equipos.
* No se envía información a servicios externos.

---

## 7. Aviso

Herramienta de **apoyo metodológico**. No reemplaza la evaluación de un experto
en prevención de riesgos ni exime al empleador de sus obligaciones legales bajo
la Ley 16.744 y el D.S. N° 44.
