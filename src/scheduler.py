"""Módulo de programación de producción para prensas con pisos."""
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from config.prensas import (
    PRENSAS, PRENSAS_BASE, obtener_pisos_compatibles, obtener_prensa_base,
    obtener_piso_complementario, verificar_compatibilidad_pisos,
    MAX_DIFERENCIA_TIEMPO, MAX_DIFERENCIA_PRESION
)


class PisoEstado:
    """Representa el estado de un piso de prensa."""
    def __init__(self, piso_id: str):
        self.piso_id = piso_id
        self.prensa_base = obtener_prensa_base(piso_id)
        self.horarios: List[Tuple[datetime, datetime, str]] = []
        self.orden_actual: Optional[dict] = None

    def disponible_desde(self, fecha_base: datetime) -> datetime:
        """Retorna cuándo está disponible el piso."""
        if not self.horarios:
            return fecha_base
        return max(h[1] for h in self.horarios)

    def agregar_horario(self, inicio: datetime, fin: datetime, orden_id: str):
        """Agrega un horario ocupado al piso."""
        self.horarios.append((inicio, fin, orden_id))


class ProgramadorPrensas:
    """Programador de produccción con lógica de pisos emparejados."""

    def __init__(self, estrategia: str = "menor_costo"):
        self.estrategia = estrategia
        self.pisos: Dict[str, PisoEstado] = {}
        self.asignaciones: List[dict] = []
        self.ciclos_prensa: Dict[str, List[dict]] = {}  # Ciclos por prensa

        for piso_id in PRENSAS.keys():
            self.pisos[piso_id] = PisoEstado(piso_id)

        for prensa in PRENSAS_BASE.keys():
            self.ciclos_prensa[prensa] = []

    def programar_orden(self, orden: dict, fecha_base: datetime) -> Optional[dict]:
        """
        Programa una orden en un piso disponible, buscando emparejamiento si es posible.

        Reglas:
        1. Si hay un ciclo activo en una prensa con un piso libre, intentar emparejar
        2. Si no, buscar un ciclo nuevo donde ambos pisos estén libres
        3. Verificar compatibilidad de tiempo y presión
        """
        dim_x = orden.get("dim_x", 0)
        dim_y = orden.get("dim_y", 0)
        cantidad = orden.get("cantidad", 1)
        tiempo_unitario = orden.get("tiempo_unitario", 0.1)
        presion = orden.get("presion_psi", None)
        tiempo_total = cantidad * tiempo_unitario
        orden_id = orden.get("id")

        pisos_compatibles = obtener_pisos_compatibles(dim_x, dim_y, orden_id)

        if not pisos_compatibles:
            return None

        # Intentar emparejar con un ciclo existente
        resultado = self._intentar_emparejar(
            orden, orden_id, tiempo_total, presion, fecha_base, pisos_compatibles
        )

        if resultado:
            return resultado

        # Si no se puede emparejar, iniciar un ciclo nuevo
        resultado = self._iniciar_ciclo_nuevo(
            orden, orden_id, tiempo_total, presion, fecha_base, pisos_compatibles
        )

        return resultado

    def _intentar_emparejar(self, orden, orden_id, tiempo_total, presion,
                            fecha_base, pisos_compatibles) -> Optional[dict]:
        """Intenta emparejar la orden con un ciclo existente en una prensa."""

        # Agrupar pisos compatibles por prensa
        prensas_con_piso_libre = {}
        for piso_id, piso_info in pisos_compatibles:
            prensa = obtener_prensa_base(piso_id)
            if prensa not in prensas_con_piso_libre:
                prensas_con_piso_libre[prensa] = []
            prensas_con_piso_libre[prensa].append(piso_id)

        # Buscar ciclos activos donde podamos emparejar
        for prensa, pisos in prensas_con_piso_libre.items():
            ciclos = self.ciclos_prensa.get(prensa, [])

            for ciclo in ciclos:
                if ciclo.get("completo", False):
                    continue

                # El ciclo tiene espacio para otra orden
                piso_usado = ciclo["piso_id"]
                otro_piso = obtener_piso_complementario(piso_usado)

                # Verificar que el otro piso esté entre los compatibles
                if otro_piso not in [p[0] for p in pisos_compatibles]:
                    continue

                # Verificar compatibilidad de tiempo y presión
                orden_en_ciclo = ciclo["orden"]
                tiempo_ciclo = orden_en_ciclo.get("tiempo_total", 0)
                presion_ciclo = orden_en_ciclo.get("presion_psi", None)

                es_compat, motivo = verificar_compatibilidad_pisos(
                    tiempo_ciclo, tiempo_total, presion_ciclo, presion
                )

                if not es_compat:
                    continue

                # Emparejar en el ciclo existente
                inicio = ciclo["inicio"]
                tiempo_maximo = max(tiempo_ciclo, tiempo_total)
                fin = inicio + timedelta(hours=tiempo_maximo)

                # Actualizar ciclo
                ciclo["completo"] = True
                ciclo["tiempo_efectivo"] = tiempo_maximo
                ciclo["ordenes"] = ciclo.get("ordenes", []) + [orden_id]

                # Registrar en el piso
                self.pisos[otro_piso].agregar_horario(inicio, fin, orden_id)

                costo_hora = PRENSAS[otro_piso]["costo_hora"]

                asignacion = {
                    "orden_id": orden_id,
                    "prensa_id": prensa,
                    "piso_id": otro_piso,
                    "inicio": inicio,
                    "fin": fin,
                    "tiempo_horas": tiempo_total,
                    "tiempo_prensa": tiempo_maximo,
                    "costo_total": tiempo_maximo * costo_hora,
                    "costo_hora": costo_hora,
                    "emparejado_con": ciclo["orden"]["id"],
                    "presion_psi": presion
                }
                self.asignaciones.append(asignacion)
                return asignacion

        return None

    def _iniciar_ciclo_nuevo(self, orden, orden_id, tiempo_total, presion,
                              fecha_base, pisos_compatibles) -> Optional[dict]:
        """Inicia un ciclo nuevo en una prensa con ambos pisos libres."""

        # Ordenar pisos por estrategia
        if self.estrategia == "menor_costo":
            pisos_ordenados = sorted(pisos_compatibles, key=lambda x: x[1]["costo_hora"])
        else:
            pisos_ordenados = sorted(
                pisos_compatibles,
                key=lambda x: len(self.pisos[x[0]].horarios)
            )

        for piso_id, piso_info in pisos_ordenados:
            prensa = obtener_prensa_base(piso_id)
            otro_piso = obtener_piso_complementario(piso_id)

            inicio = self.pisos[piso_id].disponible_desde(fecha_base)
            inicio_otro = self.pisos[otro_piso].disponible_desde(fecha_base)

            # Buscar un momento donde ambos estén libres
            inicio = max(inicio, inicio_otro)
            fin = inicio + timedelta(hours=tiempo_total)

            # Crear nuevo ciclo
            ciclo = {
                "piso_id": piso_id,
                "inicio": inicio,
                "fin": fin,
                "orden": {
                    "id": orden_id,
                    "tiempo_total": tiempo_total,
                    "presion_psi": presion
                },
                "completo": False,
                "tiempo_efectivo": tiempo_total,
                "ordenes": [orden_id]
            }
            self.ciclos_prensa[prensa].append(ciclo)

            # Registrar horario
            self.pisos[piso_id].agregar_horario(inicio, fin, orden_id)

            costo_hora = piso_info["costo_hora"]

            asignacion = {
                "orden_id": orden_id,
                "prensa_id": prensa,
                "piso_id": piso_id,
                "inicio": inicio,
                "fin": fin,
                "tiempo_horas": tiempo_total,
                "tiempo_prensa": tiempo_total,
                "costo_total": tiempo_total * costo_hora,
                "costo_hora": costo_hora,
                "emparejado_con": None,
                "presion_psi": presion
            }
            self.asignaciones.append(asignacion)
            return asignacion

        return None

    def obtener_asignaciones(self) -> pd.DataFrame:
        """Retorna las asignaciones como DataFrame."""
        return pd.DataFrame(self.asignaciones)


def programar_ordenes(ordenes: pd.DataFrame, estrategia: str = "menor_costo") -> pd.DataFrame:
    """
    Programa todas las órdenes en los pisos de prensas disponibles.

    Args:
        ordenes: DataFrame con las órdenes a programar
        estrategia: Estrategia de asignación ("menor_costo" o "balancear_carga")

    Returns:
        DataFrame con las asignaciones realizadas
    """
    horizon_start = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

    # Agregar columna tiempo_total si no existe
    if "tiempo_total" not in ordenes.columns:
        ordenes = ordenes.copy()
        ordenes["tiempo_total"] = ordenes["cantidad"] * ordenes["tiempo_unitario"]

    # Ordenar por prioridad y luego por tiempo (más largas primero para mejor emparejamiento)
    ordenes_ordenadas = ordenes.sort_values(
        by=["prioridad"] if "prioridad" in ordenes.columns else ["id"],
        ascending=True
    ).sort_values(
        by="tiempo_total",
        ascending=False,
        kind='mergesort'  # Preservar orden de prioridad
    )

    programador = ProgramadorPrensas(estrategia)

    resultados = []
    for _, orden in ordenes_ordenadas.iterrows():
        orden_dict = orden.to_dict()
        asignacion = programador.programar_orden(orden_dict, horizon_start)

        if asignacion:
            resultados.append(asignacion)
        else:
            resultados.append({
                "orden_id": orden_dict.get("id"),
                "prensa_id": None,
                "piso_id": None,
                "inicio": None,
                "fin": None,
                "tiempo_horas": None,
                "tiempo_prensa": None,
                "costo_total": None,
                "costo_hora": None,
                "emparejado_con": None,
                "presion_psi": orden_dict.get("presion_psi"),
                "error": "No hay prensa compatible o restricciones no cumplidas"
            })

    return pd.DataFrame(resultados)


def generar_resumen_carga(asignaciones: pd.DataFrame) -> pd.DataFrame:
    """Genera un resumen de carga por prensa (agregando pisos)."""
    if asignaciones.empty:
        return pd.DataFrame()

    resumen = []
    for prensa_id in PRENSAS_BASE.keys():
        prenss_asign = asignaciones[asignaciones["prensa_id"] == prensa_id]

        if prenss_asign.empty:
            resumen.append({
                "prensa": prensa_id,
                "ordenes": 0,
                "ciclos": 0,
                "horas_prensa": 0,
                "costo_total": 0,
                "pisos_utilizados": 0,
                "utilizacion": 0
            })
        else:
            # Contar ciclos únicos (combinaciones de pisos emparejados)
            ciclos = prenss_asign.groupby(["inicio", "fin"]).first().reset_index()
            horas_prensa = prenss_asign["tiempo_prensa"].sum() if "tiempo_prensa" in prenss_asign.columns else prenss_asign["tiempo_horas"].sum()
            costo = prenss_asign["costo_total"].sum() if "costo_total" in prenss_asign.columns else 0
            pisos_usados = prenss_asign["piso_id"].nunique()

            resumen.append({
                "prensa": prensa_id,
                "ordenes": len(prenss_asign),
                "ciclos": len(ciclos),
                "horas_prensa": round(horas_prensa, 2),
                "costo_total": round(costo, 2),
                "pisos_utilizados": pisos_usados,
                "utilizacion": round(horas_prensa / 24 * 100, 1) if horas_prensa else 0
            })

    return pd.DataFrame(resumen)


def generar_resumen_pisos(asignaciones: pd.DataFrame) -> pd.DataFrame:
    """Genera un resumen detallado por piso."""
    if asignaciones.empty:
        return pd.DataFrame()

    resumen = []

    # Obtener todas las prensas organizadas
    prensas_organizadas = {}
    for piso_id, info in PRENSAS.items():
        prensa = info["prensa"]
        if prensa not in prensas_organizadas:
            prensas_organizadas[prensa] = []
        prensas_organizadas[prensa].append(piso_id)

    for prensa, pisos in prensas_organizadas.items():
        for piso_id in sorted(pisos):
            piso_asign = asignaciones[asignaciones["piso_id"] == piso_id]

            if piso_asign.empty:
                resumen.append({
                    "prensa": prensa,
                    "piso": piso_id,
                    "ordenes": 0,
                    "horas_trabajo": 0,
                    "emparejadas": 0,
                    "solas": 0
                })
            else:
                emparejadas = piso_asign[piso_asign["emparejado_con"].notna()]
                solas = piso_asign[piso_asign["emparejado_con"].isna()]

                resumen.append({
                    "prensa": prensa,
                    "piso": piso_id,
                    "ordenes": len(piso_asign),
                    "horas_trabajo": round(piso_asign["tiempo_horas"].sum(), 2),
                    "emparejadas": len(emparejadas),
                    "solas": len(solas)
                })

    return pd.DataFrame(resumen)


def calcular_eficiencia_emparejamiento(asignaciones: pd.DataFrame) -> dict:
    """Calcula métricas de eficiencia del emparejamiento."""
    if asignaciones.empty:
        return {"eficiencia": 0, "ordenes_emparejadas": 0, "ordenes_solas": 0}

    validas = asignaciones[asignaciones["prensa_id"].notna()]
    emparejadas = validas[validas["emparejado_con"].notna()]
    solas = validas[validas["emparejado_con"].isna()]

    total_ordenes = len(validas)
    ordenes_emparejadas = len(emparejadas)

    # Eficiencia: porcentaje de tiempo ahorrado por emparejamiento
    if total_ordenes > 0:
        eficiencia = (ordenes_emparejadas / total_ordenes) * 100
    else:
        eficiencia = 0

    # Calcular tiempo ahorrado
    tiempo_emparejado = emparejadas["tiempo_horas"].sum() if len(emparejadas) > 0 else 0
    tiempo_prensa_emparejado = emparejadas["tiempo_prensa"].sum() if len(emparejadas) > 0 and "tiempo_prensa" in emparejadas.columns else 0
    tiempo_ahorrado = tiempo_emparejado - tiempo_prensa_emparejado if tiempo_prensa_emparejado > 0 else 0

    return {
        "eficiencia": round(eficiencia, 1),
        "ordenes_emparejadas": ordenes_emparejadas,
        "ordenes_solas": len(solas),
        "tiempo_ahorrado_horas": round(tiempo_ahorrado, 2),
        "costo_ahorrado": round(tiempo_ahorrado * 50, 2)  # Aproximación
    }


def validar_orden(row: pd.Series) -> tuple:
    """Valida los datos de una orden."""
    errores = []

    if pd.isna(row.get("id")) or str(row.get("id", "")).strip() == "":
        errores.append("ID de orden vacío")

    dim_x = row.get("dim_x")
    dim_y = row.get("dim_y")
    cantidad = row.get("cantidad")
    tiempo = row.get("tiempo_unitario")

    for campo, valor, minimo in [("dim_x", dim_x, 1), ("dim_y", dim_y, 1),
                                   ("cantidad", cantidad, 1), ("tiempo_unitario", tiempo, 0)]:
        if pd.isna(valor):
            errores.append(f"{campo} es requerido")
        elif not isinstance(valor, (int, float)):
            try:
                float(valor)
            except (ValueError, TypeError):
                errores.append(f"{campo} debe ser numérico")
        elif valor < minimo and campo != "tiempo_unitario":
            errores.append(f"{campo} debe ser >= {minimo}")

    # Validar presión si existe
    presion = row.get("presion_psi")
    if presion is not None and pd.notna(presion):
        try:
            if float(presion) < 0:
                errores.append("presion_psi debe ser positiva")
        except (ValueError, TypeError):
            errores.append("presion_psi debe ser numérico")

    return len(errores) == 0, errores
