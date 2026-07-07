"""Modelo de dominio: Producto fabricado en las prensas."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Product:
    """Representa un producto que puede ser prensado.

    Attributes:
        code:        Código único del producto.
        description: Descripción legible del producto.
        curing_time: Tiempo de curado requerido en horas.
        priority:    Prioridad de producción (1 = alta, valores mayores = menor prioridad).
    """

    code: str
    description: str
    curing_time: float
    priority: int = 3
