"""Tests split from test_meteostat_provider.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_meteostat_provider_support import *


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
        with patch.object(
            provider, "get_weather_data_batched", return_value=[]
        ) as mock_batched:
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
        with patch.object(
            provider, "get_weather_data_batched", return_value=[]
        ) as mock_batched:
            provider.get_weather_data(47.5, 19.0, "2020-01-01", "2030-01-01")

            mock_batched.assert_called_once()


class TestGetWeatherDataSingle:
    """Test get_weather_data_single method."""

    def test_get_weather_data_single_calls_make_api_request(
        self, provider: MeteostatProvider
    ) -> None:
        """get_weather_data_single calls _make_api_request with correct params."""
        with patch.object(
            provider, "_make_api_request", return_value=[]
        ) as mock_request:
            provider.get_weather_data_single(47.5, 19.0, "2020-01-01", "2020-01-31")

            mock_request.assert_called_once_with(
                {"lat": 47.5, "lon": 19.0, "start": "2020-01-01", "end": "2020-01-31"}
            )

    def test_get_weather_data_single_returns_api_response(
        self, provider: MeteostatProvider
    ) -> None:
        """get_weather_data_single returns data from API response."""
        expected_data = [{"date": "2020-01-01", "temperature_2m_mean": 5.0}]
        with patch.object(provider, "_make_api_request", return_value=expected_data):
            result = provider.get_weather_data_single(
                47.5, 19.0, "2020-01-01", "2020-01-31"
            )

            assert result == expected_data
