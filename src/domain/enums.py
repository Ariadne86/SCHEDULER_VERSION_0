"""Enumeraciones del dominio de producción."""
from enum import Enum


class PressStatus(Enum):
    """Estados posibles de una prensa industrial.

    Attributes:
        AVAILABLE:     Prensa disponible para recibir una orden.
        SETUP:         Prensa en proceso de configuración.
        HEATING:       Prensa en proceso de calentamiento.
        PRODUCING:     Prensa ejecutando una orden de producción.
        MAINTENANCE:   Prensa en mantenimiento programado.
        OUT_OF_SERVICE: Prensa fuera de servicio.
    """

    AVAILABLE = "AVAILABLE"
    SETUP = "SETUP"
    HEATING = "HEATING"
    PRODUCING = "PRODUCING"
    MAINTENANCE = "MAINTENANCE"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"


class FloorStatus(Enum):
    """Estados posibles de un piso de prensa.

    Attributes:
        FREE:      Piso libre, sin molde instalado.
        SETUP:     Piso en proceso de configuración del molde.
        HEATING:   Piso en proceso de calentamiento del molde.
        PRODUCING: Piso ejecutando el ciclo de prensado.
    """

    FREE = "FREE"
    SETUP = "SETUP"
    HEATING = "HEATING"
    PRODUCING = "PRODUCING"


class MoldStatus(Enum):
    """Estados posibles de un molde.

    Attributes:
        AVAILABLE:   Molde disponible para ser instalado.
        INSTALLED:   Molde instalado en un piso, pendiente de calentar.
        HEATING:     Molde en proceso de calentamiento.
        IN_USE:      Molde en uso activo durante el ciclo de prensado.
        MAINTENANCE: Molde en mantenimiento.
    """

    AVAILABLE = "AVAILABLE"
    INSTALLED = "INSTALLED"
    HEATING = "HEATING"
    IN_USE = "IN_USE"
    MAINTENANCE = "MAINTENANCE"


class OrderStatus(Enum):
    """Estados posibles de una orden de producción.

    Attributes:
        PENDING:     Orden pendiente de programación.
        SCHEDULED:   Orden programada pero no iniciada.
        IN_PROGRESS: Orden en proceso de producción.
        COMPLETED:   Orden completada.
        CANCELLED:   Orden cancelada.
    """

    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
