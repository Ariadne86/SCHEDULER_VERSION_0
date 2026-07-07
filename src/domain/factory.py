"""Modelo de dominio: Fábrica — contenedor principal del estado."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from .mold import Mold
from .press import Press
from .production_order import ProductionOrder
from .product import Product
from .schedule import Schedule


@dataclass
class Factory:
    """Contenedor principal del estado de la fábrica.

    Administra las colecciones de prensas, órdenes, productos y moldes,
    así como el schedule activo y el tiempo de simulación.

    Attributes:
        presses:      Diccionario de prensas indexadas por su id.
        orders:       Diccionario de órdenes de producción indexadas por su id.
        products:     Diccionario de productos indexados por su código.
        molds:        Diccionario de moldes indexados por su id.
        schedule:     Programación activa, o None si no hay ninguna.
        current_time: Tiempo actual de la simulación en horas.
    """

    presses: Dict[str, Press] = field(default_factory=dict)
    orders: Dict[str, ProductionOrder] = field(default_factory=dict)
    products: Dict[str, Product] = field(default_factory=dict)
    molds: Dict[str, Mold] = field(default_factory=dict)
    schedule: Optional[Schedule] = None
    current_time: float = 0.0

    def add_press(self, press: Press) -> None:
        """Agrega una prensa al diccionario utilizando su id.

        Args:
            press: Instancia de Press a agregar.
        """
        self.presses[press.id] = press

    def add_order(self, order: ProductionOrder) -> None:
        """Agrega una orden al diccionario.

        Args:
            order: Instancia de ProductionOrder a agregar.
        """
        self.orders[order.order_id] = order

    def add_product(self, product: Product) -> None:
        """Agrega un producto al diccionario.

        Args:
            product: Instancia de Product a agregar.
        """
        self.products[product.code] = product

    def add_mold(self, mold: Mold) -> None:
        """Agrega un molde al diccionario.

        Args:
            mold: Instancia de Mold a agregar.
        """
        self.molds[mold.id] = mold

    def get_press(self, press_id: str) -> Optional[Press]:
        """Obtiene una prensa por su identificador.

        Args:
            press_id: Identificador único de la prensa.

        Returns:
            La instancia de Press correspondiente, o None si no existe.
        """
        return self.presses.get(press_id)

    def get_order(self, order_id: str) -> Optional[ProductionOrder]:
        """Obtiene una orden por su identificador.

        Args:
            order_id: Identificador único de la orden.

        Returns:
            La instancia de ProductionOrder correspondiente, o None si no existe.
        """
        return self.orders.get(order_id)

    def advance_time(self, hours: float) -> None:
        """Incrementa el tiempo actual de la simulación.

        Args:
            hours: Número de horas a avanzar.
        """
        self.current_time += hours

    def reset(self) -> None:
        """Reinicia el estado de la fábrica para una nueva simulación.

        Vacía el schedule, reestablece el tiempo a cero y libera todas
        las prensas. No elimina productos, moldes ni órdenes.
        """
        self.schedule = None
        self.current_time = 0.0
        for press in self.presses.values():
            press.release()

    def get_state_summary(self) -> Dict[str, int | float]:
        """Devuelve un resumen del estado actual de la fábrica.

        Este método será utilizado posteriormente por Gymnasium para
        obtener una representación compacta del estado.

        Returns:
            Diccionario con:
                - number_of_presses: cantidad de prensas registradas
                - number_of_orders: cantidad de órdenes registradas
                - number_of_products: cantidad de productos registrados
                - number_of_molds: cantidad de moldes registrados
                - current_time: tiempo actual de la simulación
        """
        return {
            "number_of_presses": len(self.presses),
            "number_of_orders": len(self.orders),
            "number_of_products": len(self.products),
            "number_of_molds": len(self.molds),
            "current_time": self.current_time,
        }
