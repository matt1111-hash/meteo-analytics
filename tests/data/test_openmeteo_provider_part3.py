"""Tests split from test_openmeteo_provider.py."""

from __future__ import annotations

from unittest.mock import patch

# ruff: noqa: F403, F405
from tests.data.test_openmeteo_provider_support import *


class TestMakeApiRequest:
    """Test _make_api_request method."""

    def test_make_api_request_calls_correct_endpoint(self, provider: OpenMeteoProvider) -> None:
        """_make_api_request calls the correct Open-Meteo endpoint."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"daily": {"time": []}}

        with patch.object(provider.session, "get", return_value=mock_response) as mock_get:
            provider._make_api_request({"latitude": 47.5})

            mock_get.assert_called_once()
            args, kwargs = mock_get.call_args
            assert "archive.open-meteo.com" in args[0]
            assert kwargs["params"] == {"latitude": 47.5}
            assert kwargs["timeout"] == 30

    def test_make_api_request_returns_processed_data(self, provider: OpenMeteoProvider) -> None:
        """_make_api_request returns processed response data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "daily": {"time": ["2020-01-01"], "temperature_2m_max": [10.0]}
        }

        with patch.object(provider.session, "get", return_value=mock_response):
            result = provider._make_api_request({})

            assert len(result) == 1
            assert result[0]["date"] == "2020-01-01"

    def test_make_api_request_raises_on_missing_daily_field(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_make_api_request raises WeatherAPIError when response lacks daily field."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "Something went wrong"}

        with patch.object(provider.session, "get", return_value=mock_response):  # noqa: SIM117
            with pytest.raises(WeatherAPIError, match="Invalid response"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_400_status(self, provider: OpenMeteoProvider) -> None:
        """_make_api_request raises WeatherAPIError on 400."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid parameters"

        with patch.object(provider.session, "get", return_value=mock_response):  # noqa: SIM117
            with pytest.raises(WeatherAPIError, match="Bad request"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_429_status(self, provider: OpenMeteoProvider) -> None:
        """_make_api_request raises WeatherAPIError on 429."""
        mock_response = Mock()
        mock_response.status_code = 429

        with patch.object(provider.session, "get", return_value=mock_response):  # noqa: SIM117
            with pytest.raises(WeatherAPIError, match="Rate limit exceeded"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_other_error_status(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_make_api_request raises WeatherAPIError on non-200/400/429 status."""
        mock_response = Mock()
        mock_response.status_code = 500

        with patch.object(provider.session, "get", return_value=mock_response):  # noqa: SIM117
            with pytest.raises(WeatherAPIError, match="API error: 500"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_timeout(self, provider: OpenMeteoProvider) -> None:
        """_make_api_request raises WeatherAPIError on timeout."""
        with patch.object(provider.session, "get", side_effect=requests.exceptions.Timeout()):  # noqa: SIM117
            with pytest.raises(WeatherAPIError, match="API timeout"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_connection_error(self, provider: OpenMeteoProvider) -> None:
        """_make_api_request raises WeatherAPIError on connection error."""
        with patch.object(  # noqa: SIM117
            provider.session, "get", side_effect=requests.exceptions.ConnectionError()
        ):
            with pytest.raises(WeatherAPIError, match="Connection error"):
                provider._make_api_request({})

    def test_make_api_request_updates_request_tracking(self, provider: OpenMeteoProvider) -> None:
        """_make_api_request updates request count and last request time."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"daily": {"time": []}}

        with patch.object(provider.session, "get", return_value=mock_response):
            provider._make_api_request({})

            assert provider.request_count == 1
            assert provider.last_request_time > 0
