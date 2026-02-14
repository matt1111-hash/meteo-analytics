"""Tests for OpenMeteoProvider."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import requests

from src.data.openmeteo_provider import OpenMeteoProvider
from src.data.weather_types import WeatherAPIError


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


class TestOpenMeteoProviderInit:
    """Test OpenMeteoProvider initialization."""

    def test_init_sets_all_required_attributes(
        self, mock_api_config: Mock
    ) -> None:
        """Initialization sets all required attributes."""
        provider = OpenMeteoProvider()

        assert provider.provider_id == "open-meteo"
        assert provider.display_name == "Open-Meteo API"
        assert provider.base_url == "https://archive.open-meteo.com/v1/era5"
        assert provider.max_days_per_request == 90
        assert provider.batch_delay == 0.6

    def test_init_sets_session_headers(
        self, mock_api_config: Mock
    ) -> None:
        """Initialization sets correct session headers."""
        provider = OpenMeteoProvider()

        assert provider.session.headers["User-Agent"] == "test-agent"
        assert provider.session.headers["Accept"] == "application/json"


class TestValidateProvider:
    """Test validate_provider method."""

    def test_validate_provider_always_returns_true(
        self, provider: OpenMeteoProvider
    ) -> None:
        """validate_provider always returns True (Open-Meteo has no API key)."""
        assert provider.validate_provider() is True


class TestGetWeatherData:
    """Test get_weather_data method."""

    def test_get_weather_data_calls_single_for_short_period(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data calls single request for period <= 90 days."""
        with patch.object(
            provider, "get_weather_data_single", return_value=[]
        ) as mock_single:
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
        with patch.object(
            provider, "get_weather_data_single", return_value=[]
        ) as mock_single:
            # Jan 1 to Mar 31 = 90 days in non-leap year
            provider.get_weather_data(47.5, 19.0, "2020-01-01", "2020-03-31")

            mock_single.assert_called_once()

    def test_get_weather_data_calls_batched_for_91_days(
        self, provider: OpenMeteoProvider
    ) -> None:
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


class TestGetWeatherDataBatched:
    """Test get_weather_data_batched method."""

    def test_get_weather_data_batched_creates_correct_batches(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data_batched creates 90-day batches correctly."""
        # 180 days = 2 batches
        batch1_data = [{"date": "2020-01-01", "temperature_2m_max": 10.0}]
        batch2_data = [{"date": "2020-03-31", "temperature_2m_max": 15.0}]

        with patch.object(provider, "get_weather_data_single") as mock_single:
            mock_single.side_effect = [batch1_data, batch2_data]

            result = provider.get_weather_data_batched(47.5, 19.0, "2020-01-01", "2020-06-28")

            assert mock_single.call_count == 2
            assert len(result) == 2

    def test_get_weather_data_batched_handles_365_day_period(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data_batched handles full year with correct batch count."""
        with patch.object(provider, "get_weather_data_single", return_value=[]):
            provider.get_weather_data_batched(47.5, 19.0, "2020-01-01", "2020-12-31")

            # 365 days / 89 days per batch + 1 = ~5 batches (since max-1=89)
            # Jan 1 - Mar 30 (90 days), Mar 31 - Jun 28 (90 days), Jun 29 - Sep 26 (90 days), Sep 27 - Dec 25 (90 days), Dec 26 - Dec 31 (6 days)
            assert provider.get_weather_data_single.call_count == 5

    def test_get_weather_data_batched_sleeps_between_batches(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data_batched sleeps between batches except last."""
        with patch.object(provider, "get_weather_data_single", return_value=[]):
            with patch("time.sleep") as mock_sleep:
                provider.get_weather_data_batched(47.5, 19.0, "2020-01-01", "2020-12-31")

                # 5 batches, 4 sleeps between them
                assert mock_sleep.call_count == 4

    def test_get_weather_data_batched_continues_on_weather_api_error(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data_batched continues when one batch fails with WeatherAPIError."""
        with patch.object(provider, "get_weather_data_single") as mock_single:
            # First batch fails, second succeeds
            mock_single.side_effect = [
                WeatherAPIError("API error"),
                [{"date": "2020-03-31", "temperature_2m_max": 15.0}]
            ]

            result = provider.get_weather_data_batched(47.5, 19.0, "2020-01-01", "2020-06-28")

            # Should return only second batch data
            assert len(result) == 1
            assert result[0]["date"] == "2020-03-31"

    def test_get_weather_data_batched_returns_sorted_results(
        self, provider: OpenMeteoProvider
    ) -> None:
        """get_weather_data_batched returns results sorted by date."""
        batch1 = [{"date": "2020-03-31"}]
        batch2 = [{"date": "2020-01-01"}]

        with patch.object(provider, "get_weather_data_single") as mock_single:
            mock_single.side_effect = [batch1, batch2]

            result = provider.get_weather_data_batched(47.5, 19.0, "2020-01-01", "2020-06-28")

            assert result[0]["date"] == "2020-01-01"
            assert result[1]["date"] == "2020-03-31"


class TestGenerateBatches:
    """Test _generate_batches method."""

    def test_generate_batches_creates_single_batch_for_short_period(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_generate_batches creates single batch for period < 90 days."""
        start = datetime(2020, 1, 1)
        end = datetime(2020, 3, 30)  # 89 days < 90

        batches = provider._generate_batches(start, end)

        assert len(batches) == 1
        assert batches[0][0] == start
        assert batches[0][1] == end

    def test_generate_batches_creates_multiple_batches_for_long_period(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_generate_batches creates multiple 90-day batches."""
        start = datetime(2020, 1, 1)
        end = datetime(2020, 12, 31)  # 365 days

        batches = provider._generate_batches(start, end)

        # 365 days requires 5 batches (max_days_per_request - 1 = 89 days per batch)
        assert len(batches) == 5

        # Check first batch: Jan 1 - Mar 30 (90 days inclusive, using timedelta(days=89))
        assert batches[0][0] == datetime(2020, 1, 1)
        assert batches[0][1] == datetime(2020, 3, 30)

    def test_generate_batches_handles_exact_90_day_multiple(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_generate_batches handles exact 90-day period correctly."""
        start = datetime(2020, 1, 1)
        end = datetime(2020, 3, 30)  # 89 days from Jan 1 (within 90-day limit)

        batches = provider._generate_batches(start, end)

        assert len(batches) == 1

    def test_generate_batches_creates_correct_overlap_free_intervals(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_generate_batches creates non-overlapping intervals."""
        start = datetime(2020, 1, 1)
        end = datetime(2020, 3, 31)  # 90 days = 2 batches

        batches = provider._generate_batches(start, end)

        assert len(batches) == 2

        # First batch: Jan 1 - Mar 30 (89 days using timedelta)
        assert batches[0][0] == datetime(2020, 1, 1)
        assert batches[0][1] == datetime(2020, 3, 30)

        # Second batch: Mar 31 - Mar 31 (1 day)
        assert batches[1][0] == datetime(2020, 3, 31)
        assert batches[1][1] == datetime(2020, 3, 31)


class TestMakeApiRequest:
    """Test _make_api_request method."""

    def test_make_api_request_calls_correct_endpoint(
        self, provider: OpenMeteoProvider
    ) -> None:
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

    def test_make_api_request_returns_processed_data(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_make_api_request returns processed response data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "daily": {
                "time": ["2020-01-01"],
                "temperature_2m_max": [10.0]
            }
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

        with patch.object(provider.session, "get", return_value=mock_response):
            with pytest.raises(WeatherAPIError, match="Invalid response"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_400_status(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_make_api_request raises WeatherAPIError on 400."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid parameters"

        with patch.object(provider.session, "get", return_value=mock_response):
            with pytest.raises(WeatherAPIError, match="Bad request"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_429_status(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_make_api_request raises WeatherAPIError on 429."""
        mock_response = Mock()
        mock_response.status_code = 429

        with patch.object(provider.session, "get", return_value=mock_response):
            with pytest.raises(WeatherAPIError, match="Rate limit exceeded"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_other_error_status(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_make_api_request raises WeatherAPIError on non-200/400/429 status."""
        mock_response = Mock()
        mock_response.status_code = 500

        with patch.object(provider.session, "get", return_value=mock_response):
            with pytest.raises(WeatherAPIError, match="API error: 500"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_timeout(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_make_api_request raises WeatherAPIError on timeout."""
        with patch.object(provider.session, "get", side_effect=requests.exceptions.Timeout()):
            with pytest.raises(WeatherAPIError, match="API timeout"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_connection_error(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_make_api_request raises WeatherAPIError on connection error."""
        with patch.object(
            provider.session, "get", side_effect=requests.exceptions.ConnectionError()
        ):
            with pytest.raises(WeatherAPIError, match="Connection error"):
                provider._make_api_request({})

    def test_make_api_request_updates_request_tracking(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_make_api_request updates request count and last request time."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"daily": {"time": []}}

        with patch.object(provider.session, "get", return_value=mock_response):
            provider._make_api_request({})

            assert provider.request_count == 1
            assert provider.last_request_time > 0


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
                "temperature_2m_max": [10.0, 12.0]
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
                "precipitation_sum": [0.0, 1.5]
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
        response_data = {
            "daily": {
                "time": ["2020-01-01"]
            }
        }

        result = provider._process_response(response_data)

        assert result[0]["data_source"] == "open-meteo"

    def test_process_response_handles_missing_optional_metrics(
        self, provider: OpenMeteoProvider
    ) -> None:
        """_process_response handles records with only some metrics present."""
        response_data = {
            "daily": {
                "time": ["2020-01-01", "2020-01-02"],
                "temperature_2m_max": [10.0, None]
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
                "temperature_2m_max": [10.0, 12.0]  # Only 2 values for 3 dates
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
