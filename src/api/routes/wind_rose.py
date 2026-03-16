# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for wind_rose.py."""

from __future__ import annotations

from . import wind_rose_part3 as wind_rose_impl
from .wind_rose_part1 import DirectionData, WindRoseRequest, WindRoseResponse
from .wind_rose_part2 import _process_wind_rose_data
from .wind_rose_support import *


async def get_wind_rose(request: WindRoseRequest) -> WindRoseResponse:
    """Delegate to the split implementation with wrapper-level collaborators."""
    wind_rose_impl.WeatherClient = WeatherClient
    wind_rose_impl.get_city_manager_port = get_city_manager_port
    return await wind_rose_impl.get_wind_rose(request)
