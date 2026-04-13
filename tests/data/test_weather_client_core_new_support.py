"""Tests for WeatherClientCore from weather_client_core.py."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from src.data.weather_client_core import WeatherClient
from src.data.weather_types import ProviderNotAvailableError, WeatherAPIError

__all__ = [
    "Mock",
    "ProviderNotAvailableError",
    "WeatherAPIError",
    "WeatherClient",
    "client",
    "mock_api_config",
    "mock_providers",
    "patch",
    "pytest",
]


@pytest.fixture
def mock_providers() -> dict[str, Mock]:
    """Mock weather providers."""
    openmeteo = Mock()
    openmeteo.validate_provider.return_value = True
    openmeteo.provider_id = "open-meteo"

    meteostat = Mock()
    meteostat.validate_provider.return_value = True
    meteostat.provider_id = "meteostat"

    return {"open-meteo": openmeteo, "meteostat": meteostat}


@pytest.fixture
def mock_api_config() -> Mock:
    """Mock APIConfig."""
    with patch("src.data.weather_client_core.APIConfig") as mock:
        mock.MAX_RETRIES = 3
        mock.OPEN_METEO_ARCHIVE = "https://archive.open-meteo.com"
        mock.METEOSTAT_BASE = "https://meteostat.p.rapidapi.com"
        yield mock


@pytest.fixture
def client(mock_api_config: Mock, mock_providers: dict[str, Mock]) -> WeatherClient:
    """Create WeatherClient with mocked providers."""
    client = WeatherClient()
    client.providers = mock_providers
    return client
