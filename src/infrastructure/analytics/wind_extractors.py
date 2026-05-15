"""Compatibility wrapper for wind extraction helpers."""

from __future__ import annotations

from src.application.services.wind_extractors import (
    extract_daily_wind_data,
    identify_windy_days,
)

__all__ = ["extract_daily_wind_data", "identify_windy_days"]
