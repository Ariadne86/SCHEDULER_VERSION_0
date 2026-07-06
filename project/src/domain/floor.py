"""Modelo de dominio: Piso (compartimiento) de una prensa."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from src.domain.mold import Mold


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
        status:       Estado operativo ("idle", "running", "maintenance").
        current_mold: Molde actualmente instalado, o None si no hay ninguno.
    """

    id: str
    press_id: str
    level: int
    status: str = "idle"
    current_mold: Optional[Mold] = field(default=None, compare=False)

    def is_free(self) -> bool:
        """Indica si el piso está disponible para recibir una nueva orden.

        Returns:
            True cuando el estado es "idle" y no hay molde instalado.
        """
        return self.status == "idle" and self.current_mold is None
