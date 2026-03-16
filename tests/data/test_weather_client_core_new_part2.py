"""Tests split from test_weather_client_core_new.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_weather_client_core_new_support import *


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

        result = client._retry_weather_request(
            provider, 47.5, 19.0, "2020-01-01", "2020-01-31"
        )

        assert result == [{"date": "2020-01-01"}]
        provider.get_weather_data.assert_called_once()

    def test_retry_weather_request_retries_on_failure(
        self, client: WeatherClient
    ) -> None:
        """_retry_weather_request retries on WeatherAPIError."""
        provider = client.providers["open-meteo"]
        provider.get_weather_data.side_effect = [
            WeatherAPIError("First failure"),
            [{"date": "2020-01-01"}],
        ]

        with patch("time.sleep"):
            result = client._retry_weather_request(
                provider, 47.5, 19.0, "2020-01-01", "2020-01-31"
            )

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
                client._retry_weather_request(
                    provider, 47.5, 19.0, "2020-01-01", "2020-01-31"
                )

        assert provider.get_weather_data.call_count == 3

    def test_retry_weather_request_uses_exponential_backoff(
        self, client: WeatherClient
    ) -> None:
        """_retry_weather_request uses exponential backoff delays."""
        provider = client.providers["open-meteo"]
        provider.get_weather_data.side_effect = [
            WeatherAPIError("Fail 1"),
            WeatherAPIError("Fail 2"),
            [{"date": "2020-01-01"}],
        ]

        sleep_calls: List[float] = []

        def fake_sleep(delay: float) -> None:
            sleep_calls.append(delay)

        with patch("time.sleep", side_effect=fake_sleep):
            client._retry_weather_request(
                provider, 47.5, 19.0, "2020-01-01", "2020-01-31"
            )

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
