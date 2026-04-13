"""Tests split from test_weather_provider_base.py."""

from __future__ import annotations

from unittest.mock import patch

# ruff: noqa: F403, F405
from tests.data.test_weather_provider_base_support import *


class TestGetWeatherData:
    """Tests for get_weather_data method."""

    def test_get_weather_data_returns_data(self) -> None:
        """get_weather_data returns weather data."""
        provider = MockWeatherProvider(provider_id="test_provider", display_name="Test Provider")
        result = provider.get_weather_data(
            latitude=47.4979,
            longitude=19.0402,
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        assert isinstance(result, list)
        assert len(result) > 0
        assert "date" in result[0]

    def test_get_weather_data_calls_rate_limit_check(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_weather_data calls _rate_limit_check."""
        provider = MockWeatherProvider(provider_id="test_provider", display_name="Test Provider")

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
        provider = MockWeatherProvider(provider_id="test_provider", display_name="Test Provider")
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
        provider = MockWeatherProvider(provider_id="test_provider", display_name="Test Provider")
        result = provider.validate_provider()
        assert isinstance(result, bool)

    def test_validate_provider_mock_returns_true(self) -> None:
        """Mock provider validation returns True."""
        provider = MockWeatherProvider(provider_id="test_provider", display_name="Test Provider")
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
        provider = MockWeatherProvider(provider_id="test_provider", display_name="Test Provider")
        assert provider is not None


class TestSession:
    """Tests for requests Session."""

    def test_session_persists_across_calls(self) -> None:
        """Session persists across multiple method calls."""
        provider = MockWeatherProvider(provider_id="test_provider", display_name="Test Provider")
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
        provider = MockWeatherProvider(provider_id="test_provider", display_name="Test Provider")
        for _ in range(5):
            provider.get_weather_data(
                latitude=47.4979,
                longitude=19.0402,
                start_date="2024-01-01",
                end_date="2024-01-31",
            )
        assert provider.get_request_count() == 5

    def test_multiple_requests_respect_rate_limit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Multiple requests respect rate limiting."""
        provider = MockWeatherProvider(provider_id="test_provider", display_name="Test Provider")
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
