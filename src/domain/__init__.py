"""Domain layer package.

Re-exports the core domain entities so they can be imported directly
from :mod:`src.domain`.
"""

from src.domain.assignment import Assignment
from src.domain.schedule import Schedule

__all__ = ["Assignment", "Schedule"]
