# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for comparison_chart.py."""

from __future__ import annotations

from .comparison_chart_part1 import MultiYearComparisonChartPart1Mixin
from .comparison_chart_part2 import MultiYearComparisonChartPart2Mixin
from .comparison_chart_part3 import MultiYearComparisonChartPart3Mixin
from .comparison_chart_support import *


class MultiYearComparisonChart(
    MultiYearComparisonChartPart1Mixin,
    MultiYearComparisonChartPart2Mixin,
    MultiYearComparisonChartPart3Mixin,
    WeatherChart,
):
    """
    Több év összehasonlító chart - TREND ELEMZÉS + DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER.
    Azonos időszakok összehasonlítása különböző évekből.
    🎨 TÉMA INTEGRÁCIÓ: ColorPalette trend elemzési színek használata
    """
