"""Tests for weather analysis API routes."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app
from src.api.routes import weather
from src.domain.analytics.models import MultiCityQuery


@pytest.mark.anyio
async def test_analyze_multi_city_returns_result_and_passes_aggregate_flag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Multi-city endpoint should build query and forward aggregate flag."""
    use_case = MagicMock()
    use_case.execute.return_value = MagicMock(
        to_dict=MagicMock(return_value={"city_results": [{"city": "Budapest"}]})
    )
    query = MultiCityQuery(
        query_type="windiest_today",
        region="Global",
        date="2024-01-01",
    )
    monkeypatch.setattr(weather, "_build_use_case", MagicMock(return_value=use_case))
    monkeypatch.setattr(weather, "to_multi_city_query", MagicMock(return_value=query))

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/weather/multi-city",
            params={"aggregate": "false"},
            json={
                "cities": ["Budapest", "Szeged"],
                "date_range": {"start": "2024-01-01", "end": "2024-01-03"},
                "metric": "windspeed_10m_max",
            },
        )

    assert response.status_code == 200
    assert response.json() == {"city_results": [{"city": "Budapest"}]}
    use_case.execute.assert_called_once_with(query, aggregate=False)


@pytest.mark.anyio
async def test_analyze_multi_city_maps_value_error_to_http_400(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Route should expose validation failures as HTTP 400."""
    monkeypatch.setattr(weather, "_build_use_case", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(
        weather,
        "to_multi_city_query",
        MagicMock(side_effect=ValueError("bad date range")),
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/weather/multi-city",
            json={
                "cities": ["Budapest"],
                "date_range": {"start": "2024-01-01"},
                "metric": "temperature_2m_max",
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "bad date range"


@pytest.mark.anyio
async def test_analyze_multi_city_maps_unexpected_error_to_http_500(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unexpected failures should return HTTP 500."""
    monkeypatch.setattr(
        weather,
        "_build_use_case",
        MagicMock(side_effect=RuntimeError("dependency setup failed")),
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/weather/multi-city",
            json={
                "cities": ["Budapest"],
                "date_range": {"start": "2024-01-01", "end": "2024-01-03"},
                "metric": "temperature_2m_max",
            },
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
