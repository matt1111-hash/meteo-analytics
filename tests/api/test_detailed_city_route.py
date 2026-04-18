"""Tests for detailed city API route."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from src.api.main import app
from src.api.routes import detailed_city
from src.application.use_cases.detailed_city_use_case import DetailedCityResult


def _make_result(**overrides) -> DetailedCityResult:
    defaults = {
        "city": "Budapest",
        "start": "2024-01-01",
        "end": "2024-01-03",
        "temperature_data": [{"value": 20.0}],
        "wind_data": [{"value": 40.0}],
        "wind_gusts_data": [{"value": 60.0}],
        "precipitation_data": [{"value": 5.0}],
    }
    defaults.update(overrides)
    return DetailedCityResult(**defaults)


@pytest.mark.anyio
async def test_analyze_single_city_detailed_returns_all_metric_groups(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Detailed city endpoint should return grouped results for each metric."""
    use_case = MagicMock()
    use_case.execute.return_value = _make_result()
    monkeypatch.setattr(
        detailed_city, "build_detailed_city_use_case", MagicMock(return_value=use_case)
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/weather/single-city-detailed",
            json={"city": "Budapest", "start": "2024-01-01", "end": "2024-01-03"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Budapest"
    assert data["temperature_data"] == [{"value": 20.0}]
    assert data["wind_data"] == [{"value": 40.0}]
    assert data["wind_gusts_data"] == [{"value": 60.0}]
    assert data["precipitation_data"] == [{"value": 5.0}]

    use_case.execute.assert_called_once_with(city="Budapest", start="2024-01-01", end="2024-01-03")


@pytest.mark.anyio
async def test_analyze_single_city_detailed_maps_value_error_to_http_400(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Detailed city endpoint should map value errors to HTTP 400."""
    use_case = MagicMock()
    use_case.execute.side_effect = ValueError("bad request")
    monkeypatch.setattr(
        detailed_city, "build_detailed_city_use_case", MagicMock(return_value=use_case)
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/weather/single-city-detailed",
            json={"city": "Budapest", "start": "2024-01-01", "end": "2024-01-03"},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "bad request"


@pytest.mark.anyio
async def test_analyze_single_city_detailed_maps_unexpected_error_to_http_500(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Detailed city endpoint should map unexpected errors to HTTP 500."""
    monkeypatch.setattr(
        detailed_city,
        "build_detailed_city_use_case",
        MagicMock(side_effect=RuntimeError("boom")),
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/weather/single-city-detailed",
            json={"city": "Budapest", "start": "2024-01-01", "end": "2024-01-03"},
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
