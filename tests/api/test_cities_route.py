"""Tests for city search API routes."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from src.api.dependencies import ServiceRegistry, get_services
from src.api.main import app


def _setup_city_repo(city_repo: MagicMock) -> None:
    """Register mock service registry with the given city_repo."""
    mock_services = MagicMock(spec=ServiceRegistry)
    mock_services.city_repository = city_repo
    app.dependency_overrides[get_services] = lambda: mock_services


@pytest.mark.anyio
async def test_search_cities_returns_transformed_results() -> None:
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
    _setup_city_repo(city_repo)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/cities/search", params={"query": "bud", "limit": 5})

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "bud"
        assert data["count"] == 1
        assert data["cities"][0]["name"] == "Budapest"
        assert data["cities"][0]["coordinates"] == {"lat": 47.4979, "lon": 19.0402}
        city_repo.autocomplete_city_name.assert_called_once_with("bud", limit=5)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_search_cities_returns_none_coordinates_when_missing() -> None:
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
    _setup_city_repo(city_repo)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/cities/search", params={"query": "un", "limit": 5})

        assert response.status_code == 200
        assert response.json()["cities"][0]["coordinates"] is None
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_search_cities_returns_500_on_repository_error() -> None:
    """Repository failures should surface as HTTP 500."""
    city_repo = MagicMock()
    city_repo.autocomplete_city_name.side_effect = RuntimeError("db offline")
    _setup_city_repo(city_repo)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/cities/search", params={"query": "bud", "limit": 5})

        assert response.status_code == 500
        assert response.json()["detail"] == "Failed to search cities"
    finally:
        app.dependency_overrides.clear()
