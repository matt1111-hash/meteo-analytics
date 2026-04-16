# ruff: noqa: F403,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for analytics_tabs.py."""

from __future__ import annotations

from .analytics_tabs_part1 import (
    PrecipitationTabWidget,
    TemperatureTabWidget,
    WindGustTabWidget,
    WindTabWidget,
)
from .analytics_tabs_part3 import ClimateTabWidget
from .analytics_tabs_support import *

__all__ = [
    "ClimateTabWidget",
    "PrecipitationTabWidget",
    "TemperatureTabWidget",
    "WindGustTabWidget",
    "WindTabWidget",
]
