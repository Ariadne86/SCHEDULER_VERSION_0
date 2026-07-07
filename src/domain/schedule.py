"""Modelo de dominio: Programación de producción resultante."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Schedule:
    """Contiene el resultado completo de una programación de producción.

    Agrupa todas las asignaciones generadas por el motor de scheduling e
    incluye métricas consolidadas como costo total y makespan.

    Attributes:
        assignments: Lista de asignaciones realizadas. Cada elemento es un
                     diccionario con las claves producidas por el scheduler
                     (orden_id, prensa_id, piso_id, inicio, fin, etc.).
        total_cost:  Costo total acumulado de todas las asignaciones.
        makespan:    Duración total del plan en horas (diferencia entre el
                     inicio más temprano y el fin más tardío).
    """

    assignments: List[Dict[str, Any]] = field(default_factory=list)
    total_cost: float = 0.0
    makespan: float = 0.0

    def add_assignment(self, assignment: Dict[str, Any]) -> None:
        """Agrega una asignación al plan y actualiza las métricas.

        Args:
            assignment: Diccionario con los datos de la asignación.
                        Se espera que contenga al menos "costo_total".
        """
        self.assignments.append(assignment)
        self.total_cost = self.calculate_cost()

    def calculate_cost(self) -> float:
        """Calcula el costo total sumando todas las asignaciones vigentes.

        Returns:
            Suma de los valores "costo_total" de cada asignación.
            Las entradas sin ese campo se ignoran.
        """
        return sum(
            a.get("costo_total", 0.0) or 0.0
            for a in self.assignments
        )
