"""Schedule domain entity.

This module defines the :class:`Schedule` dataclass, which aggregates a
collection of :class:`~src.domain.assignment.Assignment` objects produced by
the scheduling algorithm. A schedule represents the complete plan of
production assignments across all presses and molds for a given set of
orders.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from src.domain.assignment import Assignment


@dataclass
class Schedule:
    """A production schedule composed of assignments.

    The :class:`Schedule` holds the ordered list of
    :class:`~src.domain.assignment.Assignment` objects that together
    describe the factory's production plan. Each assignment encodes the
    full timeline (setup, heating, production) and cost for one job on
    one press.

    Attributes:
        assignments: The ordered list of assignments that make up this
            schedule. Defaults to an empty list.
    """

    assignments: List[Assignment] = field(default_factory=list)

    def add_assignment(self, assignment: Assignment) -> None:
        """Append an assignment to this schedule.

        Args:
            assignment: The :class:`Assignment` to add.
        """
        self.assignments.append(assignment)

    def total_cost(self) -> float:
        """Return the sum of the total cost of every assignment.

        Returns:
            The aggregate cost across all assignments in the schedule.
        """
        return sum(a.total_cost for a in self.assignments)

    def total_duration(self) -> float:
        """Return the total duration across all assignments.

        Returns:
            The sum of every assignment's :meth:`~Assignment.duration`
            in seconds.
        """
        return sum(a.duration() for a in self.assignments)

    def to_dict_list(self) -> List[dict]:
        """Return a list of dictionaries, one per assignment.

        Returns:
            A list where each element is the result of
            :meth:`~Assignment.to_dict` for the corresponding
            assignment.
        """
        return [a.to_dict() for a in self.assignments]
