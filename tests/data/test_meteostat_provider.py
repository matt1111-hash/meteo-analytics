"""Tests for MeteostatProvider."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
import requests

from src.data.meteostat_provider import MeteostatProvider
from src.data.weather_types import ProviderValidationError, WeatherAPIError


@pytest.fixture
def mock_api_config() -> Mock:
    """Mock APIConfig."""
    with patch("src.data.meteostat_provider.APIConfig") as mock:
        mock.METEOSTAT_BASE = "https://meteostat.p.rapidapi.com"
        mock.USER_AGENT = "test-agent"
        mock.METEOSTAT_RATE_LIMIT = 0.1
        mock.REQUEST_TIMEOUT = 30
        yield mock


@pytest.fixture
def mock_env_with_key() -> Mock:
    """Mock environment with valid API key."""
    with patch.dict("os.environ", {"METEOSTAT_API_KEY": "a" * 32}):
        yield


@pytest.fixture
def mock_env_without_key() -> Mock:
    """Mock environment without API key."""
    with patch.dict("os.environ", {}, clear=True):
        yield


@pytest.fixture
def mock_env_with_short_key() -> Mock:
    """Mock environment with short (invalid) API key."""
    with patch.dict("os.environ", {"METEOSTAT_API_KEY": "short"}):
        yield


@pytest.fixture
def provider(mock_api_config: Mock, mock_env_with_key: Mock) -> MeteostatProvider:
    """Create MeteostatProvider with valid API key."""
    return MeteostatProvider()


@pytest.fixture
def provider_no_key(mock_api_config: Mock, mock_env_without_key: Mock) -> MeteostatProvider:
    """Create MeteostatProvider without API key."""
    return MeteostatProvider()


@pytest.fixture
def provider_short_key(
    mock_api_config: Mock, mock_env_with_short_key: Mock
) -> MeteostatProvider:
    """Create MeteostatProvider with short API key."""
    return MeteostatProvider()


class TestMeteostatProviderInit:
    """Test MeteostatProvider initialization."""

    def test_init_with_valid_key_sets_attributes(
        self, mock_api_config: Mock, mock_env_with_key: Mock
    ) -> None:
        """Initialization with valid API key sets all required attributes."""
        provider = MeteostatProvider()

        assert provider.provider_id == "meteostat"
        assert provider.display_name == "Meteostat API"
        assert provider.api_key == "a" * 32
        assert provider.base_url == "https://meteostat.p.rapidapi.com"
        assert provider.max_years_per_request == 10
        assert provider.min_request_interval == 0.1

    def test_init_without_key_sets_api_key_to_none(
        self, mock_api_config: Mock, mock_env_without_key: Mock
    ) -> None:
        """Initialization without API key sets api_key to None."""
        provider = MeteostatProvider()

        assert provider.api_key is None

    def test_init_with_short_key_sets_api_key_to_short_value(
        self, mock_api_config: Mock, mock_env_with_short_key: Mock
    ) -> None:
        """Initialization with short API key sets it anyway."""
        provider = MeteostatProvider()

        assert provider.api_key == "short"


class TestValidateProvider:
    """Test validate_provider method."""

    def test_validate_provider_returns_true_with_valid_key(
        self, provider: MeteostatProvider
    ) -> None:
        """validate_provider returns True when API key is valid."""
        assert provider.validate_provider() is True

    def test_validate_provider_returns_false_without_key(
        self, provider_no_key: MeteostatProvider
    ) -> None:
        """validate_provider returns False when API key is missing."""
        assert provider_no_key.validate_provider() is False

    def test_validate_provider_returns_false_with_short_key(
        self, provider_short_key: MeteostatProvider
    ) -> None:
        """validate_provider returns False when API key is too short."""
        assert provider_short_key.validate_provider() is False

    def test_validate_provider_returns_false_with_whitespace_key(
        self, mock_api_config: Mock
    ) -> None:
        """validate_provider returns False when API key is all whitespace."""
        with patch.dict("os.environ", {"METEOSTAT_API_KEY": "   "}):
            provider = MeteostatProvider()
            assert provider.validate_provider() is False


class TestGetWeatherData:
    """Test get_weather_data method."""

    def test_get_weather_data_raises_without_provider_key(
        self, provider_no_key: MeteostatProvider
    ) -> None:
        """get_weather_data raises ProviderValidationError when key is invalid."""
        with pytest.raises(ProviderValidationError, match="API key missing or invalid"):
            provider_no_key.get_weather_data(47.5, 19.0, "2020-01-01", "2020-01-31")

    def test_get_weather_data_calls_single_for_short_period(
        self, provider: MeteostatProvider
    ) -> None:
        """get_weather_data calls single request for period <= 10 years."""
        with patch.object(
            provider, "get_weather_data_single", return_value=[]
        ) as mock_single:
            provider.get_weather_data(47.5, 19.0, "2020-01-01", "2029-12-31")

            mock_single.assert_called_once_with(47.5, 19.0, "2020-01-01", "2029-12-31")

    def test_get_weather_data_calls_batched_for_long_period(
        self, provider: MeteostatProvider
    ) -> None:
        """get_weather_data calls batched request for period > 10 years."""
        with patch.object(provider, "get_weather_data_batched", return_value=[]) as mock_batched:
            provider.get_weather_data(47.5, 19.0, "2020-01-01", "2035-12-31")

            mock_batched.assert_called_once_with(47.5, 19.0, "2020-01-01", "2035-12-31")

    def test_get_weather_data_calls_single_for_exactly_10_years(
        self, provider: MeteostatProvider
    ) -> None:
        """get_weather_data calls single request for exactly 10 years."""
        with patch.object(
            provider, "get_weather_data_single", return_value=[]
        ) as mock_single:
            provider.get_weather_data(47.5, 19.0, "2020-01-01", "2029-12-31")

            mock_single.assert_called_once()

    def test_get_weather_data_calls_batched_for_10_years_and_one_day(
        self, provider: MeteostatProvider
    ) -> None:
        """get_weather_data calls batched request for 10 years + 1 day."""
        with patch.object(provider, "get_weather_data_batched", return_value=[]) as mock_batched:
            provider.get_weather_data(47.5, 19.0, "2020-01-01", "2030-01-01")

            mock_batched.assert_called_once()


class TestGetWeatherDataSingle:
    """Test get_weather_data_single method."""

    def test_get_weather_data_single_calls_make_api_request(
        self, provider: MeteostatProvider
    ) -> None:
        """get_weather_data_single calls _make_api_request with correct params."""
        with patch.object(provider, "_make_api_request", return_value=[]) as mock_request:
            provider.get_weather_data_single(47.5, 19.0, "2020-01-01", "2020-01-31")

            mock_request.assert_called_once_with({
                "lat": 47.5,
                "lon": 19.0,
                "start": "2020-01-01",
                "end": "2020-01-31"
            })

    def test_get_weather_data_single_returns_api_response(
        self, provider: MeteostatProvider
    ) -> None:
        """get_weather_data_single returns data from API response."""
        expected_data = [{"date": "2020-01-01", "temperature_2m_mean": 5.0}]
        with patch.object(provider, "_make_api_request", return_value=expected_data):
            result = provider.get_weather_data_single(47.5, 19.0, "2020-01-01", "2020-01-31")

            assert result == expected_data


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
                [{"date": "2030-01-01", "temperature_2m_mean": 6.0}]
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

    def test_make_api_request_calls_correct_endpoint(
        self, provider: MeteostatProvider
    ) -> None:
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

    def test_make_api_request_returns_processed_data(
        self, provider: MeteostatProvider
    ) -> None:
        """_make_api_request returns processed response data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"date": "2020-01-01", "tavg": 5.0}]
        }

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

    def test_make_api_request_raises_on_401_status(
        self, provider: MeteostatProvider
    ) -> None:
        """_make_api_request raises ProviderValidationError on 401."""
        mock_response = Mock()
        mock_response.status_code = 401

        with patch.object(provider.session, "get", return_value=mock_response):
            with pytest.raises(ProviderValidationError, match="Authentication error"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_429_status(
        self, provider: MeteostatProvider
    ) -> None:
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

    def test_make_api_request_raises_on_timeout(
        self, provider: MeteostatProvider
    ) -> None:
        """_make_api_request raises WeatherAPIError on timeout."""
        with patch.object(provider.session, "get", side_effect=requests.exceptions.Timeout()):
            with pytest.raises(WeatherAPIError, match="API timeout"):
                provider._make_api_request({})

    def test_make_api_request_raises_on_connection_error(
        self, provider: MeteostatProvider
    ) -> None:
        """_make_api_request raises WeatherAPIError on connection error."""
        with patch.object(
            provider.session, "get", side_effect=requests.exceptions.ConnectionError()
        ):
            with pytest.raises(WeatherAPIError, match="Connection error"):
                provider._make_api_request({})

    def test_make_api_request_updates_request_tracking(
        self, provider: MeteostatProvider
    ) -> None:
        """_make_api_request updates request count and last request time."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}

        with patch.object(provider.session, "get", return_value=mock_response):
            provider._make_api_request({})

            assert provider.request_count == 1
            assert provider.last_request_time > 0


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
                    "tsun": 8.0
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
        response_data = {
            "data": [
                {
                    "date": "2020-01-01",
                    "tmin": -2.0,
                    "tmax": 10.0
                }
            ]
        }

        result = provider._process_response(response_data)

        assert result[0]["apparent_temperature_max"] == 10.0
        assert result[0]["apparent_temperature_min"] == -2.0

    def test_process_response_adds_data_source_field(
        self, provider: MeteostatProvider
    ) -> None:
        """_process_response adds data_source field with provider_id."""
        response_data = {
            "data": [{"date": "2020-01-01"}]
        }

        result = provider._process_response(response_data)

        assert result[0]["data_source"] == "meteostat"

    def test_process_response_handles_missing_optional_fields(
        self, provider: MeteostatProvider
    ) -> None:
        """_process_response handles records with only some fields present."""
        response_data = {
            "data": [
                {"date": "2020-01-01", "tavg": 5.0},
                {"date": "2020-01-02", "prcp": 1.0}
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
            "data": [
                {
                    "date": "2020-01-01",
                    "tavg": None,
                    "tmin": None,
                    "tmax": None
                }
            ]
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
