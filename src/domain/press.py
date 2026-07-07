"""Modelo de dominio: Prensa industrial."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

from .enums import PressStatus, FloorStatus
from .floor import Floor


if TYPE_CHECKING:
    from .mold import Mold


@dataclass
class Press:
    """Representa una prensa industrial del área de producción.

    Attributes:
        id:            Identificador único de la prensa.
        name:          Nombre descriptivo de la prensa.
        width:         Ancho útil en milímetros.
        length:        Largo útil en milímetros.
        hourly_cost:   Costo de operación por hora.
        status:        Estado operativo de la prensa.
        floors:        Lista de pisos asociados.
        current_order: Identificador de la orden actual, o None.
        current_molds: Lista de moldes instalados.
    """

    id: str
    name: str
    width: int
    length: int
    hourly_cost: float
    status: PressStatus = PressStatus.AVAILABLE
    floors: List[Floor] = field(default_factory=list)
    current_order: str | None = None
    current_molds: List["Mold"] = field(default_factory=list)

    def can_fit(self, mold_width: int, mold_length: int) -> bool:
        """Indica si un molde cabe en la prensa.

        Args:
            mold_width:  Ancho del molde en milímetros.
            mold_length: Largo del molde en milímetros.

        Returns:
            True si el molde no excede las dimensiones de la prensa.
        """
        return mold_width <= self.width and mold_length <= self.length

    def is_available(self) -> bool:
        """Indica si la prensa está disponible.

        Returns:
            True únicamente cuando status es PressStatus.AVAILABLE.
        """
        return self.status == PressStatus.AVAILABLE

    def assign_order(self, order_id: str) -> None:
        """Asigna una orden a la prensa.

        Args:
            order_id: Identificador de la orden.
        """
        self.current_order = order_id
        self.status = PressStatus.PRODUCING

    def release(self) -> None:
        """Libera la prensa y la deja disponible."""
        self.current_order = None
        self.status = PressStatus.AVAILABLE

    def calculate_hourly_cost(self, hours: float) -> float:
        """Calcula el costo de operar durante un número de horas.

        Args:
            hours: Duración en horas.

        Returns:
            Costo total (hourly_cost * hours).
        """
        return self.hourly_cost * hours

    def install_mold(self, mold: "Mold") -> bool:
        """Instala un molde en la prensa si es compatible.

        Verifica que el molde quepa físicamente en la prensa antes
        de instalarlo. Si es compatible, lo agrega a current_molds
        y cambia el estado del molde a INSTALLED.

        Args:
            mold: Instancia de Mold a instalar.

        Returns:
            True si el molde se instaló correctamente,
            False si no cabe en la prensa.
        """
        if not self.can_fit(mold.width, mold.length):
            return False
        self.current_molds.append(mold)
        mold.install()
        return True

    def remove_mold(self, mold_id: str) -> None:
        """Remueve un molde de la prensa.

        Elimina el molde de current_molds y cambia su estado a AVAILABLE.

        Args:
            mold_id: Identificador del molde a remover.
        """
        for mold in self.current_molds:
            if mold.id == mold_id:
                self.current_molds.remove(mold)
                mold.release()
                break

    def has_mold(self, mold_id: str) -> bool:
        """Verifica si un molde ya está instalado en la prensa.

        Args:
            mold_id: Identificador del molde a verificar.

        Returns:
            True si el molde está en current_molds.
        """
        return any(mold.id == mold_id for mold in self.current_molds)

    def available_floors(self) -> List[Floor]:
        """Retorna los pisos disponibles de la prensa.

        Returns:
            Lista de pisos cuyo estado es FloorStatus.FREE.
        """
        return [floor for floor in self.floors if floor.status == FloorStatus.FREE]

    def __repr__(self) -> str:
        """Representación legible de la prensa."""
        return f"Press({self.id},{self.width}x{self.length},{self.status.value})"
