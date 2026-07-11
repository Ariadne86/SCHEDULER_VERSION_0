"""Priority queue for Digital Twin simulation events.

This module defines the :class:`EventQueue`, a chronologically ordered
queue of :class:`~src.simulation.event.Event` objects backed by
:mod:`heapq`. Events are kept sorted by ``timestamp`` so that the
simulation engine can always retrieve the next event to process in
constant time.
"""

from __future__ import annotations

import heapq
from typing import List, Optional

from src.simulation.event import Event


class EventQueue:
    """A min-heap priority queue of :class:`Event` objects.

    Events are ordered by their ``timestamp`` field. The queue uses
    :mod:`heapq` internally so that insertion and extraction of the
    earliest event are both O(log n) operations.

    A monotonically increasing counter is used as a tie-breaker in the
    heap to preserve insertion order among events that share the same
    timestamp, and to avoid comparing :class:`Event` objects directly
    (which are not orderable).
    """

    def __init__(self) -> None:
        """Initialize an empty event queue."""
        self._heap: List[tuple] = []
        self._counter: int = 0

    def add_event(self, event: Event) -> None:
        """Insert an event into the queue in chronological order.

        The event is placed according to its ``timestamp``. Events with
        identical timestamps are ordered by insertion sequence.

        Args:
            event: The :class:`Event` to insert.
        """
        heapq.heappush(self._heap, (event.timestamp, self._counter, event))
        self._counter += 1

    def next_event(self) -> Optional[Event]:
        """Remove and return the earliest event from the queue.

        Returns:
            The :class:`Event` with the smallest ``timestamp``, or
            ``None`` if the queue is empty.
        """
        if not self._heap:
            return None
        return heapq.heappop(self._heap)[2]

    def peek(self) -> Optional[Event]:
        """Return the earliest event without removing it.

        Returns:
            The next :class:`Event` to be processed, or ``None`` if the
            queue is empty.
        """
        if not self._heap:
            return None
        return self._heap[0][2]

    def is_empty(self) -> bool:
        """Return ``True`` if the queue contains no events.

        Returns:
            ``True`` when the queue is empty, ``False`` otherwise.
        """
        return len(self._heap) == 0

    def clear(self) -> None:
        """Remove all events from the queue."""
        self._heap.clear()
        self._counter = 0

    def size(self) -> int:
        """Return the number of events currently in the queue.

        Returns:
            The count of stored events.
        """
        return len(self._heap)

    def get_all_events(self) -> List[Event]:
        """Return all events in chronological order.

        The events are returned sorted by ``timestamp`` (and by
        insertion order for ties). The queue itself is not modified.

        Returns:
            A new list of every :class:`Event` in the queue, ordered
            from earliest to latest.
        """
        sorted_heap = sorted(self._heap)
        return [entry[2] for entry in sorted_heap]
