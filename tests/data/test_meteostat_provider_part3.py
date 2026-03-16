"""Tests split from test_meteostat_provider.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_meteostat_provider_support import *


class TestProcessResponse:
    """Test _process_response method."""

    def test_process_response_returns_empty_list_for_no_data(
        self, provider: MeteostatProvider
    ) -> None:
        """_process_response returns empty list when data field is empty."""
        result = provider._process_response({"data": []})

        assert result == []

    def test_process_response_maps_meteostat_fields_to_openmeteo(
        self, provider: MeteostatProvider
    ) -> None:
        """_process_response maps Meteostat field names to OpenMeteo format."""
        response_data = {
            "data": [
                {
                    "date": "2020-01-01",
                    "tavg": 5.0,
                    "tmin": -2.0,
                    "tmax": 10.0,
                    "prcp": 0.5,
                    "wspd": 15.0,
                    "wpgt": 25.0,
                    "wdir": 180.0,
                    "tsun": 8.0,
                }
            ]
        }

        result = provider._process_response(response_data)

        assert len(result) == 1
        record = result[0]
        assert record["date"] == "2020-01-01"
        assert record["temperature_2m_mean"] == 5.0
        assert record["temperature_2m_min"] == -2.0
        assert record["temperature_2m_max"] == 10.0
        assert record["precipitation_sum"] == 0.5
        assert record["windspeed_10m_max"] == 15.0
        assert record["wind_gusts_10m_max"] == 25.0
        assert record["winddirection_10m_dominant"] == 180.0
        assert record["sunshine_duration"] == 8.0

    def test_process_response_adds_apparent_temperature_fields(
        self, provider: MeteostatProvider
    ) -> None:
        """_process_response adds apparent temperature from max/min temps."""
        response_data = {"data": [{"date": "2020-01-01", "tmin": -2.0, "tmax": 10.0}]}

        result = provider._process_response(response_data)

        assert result[0]["apparent_temperature_max"] == 10.0
        assert result[0]["apparent_temperature_min"] == -2.0

    def test_process_response_adds_data_source_field(
        self, provider: MeteostatProvider
    ) -> None:
        """_process_response adds data_source field with provider_id."""
        response_data = {"data": [{"date": "2020-01-01"}]}

        result = provider._process_response(response_data)

        assert result[0]["data_source"] == "meteostat"

    def test_process_response_handles_missing_optional_fields(
        self, provider: MeteostatProvider
    ) -> None:
        """_process_response handles records with only some fields present."""
        response_data = {
            "data": [
                {"date": "2020-01-01", "tavg": 5.0},
                {"date": "2020-01-02", "prcp": 1.0},
            ]
        }

        result = provider._process_response(response_data)

        assert len(result) == 2
        assert "temperature_2m_mean" in result[0]
        assert "precipitation_sum" in result[1]

    def test_process_response_handles_null_values(
        self, provider: MeteostatProvider
    ) -> None:
        """_process_response handles null values in fields."""
        response_data = {
            "data": [{"date": "2020-01-01", "tavg": None, "tmin": None, "tmax": None}]
        }

        result = provider._process_response(response_data)

        assert len(result) == 1
        # Fields with None should not be in the output (or be None)
        assert result[0].get("temperature_2m_mean") is None


class TestInheritedMethods:
    """Test inherited methods from WeatherProvider base class."""

    def test_get_request_count_returns_zero_initially(
        self, provider: MeteostatProvider
    ) -> None:
        """get_request_count returns 0 for new provider."""
        assert provider.get_request_count() == 0

    def test_get_request_count_increments_after_requests(
        self, provider: MeteostatProvider
    ) -> None:
        """get_request_count increments after API requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}

        with patch.object(provider.session, "get", return_value=mock_response):
            provider._make_api_request({})
            provider._make_api_request({})

        assert provider.get_request_count() == 2

    def test_reset_request_count_clears_counter(
        self, provider: MeteostatProvider
    ) -> None:
        """reset_request_count sets request count to 0."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}

        with patch.object(provider.session, "get", return_value=mock_response):
            provider._make_api_request({})

        assert provider.get_request_count() == 1

        provider.reset_request_count()
        assert provider.get_request_count() == 0

    def test_rate_limit_check_sleeps_when_needed(
        self, provider: MeteostatProvider
    ) -> None:
        """_rate_limit_check sleeps when requests are too frequent."""
        provider.last_request_time = 0  # Far in the past
        provider.min_request_interval = 0.5

        current_time = 100.0
        with patch("time.time", return_value=current_time):
            provider._rate_limit_check()
            # No sleep since time since last is large

        provider.last_request_time = current_time
        with patch("time.time", return_value=current_time + 0.1):
            with patch("time.sleep") as mock_sleep:
                provider._rate_limit_check()
                assert mock_sleep.call_count == 1
                sleep_time = mock_sleep.call_args[0][0]
                assert abs(sleep_time - 0.4) < 0.01
