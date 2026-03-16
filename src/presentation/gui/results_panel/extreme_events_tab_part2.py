# ruff: noqa: F401,F403,F405,I001
# mypy: ignore-errors
"""Compatibility wrapper for extreme_events_tab_part2.py."""

from __future__ import annotations

from .extreme_events_tab_part2_support import *
from .extreme_events_tab_part2_part1 import ExtremeEventsTabPart1Mixin
from .extreme_events_tab_part2_part2 import ExtremeEventsTabPart2Mixin


class ExtremeEventsTab(ExtremeEventsTabPart1Mixin, ExtremeEventsTabPart2Mixin, QWidget):
    """
    ⚡ Extrém Események Tab.
    Közvetlenül használja az Application Use Case-t az anomáliák kimutatásához.
    """

    extreme_weather_requested = Signal()
