"""Modelo de dominio: Molde utilizado en el proceso de prensado."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.press import Press


@dataclass
class Mold:
    """Representa un molde que se instala en un piso de prensa.

    Attributes:
        id:           Identificador único del molde.
        product_code: Código del producto para el que está diseñado.
        width:        Ancho del molde en milímetros.
        length:       Largo del molde en milímetros.
        setup_time:   Tiempo de instalación en horas.
        heating_time: Tiempo de calentamiento previo en horas.
        status:       Estado actual ("available", "in_use", "maintenance").
    """

    id: str
    product_code: str
    width: int
    length: int
    setup_time: float
    heating_time: float
    status: str = "available"

    def fits_press(self, press: Press) -> bool:
        """Indica si el molde cabe físicamente en la prensa dada.

        Args:
            press: Prensa contra la que se verifica la compatibilidad.

        Returns:
            True si las dimensiones del molde no exceden las de la prensa.
        """
        return self.width <= press.width and self.length <= press.length
