#!/usr/bin/env python3
"""
Weather Client - Data Types and Exceptions
Global Weather Analyzer project

Part of the weather_client refactoring - split into focused modules.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class WeatherData:
    """
    Weather data structure - multi-year ready.

    Contains daily weather metrics for a single day.
    """

    date: str
    temperature_2m_max: Optional[float] = None
    temperature_2m_min: Optional[float] = None
    temperature_2m_mean: Optional[float] = None
    apparent_temperature_max: Optional[float] = None
    apparent_temperature_min: Optional[float] = None
    precipitation_sum: Optional[float] = None
    rain_sum: Optional[float] = None
    snowfall_sum: Optional[float] = None
    precipitation_hours: Optional[int] = None
    windspeed_10m_max: Optional[float] = None
    wind_gusts_10m_max: Optional[float] = None
    winddirection_10m_dominant: Optional[float] = None
    shortwave_radiation_sum: Optional[float] = None
    sunshine_duration: Optional[float] = None
    uv_index_max: Optional[float] = None
    uv_index_clear_sky_max: Optional[float] = None

    # Provider tracking
    data_source: Optional[str] = None

    # Calculated values
    temperature_range: Optional[float] = None

    def __post_init__(self):
        """Calculate computed values automatically."""
        if self.temperature_2m_max is not None and self.temperature_2m_min is not None:
            self.temperature_range = self.temperature_2m_max - self.temperature_2m_min

        if (
            self.temperature_2m_max is not None
            and self.temperature_2m_min is not None
            and self.temperature_2m_mean is None
        ):
            self.temperature_2m_mean = (
                self.temperature_2m_max + self.temperature_2m_min
            ) / 2


class WeatherAPIError(Exception):
    """Weather API specific errors."""

    pass


class ProviderNotAvailableError(WeatherAPIError):
    """Provider not available error."""

    pass


class ProviderValidationError(WeatherAPIError):
    """Provider validation error."""

    pass


__all__ = [
    "WeatherData",
    "WeatherAPIError",
    "ProviderNotAvailableError",
    "ProviderValidationError",
]
