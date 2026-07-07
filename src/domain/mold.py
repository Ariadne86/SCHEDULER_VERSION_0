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

    def install(self) -> None:
        """Marca el molde como instalado en una prensa."""
        self.status = MoldStatus.INSTALLED

    def start_heating(self) -> None:
        """Marca el molde como en proceso de calentamiento."""
        self.status = MoldStatus.HEATING

    def start_production(self) -> None:
        """Marca el molde como en uso activo durante el ciclo de prensado."""
        self.status = MoldStatus.IN_USE

    def release(self) -> None:
        """Marca el molde como disponible para ser reutilizado."""
        self.status = MoldStatus.AVAILABLE
