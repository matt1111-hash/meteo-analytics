"""Tests for anomaly detection API routes."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from src.api.main import app
from src.api.routes import anomalies
from src.domain.entities.climate_anomaly import ClimateAnomaly


def _build_weather_use_case() -> MagicMock:
    """Create a weather use case mock for anomaly endpoint tests."""
    use_case = MagicMock()
    use_case.city_repository = MagicMock()
    use_case.weather_fetch_service = MagicMock()
    use_case.regions = {"Global": {"max_cities": 10}}
    return use_case


@pytest.mark.anyio
async def test_detect_anomalies_returns_serialized_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Endpoint should return serialized anomalies for all categories."""
    weather_use_case = _build_weather_use_case()
    weather_use_case.city_repository.get_cities_by_names.return_value = [{"city": "Budapest"}]
    weather_use_case.weather_fetch_service.fetch_weather_data_dual_api_batch.return_value = [
        MagicMock(
            temperature_2m_max=33.0,
            temperature_2m_min=20.0,
            precipitation_sum=12.0,
            windspeed_10m_max=75.0,
        )
    ]
    anomaly_result = {
        "temperature": ClimateAnomaly(
            location_name="Budapest",
            date=date(2024, 1, 2),
            parameter="temperature",
            measured_value=33.0,
            category="hot",
            severity="warning",
            message="Hot day",
            threshold=30.0,
        ),
        "precipitation": None,
        "wind": ClimateAnomaly(
            location_name="Budapest",
            date=date(2024, 1, 2),
            parameter="wind",
            measured_value=75.0,
            category="storm",
            severity="error",
            message="Strong wind",
            threshold=60.0,
        ),
    }
    anomaly_use_case = MagicMock()
    anomaly_use_case.execute.return_value = anomaly_result
    monkeypatch.setattr(anomalies, "_build_use_case", MagicMock(return_value=weather_use_case))
    monkeypatch.setattr(anomalies, "anomaly_use_case", anomaly_use_case)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/weather/anomalies",
            json={"city": "Budapest", "start": "2024-01-01", "end": "2024-01-03"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Budapest"
    assert data["anomalies"]["temperature"]["category"] == "hot"
    assert data["anomalies"]["temperature"]["date"] == "2024-01-02"
    assert data["anomalies"]["precipitation"] is None
    assert data["anomalies"]["wind"]["severity"] == "error"
    anomaly_use_case.execute.assert_called_once()


@pytest.mark.anyio
async def test_detect_anomalies_returns_404_when_city_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Endpoint should return 404 when the city lookup returns no match."""
    weather_use_case = _build_weather_use_case()
    weather_use_case.city_repository.get_cities_by_names.return_value = []
    monkeypatch.setattr(anomalies, "_build_use_case", MagicMock(return_value=weather_use_case))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/weather/anomalies",
            json={"city": "Missing", "start": "2024-01-01", "end": "2024-01-03"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "City not found: Missing"


@pytest.mark.anyio
async def test_detect_anomalies_returns_404_when_weather_data_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Endpoint should return 404 when weather fetch returns no rows."""
    weather_use_case = _build_weather_use_case()
    weather_use_case.city_repository.get_cities_by_names.return_value = [{"city": "Budapest"}]
    weather_use_case.weather_fetch_service.fetch_weather_data_dual_api_batch.return_value = []
    monkeypatch.setattr(anomalies, "_build_use_case", MagicMock(return_value=weather_use_case))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/weather/anomalies",
            json={"city": "Budapest", "start": "2024-01-01", "end": "2024-01-03"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "No weather data found for Budapest"


@pytest.mark.anyio
async def test_detect_anomalies_maps_value_error_to_http_400(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Value errors should map to HTTP 400."""
    weather_use_case = _build_weather_use_case()
    weather_use_case.city_repository.get_cities_by_names.return_value = [{"city": "Budapest"}]
    weather_use_case.weather_fetch_service.fetch_weather_data_dual_api_batch.return_value = [
        MagicMock(
            temperature_2m_max=33.0,
            temperature_2m_min=20.0,
            precipitation_sum=12.0,
            windspeed_10m_max=75.0,
        )
    ]
    anomaly_use_case = MagicMock()
    anomaly_use_case.execute.side_effect = ValueError("bad thresholds")
    monkeypatch.setattr(anomalies, "_build_use_case", MagicMock(return_value=weather_use_case))
    monkeypatch.setattr(anomalies, "anomaly_use_case", anomaly_use_case)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/weather/anomalies",
            json={"city": "Budapest", "start": "2024-01-01", "end": "2024-01-03"},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "bad thresholds"


@pytest.mark.anyio
async def test_detect_anomalies_maps_unexpected_error_to_http_500(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unexpected errors should map to HTTP 500."""
    monkeypatch.setattr(
        anomalies,
        "_build_use_case",
        MagicMock(side_effect=RuntimeError("broken dependency graph")),
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/weather/anomalies",
            json={"city": "Budapest", "start": "2024-01-01", "end": "2024-01-03"},
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
