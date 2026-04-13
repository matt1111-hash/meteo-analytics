# ruff: noqa: F403,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for analytics_statistics.py."""

from __future__ import annotations

from .analytics_statistics_part1 import AnalyticsStatisticsPart1Mixin
from .analytics_statistics_part2 import AnalyticsStatisticsPart2Mixin
from .analytics_statistics_support import *


class AnalyticsStatistics(AnalyticsStatisticsPart1Mixin, AnalyticsStatisticsPart2Mixin):
    """📊 Analytics statisztika számító osztály"""


__all__ = [
    "AnalyticsStatistics",
]
