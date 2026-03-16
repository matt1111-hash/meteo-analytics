"""Tests split from test_openmeteo_provider.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_openmeteo_provider_support import *


class TestProcessResponse:
    """Test _process_response method."""

    def test_process_response_returns_empty_list_for_no_dates(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_process_response returns empty list when time field is empty."""
        result = provider._process_response({"daily": {"time": []}})

        assert result == []

    def test_process_response_returns_empty_list_for_missing_daily(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_process_response returns empty list when daily field is missing."""
        result = provider._process_response({})

        assert result == []

    def test_process_response_creates_records_for_each_date(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_process_response creates one record per date."""
        response_data = {
            "daily": {
                "time": ["2020-01-01", "2020-01-02"],
                "temperature_2m_max": [10.0, 12.0],
            }
        }

        result = provider._process_response(response_data)

        assert len(result) == 2

    def test_process_response_maps_all_metrics_to_dates(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_process_response correctly maps metrics to their corresponding dates."""
        response_data = {
            "daily": {
                "time": ["2020-01-01", "2020-01-02"],
                "temperature_2m_max": [10.0, 12.0],
                "temperature_2m_min": [-2.0, 0.0],
                "precipitation_sum": [0.0, 1.5],
            }
        }

        result = provider._process_response(response_data)

        assert result[0]["date"] == "2020-01-01"
        assert result[0]["temperature_2m_max"] == 10.0
        assert result[0]["temperature_2m_min"] == -2.0
        assert result[0]["precipitation_sum"] == 0.0

        assert result[1]["date"] == "2020-01-02"
        assert result[1]["temperature_2m_max"] == 12.0
        assert result[1]["temperature_2m_min"] == 0.0
        assert result[1]["precipitation_sum"] == 1.5

    def test_process_response_adds_data_source_field(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_process_response adds data_source field with provider_id."""
        response_data = {"daily": {"time": ["2020-01-01"]}}

        result = provider._process_response(response_data)

        assert result[0]["data_source"] == "open-meteo"

    def test_process_response_handles_missing_optional_metrics(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_process_response handles records with only some metrics present."""
        response_data = {
            "daily": {
                "time": ["2020-01-01", "2020-01-02"],
                "temperature_2m_max": [10.0, None],
            }
        }

        result = provider._process_response(response_data)

        assert len(result) == 2
        assert result[0]["temperature_2m_max"] == 10.0
        assert result[1]["temperature_2m_max"] is None

    def test_process_response_handles_metric_lists_shorter_than_dates(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_process_response handles metric lists shorter than date list."""
        response_data = {
            "daily": {
                "time": ["2020-01-01", "2020-01-02", "2020-01-03"],
                "temperature_2m_max": [10.0, 12.0],  # Only 2 values for 3 dates
            }
        }

        result = provider._process_response(response_data)

        assert len(result) == 3
        assert result[0]["temperature_2m_max"] == 10.0
        assert result[1]["temperature_2m_max"] == 12.0
        assert "temperature_2m_max" not in result[2]  # No value available


class TestInheritedMethods:
    """Test inherited methods from WeatherProvider base class."""

    def test_get_request_count_returns_zero_initially(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_request_count returns 0 for new provider."""
        assert provider.get_request_count() == 0

    def test_get_request_count_increments_after_requests(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_request_count increments after API requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"daily": {"time": []}}

        with patch.object(provider.session, "get", return_value=mock_response):
            provider._make_api_request({})
            provider._make_api_request({})

        assert provider.get_request_count() == 2

    def test_reset_request_count_clears_counter(
        self, provider: OpenMeteoProvider
    ) -> None:
        """reset_request_count sets request count to 0."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"daily": {"time": []}}

        with patch.object(provider.session, "get", return_value=mock_response):
            provider._make_api_request({})

        assert provider.get_request_count() == 1

        provider.reset_request_count()
        assert provider.get_request_count() == 0
