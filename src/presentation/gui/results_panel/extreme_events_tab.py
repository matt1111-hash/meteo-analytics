# ruff: noqa: F401, F403,noqa: I001
# mypy: ignore-errors
"""Merged extreme_events_tab.py."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from .extreme_events_tab_part1 import AnomalyResult
from .extreme_events_tab_part2 import ExtremeEventsTabPart1Mixin, ExtremeEventsTabPart2Mixin
from .extreme_events_tab_part2_support import *
from .extreme_events_tab_support import *


class ExtremeEventsTab(ExtremeEventsTabPart1Mixin, ExtremeEventsTabPart2Mixin, QWidget):
    """
    ⚡ Extrém Események Tab.
    Közvetlenül használja az Application Use Case-t az anomáliák kimutatásához.
    """

    extreme_weather_requested = Signal()
