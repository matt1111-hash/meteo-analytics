# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for analysis_type_widget.py."""

from __future__ import annotations

from .analysis_type_widget_part1 import AnalysisTypeWidgetPart1Mixin
from .analysis_type_widget_part2 import AnalysisTypeWidgetPart2Mixin
from .analysis_type_widget_support import *


class AnalysisTypeWidget(
    AnalysisTypeWidgetPart1Mixin, AnalysisTypeWidgetPart2Mixin, QWidget
):
    """
    🎯 ELEMZÉSI TÍPUS VÁLASZTÓ WIDGET - CLEAN ARCHITECTURE

    Felelősség:
    - Analysis type radio buttonok (single_location/region/county)
    - State management és validation
    - Clean signal emission

    Interface:
    - analysis_type_changed = Signal(str) - kimenő signal
    - get_state() -> dict - aktuális állapot lekérdezése
    - set_state(dict) - állapot beállítása
    - is_valid() -> bool - validáció
    """

    # === KIMENŐ SIGNAL ===
    analysis_type_changed = Signal(str)  # "single_location", "region", "county"
