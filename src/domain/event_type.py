"""EventType enum for the Digital Twin simulation.

This module defines the :class:`EventType` enumeration, which enumerates
every kind of discrete event that can occur during a simulated production
run. Events are emitted by the simulation engine as presses transition
through setup, heating, production, and maintenance phases.
"""

from __future__ import annotations

from enum import Enum


class EventType(Enum):
    """Enumeration of all possible simulation event types.

    Each value represents a discrete state transition in the life cycle
    of a press, mold, or production order within the Digital Twin.

    Attributes:
        SETUP_STARTED: A press has begun the setup phase for a new order.
        SETUP_FINISHED: The setup phase has completed.
        HEATING_STARTED: A press has begun heating a mold.
        HEATING_FINISHED: The heating phase has completed.
        PRODUCTION_STARTED: Production of units has started.
        PRODUCTION_FINISHED: Production of units has finished.
        PRESS_RELEASED: A press has been released and is now idle.
        MOLD_INSTALLED: A mold has been installed onto a press.
        MOLD_REMOVED: A mold has been removed from a press.
        MAINTENANCE_STARTED: Maintenance on a press has started.
        MAINTENANCE_FINISHED: Maintenance on a press has finished.
    """

    SETUP_STARTED = "SETUP_STARTED"
    SETUP_FINISHED = "SETUP_FINISHED"
    HEATING_STARTED = "HEATING_STARTED"
    HEATING_FINISHED = "HEATING_FINISHED"
    PRODUCTION_STARTED = "PRODUCTION_STARTED"
    PRODUCTION_FINISHED = "PRODUCTION_FINISHED"
    PRESS_RELEASED = "PRESS_RELEASED"
    MOLD_INSTALLED = "MOLD_INSTALLED"
    MOLD_REMOVED = "MOLD_REMOVED"
    MAINTENANCE_STARTED = "MAINTENANCE_STARTED"
    MAINTENANCE_FINISHED = "MAINTENANCE_FINISHED"
