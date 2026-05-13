#!/usr/bin/env python3
"""
Weather Client - Data Types and Exceptions
Global Weather Analyzer project

Part of the weather_client refactoring - split into focused modules.
"""

from dataclasses import dataclass


@dataclass
class WeatherData:
    """
    Weather data structure - multi-year ready.

    Contains daily weather metrics for a single day.
    """

    date: str
    temperature_2m_max: float | None = None
    temperature_2m_min: float | None = None
    temperature_2m_mean: float | None = None
    apparent_temperature_max: float | None = None
    apparent_temperature_min: float | None = None
    precipitation_sum: float | None = None
    rain_sum: float | None = None
    snowfall_sum: float | None = None
    precipitation_hours: int | None = None
    windspeed_10m_max: float | None = None
    wind_gusts_10m_max: float | None = None
    winddirection_10m_dominant: float | None = None
    shortwave_radiation_sum: float | None = None
    sunshine_duration: float | None = None
    uv_index_max: float | None = None
    uv_index_clear_sky_max: float | None = None

    # Provider tracking
    data_source: str | None = None

    # Calculated values
    temperature_range: float | None = None

    def __post_init__(self):
        """Calculate computed values automatically."""
        if self.temperature_2m_max is not None and self.temperature_2m_min is not None:
            self.temperature_range = self.temperature_2m_max - self.temperature_2m_min

        if (
            self.temperature_2m_max is not None
            and self.temperature_2m_min is not None
            and self.temperature_2m_mean is None
        ):
            self.temperature_2m_mean = (self.temperature_2m_max + self.temperature_2m_min) / 2


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
    "ProviderNotAvailableError",
    "ProviderValidationError",
    "WeatherAPIError",
    "WeatherData",
]
