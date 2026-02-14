"""WeatherClient logikai egységeinek izolált tesztjei."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Dict, List, Tuple

import pytest

from src.data import weather_client as weather_client_module

WeatherData = weather_client_module.WeatherData
OpenMeteoProvider = weather_client_module.OpenMeteoProvider
WeatherClient = weather_client_module.WeatherClient


def test_weather_data_post_init_computes_range_and_mean() -> None:
    """A dataclass automatikusan kiszámolja a tartományt és az átlagot."""
    record = WeatherData(
        date="2024-01-01",
        temperature_2m_max=24.0,
        temperature_2m_min=14.0,
        temperature_2m_mean=None,
    )
    assert record.temperature_range == 10.0
    assert record.temperature_2m_mean == 19.0


def test_openmeteo_generate_batches_limits_duration() -> None:
    """A batch generátor legfeljebb 90 napos szegmenseket ad vissza."""
    provider = OpenMeteoProvider()
    start = datetime(2024, 1, 1)
    end = datetime(2024, 5, 1)
    batches = provider._generate_batches(start, end)
    assert len(batches) == 2

    first_span = (batches[0][1] - batches[0][0]).days + 1
    second_span = (batches[1][1] - batches[1][0]).days + 1
    assert first_span == provider.max_days_per_request
    assert second_span == (end - batches[1][0]).days + 1


def test_rate_limit_check_triggers_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """A rate limiter túl gyors hívás esetén várakozást iktat be."""
    provider = OpenMeteoProvider()
    provider.last_request_time = 5.0
    provider.min_request_interval = 1.0

    monkeypatch.setattr(time, "time", lambda: 5.5)
    slept: Dict[str, float] = {}

    def fake_sleep(delay: float) -> None:
        slept["value"] = delay

    monkeypatch.setattr(time, "sleep", fake_sleep)
    provider._rate_limit_check()
    assert slept["value"] == pytest.approx(0.5)


def test_weather_client_validate_inputs_rejects_invalid_values() -> None:
    """Rosszul megadott koordináták vagy dátumok ValueError-t generálnak."""
    client = WeatherClient()

    with pytest.raises(ValueError):
        client._validate_inputs(123.0, 10.0, "2024-01-01", "2024-01-02")
    with pytest.raises(ValueError):
        client._validate_inputs(45.0, -190.0, "2024-01-01", "2024-01-02")
    with pytest.raises(ValueError):
        client._validate_inputs(45.0, 10.0, "20240101", "2024-01-02")
    with pytest.raises(ValueError):
        client._validate_inputs(45.0, 10.0, "2024-02-02", "2024-01-01")


def test_handle_successful_request_updates_callbacks() -> None:
    """Fallback esetén mindkét callback értesítést kap."""
    client = WeatherClient()
    client.preferred_provider = "open-meteo"

    fallback_events: List[Tuple[str, str]] = []
    change_events: List[Tuple[str, str]] = []

    def on_fallback(requested: str, used: str) -> None:
        fallback_events.append((requested, used))

    def on_change(previous: str, current: str) -> None:
        change_events.append((previous, current))

    client.set_provider_fallback_callback(on_fallback)
    client.set_provider_change_callback(on_change)
    client._handle_successful_request("meteostat", "open-meteo")

    assert client.current_provider == "meteostat"
    assert fallback_events == [("open-meteo", "meteostat")]
    assert change_events == [("open-meteo", "meteostat")]
