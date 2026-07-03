"""Configuración de prensas disponibles con pisos."""

# Prensas con dos pisos cada una
PRENSAS = {
    "P1-1": {"prensa": "P1", "piso": 1, "dim_x": 1200, "dim_y": 600, "costo_hora": 50},
    "P1-2": {"prensa": "P1", "piso": 2, "dim_x": 1200, "dim_y": 600, "costo_hora": 50},
    "P2-1": {"prensa": "P2", "piso": 1, "dim_x": 1200, "dim_y": 600, "costo_hora": 50},
    "P2-2": {"prensa": "P2", "piso": 2, "dim_x": 1200, "dim_y": 600, "costo_hora": 50},
    "P5-1": {"prensa": "P5", "piso": 1, "dim_x": 1500, "dim_y": 600, "costo_hora": 60},
    "P5-2": {"prensa": "P5", "piso": 2, "dim_x": 1500, "dim_y": 600, "costo_hora": 60},
    "P6-1": {"prensa": "P6", "piso": 1, "dim_x": 1800, "dim_y": 800, "costo_hora": 75},
    "P6-2": {"prensa": "P6", "piso": 2, "dim_x": 1800, "dim_y": 800, "costo_hora": 75},
    "P7-1": {"prensa": "P7", "piso": 1, "dim_x": 2000, "dim_y": 2000, "costo_hora": 100},
    "P7-2": {"prensa": "P7", "piso": 2, "dim_x": 2000, "dim_y": 2000, "costo_hora": 100},
}

# Máscaras de prensas (para mostrar en UI sin pisos)
PRENSAS_BASE = {
    "P1": {"dim_x": 1200, "dim_y": 600, "costo_hora": 50},
    "P2": {"dim_x": 1200, "dim_y": 600, "costo_hora": 50},
    "P5": {"dim_x": 1500, "dim_y": 600, "costo_hora": 60},
    "P6": {"dim_x": 1800, "dim_y": 800, "costo_hora": 75},
    "P7": {"dim_x": 2000, "dim_y": 2000, "costo_hora": 100}
}

# Restricciones
MAX_DIFERENCIA_TIEMPO = 0.50  # 50% máximo de diferencia de tiempo
MAX_DIFERENCIA_PRESION = 20    # 20 PSI máximo de diferencia de presión

# Geometrías restringidas: orden_id => lista de prensas permitidas
# Si una orden tiene geometría restringida, solo puede ir en las prensas especificadas
GEOGRAFIAS_RESTRINGIDAS = {}


def es_prensa_compatible(prensa_id: str, dim_x: int, dim_y: int, orden_id: str = None) -> bool:
    """Verifica si un piso de prensa puede procesar una orden según sus dimensiones."""
    if prensa_id not in PRENSAS:
        return False
    prensa = PRENSAS[prensa_id]
    compatible_dim = dim_x <= prensa["dim_x"] and dim_y <= prensa["dim_y"]

    # Verificar restricción geométrica
    if orden_id and orden_id in GEOGRAFIAS_RESTRINGIDAS:
        prensas_permitidas = GEOGRAFIAS_RESTRINGIDAS[orden_id]
        prensa_base = PRENSAS[prensa_id]["prensa"]
        if prensa_base not in prensas_permitidas:
            return False

    return compatible_dim


def obtener_pisos_compatibles(dim_x: int, dim_y: int, orden_id: str = None) -> list:
    """Retorna lista de pisos compatibles ordenados por costo (menor a mayor)."""
    compatibles = []
    for pid, p in PRENSAS.items():
        if es_prensa_compatible(pid, dim_x, dim_y, orden_id):
            compatibles.append((pid, p))
    return sorted(compatibles, key=lambda x: x[1]["costo_hora"])


def verificar_compatibilidad_pisos(tiempo1: float, tiempo2: float,
                                    presion1: float, presion2: float) -> tuple:
    """
    Verifica si dos órdenes pueden procesarse simultáneamente en los pisos de una prensa.

    Returns:
        (es_compatible, motivo_incompatibilidad)
    """
    if tiempo1 is None or tiempo2 is None:
        return True, None

    # Verificar diferencia de tiempo (máximo 50% del menor)
    tiempo_menor = min(tiempo1, tiempo2)
    tiempo_mayor = max(tiempo1, tiempo2)
    diferencia_tiempo = (tiempo_mayor - tiempo_menor) / tiempo_menor if tiempo_menor > 0 else 0

    if diferencia_tiempo > MAX_DIFERENCIA_TIEMPO:
        return False, f"Diferencia de tiempo {diferencia_tiempo*100:.1f}% excede el máximo {MAX_DIFERENCIA_TIEMPO*100}%"

    # Verificar diferencia de presión
    if presion1 is not None and presion2 is not None:
        diferencia_presion = abs(presion1 - presion2)
        if diferencia_presion > MAX_DIFERENCIA_PRESION:
            return False, f"Diferencia de presión {diferencia_presion:.1f} PSI excede el máximo {MAX_DIFERENCIA_PRESION} PSI"

    return True, None


def obtener_prensa_base(piso_id: str) -> str:
    """Obtiene el identificador base de la prensa (sin piso)."""
    if piso_id in PRENSAS:
        return PRENSAS[piso_id]["prensa"]
    return piso_id.split("-")[0] if "-" in piso_id else piso_id


def obtener_piso_complementario(piso_id: str) -> str:
    """Obtiene el ID del otro piso de la misma prensa."""
    prensa_base = obtener_prensa_base(piso_id)
    piso_num = PRENSAS[piso_id]["piso"]
    otro_piso = 2 if piso_num == 1 else 1
    return f"{prensa_base}-{otro_piso}"
