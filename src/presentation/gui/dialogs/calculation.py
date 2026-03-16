# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for calculation.py."""

from __future__ import annotations

from .calculation_part1 import (
    _calculate_daily_extremes,
    _calculate_extremes,
    _extract_weather_dataframe,
)
from .calculation_part2 import _calculate_monthly_extremes
from .calculation_support import *
