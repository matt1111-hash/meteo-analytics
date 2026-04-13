# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for core.py."""

from __future__ import annotations

from .core_part1 import AnalyticsViewPart1Mixin
from .core_part2 import AnalyticsViewPart2Mixin
from .core_support import *


class AnalyticsView(AnalyticsViewPart1Mixin, AnalyticsViewPart2Mixin, QWidget):
    """
    🎯 REFAKTORÁLT KONSTANS HEATMAP Analytics View - KÖZPONTI SIGNAL RENDSZERREL + DEDICATED WIND CHARTOK

    ✅ REFAKTORÁLT MŰKÖDÉS:
    - A nézet most már nem indít saját lekérdezéseket.
    - A gombok egy központi `multi_city_query_requested` signalt bocsátanak ki.
    - A MainWindow kezeli a lekérdezést és az eredményt egy publikus slot-on
      (`update_with_multi_city_result`) keresztül küldi vissza.
    - Ezzel a nézet teljesen szinkronban van a többi modullal (Térkép, ControlPanel).
    """

    # Signalok
    analysis_started = Signal()
    analysis_completed = Signal()
    error_occurred = Signal(str)

    # 🚀 ÚJ: Signal a lekérdezés indításához a MainWindow felé
    multi_city_query_requested = Signal(str, str)  # query_type, region_name
