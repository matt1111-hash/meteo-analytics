"""Tests split from test_weather_client_core_new.py."""

from __future__ import annotations

from unittest.mock import patch

# ruff: noqa: F403, F405
from tests.data.test_weather_client_core_new_support import *


class TestWeatherClientInit:
    """Test WeatherClient initialization."""

    def test_init_with_default_preferred_provider(self, mock_api_config: Mock) -> None:
        """Initialization with default preferred_provider='auto'."""
        client = WeatherClient()

        assert client.preferred_provider == "auto"
        assert client.current_provider is None
        assert isinstance(client.provider_usage_stats, dict)
        assert "open-meteo" in client.providers
        assert "meteostat" in client.providers
        assert client.max_retries == 3
        assert client.retry_delay == 1.0

    def test_init_with_custom_preferred_provider(self, mock_api_config: Mock) -> None:
        """Initialization with custom preferred_provider."""
        client = WeatherClient(preferred_provider="open-meteo")

        assert client.preferred_provider == "open-meteo"


class TestSetProviderChangeCallback:
    """Test set_provider_change_callback method."""

    def test_set_provider_change_callback_sets_callback(self, client: WeatherClient) -> None:
        """set_provider_change_callback sets the callback function."""
        callback = Mock()
        client.set_provider_change_callback(callback)

        assert client.provider_change_callback == callback

    def test_set_provider_fallback_callback_sets_callback(self, client: WeatherClient) -> None:
        """set_provider_fallback_callback sets the callback function."""
        callback = Mock()
        client.set_provider_fallback_callback(callback)

        assert client.provider_fallback_callback == callback


class TestValidateInputs:
    """Test _validate_inputs method."""

    def test_validate_inputs_accepts_valid_coordinates(self, client: WeatherClient) -> None:
        """_validate_inputs accepts valid latitude and longitude."""
        # Should not raise
        client._validate_inputs(47.5, 19.0, "2020-01-01", "2020-01-31")

    def test_validate_inputs_accepts_boundary_values(self, client: WeatherClient) -> None:
        """_validate_inputs accepts boundary coordinate values."""
        # Should not raise
        client._validate_inputs(-90, -180, "2020-01-01", "2020-01-31")
        client._validate_inputs(90, 180, "2020-01-01", "2020-01-31")

    def test_validate_inputs_rejects_invalid_latitude(self, client: WeatherClient) -> None:
        """_validate_inputs raises ValueError for invalid latitude."""
        with pytest.raises(ValueError, match="Invalid latitude"):
            client._validate_inputs(91, 0, "2020-01-01", "2020-01-31")

        with pytest.raises(ValueError, match="Invalid latitude"):
            client._validate_inputs(-91, 0, "2020-01-01", "2020-01-31")

    def test_validate_inputs_rejects_invalid_longitude(self, client: WeatherClient) -> None:
        """_validate_inputs raises ValueError for invalid longitude."""
        with pytest.raises(ValueError, match="Invalid longitude"):
            client._validate_inputs(0, 181, "2020-01-01", "2020-01-31")

        with pytest.raises(ValueError, match="Invalid longitude"):
            client._validate_inputs(0, -181, "2020-01-01", "2020-01-31")

    def test_validate_inputs_rejects_invalid_date_format(self, client: WeatherClient) -> None:
        """_validate_inputs raises ValueError for invalid date format."""
        with pytest.raises(ValueError, match="Invalid date format"):
            client._validate_inputs(47.5, 19.0, "01-01-2020", "2020-01-31")

        with pytest.raises(ValueError, match="Invalid date format"):
            client._validate_inputs(47.5, 19.0, "2020/01/01", "2020-01-31")

    def test_validate_inputs_rejects_start_after_end(self, client: WeatherClient) -> None:
        """_validate_inputs raises ValueError when start_date > end_date."""
        with pytest.raises(ValueError, match="Start date cannot be after end date"):
            client._validate_inputs(47.5, 19.0, "2020-12-31", "2020-01-01")


class TestSelectProvider:
    """Test _select_provider method."""

    def test_select_provider_returns_user_override_when_valid(self, client: WeatherClient) -> None:
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

    def test_select_provider_with_auto_mode(self, client: WeatherClient) -> None:
        """_select_provider with auto mode selects optimal provider."""
        with patch(
            "src.data.weather_client_core.get_optimal_data_source",
            return_value="open-meteo",
        ):
            result = client._select_provider()

            assert result == "open-meteo"

    def test_select_provider_with_auto_fallback_to_any_available(
        self, client: WeatherClient
    ) -> None:
        """_select_provider with auto mode falls back to any available provider."""
        # Make get_optimal_data_source return invalid provider
        with patch(
            "src.data.weather_client_core.get_optimal_data_source",
            return_value="invalid",
        ):
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

    def test_select_provider_with_explicit_preferred_provider(self, client: WeatherClient) -> None:
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
