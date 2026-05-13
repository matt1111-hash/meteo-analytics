"""Weather provider base class tests."""

from __future__ import annotations

from typing import Any

import pytest
import requests
from src.infrastructure.weather.weather_provider_base import WeatherProvider

__all__ = [
    "MockWeatherProvider",
    "WeatherProvider",
    "pytest",
    "requests",
]


class MockWeatherProvider(WeatherProvider):
    """Concrete implementation of WeatherProvider for testing."""

    def get_weather_data(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
    ) -> list[dict[str, Any]]:
        """Mock implementation returning test data."""
        self._rate_limit_check()
        self._update_request_tracking()
        return [
            {
                "date": start_date,
                "temperature_2m_max": 20.0,
                "temperature_2m_min": 10.0,
            }
        ]

    def validate_provider(self) -> bool:
        """Mock implementation always returns True."""
        return True
