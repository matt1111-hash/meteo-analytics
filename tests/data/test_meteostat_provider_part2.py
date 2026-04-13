"""Tests split from test_meteostat_provider.py."""

from __future__ import annotations

from unittest.mock import patch

# ruff: noqa: F403, F405
from tests.data.test_meteostat_provider_support import *


class TestGetWeatherDataBatched:
    """Test get_weather_data_batched method."""

    def test_get_weather_data_batched_creates_correct_batches(
        self, provider: MeteostatProvider
    ) -> None:
        """get_weather_data_batched creates 10-year batches correctly."""
        # 15 years = 2 batches (10 years + 5 years)
        batch1_data = [{"date": "2020-01-01", "temperature_2m_mean": 5.0}]
        batch2_data = [{"date": "2030-01-01", "temperature_2m_mean": 6.0}]

        with patch.object(provider, "get_weather_data_single") as mock_single:
            mock_single.side_effect = [batch1_data, batch2_data]

            result = provider.get_weather_data_batched(47.5, 19.0, "2020-01-01", "2034-12-31")

            assert mock_single.call_count == 2
            assert len(result) == 2

    def test_get_weather_data_batched_handles_20_year_period(
        self, provider: MeteostatProvider
    ) -> None:
        """get_weather_data_batched handles 20-year period with 2 batches."""
        with patch.object(provider, "get_weather_data_single", return_value=[]):
            provider.get_weather_data_batched(47.5, 19.0, "2020-01-01", "2039-12-31")

            # 20 years = 2 batches
            assert provider.get_weather_data_single.call_count == 2

    def test_get_weather_data_batched_sleeps_between_batches(
        self, provider: MeteostatProvider
    ) -> None:
        """get_weather_data_batched sleeps between batches except last."""
        with patch.object(provider, "get_weather_data_single", return_value=[]):
            with patch("time.sleep") as mock_sleep:
                provider.get_weather_data_batched(47.5, 19.0, "2020-01-01", "2034-12-31")

                # 2 batches, 1 sleep between them
                mock_sleep.assert_called_once_with(0.1)

    def test_get_weather_data_batched_continues_on_batch_error(
        self, provider: MeteostatProvider
    ) -> None:
        """get_weather_data_batched continues when one batch fails."""
        with patch.object(provider, "get_weather_data_single") as mock_single:
            # First batch fails, second succeeds
            mock_single.side_effect = [
                Exception("Network error"),
                [{"date": "2030-01-01", "temperature_2m_mean": 6.0}],
            ]

            result = provider.get_weather_data_batched(47.5, 19.0, "2020-01-01", "2034-12-31")

            # Should return only second batch data
            assert len(result) == 1
            assert result[0]["date"] == "2030-01-01"

    def test_get_weather_data_batched_returns_sorted_results(
        self, provider: MeteostatProvider
    ) -> None:
        """get_weather_data_batched returns results sorted by date."""
        batch1 = [{"date": "2025-01-01"}]
        batch2 = [{"date": "2015-01-01"}]

        with patch.object(provider, "get_weather_data_single") as mock_single:
            mock_single.side_effect = [batch1, batch2]

            result = provider.get_weather_data_batched(47.5, 19.0, "2015-01-01", "2025-12-31")

            assert result[0]["date"] == "2015-01-01"
            assert result[1]["date"] == "2025-01-01"


class TestMakeApiRequest:
    """Test _make_api_request method."""

    def test_make_api_request_calls_correct_endpoint(self, provider: MeteostatProvider) -> None:
        """_make_api_request calls the correct Meteostat endpoint."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}

        with patch.object(provider.session, "get", return_value=mock_response) as mock_get:
            provider._make_api_request({"lat": 47.5})

            mock_get.assert_called_once()
            args, kwargs = mock_get.call_args
            assert "meteostat.p.rapidapi.com" in args[0]
            assert kwargs["params"] == {"lat": 47.5}
            assert kwargs["timeout"] == 30

    def test_make_api_request_returns_processed_data(self, provider: MeteostatProvider) -> None:
        """_make_api_request returns processed response data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"date": "2020-01-01", "tavg": 5.0}]}

        with patch.object(provider.session, "get", return_value=mock_response):
            result = provider._make_api_request({})

            assert len(result) == 1
            assert result[0]["date"] == "2020-01-01"

    def test_make_api_request_raises_on_missing_data_field(
        self, provider: MeteostatProvider
    ) -> None:
        """_make_api_request raises WeatherAPIError when response lacks data field."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "Something went wrong"}

        with patch.object(provider.session, "get", return_value=mock_response):
            with pytest.raises(WeatherAPIError, match="Invalid response"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_401_status(self, provider: MeteostatProvider) -> None:
        """_make_api_request raises ProviderValidationError on 401."""
        mock_response = Mock()
        mock_response.status_code = 401

        with patch.object(provider.session, "get", return_value=mock_response):
            with pytest.raises(ProviderValidationError, match="Authentication error"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_429_status(self, provider: MeteostatProvider) -> None:
        """_make_api_request raises WeatherAPIError on 429."""
        mock_response = Mock()
        mock_response.status_code = 429

        with patch.object(provider.session, "get", return_value=mock_response):
            with pytest.raises(WeatherAPIError, match="Rate limit exceeded"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_other_error_status(
        self, provider: MeteostatProvider
    ) -> None:
        """_make_api_request raises WeatherAPIError on non-200/401/429 status."""
        mock_response = Mock()
        mock_response.status_code = 500

        with patch.object(provider.session, "get", return_value=mock_response):
            with pytest.raises(WeatherAPIError, match="API error: 500"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_timeout(self, provider: MeteostatProvider) -> None:
        """_make_api_request raises WeatherAPIError on timeout."""
        with patch.object(provider.session, "get", side_effect=requests.exceptions.Timeout()):
            with pytest.raises(WeatherAPIError, match="API timeout"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_connection_error(self, provider: MeteostatProvider) -> None:
        """_make_api_request raises WeatherAPIError on connection error."""
        with patch.object(
            provider.session, "get", side_effect=requests.exceptions.ConnectionError()
        ):
            with pytest.raises(WeatherAPIError, match="Connection error"):
                provider._make_api_request({})

    def test_make_api_request_updates_request_tracking(self, provider: MeteostatProvider) -> None:
        """_make_api_request updates request count and last request time."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}

        with patch.object(provider.session, "get", return_value=mock_response):
            provider._make_api_request({})

            assert provider.request_count == 1
            assert provider.last_request_time > 0
