"""Tests for city search API routes."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app
from src.api.routes import cities


@pytest.mark.anyio
async def test_search_cities_returns_transformed_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Search endpoint should transform repository rows into API payloads."""
    city_repo = MagicMock()
    city_repo.autocomplete_city_name.return_value = [
        {
            "city": "Budapest",
            "country": "Hungary",
            "country_code": "HU",
            "lat": 47.4979,
            "lon": 19.0402,
            "population": 1756000,
            "meteostat_station_id": "BUD",
            "data_quality_score": 0.98,
        }
    ]
    monkeypatch.setattr(
        cities, "get_city_repository_port", MagicMock(return_value=city_repo)
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/cities/search", params={"query": "bud", "limit": 5}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "bud"
    assert data["count"] == 1
    assert data["cities"][0]["name"] == "Budapest"
    assert data["cities"][0]["coordinates"] == {"lat": 47.4979, "lon": 19.0402}
    city_repo.autocomplete_city_name.assert_called_once_with("bud", limit=5)


@pytest.mark.anyio
async def test_search_cities_returns_none_coordinates_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Search endpoint should emit null coordinates when lat/lon are missing."""
    city_repo = MagicMock()
    city_repo.autocomplete_city_name.return_value = [
        {
            "city": "Unknown",
            "country": "Hungary",
            "country_code": "HU",
            "lat": None,
            "lon": None,
            "population": None,
            "meteostat_station_id": None,
            "data_quality_score": 0.5,
        }
    ]
    monkeypatch.setattr(
        cities, "get_city_repository_port", MagicMock(return_value=city_repo)
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/cities/search", params={"query": "un", "limit": 5}
        )

    assert response.status_code == 200
    assert response.json()["cities"][0]["coordinates"] is None


@pytest.mark.anyio
async def test_search_cities_returns_500_on_repository_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Repository failures should surface as HTTP 500."""
    city_repo = MagicMock()
    city_repo.autocomplete_city_name.side_effect = RuntimeError("db offline")
    monkeypatch.setattr(
        cities, "get_city_repository_port", MagicMock(return_value=city_repo)
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/cities/search", params={"query": "bud", "limit": 5}
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to search cities"
