"""Tests for OpenMeteoProvider."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from src.data.openmeteo_provider import OpenMeteoProvider


@pytest.fixture
def mock_api_config() -> Mock:
    """Mock APIConfig."""
    with patch("src.data.openmeteo_provider.APIConfig") as mock:
        mock.OPEN_METEO_ARCHIVE = "https://archive.open-meteo.com/v1/era5"
        mock.USER_AGENT = "test-agent"
        mock.REQUEST_TIMEOUT = 30
        yield mock


@pytest.fixture
def provider(mock_api_config: Mock) -> OpenMeteoProvider:
    """Create OpenMeteoProvider instance."""
    return OpenMeteoProvider()
