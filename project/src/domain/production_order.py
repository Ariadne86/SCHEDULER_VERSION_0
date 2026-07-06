"""Modelo de dominio: Orden de producción."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from src.domain.product import Product


@dataclass
class ProductionOrder:
    """Representa una orden de producción que debe programarse en las prensas.

    Attributes:
        order_id:          Identificador único de la orden.
        product:           Producto a fabricar.
        quantity:          Cantidad total de piezas solicitadas.
        due_date:          Fecha límite de entrega.
        priority:          Prioridad de la orden (1 = urgente, valores mayores = menor urgencia).
        status:            Estado actual ("pending", "scheduled", "in_progress", "done").
        produced_quantity: Cantidad de piezas ya producidas.
    """

    order_id: str
    product: Product
    quantity: int
    due_date: datetime
    priority: int = 3
    status: str = "pending"
    produced_quantity: int = field(default=0, compare=False)

    def remaining_quantity(self) -> int:
        """Calcula la cantidad de piezas pendientes de producir.

        Returns:
            Diferencia entre la cantidad solicitada y la ya producida.
            Nunca retorna un valor negativo.
        """
        return max(0, self.quantity - self.produced_quantity)
