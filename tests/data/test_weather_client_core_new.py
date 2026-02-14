"""Tests for WeatherClientCore from weather_client_core.py."""

from __future__ import annotations

from typing import Dict, List
from unittest.mock import Mock, patch

import pytest

from src.data.weather_client_core import WeatherClient
from src.data.weather_types import ProviderNotAvailableError, WeatherAPIError


@pytest.fixture
def mock_providers() -> Dict[str, Mock]:
    """Mock weather providers."""
    openmeteo = Mock()
    openmeteo.validate_provider.return_value = True
    openmeteo.provider_id = "open-meteo"

    meteostat = Mock()
    meteostat.validate_provider.return_value = True
    meteostat.provider_id = "meteostat"

    return {"open-meteo": openmeteo, "meteostat": meteostat}


@pytest.fixture
def mock_api_config() -> Mock:
    """Mock APIConfig."""
    with patch("src.data.weather_client_core.APIConfig") as mock:
        mock.MAX_RETRIES = 3
        mock.OPEN_METEO_ARCHIVE = "https://archive.open-meteo.com"
        mock.METEOSTAT_BASE = "https://meteostat.p.rapidapi.com"
        yield mock


@pytest.fixture
def client(mock_api_config: Mock, mock_providers: Dict[str, Mock]) -> WeatherClient:
    """Create WeatherClient with mocked providers."""
    client = WeatherClient()
    client.providers = mock_providers
    return client


class TestWeatherClientInit:
    """Test WeatherClient initialization."""

    def test_init_with_default_preferred_provider(
        self, mock_api_config: Mock
    ) -> None:
        """Initialization with default preferred_provider='auto'."""
        client = WeatherClient()

        assert client.preferred_provider == "auto"
        assert client.current_provider is None
        assert isinstance(client.provider_usage_stats, dict)
        assert "open-meteo" in client.providers
        assert "meteostat" in client.providers
        assert client.max_retries == 3
        assert client.retry_delay == 1.0

    def test_init_with_custom_preferred_provider(
        self, mock_api_config: Mock
    ) -> None:
        """Initialization with custom preferred_provider."""
        client = WeatherClient(preferred_provider="open-meteo")

        assert client.preferred_provider == "open-meteo"


class TestSetProviderChangeCallback:
    """Test set_provider_change_callback method."""

    def test_set_provider_change_callback_sets_callback(
        self, client: WeatherClient
    ) -> None:
        """set_provider_change_callback sets the callback function."""
        callback = Mock()
        client.set_provider_change_callback(callback)

        assert client.provider_change_callback == callback

    def test_set_provider_fallback_callback_sets_callback(
        self, client: WeatherClient
    ) -> None:
        """set_provider_fallback_callback sets the callback function."""
        callback = Mock()
        client.set_provider_fallback_callback(callback)

        assert client.provider_fallback_callback == callback


class TestValidateInputs:
    """Test _validate_inputs method."""

    def test_validate_inputs_accepts_valid_coordinates(
        self, client: WeatherClient
    ) -> None:
        """_validate_inputs accepts valid latitude and longitude."""
        # Should not raise
        client._validate_inputs(47.5, 19.0, "2020-01-01", "2020-01-31")

    def test_validate_inputs_accepts_boundary_values(
        self, client: WeatherClient
    ) -> None:
        """_validate_inputs accepts boundary coordinate values."""
        # Should not raise
        client._validate_inputs(-90, -180, "2020-01-01", "2020-01-31")
        client._validate_inputs(90, 180, "2020-01-01", "2020-01-31")

    def test_validate_inputs_rejects_invalid_latitude(
        self, client: WeatherClient
    ) -> None:
        """_validate_inputs raises ValueError for invalid latitude."""
        with pytest.raises(ValueError, match="Invalid latitude"):
            client._validate_inputs(91, 0, "2020-01-01", "2020-01-31")

        with pytest.raises(ValueError, match="Invalid latitude"):
            client._validate_inputs(-91, 0, "2020-01-01", "2020-01-31")

    def test_validate_inputs_rejects_invalid_longitude(
        self, client: WeatherClient
    ) -> None:
        """_validate_inputs raises ValueError for invalid longitude."""
        with pytest.raises(ValueError, match="Invalid longitude"):
            client._validate_inputs(0, 181, "2020-01-01", "2020-01-31")

        with pytest.raises(ValueError, match="Invalid longitude"):
            client._validate_inputs(0, -181, "2020-01-01", "2020-01-31")

    def test_validate_inputs_rejects_invalid_date_format(
        self, client: WeatherClient
    ) -> None:
        """_validate_inputs raises ValueError for invalid date format."""
        with pytest.raises(ValueError, match="Invalid date format"):
            client._validate_inputs(47.5, 19.0, "01-01-2020", "2020-01-31")

        with pytest.raises(ValueError, match="Invalid date format"):
            client._validate_inputs(47.5, 19.0, "2020/01/01", "2020-01-31")

    def test_validate_inputs_rejects_start_after_end(
        self, client: WeatherClient
    ) -> None:
        """_validate_inputs raises ValueError when start_date > end_date."""
        with pytest.raises(ValueError, match="Start date cannot be after end date"):
            client._validate_inputs(47.5, 19.0, "2020-12-31", "2020-01-01")


class TestSelectProvider:
    """Test _select_provider method."""

    def test_select_provider_returns_user_override_when_valid(
        self, client: WeatherClient
    ) -> None:
        """_select_provider returns user_override when provider is valid."""
        result = client._select_provider("open-meteo")

        assert result == "open-meteo"

    def test_select_provider_falls_back_to_auto_when_override_invalid(
        self, client: WeatherClient
    ) -> None:
        """_select_provider falls back to auto mode when user_override is not a valid provider."""
        result = client._select_provider("invalid-provider")

        # Falls back to auto mode which returns first valid provider
        assert result in ["open-meteo", "meteostat"]

    def test_select_provider_with_auto_mode(
        self, client: WeatherClient
    ) -> None:
        """_select_provider with auto mode selects optimal provider."""
        with patch("src.data.weather_client_core.get_optimal_data_source", return_value="open-meteo"):
            result = client._select_provider()

            assert result == "open-meteo"

    def test_select_provider_with_auto_fallback_to_any_available(
        self, client: WeatherClient
    ) -> None:
        """_select_provider with auto mode falls back to any available provider."""
        # Make get_optimal_data_source return invalid provider
        with patch("src.data.weather_client_core.get_optimal_data_source", return_value="invalid"):
            # Still should return a valid provider
            result = client._select_provider()

            assert result in ["open-meteo", "meteostat"]

    def test_select_provider_returns_none_when_no_providers_available(
        self, client: WeatherClient
    ) -> None:
        """_select_provider returns None when no providers are valid."""
        for provider in client.providers.values():
            provider.validate_provider.return_value = False

        result = client._select_provider()

        assert result is None

    def test_select_provider_with_explicit_preferred_provider(
        self, client: WeatherClient
    ) -> None:
        """_select_provider with explicit preferred provider returns that provider."""
        client.preferred_provider = "meteostat"

        result = client._select_provider()

        assert result == "meteostat"

    def test_select_provider_raises_recursion_error_when_preferred_invalid_in_providers(
        self, client: WeatherClient
    ) -> None:
        """_select_provider raises RecursionError when preferred provider is invalid but in providers dict (BUG)."""
        client.preferred_provider = "invalid"
        client.providers["invalid"] = Mock()
        client.providers["invalid"].validate_provider.return_value = False

        # This triggers infinite recursion due to bug at line 138 of weather_client_core.py
        with pytest.raises(RecursionError):
            client._select_provider()


class TestGetProviderFallbackChain:
    """Test _get_provider_fallback_chain method."""

    def test_get_provider_fallback_chain_puts_primary_first(
        self, client: WeatherClient
    ) -> None:
        """_get_provider_fallback_chain puts primary provider first."""
        chain = client._get_provider_fallback_chain("open-meteo")

        assert chain[0] == "open-meteo"

    def test_get_provider_fallback_chain_includes_all_valid_providers(
        self, client: WeatherClient
    ) -> None:
        """_get_provider_fallback_chain includes all valid providers."""
        chain = client._get_provider_fallback_chain("open-meteo")

        assert len(chain) == 2
        assert "open-meteo" in chain
        assert "meteostat" in chain

    def test_get_provider_fallback_chain_excludes_invalid_providers(
        self, client: WeatherClient
    ) -> None:
        """_get_provider_fallback_chain excludes invalid providers."""
        client.providers["meteostat"].validate_provider.return_value = False

        chain = client._get_provider_fallback_chain("open-meteo")

        assert chain == ["open-meteo"]

    def test_get_provider_fallback_chain_orders_correctly(
        self, client: WeatherClient
    ) -> None:
        """_get_provider_fallback_chain orders providers correctly."""
        chain = client._get_provider_fallback_chain("meteostat")

        assert chain[0] == "meteostat"
        assert chain[1] == "open-meteo"


class TestRetryWeatherRequest:
    """Test _retry_weather_request method."""

    def test_retry_weather_request_returns_on_first_success(
        self, client: WeatherClient
    ) -> None:
        """_retry_weather_request returns immediately on first success."""
        provider = client.providers["open-meteo"]
        provider.get_weather_data.return_value = [{"date": "2020-01-01"}]

        result = client._retry_weather_request(provider, 47.5, 19.0, "2020-01-01", "2020-01-31")

        assert result == [{"date": "2020-01-01"}]
        provider.get_weather_data.assert_called_once()

    def test_retry_weather_request_retries_on_failure(
        self, client: WeatherClient
    ) -> None:
        """_retry_weather_request retries on WeatherAPIError."""
        provider = client.providers["open-meteo"]
        provider.get_weather_data.side_effect = [
            WeatherAPIError("First failure"),
            [{"date": "2020-01-01"}]
        ]

        with patch("time.sleep"):
            result = client._retry_weather_request(provider, 47.5, 19.0, "2020-01-01", "2020-01-31")

        assert result == [{"date": "2020-01-01"}]
        assert provider.get_weather_data.call_count == 2

    def test_retry_weather_request_raises_after_max_retries(
        self, client: WeatherClient
    ) -> None:
        """_retry_weather_request raises after max retries exhausted."""
        provider = client.providers["open-meteo"]
        provider.get_weather_data.side_effect = WeatherAPIError("Always fails")

        with patch("time.sleep"):
            with pytest.raises(WeatherAPIError, match="Always fails"):
                client._retry_weather_request(provider, 47.5, 19.0, "2020-01-01", "2020-01-31")

        assert provider.get_weather_data.call_count == 3

    def test_retry_weather_request_uses_exponential_backoff(
        self, client: WeatherClient
    ) -> None:
        """_retry_weather_request uses exponential backoff delays."""
        provider = client.providers["open-meteo"]
        provider.get_weather_data.side_effect = [
            WeatherAPIError("Fail 1"),
            WeatherAPIError("Fail 2"),
            [{"date": "2020-01-01"}]
        ]

        sleep_calls: List[float] = []

        def fake_sleep(delay: float) -> None:
            sleep_calls.append(delay)

        with patch("time.sleep", side_effect=fake_sleep):
            client._retry_weather_request(provider, 47.5, 19.0, "2020-01-01", "2020-01-31")

        # Should have slept with delays: 1.0, 2.0 (attempt + 1)
        assert sleep_calls == [1.0, 2.0]


class TestHandleSuccessfulRequest:
    """Test _handle_successful_request method."""

    def test_handle_successful_request_updates_current_provider(
        self, client: WeatherClient
    ) -> None:
        """_handle_successful_request updates current_provider."""
        client._handle_successful_request("open-meteo", "open-meteo")

        assert client.current_provider == "open-meteo"

    def test_handle_successful_request_calls_fallback_callback_on_mismatch(
        self, client: WeatherClient
    ) -> None:
        """_handle_successful_request calls fallback callback when providers differ."""
        callback = Mock()
        client.set_provider_fallback_callback(callback)

        client._handle_successful_request("meteostat", "open-meteo")

        callback.assert_called_once_with("open-meteo", "meteostat")

    def test_handle_successful_request_no_fallback_callback_when_same(
        self, client: WeatherClient
    ) -> None:
        """_handle_successful_request doesn't call fallback when providers match."""
        callback = Mock()
        client.set_provider_fallback_callback(callback)

        client._handle_successful_request("open-meteo", "open-meteo")

        callback.assert_not_called()

    def test_handle_successful_request_calls_change_callback_on_preferred_mismatch(
        self, client: WeatherClient
    ) -> None:
        """_handle_successful_request calls change callback when used != preferred."""
        client.preferred_provider = "meteostat"
        callback = Mock()
        client.set_provider_change_callback(callback)

        client._handle_successful_request("open-meteo", "meteostat")

        callback.assert_called_once_with("meteostat", "open-meteo")

    def test_handle_successful_request_no_change_callback_with_auto_mode(
        self, client: WeatherClient
    ) -> None:
        """_handle_successful_request doesn't call change callback in auto mode."""
        callback = Mock()
        client.set_provider_change_callback(callback)

        client._handle_successful_request("open-meteo", "meteostat")

        callback.assert_not_called()


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
        client.providers["open-meteo"].get_weather_data.side_effect = WeatherAPIError("Primary failed")
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
        client.providers["open-meteo"].get_weather_data.side_effect = WeatherAPIError("Failed")
        client.providers["meteostat"].get_weather_data.side_effect = WeatherAPIError("Failed")

        with pytest.raises(ProviderNotAvailableError, match="All providers failed"):
            client.get_weather_data(47.5, 19.0, "2020-01-01", "2020-01-31")

    def test_get_weather_data_validates_inputs(
        self, client: WeatherClient
    ) -> None:
        """get_weather_data validates input parameters."""
        with pytest.raises(ValueError, match="Invalid latitude"):
            client.get_weather_data(91, 0, "2020-01-01", "2020-01-31")

    def test_get_weather_data_updates_usage_stats(
        self, client: WeatherClient
    ) -> None:
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

        result = client.get_weather_data(47.5, 19.0, "2020-01-01", "2020-01-31", user_override_provider="meteostat")

        assert len(result) == 1
        client.providers["meteostat"].get_weather_data.assert_called_once()

    def test_get_weather_data_handles_fallback_callbacks(
        self, client: WeatherClient
    ) -> None:
        """get_weather_data triggers fallback callbacks correctly."""
        client.preferred_provider = "open-meteo"
        fallback_callback = Mock()
        client.set_provider_fallback_callback(fallback_callback)

        client.providers["open-meteo"].get_weather_data.side_effect = WeatherAPIError("Failed")
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

        client.get_weather_data(47.5, 19.0, "2020-01-01", "2020-01-31", user_override_provider="open-meteo")
        client.get_weather_data(47.5, 19.0, "2020-02-01", "2020-02-28", user_override_provider="meteostat")
        client.get_weather_data(47.5, 19.0, "2020-03-01", "2020-03-31", user_override_provider="open-meteo")

        assert client.provider_usage_stats.get("open-meteo") == 2
        assert client.provider_usage_stats.get("meteostat") == 1
