"""Tests split from test_openmeteo_provider.py."""

from __future__ import annotations

from unittest.mock import patch

# ruff: noqa: F403, F405
from tests.data.test_openmeteo_provider_support import *


class TestOpenMeteoProviderInit:
    """Test OpenMeteoProvider initialization."""

    def test_init_sets_all_required_attributes(self, mock_api_config: Mock) -> None:
        """Initialization sets all required attributes."""
        provider = OpenMeteoProvider()

        assert provider.provider_id == "open-meteo"
        assert provider.display_name == "Open-Meteo API"
        assert provider.base_url == "https://archive.open-meteo.com/v1/era5"
        assert provider.max_days_per_request == 90
        assert provider.batch_delay == 0.6

    def test_init_sets_session_headers(self, mock_api_config: Mock) -> None:
        """Initialization sets correct session headers."""
        provider = OpenMeteoProvider()

        assert provider.session.headers["User-Agent"] == "test-agent"
        assert provider.session.headers["Accept"] == "application/json"


class TestValidateProvider:
    """Test validate_provider method."""

    def test_validate_provider_always_returns_true(self, provider: OpenMeteoProvider) -> None:
        """validate_provider always returns True (Open-Meteo has no API key)."""
        assert provider.validate_provider() is True


class TestGetWeatherData:
    """Test get_weather_data method."""

    def test_get_weather_data_calls_single_for_short_period(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data calls single request for period <= 90 days."""
        with patch.object(provider, "get_weather_data_single", return_value=[]) as mock_single:
            provider.get_weather_data(47.5, 19.0, "2020-01-01", "2020-03-31")

            mock_single.assert_called_once_with(47.5, 19.0, "2020-01-01", "2020-03-31")

    def test_get_weather_data_calls_batched_for_long_period(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data calls batched request for period > 90 days."""
        with patch.object(provider, "get_weather_data_batched", return_value=[]) as mock_batched:
            provider.get_weather_data(47.5, 19.0, "2020-01-01", "2020-12-31")

            mock_batched.assert_called_once_with(47.5, 19.0, "2020-01-01", "2020-12-31")

    def test_get_weather_data_calls_single_for_exactly_90_days(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data calls single request for exactly 90 days."""
        with patch.object(provider, "get_weather_data_single", return_value=[]) as mock_single:
            # Jan 1 to Mar 31 = 90 days in non-leap year
            provider.get_weather_data(47.5, 19.0, "2020-01-01", "2020-03-31")

            mock_single.assert_called_once()

    def test_get_weather_data_calls_batched_for_91_days(self, provider: OpenMeteoProvider) -> None:
        """get_weather_data calls batched request for 91 days."""
        with patch.object(provider, "get_weather_data_batched", return_value=[]) as mock_batched:
            provider.get_weather_data(47.5, 19.0, "2020-01-01", "2020-04-01")

            mock_batched.assert_called_once()


class TestGetWeatherDataSingle:
    """Test get_weather_data_single method."""

    def test_get_weather_data_single_calls_make_api_request_with_correct_params(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data_single calls _make_api_request with all required params."""
        with patch.object(provider, "_make_api_request", return_value=[]) as mock_request:
            provider.get_weather_data_single(47.5, 19.0, "2020-01-01", "2020-01-31")

            call_args = mock_request.call_args[0][0]
            assert call_args["latitude"] == 47.5
            assert call_args["longitude"] == 19.0
            assert call_args["start_date"] == "2020-01-01"
            assert call_args["end_date"] == "2020-01-31"
            assert call_args["timezone"] == "auto"
            assert call_args["models"] == "era5_seamless"
            assert "temperature_2m_max" in call_args["daily"]
            assert "precipitation_sum" in call_args["daily"]

    def test_get_weather_data_single_includes_all_required_daily_params(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data_single includes all required daily parameters."""
        with patch.object(provider, "_make_api_request", return_value=[]) as mock_request:
            provider.get_weather_data_single(47.5, 19.0, "2020-01-01", "2020-01-31")

            call_args = mock_request.call_args[0][0]
            daily_params = call_args["daily"]

            # Standard temperature params
            assert "temperature_2m_max" in daily_params
            assert "temperature_2m_min" in daily_params
            assert "temperature_2m_mean" in daily_params

            # Precipitation and wind
            assert "precipitation_sum" in daily_params
            assert "windspeed_10m_max" in daily_params
            assert "wind_gusts_10m_max" in daily_params
            assert "winddirection_10m_dominant" in daily_params

            # Extended params for extreme events
            assert "relative_humidity_2m_max" in daily_params
            assert "relative_humidity_2m_min" in daily_params
            assert "pressure_msl_max" in daily_params
            assert "pressure_msl_min" in daily_params
            assert "surface_pressure_max" in daily_params
            assert "surface_pressure_min" in daily_params
            assert "sunshine_duration" in daily_params
            assert "uv_index_max" in daily_params

    def test_get_weather_data_single_returns_api_response(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data_single returns data from API response."""
        expected_data = [{"date": "2020-01-01", "temperature_2m_max": 10.0}]
        with patch.object(provider, "_make_api_request", return_value=expected_data):
            result = provider.get_weather_data_single(47.5, 19.0, "2020-01-01", "2020-01-31")

            assert result == expected_data
