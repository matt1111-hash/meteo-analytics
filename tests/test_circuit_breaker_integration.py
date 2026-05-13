"""Integration test: WeatherClient fallback chain with circuit breaker."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from src.infrastructure.resilience.circuit_breaker import CircuitState
from src.infrastructure.weather.weather_client_core import WeatherClient
from src.infrastructure.weather.weather_types import ProviderNotAvailableError, WeatherAPIError


def _make_client() -> WeatherClient:
    return WeatherClient()


class TestFallbackWithCircuitBreaker:
    def test_circuit_breakers_created_for_each_provider(self) -> None:
        client = _make_client()
        assert "open-meteo" in client.circuit_breakers
        assert "meteostat" in client.circuit_breakers
        for cb in client.circuit_breakers.values():
            assert cb.state == CircuitState.CLOSED

    def test_open_circuit_skips_provider(self) -> None:
        client = _make_client()

        # Force open-meteo circuit open
        cb_om = client.circuit_breakers["open-meteo"]
        for _ in range(5):
            cb_om.record_failure()
        assert cb_om.state == CircuitState.OPEN

        # get_weather_data should skip open-meteo and try meteostat
        # (meteostat may not be configured, but the circuit skip is the point)
        with (
            patch.object(
                client.providers["meteostat"],
                "validate_provider",
                return_value=False,
            ),
            pytest.raises(ProviderNotAvailableError),
        ):
            client.get_weather_data(
                latitude=47.5,
                longitude=19.0,
                start_date="2024-01-01",
                end_date="2024-01-02",
                user_override_provider="open-meteo",
            )

    def test_success_closes_half_open_circuit(self) -> None:
        client = _make_client()

        cb_om = client.circuit_breakers["open-meteo"]
        cb_om.record_failure()  # failure_count=1, threshold=5

        # Manually set to HALF_OPEN
        cb_om._state = CircuitState.HALF_OPEN

        mock_data = [{"date": "2024-01-01", "temp": 5.0}]
        with (
            patch.object(
                client.providers["open-meteo"],
                "get_weather_data",
                return_value=mock_data,
            ),
            patch.object(
                client.providers["open-meteo"],
                "validate_provider",
                return_value=True,
            ),
        ):
            result = client.get_weather_data(
                latitude=47.5,
                longitude=19.0,
                start_date="2024-01-01",
                end_date="2024-01-02",
                user_override_provider="open-meteo",
            )

        assert result == mock_data
        assert cb_om.state == CircuitState.CLOSED
        assert cb_om.failure_count == 0

    def test_failure_opens_circuit_after_threshold(self) -> None:
        client = _make_client()
        cb_om = client.circuit_breakers["open-meteo"]

        with (
            patch.object(
                client.providers["open-meteo"],
                "get_weather_data",
                side_effect=WeatherAPIError("fail"),
            ),
            patch.object(
                client.providers["open-meteo"],
                "validate_provider",
                return_value=True,
            ),
            patch.object(
                client.providers["meteostat"],
                "validate_provider",
                return_value=False,
            ),
        ):
            for _ in range(5):
                with pytest.raises(ProviderNotAvailableError):
                    client.get_weather_data(
                        latitude=47.5,
                        longitude=19.0,
                        start_date="2024-01-01",
                        end_date="2024-01-02",
                        user_override_provider="open-meteo",
                    )

        assert cb_om.state == CircuitState.OPEN

    def test_circuit_breaker_independent_per_provider(self) -> None:
        client = _make_client()
        cb_om = client.circuit_breakers["open-meteo"]
        cb_meta = client.circuit_breakers["meteostat"]

        # Trip open-meteo
        for _ in range(5):
            cb_om.record_failure()
        assert cb_om.state == CircuitState.OPEN
        assert cb_meta.state == CircuitState.CLOSED

    def test_fallback_to_second_provider_when_primary_circuit_open(self) -> None:
        client = _make_client()

        # Open open-meteo circuit
        cb_om = client.circuit_breakers["open-meteo"]
        for _ in range(5):
            cb_om.record_failure()

        mock_data = [{"date": "2024-01-01", "temp": 3.0}]
        with (
            patch.object(
                client.providers["meteostat"],
                "get_weather_data",
                return_value=mock_data,
            ),
            patch.object(
                client.providers["meteostat"],
                "validate_provider",
                return_value=True,
            ),
        ):
            result = client.get_weather_data(
                latitude=47.5,
                longitude=19.0,
                start_date="2024-01-01",
                end_date="2024-01-02",
                user_override_provider="open-meteo",
            )

        assert result == mock_data
