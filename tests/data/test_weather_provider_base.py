"""Weather provider base class tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest
import requests

from src.data.weather_provider_base import WeatherProvider


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


class TestWeatherProviderInitialization:
    """Tests for WeatherProvider initialization."""

    def test_initialization_sets_attributes(self) -> None:
        """Provider is initialized with correct attributes."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        assert provider.provider_id == "test_provider"
        assert provider.display_name == "Test Provider"

    def test_initialization_creates_session(self) -> None:
        """A requests Session is created on initialization."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        assert isinstance(provider.session, requests.Session)

    def test_initialization_sets_request_count_to_zero(self) -> None:
        """Request count is initialized to zero."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        assert provider.request_count == 0

    def test_initialization_sets_last_request_time_to_zero(self) -> None:
        """Last request time is initialized to zero."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        assert provider.last_request_time == 0

    def test_initialization_sets_default_min_request_interval(self) -> None:
        """Default minimum request interval is set."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        assert provider.min_request_interval == 0.1


class TestRateLimitCheck:
    """Tests for _rate_limit_check method."""

    def test_no_delay_when_sufficient_time_passed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """No sleep when time since last request is sufficient."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        provider.last_request_time = 0.0
        provider.min_request_interval = 0.1

        slept: dict[str, float] = {}

        def fake_sleep(delay: float) -> None:
            slept["value"] = delay

        monkeypatch.setattr("time.sleep", fake_sleep)
        monkeypatch.setattr("time.time", lambda: 1.0)  # 1 second passed

        provider._rate_limit_check()
        assert "value" not in slept

    def test_sleep_when_insufficient_time_passed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Sleep is called when time since last request is insufficient."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        provider.last_request_time = 0.0
        provider.min_request_interval = 0.5

        slept: dict[str, float] = {}

        def fake_sleep(delay: float) -> None:
            slept["value"] = delay

        monkeypatch.setattr("time.sleep", fake_sleep)
        monkeypatch.setattr("time.time", lambda: 0.2)  # Only 0.2 seconds passed

        provider._rate_limit_check()
        assert slept["value"] == pytest.approx(0.3)  # 0.5 - 0.2 = 0.3

    def test_exact_boundary_no_sleep(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """No sleep when time since last request equals min interval."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        provider.last_request_time = 0.0
        provider.min_request_interval = 0.5

        slept: dict[str, float] = {}

        def fake_sleep(delay: float) -> None:
            slept["value"] = delay

        monkeypatch.setattr("time.sleep", fake_sleep)
        monkeypatch.setattr("time.time", lambda: 0.5)  # Exactly 0.5 seconds passed

        provider._rate_limit_check()
        assert "value" not in slept


class TestUpdateRequestTracking:
    """Tests for _update_request_tracking method."""

    def test_request_count_increments(self) -> None:
        """Request count is incremented."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        initial_count = provider.request_count
        provider._update_request_tracking()
        assert provider.request_count == initial_count + 1

    def test_last_request_time_is_updated(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Last request time is set to current time."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        current_time = 12345.67

        monkeypatch.setattr("time.time", lambda: current_time)
        provider._update_request_tracking()
        assert provider.last_request_time == current_time


class TestGetRequestCount:
    """Tests for get_request_count method."""

    def test_get_request_count_returns_current_count(self) -> None:
        """get_request_count returns the current request count."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        provider.request_count = 42
        assert provider.get_request_count() == 42

    def test_get_request_count_after_updates(self) -> None:
        """get_request_count reflects updates to request_count."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        assert provider.get_request_count() == 0
        provider._update_request_tracking()
        assert provider.get_request_count() == 1
        provider._update_request_tracking()
        assert provider.get_request_count() == 2


class TestResetRequestCount:
    """Tests for reset_request_count method."""

    def test_reset_request_count_sets_to_zero(self) -> None:
        """reset_request_count resets count to zero."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        provider.request_count = 100
        provider.reset_request_count()
        assert provider.request_count == 0

    def test_reset_request_count_when_already_zero(self) -> None:
        """reset_request_count works when count is already zero."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        assert provider.request_count == 0
        provider.reset_request_count()
        assert provider.request_count == 0


class TestGetWeatherData:
    """Tests for get_weather_data method."""

    def test_get_weather_data_returns_data(self) -> None:
        """get_weather_data returns weather data."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        result = provider.get_weather_data(
            latitude=47.4979,
            longitude=19.0402,
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        assert isinstance(result, list)
        assert len(result) > 0
        assert "date" in result[0]

    def test_get_weather_data_calls_rate_limit_check(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """get_weather_data calls _rate_limit_check."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )

        with patch.object(provider, "_rate_limit_check") as mock_check:
            provider.get_weather_data(
                latitude=47.4979,
                longitude=19.0402,
                start_date="2024-01-01",
                end_date="2024-01-31",
            )
            mock_check.assert_called_once()

    def test_get_weather_data_updates_tracking(self) -> None:
        """get_weather_data updates request tracking."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        initial_count = provider.get_request_count()
        provider.get_weather_data(
            latitude=47.4979,
            longitude=19.0402,
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        assert provider.get_request_count() == initial_count + 1


class TestValidateProvider:
    """Tests for validate_provider method."""

    def test_validate_provider_returns_bool(self) -> None:
        """validate_provider returns a boolean."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        result = provider.validate_provider()
        assert isinstance(result, bool)

    def test_validate_provider_mock_returns_true(self) -> None:
        """Mock provider validation returns True."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        assert provider.validate_provider() is True


class TestAbstractMethods:
    """Tests for abstract method enforcement."""

    def test_weather_provider_cannot_be_instantiated(self) -> None:
        """WeatherProvider ABC cannot be instantiated directly."""
        with pytest.raises(TypeError):
            WeatherProvider(  # type: ignore[abstract]
                provider_id="test", display_name="Test"
            )

    def test_concrete_implementation_can_be_instantiated(self) -> None:
        """Concrete implementation can be instantiated."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        assert provider is not None


class TestSession:
    """Tests for requests Session."""

    def test_session_persists_across_calls(self) -> None:
        """Session persists across multiple method calls."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        session1 = provider.session
        provider.get_weather_data(
            latitude=47.4979,
            longitude=19.0402,
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        session2 = provider.session
        assert session1 is session2


class TestMultipleRequests:
    """Tests for multiple request behavior."""

    def test_multiple_requests_increment_count(self) -> None:
        """Multiple requests increment count correctly."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        for _ in range(5):
            provider.get_weather_data(
                latitude=47.4979,
                longitude=19.0402,
                start_date="2024-01-01",
                end_date="2024-01-31",
            )
        assert provider.get_request_count() == 5

    def test_multiple_requests_respect_rate_limit(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Multiple requests respect rate limiting."""
        provider = MockWeatherProvider(
            provider_id="test_provider", display_name="Test Provider"
        )
        provider.min_request_interval = 0.5

        sleep_count: dict[str, int] = {"count": 0}

        def fake_sleep(delay: float) -> None:
            sleep_count["count"] += 1

        monkeypatch.setattr("time.sleep", fake_sleep)

        # First request at t=0
        monkeypatch.setattr("time.time", lambda: 0.0)
        provider.get_weather_data(
            latitude=47.4979,
            longitude=19.0402,
            start_date="2024-01-01",
            end_date="2024-01-31",
        )

        # Second request at t=0.1 (should sleep)
        monkeypatch.setattr("time.time", lambda: 0.1)
        provider.get_weather_data(
            latitude=47.4979,
            longitude=19.0402,
            start_date="2024-01-01",
            end_date="2024-01-31",
        )

        # Should have slept (at least once - _rate_limit_check is called in get_weather_data)
        assert sleep_count["count"] >= 1
