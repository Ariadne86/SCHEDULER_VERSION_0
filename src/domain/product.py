"""Modelo de dominio: Producto."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Product:
    """Representa un producto fabricado en las prensas.

    Attributes:
        code:        Código único del producto.
        description: Descripción del producto.
        curing_time: Tiempo de curado en horas.
        priority:    Prioridad de producción (1 = alta).
    """

    code: str
    description: str
    curing_time: float
    priority: int = 3
