"""Tests for MeteostatProvider."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from src.data.meteostat_provider import MeteostatProvider


@pytest.fixture
def mock_api_config() -> Mock:
    """Mock APIConfig."""
    with patch("src.data.meteostat_provider.APIConfig") as mock:
        mock.METEOSTAT_BASE = "https://meteostat.p.rapidapi.com"
        mock.USER_AGENT = "test-agent"
        mock.METEOSTAT_RATE_LIMIT = 0.1
        mock.REQUEST_TIMEOUT = 30
        yield mock


@pytest.fixture
def mock_env_with_key() -> Mock:
    """Mock environment with valid API key."""
    with patch.dict("os.environ", {"METEOSTAT_API_KEY": "a" * 32}):
        yield


@pytest.fixture
def mock_env_without_key() -> Mock:
    """Mock environment without API key."""
    with patch.dict("os.environ", {}, clear=True):
        yield


@pytest.fixture
def mock_env_with_short_key() -> Mock:
    """Mock environment with short (invalid) API key."""
    with patch.dict("os.environ", {"METEOSTAT_API_KEY": "short"}):
        yield


@pytest.fixture
def provider(mock_api_config: Mock, mock_env_with_key: Mock) -> MeteostatProvider:
    """Create MeteostatProvider with valid API key."""
    return MeteostatProvider()


@pytest.fixture
def provider_no_key(mock_api_config: Mock, mock_env_without_key: Mock) -> MeteostatProvider:
    """Create MeteostatProvider without API key."""
    return MeteostatProvider()


@pytest.fixture
def provider_short_key(mock_api_config: Mock, mock_env_with_short_key: Mock) -> MeteostatProvider:
    """Create MeteostatProvider with short API key."""
    return MeteostatProvider()
