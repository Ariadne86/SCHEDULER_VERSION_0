"""Event entity for the Digital Twin simulation.

This module defines the :class:`Event` dataclass, which represents a single
discrete event in the simulated production timeline. Events are the atomic
unit of the Digital Twin's discrete-event simulation — each one captures a
state transition (setup, heating, production, maintenance, etc.) at a
specific point in time, optionally tied to a press, floor, mold, and/or
order.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

from src.domain.event_type import EventType


@dataclass
class Event:
    """A single discrete event in the Digital Twin simulation.

    Each :class:`Event` records a state transition that occurred at a
    specific timestamp. Events may be associated with a press, a floor
    level, a mold, and/or a production order, depending on the nature of
    the event. Once an event has been consumed by the simulation engine,
    it is marked as processed.

    Attributes:
        event_id: Unique identifier for this event.
        event_type: The :class:`~src.domain.event_type.EventType` of
            this event.
        timestamp: Absolute time at which the event occurs (epoch
            seconds).
        press_id: Identifier of the press involved, or ``None`` if not
            applicable.
        floor_level: Floor level of the press, or ``None`` if not
            applicable.
        mold_id: Identifier of the mold involved, or ``None`` if not
            applicable.
        order_id: Identifier of the order involved, or ``None`` if not
            applicable.
        description: Human-readable description of the event.
        processed: Whether this event has been consumed by the
            simulation engine. Defaults to ``False``.
    """

    event_id: str
    event_type: EventType
    timestamp: float
    press_id: Optional[str]
    floor_level: Optional[int]
    mold_id: Optional[str]
    order_id: Optional[str]
    description: str
    processed: bool = False

    def process(self) -> None:
        """Mark this event as processed.

        This is a convenience method that sets :attr:`processed` to
        ``True``. It is intended to be called by the simulation engine
        once the event has been consumed and its effects applied to the
        Digital Twin state.
        """
        self.processed = True

    def mark_processed(self) -> None:
        """Alias for :meth:`process`.

        Marks this event as processed by setting :attr:`processed` to
        ``True``. Provided as an alternative name for callers that
        prefer the explicit ``mark_processed`` verb.
        """
        self.processed = True

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of this event.

        The :attr:`event_type` enum is converted to its string value so
        the resulting dictionary is JSON-serializable.

        Returns:
            A dictionary mapping every field name to its current value,
            with ``event_type`` represented as a string.
        """
        result: Dict[str, Any] = asdict(self)
        result["event_type"] = self.event_type.value
        return result
