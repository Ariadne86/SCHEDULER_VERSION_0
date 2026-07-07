"""Modelo de dominio: Orden de producción."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .enums import OrderStatus
from .product import Product


@dataclass
class ProductionOrder:
    """Representa una orden de producción.

    Attributes:
        order_id:          Identificador único de la orden.
        product:           Producto a fabricar.
        quantity:          Cantidad total solicitada.
        due_date:          Fecha límite de entrega.
        priority:          Prioridad de la orden (1 = urgente).
        status:            Estado actual de la orden.
        produced_quantity: Cantidad ya producida.
    """

    order_id: str
    product: Product
    quantity: int
    due_date: datetime
    priority: int = 3
    status: OrderStatus = OrderStatus.PENDING
    produced_quantity: int = field(default=0, compare=False)

    def remaining_quantity(self) -> int:
        """Calcula la cantidad pendiente de producir.

        Returns:
            Cantidad restante (nunca negativa).
        """
        return max(0, self.quantity - self.produced_quantity)
