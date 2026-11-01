"""Datos de ejemplo basados en el Excel de referencia v4 (techumbres).

Permiten probar la aplicación sin digitar: ``Cargar datos de ejemplo`` en la
barra lateral reconstruye la matriz de 8 actividades y 15 peligros.
"""

from __future__ import annotations

from .models import FilaIPER

_DEMO: tuple[dict, ...] = (
    {
        "tarea": "Inspección previa de techumbres y acceso a cubierta",
        "rutinaria": "SI",
        "peligro": "Estructuras o planchas deterioradas, traslúcidas o frágiles",
        "incidente": "Caída de altura por colapso / ruptura de cubierta",
        "lesiones": "Traumatismo craneoencefálico, fracturas múltiples, muerte",
        "control": (
            "• C1: Instalación de escalas mecánicas y pasarelas sobre techumbre.\n"
            "• D1: Señalización de tragaluces y planchas frágiles.\n"
            "• E1: Procedimiento de Trabajo Seguro (PTS) en techumbres.\n"
            "• F1: Cumplimiento OGUC Art. 4.1.10 y NCh 1258.\n"
            "• G1: Uso obligatorio de Sistema Personal de Detención de Caídas (SPDC) "
            "enganchado a línea de vida."
        ),
        "categorias": ["C", "D", "E", "F", "G"],
        "frecuencia": "Diario",
        "responsable": "Supervisor / Prevencionista / Trabajador",
        "p": 4,
        "c": 8,
        "p_res": 2,
        "c_res": 4,
    },
    {
        "tarea": "Inspección previa de techumbres y acceso a cubierta",
        "rutinaria": "SI",
        "peligro": "Escalas de acceso inestables, defectuosas o mal afianzadas",
        "incidente": "Caída a distinto nivel durante el ascenso / descenso",
        "lesiones": "Fracturas de extremidades, contusiones graves, muerte",
        "control": (
            "• C1: Fijación y amarrado rígido de escala en punto superior e inferior "
            "(1 m sobre desembarque).\n"
            "• E1: Lista de chequeo previa de escalas de mano/extensión.\n"
            "• F1: Cumplimiento DS 594 Art. 7 y 8 sobre vías de acceso seguras.\n"
            "• G1: Uso de calzado de seguridad antideslizante y EPP de altura."
        ),
        "categorias": ["C", "E", "F", "G"],
        "frecuencia": "Siempre",
        "responsable": "Capataz / Trabajador",
        "p": 4,
        "c": 8,
        "p_res": 2,
        "c_res": 4,
    },
    {
        "tarea": "Montaje, reparación y desplazamiento sobre techumbre",
        "rutinaria": "SI",
        "peligro": "Bordes libres sin protección perimetral o aberturas expuestas",
        "incidente": "Caída a distinto nivel (al exterior o patio interior)",
        "lesiones": "Politraumatismo, fracturas, incapacidad permanente, muerte",
        "control": (
            "• C1: Barandillas perimetrales rígidas o mallas de seguridad anticaídas.\n"
            "• C2: Líneas de vida horizontales certificadas.\n"
            "• E1: Examen de salud compatible para trabajos en altura.\n"
            "• F1: Cumplimiento NCh 1258 y DS 40 / DS 594.\n"
            "• G1: Arnés de cuerpo entero de doble cabo con mosquetón de 110 mm."
        ),
        "categorias": ["C", "E", "F", "G"],
        "frecuencia": "Siempre",
        "responsable": "Jefe de Terreno / Prevencionista / Supervisor",
        "p": 4,
        "c": 8,
        "p_res": 2,
        "c_res": 4,
    },
    {
        "tarea": "Montaje, reparación y desplazamiento sobre techumbre",
        "rutinaria": "SI",
        "peligro": "Acopio o manipulación inestable de planchas, tejas y herramientas",
        "incidente": "Caída de objetos / materiales a niveles inferiores",
        "lesiones": "Golpes, fracturas, traumatismo craneal en terceros",
        "control": (
            "• D1: Delimitación y cierre perimetral de la zona inferior con letreros.\n"
            "• E1: Prohibición de acopio excesivo en pendientes.\n"
            "• F1: Cumplimiento OGUC Art. 5.8.3 en medidas de protección a la vía "
            "pública y predios vecinos.\n"
            "• G1: Casco de seguridad con barbiquejo obligatorio de 3 o 4 puntos."
        ),
        "categorias": ["D", "E", "F", "G"],
        "frecuencia": "Siempre",
        "responsable": "Capataz / Trabajador",
        "p": 4,
        "c": 8,
        "p_res": 2,
        "c_res": 2,
    },
    {
        "tarea": "Instalación de aislamiento térmico, barreras de vapor y ventilación",
        "rutinaria": "SI",
        "peligro": "Exposición a fibras minerales (lana de vidrio/roca) y solventes de sellado",
        "incidente": "Inhalación de fibras y contacto dérmico con solventes",
        "lesiones": "Irritación respiratoria, dermatitis, alergias oculares",
        "control": (
            "• C1: Ventilación cruzada continua en entretechos y mansardas.\n"
            "• E1: Estándar de instalación de aislación térmica/acústica según OGUC "
            "Art. 4.1.10.\n"
            "• F1: Cumplimiento DS 594 Art. 65 (límites permisibles de polvo y fibras "
            "respirables).\n"
            "• G1: Respirador N95/P100, mazo/manga larga y antiparras herméticas."
        ),
        "categorias": ["C", "E", "F", "G"],
        "frecuencia": "Siempre",
        "responsable": "Capataz / Trabajador",
        "p": 4,
        "c": 4,
        "p_res": 2,
        "c_res": 2,
    },
    {
        "tarea": "Instalación de aislamiento térmico, barreras de vapor y ventilación",
        "rutinaria": "SI",
        "peligro": (
            "Manipulación de barreras de humedad, fijaciones y tijerales en espacio "
            "confinado de entretecho"
        ),
        "incidente": "Golpe contra estructura, atrapamiento y estrés térmico",
        "lesiones": "Golpes en cabeza, atrapamiento, sofocación térmica",
        "control": (
            "• C1: Iluminación LED portátil de baja tensión (12V/24V) en entretechos.\n"
            "• E1: Procedimiento de trabajo en espacios reducidos y climatización "
            "habitable.\n"
            "• F1: Cumplimiento OGUC Art. 4.1.10 en ventilación de entretechos para "
            "evitar condensación.\n"
            "• G1: Casco de seguridad tipo jockey de bajo perfil con barbiquejo."
        ),
        "categorias": ["C", "E", "F", "G"],
        "frecuencia": "Siempre",
        "responsable": "Capataz / Supervisor",
        "p": 4,
        "c": 4,
        "p_res": 2,
        "c_res": 2,
    },
    {
        "tarea": "Izamiento y traslado manual/mecánico de materiales",
        "rutinaria": "SI",
        "peligro": "Manipulación de planchas metálicas, tejas o perfiles con bordes filosos",
        "incidente": "Corte o laceración durante la manipulación",
        "lesiones": "Cortes, laceraciones o heridas en extremidades superiores",
        "control": (
            "• E1: Charla de 5 minutos sobre manipulación segura de cargas cortantes.\n"
            "• E2: Trabajo coordinado en parejas para izamiento.\n"
            "• F1: Cumplimiento Ley 16.744 sobre prevención de accidentes del trabajo.\n"
            "• G1: Uso obligatorio de guantes de cabritilla o anticorte nivel 5."
        ),
        "categorias": ["E", "F", "G"],
        "frecuencia": "Siempre",
        "responsable": "Capataz / Trabajador",
        "p": 4,
        "c": 4,
        "p_res": 2,
        "c_res": 2,
    },
    {
        "tarea": "Izamiento y traslado manual/mecánico de materiales",
        "rutinaria": "SI",
        "peligro": "Levantamiento de cargas pesadas o posturas forzadas en pendiente",
        "incidente": "Sobreesfuerzo por manejo manual de cargas",
        "lesiones": "Lumbago, lesiones musculoesqueléticas, hernia discal",
        "control": (
            "• A1: Uso de camión pluma, huinche o aparejo mecánico para izamiento.\n"
            "• F1: Cumplimiento Ley 20.001 y DFL 1 Código del Trabajo (máx. 25 kg).\n"
            "• E1: Pausas activas y rotación periódica del personal."
        ),
        "categorias": ["A", "E", "F"],
        "frecuencia": "Siempre",
        "responsable": "Supervisor / Capataz",
        "p": 4,
        "c": 4,
        "p_res": 2,
        "c_res": 2,
    },
    {
        "tarea": "Trabajos de hojalatería, corte y fijación de cubiertas",
        "rutinaria": "SI",
        "peligro": "Uso de esmeril angular o cortadora de metal para remates de cubierta",
        "incidente": "Proyección de partículas incandescentes y contacto con disco",
        "lesiones": "Heridas oculares, quemaduras, amputaciones",
        "control": (
            "• C1: Guardas de protección instaladas y operativas en esmeril.\n"
            "• E1: Procedimiento de uso seguro de herramientas de corte.\n"
            "• F1: Cumplimiento DS 594 sobre protección de maquinaria e higiene "
            "industrial.\n"
            "• G1: Careta facial transparente + lentes de seguridad con protección "
            "lateral."
        ),
        "categorias": ["C", "E", "F", "G"],
        "frecuencia": "Diario",
        "responsable": "Capataz / Trabajador",
        "p": 4,
        "c": 8,
        "p_res": 2,
        "c_res": 4,
    },
    {
        "tarea": "Trabajos de hojalatería, corte y fijación de cubiertas",
        "rutinaria": "SI",
        "peligro": "Extensión eléctrica defectuosa, sin tierra o expuesta a la intemperie",
        "incidente": "Contacto eléctrico indirecto",
        "lesiones": "Electrocución, fibrilación ventricular, quemaduras",
        "control": (
            "• C1: Tableros de faena provisorios con interruptores diferenciales y "
            "protecciones magnetotérmicas.\n"
            "• E1: Inspección de extensiones de uso industrial resistente al agua.\n"
            "• F1: Cumplimiento normativa RIC N° 06 y DS 594.\n"
            "• G1: Calzado dieléctrico de seguridad."
        ),
        "categorias": ["C", "E", "F", "G"],
        "frecuencia": "Siempre",
        "responsable": "Electricista de Obra / Capataz",
        "p": 4,
        "c": 8,
        "p_res": 1,
        "c_res": 8,
    },
    {
        "tarea": "Sellado e impermeabilización de cubiertas (termofusión / solventes)",
        "rutinaria": "NO",
        "peligro": "Uso de soplete a gas licuado para instalación de membranas asfálticas",
        "incidente": "Incendio y quemaduras por llama abierta",
        "lesiones": "Quemaduras de 2° y 3° grado, intoxicación por humo",
        "control": (
            "• D1: Mantener extintor PQS de 10 kg operativo y certificado en el área "
            "de trabajo.\n"
            "• E1: Tramitación de Permiso de Trabajo en Caliente (Hot Work Permit).\n"
            "• F1: Cumplimiento OGUC Art. 4.3.3 (resistencia al fuego de techumbres) y "
            "DS 594 Art. 44-48.\n"
            "• G1: Ropa de trabajo ignífuga/algodón, coleto de cuero y guantes "
            "mosquetero."
        ),
        "categorias": ["D", "E", "F", "G"],
        "frecuencia": "Por tarea",
        "responsable": "Prevencionista / Supervisor",
        "p": 4,
        "c": 8,
        "p_res": 2,
        "c_res": 4,
    },
    {
        "tarea": "Sellado e impermeabilización de cubiertas (termofusión / solventes)",
        "rutinaria": "NO",
        "peligro": "Exposición a vapores orgánicos de sellantes, adhesivos o imprimantes",
        "incidente": "Inhalación de vapores orgánicos",
        "lesiones": "Intoxicación, mareos, cefalea, daño hepático",
        "control": (
            "• E1: Disponer de Hojas de Datos de Seguridad (HDS) en terreno.\n"
            "• E2: Aplicación en áreas con ventilación natural adecuada.\n"
            "• F1: Cumplimiento DS 594 Art. 66 (límites de tolerancia biológica a "
            "solventes).\n"
            "• G1: Respirador de doble vía con filtros para vapores orgánicos."
        ),
        "categorias": ["E", "F", "G"],
        "frecuencia": "Por tarea",
        "responsable": "Capataz / Trabajador",
        "p": 4,
        "c": 4,
        "p_res": 2,
        "c_res": 2,
    },
    {
        "tarea": "Exposición a factores ambientales y meteorológicos",
        "rutinaria": "SI",
        "peligro": "Exposición a radiación solar directa sobre techumbre",
        "incidente": "Exposición prolongada a radiación ultravioleta",
        "lesiones": "Eritema solar, golpe de calor, deshidratación, cáncer de piel",
        "control": (
            "• D1: Publicación diaria del índice UV en pizarra de faena.\n"
            "• E1: Cumplimiento de protocolo MINSAL RUV (DS 594 Art. 109a).\n"
            "• E2: Disposición de dispensadores de agua potable fresca.\n"
            "• G1: Bloqueador solar FPS 50+, legionario, lentes UV y manga larga."
        ),
        "categorias": ["D", "E", "F", "G"],
        "frecuencia": "Diario",
        "responsable": "Prevencionista / Capataz",
        "p": 8,
        "c": 4,
        "p_res": 2,
        "c_res": 4,
    },
    {
        "tarea": "Exposición a factores ambientales y meteorológicos",
        "rutinaria": "NO",
        "peligro": "Vientos fuertes (≥ 30 km/h) o lluvias / cubiertas mojadas y resbaladizas",
        "incidente": "Pérdida de equilibrio y voladura de planchas",
        "lesiones": "Caída de altura, fracturas, muerte",
        "control": (
            "• E1: Suspensión inmediata de trabajos en techumbre ante vientos "
            "superiores a 30 km/h o presencia de lluvias.\n"
            "• F1: Cumplimiento OGUC y DS 594 en seguridad de faenas climáticas.\n"
            "• G1: Traje impermeable en caso de evacuación o trabajos de emergencia."
        ),
        "categorias": ["E", "F", "G"],
        "frecuencia": "Eventual",
        "responsable": "Jefe de Terreno / Prevencionista",
        "p": 4,
        "c": 8,
        "p_res": 1,
        "c_res": 8,
    },
    {
        "tarea": "Emergencias, sismos y evacuación desde la cubierta",
        "rutinaria": "NO",
        "peligro": "Ocurrencia de sismo, incendio o accidente grave sobre la techumbre",
        "incidente": "Evento de emergencia con trabajadores en altura",
        "lesiones": "Atrapamiento, caída por pánico, politraumatismo, muerte",
        "control": (
            "• D1: Señalización de vías de evacuación y Puntos de Encuentro de "
            "Emergencia (PEE).\n"
            "• E1: Plan de Rescate en Altura específico para techumbres y brigada de "
            "emergencia.\n"
            "• F1: Cumplimiento DS 594 Art. 37, 42 y OGUC Capítulo 3 sobre protección "
            "contra incendios.\n"
            "• G1: Equipamiento de rescate operacional (camilla rígida de rescate, "
            "cuerdas, poleas)."
        ),
        "categorias": ["D", "E", "F", "G"],
        "frecuencia": "Por proyecto",
        "responsable": "Prevencionista / Comité Paritario",
        "p": 4,
        "c": 8,
        "p_res": 2,
        "c_res": 4,
    },
)


def filas_demo() -> list[FilaIPER]:
    """Devuelve una copia nueva de las filas de ejemplo (nunca la misma lista)."""
    return [FilaIPER.from_dict(dict(item)) for item in _DEMO]
