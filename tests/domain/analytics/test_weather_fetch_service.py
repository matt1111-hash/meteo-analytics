"""Tests for WeatherFetchService."""

from __future__ import annotations

from typing import Any

import pytest
from src.domain.analytics.models import CityWeatherData
from src.domain.analytics.services.weather_fetch_service import WeatherFetchService


class _DummyWeatherClient:
    def __init__(self, responses: list[Any] | None = None, raise_error: bool = False) -> None:
        self.responses = responses or []
        self.raise_error = raise_error
        self.calls: list[dict[str, Any]] = []

    def get_weather_data(self, lat: float, lon: float, start: str, end: str) -> Any:
        self.calls.append({"lat": lat, "lon": lon, "start": start, "end": end})
        if self.raise_error:
            raise RuntimeError("client error")
        return self.responses.pop(0) if self.responses else []


def _service(client: Any) -> WeatherFetchService:
    return WeatherFetchService(
        weather_client=client,
        max_workers=2,
        request_timeout=5.0,
        max_retries=2,
        retry_delay=0.0,
    )


def test_fetch_weather_data_dual_api_batch_returns_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)
    client = _DummyWeatherClient(
        responses=[
            [
                {
                    "temperature_2m_max": 10.0,
                    "temperature_2m_min": 2.0,
                    "temperature_2m_mean": 6.0,
                    "precipitation_sum": 1.0,
                    "windspeed_10m_max": 20.0,
                    "windgusts_10m_max": 22.0,
                }
            ]
        ]
    )
    service = _service(client)
    cities = [
        {
            "city": "Budapest",
            "country": "Hungary",
            "country_code": "HU",
            "lat": 47.5,
            "lon": 19.0,
        }
    ]
    region_config = {"batch_size": 1, "rate_limit_delay": 0.0}

    results = service.fetch_weather_data_dual_api_batch(cities, "2024-01-01", region_config)

    assert len(results) == 1
    city_data = results[0]
    assert isinstance(city_data, CityWeatherData)
    assert city_data.fetch_success is True
    assert city_data.temperature_range == pytest.approx(8.0)
    assert city_data.windspeed_10m_max == 20.0
    assert client.calls[-1]["lat"] == 47.5


def test_fetch_weather_data_dual_api_batch_returns_empty_on_missing_client() -> None:
    service = _service(None)
    cities = [{"city": "Test", "country": "X", "country_code": "XX", "lat": 0.0, "lon": 0.0}]
    region_config = {"batch_size": 1, "rate_limit_delay": 0.0}

    results = service.fetch_weather_data_dual_api_batch(cities, "2024-01-01", region_config)

    assert len(results) == 1
    assert results[0].fetch_success is False
    assert results[0].data_source == "error"


def test_fetch_single_city_weather_dual_api_returns_empty_after_retries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)
    client = _DummyWeatherClient(raise_error=True)
    service = _service(client)
    city = {
        "city": "Failtown",
        "country": "X",
        "country_code": "XX",
        "lat": 0.0,
        "lon": 0.0,
    }

    result = service.fetch_single_city_weather_dual_api(city, "2024-01-01")

    assert result[0].fetch_success is False
    assert "client error" in (result[0].error_message or "")
