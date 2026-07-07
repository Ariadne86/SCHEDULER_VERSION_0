"""Modelo de dominio: Piso (compartimiento) de una prensa."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from .enums import FloorStatus
from .mold import Mold


@dataclass
class Floor:
    """Representa uno de los dos pisos de una prensa industrial.

    Cada prensa tiene un piso superior (level=1) y uno inferior (level=2).
    Ambos pisos operan simultáneamente dentro del mismo ciclo de prensado,
    pero pueden procesar productos distintos siempre que cumplan las
    restricciones de compatibilidad.

    Attributes:
        id:           Identificador único del piso (ej. "P1-1").
        press_id:     Identificador de la prensa a la que pertenece.
        level:        Nivel del piso dentro de la prensa (1=superior, 2=inferior).
        status:       Estado operativo del piso.
        current_mold: Molde actualmente instalado, o None si no hay ninguno.
    """

    id: str
    press_id: str
    level: int
    status: FloorStatus = FloorStatus.FREE
    current_mold: Optional[Mold] = field(default=None, compare=False)

    def is_free(self) -> bool:
        """Indica si el piso está disponible para recibir una nueva orden.

        Returns:
            True cuando el estado es FREE y no hay molde instalado.
        """
        return self.status == FloorStatus.FREE and self.current_mold is None

    def assign_mold(self, mold: Mold) -> None:
        """Asigna un molde al piso y cambia el estado a SETUP.

        Args:
            mold: Instancia de Mold a instalar en el piso.
        """
        self.current_mold = mold
        self.status = FloorStatus.SETUP

    def release_mold(self) -> None:
        """Libera el molde del piso y restablece el estado a FREE."""
        self.current_mold = None
        self.status = FloorStatus.FREE

    def is_occupied(self) -> bool:
        """Indica si el piso tiene un molde instalado.

        Returns:
            True si hay un molde asignado al piso.
        """
        return self.current_mold is not None
