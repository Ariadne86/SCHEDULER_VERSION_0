"""Servicio de programación: encapsula el scheduler de prensas."""
import pandas as pd

from src.scheduler.scheduler import programar_ordenes


class SchedulerService:
    """Punto de entrada de la capa de servicios para la programación de producción."""

    def generate_schedule(
        self,
        ordenes: pd.DataFrame,
        estrategia: str = "menor_costo",
    ) -> pd.DataFrame:
        """
        Genera la programación de órdenes en prensas.

        Args:
            ordenes:   DataFrame con las órdenes a programar.
            estrategia: "menor_costo" o "balancear_carga".

        Returns:
            DataFrame con las asignaciones realizadas (mismo formato que
            programar_ordenes).
        """
        return programar_ordenes(ordenes, estrategia)
