"""Tests for metadata API routes."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app


@pytest.mark.anyio
async def test_get_available_metrics_returns_expected_structure() -> None:
    """Metrics endpoint should expose metric metadata and enum values."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/weather/metrics")

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 7
    assert data["metrics"]["temperature_2m_max"]["unit"] == "°C"
    assert "temperature_2m_max" in data["enum_values"]
    assert "precipitation_sum" in data["metrics"]


@pytest.mark.anyio
async def test_get_available_regions_returns_region_metadata() -> None:
    """Regions endpoint should return region names, limits, and country codes."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/weather/regions")

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 3
    assert "Hungary" in data["regions"]
    assert "region_keys" in data
    assert isinstance(data["regions"]["Hungary"]["country_codes"], list)


@pytest.mark.anyio
async def test_get_query_types_returns_frontend_friendly_config() -> None:
    """Query types endpoint should expose templates, metrics, and enum values."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/weather/query-types")

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 1
    assert "hottest_today" in data["query_types"]
    hottest = data["query_types"]["hottest_today"]
    assert hottest["metric"] == "temperature_2m_max"
    assert hottest["metric_enum"] == "temperature_2m_max"
    assert hottest["sort_desc"] is True
