"""Modelo de dominio: Fábrica — raíz agregada del dominio."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from src.domain.mold import Mold
from src.domain.press import Press
from src.domain.production_order import ProductionOrder
from src.domain.schedule import Schedule


@dataclass
class Factory:
    """Raíz del agregado de dominio: representa el área de prensas.

    Concentra las colecciones principales del sistema (prensas, órdenes y
    moldes) y proporciona métodos de acceso por identificador. El atributo
    ``schedule`` almacena la programación vigente una vez que el motor de
    scheduling la genera.

    Attributes:
        presses:  Lista de prensas disponibles en el área de producción.
        orders:   Lista de órdenes de producción pendientes o programadas.
        molds:    Lista de moldes registrados en el sistema.
        schedule: Programación activa generada por el scheduler, o None si
                  aún no se ha ejecutado ninguna planificación.
    """

    presses: List[Press] = field(default_factory=list)
    orders: List[ProductionOrder] = field(default_factory=list)
    molds: List[Mold] = field(default_factory=list)
    schedule: Optional[Schedule] = field(default=None, compare=False)

    def get_press(self, press_id: str) -> Optional[Press]:
        """Busca y retorna una prensa por su identificador.

        Args:
            press_id: Identificador único de la prensa (ej. "P1").

        Returns:
            La instancia ``Press`` correspondiente, o None si no existe.
        """
        for press in self.presses:
            if press.id == press_id:
                return press
        return None

    def get_order(self, order_id: str) -> Optional[ProductionOrder]:
        """Busca y retorna una orden de producción por su identificador.

        Args:
            order_id: Identificador único de la orden.

        Returns:
            La instancia ``ProductionOrder`` correspondiente, o None si no existe.
        """
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None
