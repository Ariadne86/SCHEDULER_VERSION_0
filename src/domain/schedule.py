"""Modelo de dominio: Programación de producción."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Schedule:
    """Contiene el resultado de una programación de producción.

    Attributes:
        assignments: Lista de asignaciones realizadas.
        total_cost:  Costo total acumulado.
        makespan:    Duración total del plan en horas.
    """

    assignments: List[Dict[str, Any]] = field(default_factory=list)
    total_cost: float = 0.0
    makespan: float = 0.0

    def add_assignment(self, assignment: Dict[str, Any]) -> None:
        """Agrega una asignación al plan.

        Args:
            assignment: Diccionario con datos de la asignación.
        """
        self.assignments.append(assignment)
        self.total_cost = self.calculate_cost()

    def calculate_cost(self) -> float:
        """Calcula el costo total de todas las asignaciones.

        Returns:
            Suma de los valores 'costo_total' de cada asignación.
        """
        return sum(
            a.get("costo_total", 0.0) or 0.0
            for a in self.assignments
        )
