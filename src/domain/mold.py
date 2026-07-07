"""Modelo de dominio: Molde."""
from __future__ import annotations

from dataclasses import dataclass

from .enums import MoldStatus


@dataclass
class Mold:
    """Representa un molde utilizado en el proceso de prensado.

    Attributes:
        id:           Identificador único del molde.
        product_code: Código del producto para el que está diseñado.
        width:        Ancho del molde en milímetros.
        length:       Largo del molde en milímetros.
        setup_time:   Tiempo de instalación en horas.
        heating_time: Tiempo de calentamiento en horas.
        status:       Estado actual del molde.
    """

    id: str
    product_code: str
    width: int
    length: int
    setup_time: float
    heating_time: float
    status: MoldStatus = MoldStatus.AVAILABLE
