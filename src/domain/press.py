"""Modelo de dominio: Prensa industrial."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Press:
    """Representa una prensa industrial del área de producción.

    Attributes:
        id:            Identificador único de la prensa (ej. "P1").
        name:          Nombre descriptivo de la prensa.
        width:         Ancho útil en milímetros (dimensión X).
        length:        Largo útil en milímetros (dimensión Y).
        hourly_cost:   Costo de operación por hora en la moneda base.
        status:        Estado operativo de la prensa. Valores posibles:
                       "AVAILABLE" (libre) o "BUSY" (ocupada).
        floors:        Lista de pisos asociados a esta prensa.
        current_order: Identificador de la orden asignada actualmente,
                       o None si la prensa está libre.
        current_molds: Lista de moldes instalados en el ciclo actual.
    """

    id: str
    name: str
    width: int
    length: int
    hourly_cost: float
    status: str = "AVAILABLE"
    floors: list = field(default_factory=list)
    current_order: str | None = None
    current_molds: list = field(default_factory=list)

    def can_fit(self, mold_width: int, mold_length: int) -> bool:
        """Indica si un molde de las dimensiones dadas cabe en esta prensa.

        Args:
            mold_width:  Ancho del molde en milímetros.
            mold_length: Largo del molde en milímetros.

        Returns:
            True si el molde no excede ninguna dimensión útil de la prensa.
        """
        return mold_width <= self.width and mold_length <= self.length

    def is_available(self) -> bool:
        """Indica si la prensa está disponible para recibir una nueva orden.

        Returns:
            True únicamente cuando el estado es "AVAILABLE".
        """
        return self.status == "AVAILABLE"

    def assign_order(self, order_id: str) -> None:
        """Asigna una orden a la prensa y la marca como ocupada.

        Args:
            order_id: Identificador único de la orden a asignar.
        """
        self.current_order = order_id
        self.status = "BUSY"

    def release(self) -> None:
        """Libera la prensa y la deja disponible para una nueva orden.

        Elimina la referencia a la orden actual y restablece el estado
        a "AVAILABLE".
        """
        self.current_order = None
        self.status = "AVAILABLE"

    def calculate_hourly_cost(self, hours: float) -> float:
        """Calcula el costo de operar la prensa durante un número de horas.

        Args:
            hours: Duración de la operación en horas.

        Returns:
            Costo total resultante de multiplicar el costo horario por las horas.
        """
        return self.hourly_cost * hours

    def __repr__(self) -> str:
        """Representación legible de la prensa.

        Returns:
            Cadena con el formato Press({id},{width}x{length},{status}).
            Ejemplo: Press(P1,1200x600,BUSY)
        """
        return f"Press({self.id},{self.width}x{self.length},{self.status})"
