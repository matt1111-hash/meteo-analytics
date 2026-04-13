# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from extreme_events_tab.py."""

from __future__ import annotations

from .extreme_events_tab_support import *


@dataclass
class AnomalyResult:
    """GUI-barát eredmény az anomália detektáláshoz."""

    category: str
    message: str
    status: str  # 'success' | 'warning' | 'error' | 'disabled'
    value: Optional[float] = None
    threshold: Optional[float] = None
    details: Optional[str] = None
