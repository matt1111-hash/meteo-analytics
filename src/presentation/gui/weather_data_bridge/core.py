# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for core.py."""

from __future__ import annotations

from .core_part1 import WeatherDataBridgePart1Mixin
from .core_part2 import WeatherDataBridgePart2Mixin
from .core_support import *


class WeatherDataBridge(WeatherDataBridgePart1Mixin, WeatherDataBridgePart2Mixin):
    """
    Weather Data Bridge - Analytics Engine → Folium Map Integration.

    Responsibilities:
    - AnalyticsResult → Folium overlay format conversion
    - 4 weather types supported (temperature, precipitation, wind, wind_gusts)
    - Coordinates + values extraction
    - Metric-based overlay type auto-detection
    - Min/max values calculation for color scales
    """

    METRIC_MAP = METRIC_MAP
    METRIC_TO_OVERLAY = METRIC_MAP
    OVERLAY_CONFIGS = OVERLAY_CONFIGS
