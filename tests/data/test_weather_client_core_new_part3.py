"""Tests split from test_weather_client_core_new.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_weather_client_core_new_support import *


class TestGetWeatherData:
    """Test get_weather_data method."""

    def test_get_weather_data_returns_data_from_primary_provider(
        self, client: WeatherClient
    ) -> None:
        """get_weather_data returns data from primary provider."""
        client.providers["open-meteo"].get_weather_data.return_value = [
            {"date": "2020-01-01", "temperature_2m_max": 10.0}
        ]

        result = client.get_weather_data(47.5, 19.0, "2020-01-01", "2020-01-31")

        assert len(result) == 1
        assert result[0]["date"] == "2020-01-01"

    def test_get_weather_data_falls_back_to_secondary_provider(
        self, client: WeatherClient
    ) -> None:
        """get_weather_data falls back to secondary provider on primary failure."""
        client.providers["open-meteo"].get_weather_data.side_effect = WeatherAPIError(
            "Primary failed"
        )
        client.providers["meteostat"].get_weather_data.return_value = [
            {"date": "2020-01-01", "temperature_2m_max": 10.0}
        ]

        result = client.get_weather_data(47.5, 19.0, "2020-01-01", "2020-01-31")

        assert len(result) == 1
        assert client.current_provider == "meteostat"

    def test_get_weather_data_raises_provider_not_available_when_all_fail(
        self, client: WeatherClient
    ) -> None:
        """get_weather_data raises ProviderNotAvailableError when all providers fail."""
        client.providers["open-meteo"].get_weather_data.side_effect = WeatherAPIError(
            "Failed"
        )
        client.providers["meteostat"].get_weather_data.side_effect = WeatherAPIError(
            "Failed"
        )

        with pytest.raises(ProviderNotAvailableError, match="All providers failed"):
            client.get_weather_data(47.5, 19.0, "2020-01-01", "2020-01-31")

    def test_get_weather_data_validates_inputs(self, client: WeatherClient) -> None:
        """get_weather_data validates input parameters."""
        with pytest.raises(ValueError, match="Invalid latitude"):
            client.get_weather_data(91, 0, "2020-01-01", "2020-01-31")

    def test_get_weather_data_updates_usage_stats(self, client: WeatherClient) -> None:
        """get_weather_data updates provider usage statistics."""
        client.providers["open-meteo"].get_weather_data.return_value = []

        client.get_weather_data(47.5, 19.0, "2020-01-01", "2020-01-31")

        assert client.provider_usage_stats.get("open-meteo") == 1

    def test_get_weather_data_with_user_override_provider(
        self, client: WeatherClient
    ) -> None:
        """get_weather_data uses user_override_provider when specified."""
        client.providers["meteostat"].get_weather_data.return_value = [
            {"date": "2020-01-01"}
        ]

        result = client.get_weather_data(
            47.5, 19.0, "2020-01-01", "2020-01-31", user_override_provider="meteostat"
        )

        assert len(result) == 1
        client.providers["meteostat"].get_weather_data.assert_called_once()

    def test_get_weather_data_handles_fallback_callbacks(
        self, client: WeatherClient
    ) -> None:
        """get_weather_data triggers fallback callbacks correctly."""
        client.preferred_provider = "open-meteo"
        fallback_callback = Mock()
        client.set_provider_fallback_callback(fallback_callback)

        client.providers["open-meteo"].get_weather_data.side_effect = WeatherAPIError(
            "Failed"
        )
        client.providers["meteostat"].get_weather_data.return_value = []

        client.get_weather_data(47.5, 19.0, "2020-01-01", "2020-01-31")

        fallback_callback.assert_called_once_with("open-meteo", "meteostat")


class TestProviderUsageStats:
    """Test provider usage statistics tracking."""

    def test_provider_usage_stats_increment_on_successful_requests(
        self, client: WeatherClient
    ) -> None:
        """Provider usage stats increment with each successful request."""
        client.providers["open-meteo"].get_weather_data.return_value = []

        client.get_weather_data(47.5, 19.0, "2020-01-01", "2020-01-31")
        client.get_weather_data(47.5, 19.0, "2020-02-01", "2020-02-28")

        assert client.provider_usage_stats.get("open-meteo") == 2

    def test_provider_usage_stats_track_multiple_providers(
        self, client: WeatherClient
    ) -> None:
        """Provider usage stats track usage across multiple providers."""
        client.providers["open-meteo"].get_weather_data.return_value = []
        client.providers["meteostat"].get_weather_data.return_value = []

        client.get_weather_data(
            47.5, 19.0, "2020-01-01", "2020-01-31", user_override_provider="open-meteo"
        )
        client.get_weather_data(
            47.5, 19.0, "2020-02-01", "2020-02-28", user_override_provider="meteostat"
        )
        client.get_weather_data(
            47.5, 19.0, "2020-03-01", "2020-03-31", user_override_provider="open-meteo"
        )

        assert client.provider_usage_stats.get("open-meteo") == 2
        assert client.provider_usage_stats.get("meteostat") == 1
