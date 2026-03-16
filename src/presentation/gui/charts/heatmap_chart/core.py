# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for core.py."""

from __future__ import annotations

from .core_part1 import HeatmapCalendarChartPart1Mixin
from .core_part2 import HeatmapCalendarChartPart2Mixin
from .core_support import *


class HeatmapCalendarChart(
    HeatmapCalendarChartPart1Mixin, HeatmapCalendarChartPart2Mixin, WeatherChart
):
    """
    🎯 HEATMAP CHART - CLEAN VERZIÓ

    FELELŐSSÉGEK:
    - ✅ TELJES TÉGLALAP renderelése (pcolormesh)
    - ✅ Custom meteorológiai színskálák
    - ✅ Dinamikus paraméter kezelés (hőmérséklet/csapadék/szél)
    - ✅ 365 konstans téglalap logika aggregációval
    - ✅ Kalendár mátrix építés (7×53 cellák)
    - ✅ Valódi hónap címkék
    """
