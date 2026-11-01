"""Criterios, catálogos y constantes metodológicas del sistema MIPER.

Metodología
-----------
Matriz de Identificación de Peligros y Evaluación de Riesgos (MIPER / IPER)
con escala de 4 niveles por variable. Los valores numéricos siguen el ejemplo
corporativo ``MATRIZ_DE_RIESGO_TECHUMBRES_CON_CRITERIOS_v4.xlsx``:

    Probabilidad (P)  ∈ {1, 2, 4, 8}
    Consecuencia (C)  ∈ {1, 2, 4, 8}
    Magnitud (MR)     =  P × C   →  1 .. 64

Clasificación (idéntica al Excel de referencia):

    MR ≥ 24        → Riesgo Crítico / Elevado   (Rojo)
    8 ≤ MR < 24    → Riesgo Moderado            (Ámbar / Amarillo)
    MR < 8         → Riesgo Aceptable / Leve    (Verde)

Marco legal de referencia (Chile)
---------------------------------
* Ley 16.744 – Accidentes del trabajo y enfermedades profesionales.
* D.S. N° 40 – Prevención de riesgos profesionales (obligación de informar).
* D.S. N° 44 – Gestión preventiva de los riesgos laborales (vigente 2024).
* D.S. N° 594 – Condiciones sanitarias y ambientales en los lugares de trabajo.
* NCh 1258 / NCh 1411 – Señalización y trabajos en altura.
* OGUC Art. 4.1.10 – Acondicionamiento térmico y habitabilidad.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Escalas de evaluación
# ---------------------------------------------------------------------------

ESCALA_PROBABILIDAD: tuple[dict, ...] = (
    {
        "valor": 1,
        "nivel": "Baja / Rara",
        "alias": "Muy Baja",
        "descripcion": (
            "El hecho ocurre raras veces o casi nunca. Exposición esporádica "
            "o menor a 1 vez al año."
        ),
    },
    {
        "valor": 2,
        "nivel": "Media / Ocasional",
        "alias": "Media",
        "descripcion": (
            "El hecho puede ocurrir en algunas ocasiones. Exposición mensual "
            "o semanal."
        ),
    },
    {
        "valor": 4,
        "nivel": "Alta / Frecuente",
        "alias": "Alta",
        "descripcion": (
            "El hecho ocurre habitualmente. Exposición diaria o continua durante "
            "la jornada."
        ),
    },
    {
        "valor": 8,
        "nivel": "Muy Alta / Continua",
        "alias": "Muy Alta",
        "descripcion": (
            "El hecho ocurre casi con certeza / exposición permanente sin descanso."
        ),
    },
)

ESCALA_CONSECUENCIA: tuple[dict, ...] = (
    {
        "valor": 1,
        "nivel": "Ligeramente Dañino",
        "alias": "Muy Leve",
        "descripcion": (
            "Lesiones superficiales, pequeños cortes, molestias temporales. "
            "Primeros auxilios sin reposo."
        ),
    },
    {
        "valor": 2,
        "nivel": "Dañino",
        "alias": "Leve",
        "descripcion": (
            "Lesiones con incapacidad temporal, torceduras, quemaduras leves, "
            "amonestación o daño material menor."
        ),
    },
    {
        "valor": 4,
        "nivel": "Grave",
        "alias": "Grave",
        "descripcion": (
            "Lesiones graves con incapacidad temporal prolongada, fracturas de "
            "huesos cortos, licencias médicas prolongadas."
        ),
    },
    {
        "valor": 8,
        "nivel": "Muy Grave / Fatal",
        "alias": "Muy Grave / Fatal",
        "descripcion": (
            "Incapacidad permanente (total o parcial), amputaciones, fatalidad "
            "(muerte) o daño estructural masivo."
        ),
    },
)


def etiqueta_probabilidad(valor: int) -> str:
    """Devuelve la etiqueta legible de un valor de probabilidad."""
    for item in ESCALA_PROBABILIDAD:
        if item["valor"] == valor:
            return f"{valor} · {item['nivel']}"
    return str(valor)


def etiqueta_consecuencia(valor: int) -> str:
    """Devuelve la etiqueta legible de un valor de consecuencia."""
    for item in ESCALA_CONSECUENCIA:
        if item["valor"] == valor:
            return f"{valor} · {item['nivel']}"
    return str(valor)


# ---------------------------------------------------------------------------
# Clasificación del riesgo
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NivelRiesgo:
    """Nivel de criticidad con su código de color y acción requerida."""

    clave: str
    etiqueta: str
    alias: str
    rango: str
    mr_min: int
    mr_max: int
    color_fondo: str          # Código HEX sin "#" (formato openpyxl)
    color_texto: str
    accion: str
    orden: int = field(default=0)


NIVELES_RIESGO: tuple[NivelRiesgo, ...] = (
    NivelRiesgo(
        clave="critico",
        etiqueta="Riesgo Crítico / Elevado",
        alias="Inaceptable · Alto",
        rango="MR ≥ 24 (24 a 64)",
        mr_min=24,
        mr_max=64,
        color_fondo="C00000",
        color_texto="FFFFFF",
        accion=(
            "Peligro inminente. No se debe iniciar ni continuar la tarea sin "
            "implementar controles inmediatos. Requiere revisión de la línea de "
            "mando y Permiso de Trabajo Seguro (PTSA)."
        ),
        orden=1,
    ),
    NivelRiesgo(
        clave="moderado",
        etiqueta="Riesgo Moderado",
        alias="Medio",
        rango="8 ≤ MR < 24 (8 a 16)",
        mr_min=8,
        mr_max=23,
        color_fondo="FFC000",
        color_texto="3F2A00",
        accion=(
            "Requiere atención y controles específicos antes de iniciar la tarea. "
            "Se deben aplicar procedimientos, AST, difusión y supervisión regular "
            "en terreno."
        ),
        orden=2,
    ),
    NivelRiesgo(
        clave="aceptable",
        etiqueta="Riesgo Aceptable / Leve",
        alias="Bajo",
        rango="1 ≤ MR < 8 (1 a 4)",
        mr_min=1,
        mr_max=7,
        color_fondo="00B050",
        color_texto="FFFFFF",
        accion=(
            "Riesgo bajo o controlado. La tarea se puede realizar bajo los "
            "procedimientos estándar de la empresa y uso de EPP básico de faena."
        ),
        orden=3,
    ),
)

NIVELES_POR_CLAVE: dict[str, NivelRiesgo] = {n.clave: n for n in NIVELES_RIESGO}

#: Colores suaves para pintar grillas / filas completas en Excel.
COLOR_SUAVE = {
    "critico": "FFC7CE",
    "moderado": "FFEB9C",
    "aceptable": "C6EFCE",
}


def obtener_nivel(mr: int | float) -> NivelRiesgo:
    """Clasifica una magnitud de riesgo según los umbrales del Excel de referencia."""
    mr = int(mr)
    for nivel in NIVELES_RIESGO:
        if nivel.mr_min <= mr <= nivel.mr_max:
            return nivel
    # Resguardo: cualquier valor fuera de rango se trata como el más crítico.
    return NIVELES_RIESGO[0]


# ---------------------------------------------------------------------------
# Jerarquía de controles (Ley 16.744 / DS 44 / ISO 45001)
# ---------------------------------------------------------------------------

CATEGORIAS_CONTROL: tuple[dict, ...] = (
    {
        "codigo": "A",
        "nombre": "Eliminación",
        "descripcion": (
            "Modificar el diseño o proceso para eliminar completamente el peligro "
            "(ej. prefabricar tramos de cubierta en piso)."
        ),
        "efectividad": "Máxima (100%)",
    },
    {
        "codigo": "B",
        "nombre": "Sustitución",
        "descripcion": (
            "Reemplazar un material o equipo peligroso por uno más seguro "
            "(ej. sustituir sellantes tóxicos por ecológicos)."
        ),
        "efectividad": "Alta",
    },
    {
        "codigo": "C",
        "nombre": "Controles de Ingeniería",
        "descripcion": (
            "Rediseño de infraestructura y protecciones físicas colectivas "
            "(ej. redes anticaídas, barandillas perimetrales, pasarelas)."
        ),
        "efectividad": "Alta - Media",
    },
    {
        "codigo": "D",
        "nombre": "Señalización y Advertencias",
        "descripcion": (
            "Avisos visuales, delimitación de zonas de riesgo y barreras "
            "(ej. cintas de peligro, letreros de riesgo en altura)."
        ),
        "efectividad": "Media",
    },
    {
        "codigo": "E",
        "nombre": "Controles Administrativos",
        "descripcion": (
            "Procedimientos de trabajo seguro (PTS), permisos de trabajo en altura "
            "(PTSA), charlas de 5 min y capacitaciones."
        ),
        "efectividad": "Media - Baja",
    },
    {
        "codigo": "F",
        "nombre": "Requisito Legal y Normativo",
        "descripcion": (
            "Cumplimiento obligatorio de normas técnicas y reglamentos "
            "(ej. OGUC Art. 4.1.10, DS 594, Ley 16.744, RIC N° 06)."
        ),
        "efectividad": "Obligatorio",
    },
    {
        "codigo": "G",
        "nombre": "Equipos de Protección Personal (EPP)",
        "descripcion": (
            "Elementos entregados al trabajador para minimizar el daño individual "
            "(ej. arnés de seguridad de doble cabo, casco, guantes)."
        ),
        "efectividad": "Última barrera",
    },
)

CATEGORIAS_POR_CODIGO: dict[str, dict] = {c["codigo"]: c for c in CATEGORIAS_CONTROL}

# ---------------------------------------------------------------------------
# Catálogos de apoyo para el ingreso de datos
# ---------------------------------------------------------------------------

ACTIVIDADES_SUGERIDAS: tuple[str, ...] = (
    "Inspección previa de techumbres y acceso a cubierta",
    "Montaje, reparación y desplazamiento sobre techumbre",
    "Instalación de aislamiento térmico, barreras de vapor y ventilación",
    "Izamiento y traslado manual/mecánico de materiales",
    "Trabajos de hojalatería, corte y fijación de cubiertas",
    "Sellado e impermeabilización de cubiertas (termofusión / solventes)",
    "Exposición a factores ambientales y meteorológicos",
    "Emergencias, sismos y evacuación desde la cubierta",
    "Movimiento de tierras y excavaciones",
    "Trabajos en altura en andamios",
    "Mantención eléctrica y tableros de faena",
    "Operación de maquinaria pesada",
    "Limpieza y orden de faena",
    "Bodega, acopio y manejo de sustancias peligrosas",
)

PELIGROS_SUGERIDOS: tuple[str, ...] = (
    "Ruido (exposición a niveles sobre 85 dB(A))",
    "Manejo manual de cargas (MMC)",
    "Superficies irregulares, resbaladizas o en desnivel",
    "Contacto eléctrico directo / indirecto",
    "Radiación ultravioleta (RUV)",
    "Caída a distinto nivel",
    "Caída de objetos o materiales",
    "Proyección de partículas incandescentes",
    "Atrapamiento por o entre partes móviles",
    "Golpes por o contra objetos",
    "Cortes y laceraciones con bordes filosos",
    "Vapores orgánicos y sustancias químicas",
    "Fibras minerales respirables (lana de vidrio / roca)",
    "Sobreesfuerzo y posturas forzadas",
    "Estrés térmico (calor / frío)",
    "Vibración mano-brazo",
    "Iluminación insuficiente",
    "Espacio confinado / atmósfera deficiente",
    "Incendio y explosión",
    "Sismo y eventos naturales",
    "Riesgo psicosocial (carga mental, turnos)",
    "Riesgo biológico (hongos, bacterias, vectores)",
    "Tránsito vehicular y maquinaria en movimiento",
    "Trabajo aislado o en solitario",
)

FRECUENCIAS: tuple[str, ...] = (
    "Siempre",
    "Diario",
    "Semanal",
    "Mensual",
    "Por tarea",
    "Eventual",
    "Por proyecto",
)

RESPONSABLES_SUGERIDOS: tuple[str, ...] = (
    "Trabajador",
    "Capataz / Trabajador",
    "Supervisor / Capataz",
    "Supervisor / Prevencionista / Trabajador",
    "Jefe de Terreno / Supervisor",
    "Jefe de Terreno / Prevencionista",
    "Prevencionista / Supervisor",
    "Prevencionista / Capataz",
    "Prevencionista / Comité Paritario",
    "Electricista de Obra / Capataz",
    "Administración de Obra",
    "Experto en Prevención de Riesgos",
)

MARCO_NORMATIVO: tuple[str, ...] = (
    "Ley 16.744 – Accidentes del trabajo y enfermedades profesionales",
    "D.S. N° 40 – Prevención de riesgos profesionales",
    "D.S. N° 44 – Gestión preventiva de los riesgos laborales",
    "D.S. N° 594 – Condiciones sanitarias y ambientales",
    "NCh 1258 – Señalización de seguridad",
    "NCh 1411 – Prevención de riesgos en trabajos en altura",
    "OGUC Art. 4.1.10 – Acondicionamiento térmico y habitabilidad",
    "RIC N° 06 – Instalaciones eléctricas de faena",
    "Ley 20.001 – Peso máximo de carga humana",
)

#: Metadatos por defecto del encabezado del registro (editables en la app).
META_POR_DEFECTO: dict[str, str] = {
    "obra": "Obra de Techumbres, Cubiertas y Reacondicionamiento Habitable",
    "contrato": "Montaje, Aislamiento y Mantención de Techumbres",
    "actividad": "Techumbres, Impermeabilización y Acondicionamiento Térmico / Acústico",
    "realizado_por": "Departamento de Prevención de Riesgos",
    "aprobado_por": "Administración de Obra / Jefe de Terreno",
    "marco_normativo": (
        "OGUC Art. 4.1.10 / DS 594 / Ley 16.744 / DS 40 / DS 44 / NCh 1258"
    ),
    "codigo": "SSO-P01/01-MTZ-0002",
    "revision": "C",
}
