"""Tests for detailed city API route."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from src.api.dependencies import ServiceRegistry, get_services
from src.api.main import app
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


def _setup_services(use_case: MagicMock) -> None:
    """Register mock service registry with the given use case."""
    mock_services = MagicMock(spec=ServiceRegistry)
    mock_services.detailed_city_use_case = use_case
    app.dependency_overrides[get_services] = lambda: mock_services


@pytest.mark.anyio
async def test_analyze_single_city_detailed_returns_all_metric_groups() -> None:
    """Detailed city endpoint should return grouped results for each metric."""
    use_case = MagicMock()
    use_case.execute.return_value = _make_result()
    _setup_services(use_case)

    try:
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

        use_case.execute.assert_called_once_with(
            city="Budapest", start="2024-01-01", end="2024-01-03"
        )
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_analyze_single_city_detailed_maps_value_error_to_http_400() -> None:
    """Detailed city endpoint should map value errors to HTTP 400."""
    use_case = MagicMock()
    use_case.execute.side_effect = ValueError("bad request")
    _setup_services(use_case)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/weather/single-city-detailed",
                json={"city": "Budapest", "start": "2024-01-01", "end": "2024-01-03"},
            )

        assert response.status_code == 400
        assert response.json()["detail"] == "bad request"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_analyze_single_city_detailed_maps_unexpected_error_to_http_500() -> None:
    """Detailed city endpoint should map unexpected errors to HTTP 500."""
    mock_services = MagicMock(spec=ServiceRegistry)
    type(mock_services).detailed_city_use_case = property(
        lambda self: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    app.dependency_overrides[get_services] = lambda: mock_services

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/weather/single-city-detailed",
                json={"city": "Budapest", "start": "2024-01-01", "end": "2024-01-03"},
            )

        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"
    finally:
        app.dependency_overrides.clear()
