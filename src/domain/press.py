"""Modelo de dominio: Prensa industrial."""
from __future__ import annotations

from dataclasses import dataclass, field

from .enums import PressStatus


@dataclass
class Press:
    """Representa una prensa industrial del área de producción.

    Attributes:
        id:            Identificador único de la prensa.
        name:          Nombre descriptivo de la prensa.
        width:         Ancho útil en milímetros.
        length:        Largo útil en milímetros.
        hourly_cost:   Costo de operación por hora.
        status:        Estado operativo de la prensa.
        floors:        Lista de pisos asociados.
        current_order: Identificador de la orden actual, o None.
        current_molds: Lista de moldes instalados.
    """

    id: str
    name: str
    width: int
    length: int
    hourly_cost: float
    status: PressStatus = PressStatus.AVAILABLE
    floors: list = field(default_factory=list)
    current_order: str | None = None
    current_molds: list = field(default_factory=list)

    def can_fit(self, mold_width: int, mold_length: int) -> bool:
        """Indica si un molde cabe en la prensa.

        Args:
            mold_width:  Ancho del molde en milímetros.
            mold_length: Largo del molde en milímetros.

        Returns:
            True si el molde no excede las dimensiones de la prensa.
        """
        return mold_width <= self.width and mold_length <= self.length

    def is_available(self) -> bool:
        """Indica si la prensa está disponible.

        Returns:
            True únicamente cuando status es PressStatus.AVAILABLE.
        """
        return self.status == PressStatus.AVAILABLE

    def assign_order(self, order_id: str) -> None:
        """Asigna una orden a la prensa.

        Args:
            order_id: Identificador de la orden.
        """
        self.current_order = order_id
        self.status = PressStatus.PRODUCING

    def release(self) -> None:
        """Libera la prensa y la deja disponible."""
        self.current_order = None
        self.status = PressStatus.AVAILABLE

    def calculate_hourly_cost(self, hours: float) -> float:
        """Calcula el costo de operar durante un número de horas.

        Args:
            hours: Duración en horas.

        Returns:
            Costo total (hourly_cost * hours).
        """
        return self.hourly_cost * hours

    def __repr__(self) -> str:
        """Representación legible de la prensa."""
        return f"Press({self.id},{self.width}x{self.length},{self.status.value})"
