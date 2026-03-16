"""Tests split from test_weather_provider_base.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_weather_provider_base_support import *


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
