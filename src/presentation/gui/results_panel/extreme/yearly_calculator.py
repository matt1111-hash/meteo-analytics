# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for yearly_calculator.py."""

from __future__ import annotations

from .yearly_calculator_part1 import YearlyCalculator
from .yearly_calculator_part2 import _calculate_climate_trends, _get_wind_column
from .yearly_calculator_support import *
