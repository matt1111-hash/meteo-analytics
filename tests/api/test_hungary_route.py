"""Tests for Hungary-specific API routes."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from src.api.dependencies import ServiceRegistry, get_services
from src.api.main import app


def _setup_city_manager(city_manager: MagicMock) -> None:
    """Register mock service registry with the given city_manager."""
    mock_services = MagicMock(spec=ServiceRegistry)
    mock_services.city_manager = city_manager
    app.dependency_overrides[get_services] = lambda: mock_services


@pytest.mark.anyio
async def test_get_hungarian_counties_normalizes_and_sorts() -> None:
    """Counties endpoint should normalize Budapest aliases and remove blanks."""
    city_manager = MagicMock()
    city_manager.get_hungarian_counties.return_value = [
        "Pest",
        "",
        "főváros",
        "Bács-Kiskun",
    ]
    _setup_city_manager(city_manager)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/hungary/counties")

        assert response.status_code == 200
        assert response.json() == {
            "count": 3,
            "counties": ["Budapest", "Bács-Kiskun", "Pest"],
        }
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_hungarian_regions_returns_static_regions() -> None:
    """Regions endpoint should return the predefined Hungarian statistical regions."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/hungary/regions")

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 7
    assert "Közép-Magyarország" in data["regions"]
    assert "Nyugat-Dunántúl" in data["regions"]


@pytest.mark.anyio
async def test_get_hungarian_settlements_filters_county_and_type() -> None:
    """Settlements endpoint should use county filter and settlement type filtering."""
    city_manager = MagicMock()
    city_manager.get_cities_for_hungarian_county.return_value = [
        {
            "city": "Kecskemét",
            "megye": "Bács-Kiskun",
            "settlement_type": "város",
            "lat": 46.9,
            "lon": 19.7,
            "population": 110000,
            "region_priority": 1,
        },
        {
            "city": "Bugac",
            "megye": "Bács-Kiskun",
            "settlement_type": "község",
            "lat": 46.7,
            "lon": 19.6,
            "population": 2500,
            "region_priority": 2,
        },
    ]
    _setup_city_manager(city_manager)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/api/hungary/settlements",
                params={"county": "Bács-Kiskun", "settlement_type": "város", "limit": 10},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["filter"]["county"] == "Bács-Kiskun"
        assert data["settlements"][0]["name"] == "Kecskemét"
        assert data["settlements"][0]["coordinates"] == {"lat": 46.9, "lon": 19.7}
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_hungarian_settlements_uses_region_lookup_without_county() -> None:
    """Settlements endpoint should use region lookup when county is omitted."""
    city_manager = MagicMock()
    city_manager.get_cities_for_region.return_value = [
        {
            "city": "Szeged",
            "settlement_type": "város",
            "lat": None,
            "lon": 20.1,
            "population": 160000,
            "region_priority": 1,
        }
    ]
    _setup_city_manager(city_manager)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/hungary/settlements", params={"limit": 3})

        assert response.status_code == 200
        data = response.json()
        city_manager.get_cities_for_region.assert_called_once_with("Hungary", limit=3)
        assert data["count"] == 1
        assert data["settlements"][0]["county"] is None
        assert data["settlements"][0]["coordinates"] is None
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_hungarian_weather_stations_aggregates_all_counties() -> None:
    """Stations endpoint should use bulk query when county not set."""
    city_manager = MagicMock()
    city_manager.get_settlements_bulk.return_value = [
        {
            "id": 1,
            "city": "Vác",
            "megye": "Pest",
            "settlement_type": "város",
            "lat": 47.78,
            "lon": 19.13,
            "population": 33000,
            "region_priority": 1,
        },
        {
            "id": 2,
            "city": "Budapest",
            "megye": "Budapest",
            "settlement_type": "főváros",
            "lat": 47.49,
            "lon": 19.04,
            "population": 1700000,
            "region_priority": 1,
        },
    ]
    _setup_city_manager(city_manager)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/hungary/stations", params={"limit": 5})

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert {station["id"] for station in data["stations"]} == {"HU-1", "HU-2"}
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_hungarian_weather_stations_filters_specific_county() -> None:
    """Stations endpoint should use direct county lookup when county is provided."""
    city_manager = MagicMock()
    city_manager.get_cities_for_hungarian_county.return_value = [
        {
            "id": 7,
            "city": "Debrecen",
            "megye": "Hajdú-Bihar",
            "settlement_type": "város",
            "lat": None,
            "lon": 21.6,
            "population": 200000,
            "region_priority": 1,
        }
    ]
    _setup_city_manager(city_manager)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/api/hungary/stations",
                params={"county": "Hajdú-Bihar", "limit": 5},
            )

        assert response.status_code == 200
        data = response.json()
        city_manager.get_cities_for_hungarian_county.assert_called_once_with("Hajdú-Bihar")
        assert data["filter"]["county"] == "Hajdú-Bihar"
        assert data["stations"][0]["coordinates"] is None
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_hungarian_counties_returns_500_on_failure() -> None:
    """Counties endpoint should surface backend failures as HTTP 500."""
    city_manager = MagicMock()
    city_manager.get_hungarian_counties.side_effect = RuntimeError("boom")
    _setup_city_manager(city_manager)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/hungary/counties")

        assert response.status_code == 500
        assert response.json()["detail"] == "Failed to get Hungarian counties"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_hungarian_settlements_returns_500_on_failure() -> None:
    """Settlements endpoint should convert backend errors to HTTP 500."""
    city_manager = MagicMock()
    city_manager.get_cities_for_region.side_effect = RuntimeError("boom")
    _setup_city_manager(city_manager)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/hungary/settlements")

        assert response.status_code == 500
        assert response.json()["detail"] == "Failed to get Hungarian settlements"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_hungarian_weather_stations_returns_500_on_failure() -> None:
    """Stations endpoint should convert backend errors to HTTP 500."""
    city_manager = MagicMock()
    city_manager.get_settlements_bulk.side_effect = RuntimeError("boom")
    _setup_city_manager(city_manager)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/hungary/stations")

        assert response.status_code == 500
        assert response.json()["detail"] == "Failed to get Hungarian weather stations"
    finally:
        app.dependency_overrides.clear()
