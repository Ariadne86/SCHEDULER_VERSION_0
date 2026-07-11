"""Assignment domain entity.

This module defines the :class:`Assignment` dataclass, which represents the
allocation of a production order to a specific press and mold within the
factory floor. An assignment captures the full timeline of a job — setup,
heating, and production phases — along with its associated costs and current
status.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict


@dataclass
class Assignment:
    """A single production assignment of an order to a press and mold.

    An :class:`Assignment` records every timestamp that delineates the
    manufacturing phases (setup, heating, production) as well as the
    financial cost incurred. The lifecycle of an assignment is tracked
    through :attr:`status`, which defaults to ``"PLANNED"``.

    Attributes:
        assignment_id: Unique identifier for this assignment.
        order_id: Identifier of the order being fulfilled.
        product_code: Code of the product to be manufactured.
        press_id: Identifier of the press assigned to the job.
        floor_level: Floor level where the press is located.
        mold_id: Identifier of the mold used for production.
        start_time: Absolute start time of the assignment (epoch seconds).
        setup_start: Start time of the setup phase.
        setup_finish: Finish time of the setup phase.
        heating_start: Start time of the heating phase.
        heating_finish: Finish time of the heating phase.
        production_start: Start time of the production phase.
        production_finish: Finish time of the production phase.
        quantity: Number of units to produce.
        hourly_cost: Cost per hour of running the press.
        total_cost: Total cost of the assignment (computed).
        status: Current lifecycle status. Defaults to ``"PLANNED"``.
    """

    assignment_id: str
    order_id: str
    product_code: str
    press_id: str
    floor_level: int
    mold_id: str
    start_time: float
    setup_start: float
    setup_finish: float
    heating_start: float
    heating_finish: float
    production_start: float
    production_finish: float
    quantity: int
    hourly_cost: float
    total_cost: float = 0.0
    status: str = "PLANNED"

    def duration(self) -> float:
        """Return the total duration of the assignment in seconds.

        The total duration is measured from :attr:`start_time` to
        :attr:`production_finish`.

        Returns:
            The elapsed time in seconds. Returns ``0.0`` if the
            production finish time is earlier than the start time.
        """
        return max(self.production_finish - self.start_time, 0.0)

    def setup_duration(self) -> float:
        """Return the duration of the setup phase in seconds.

        Returns:
            The elapsed time between :attr:`setup_start` and
            :attr:`setup_finish`. Returns ``0.0`` if negative.
        """
        return max(self.setup_finish - self.setup_start, 0.0)

    def heating_duration(self) -> float:
        """Return the duration of the heating phase in seconds.

        Returns:
            The elapsed time between :attr:`heating_start` and
            :attr:`heating_finish`. Returns ``0.0`` if negative.
        """
        return max(self.heating_finish - self.heating_start, 0.0)

    def production_duration(self) -> float:
        """Return the duration of the production phase in seconds.

        Returns:
            The elapsed time between :attr:`production_start` and
            :attr:`production_finish`. Returns ``0.0`` if negative.
        """
        return max(self.production_finish - self.production_start, 0.0)

    def calculate_total_cost(self) -> float:
        """Compute and store the total cost of this assignment.

        The total cost is derived from the overall :meth:`duration`
        (converted to hours) multiplied by :attr:`hourly_cost`. The
        result is stored in :attr:`total_cost` and also returned.

        Returns:
            The computed total cost.
        """
        hours = self.duration() / 3600.0
        self.total_cost = hours * self.hourly_cost
        return self.total_cost

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of this assignment.

        Returns:
            A dictionary mapping every field name to its current value.
        """
        return asdict(self)
