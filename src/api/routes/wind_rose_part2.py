# ruff: noqa: F403, F405,noqa: I001  # noqa: RUF100
"""Split definitions from wind_rose.py — route-level adapter."""

from __future__ import annotations

from src.domain.analytics.services.wind_rose_calculator import (
    WindRoseCalculator,
)

from .wind_rose_support import *

_wind_rose_calculator = WindRoseCalculator()


def _process_wind_rose_data(daily_data: dict) -> dict:
    """Process daily weather data into wind rose format (route adapter).

    Converts ValueError from domain service to HTTPException.
    """
    try:
        return _wind_rose_calculator.calculate(daily_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
