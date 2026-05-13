"""
Integration tests for city search and weather endpoints.

These tests exercise the full stack (FastAPI → routes → DI → repository → database)
without mocking, verifying that real data flows correctly through the system.
"""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from src.api.main import app

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client():
    """Async HTTP client wired to the real FastAPI app (with real services)."""
    from src.api.dependencies import build_service_registry  # noqa: PLC0415

    app.state.services = build_service_registry()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c
    del app.state.services


# ---------------------------------------------------------------------------
# City Search — integration with real SQLite database
# ---------------------------------------------------------------------------


class TestCitySearchIntegration:
    """City search using the real city repository and database."""

    @pytest.mark.anyio
    async def test_search_hungarian_capital(self, client: AsyncClient) -> None:
        response = await client.get("/api/cities/search", params={"query": "Budapest"})
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["count"] >= 1
        city = body["cities"][0]
        assert city["name"] == "Budapest"
        assert city["country"] == "Hungary"
        assert city["coordinates"] is not None
        assert city["coordinates"]["lat"] == pytest.approx(47.5, abs=1.0)

    @pytest.mark.anyio
    async def test_search_partial_match(self, client: AsyncClient) -> None:
        response = await client.get("/api/cities/search", params={"query": "Deb", "limit": 5})
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["count"] >= 1
        names = [c["name"] for c in body["cities"]]
        assert any("Debrecen" in n for n in names)

    @pytest.mark.anyio
    async def test_search_returns_consistent_structure(self, client: AsyncClient) -> None:
        response = await client.get("/api/cities/search", params={"query": "Pécs"})
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert "query" in body
        assert "count" in body
        assert "cities" in body
        assert body["query"] == "Pécs"

        if body["count"] > 0:
            city = body["cities"][0]
            required_keys = {"name", "country", "country_code", "coordinates"}
            assert required_keys.issubset(city.keys())

    @pytest.mark.anyio
    async def test_search_limit_parameter(self, client: AsyncClient) -> None:
        response = await client.get("/api/cities/search", params={"query": "Bu", "limit": 3})
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["count"] <= 3

    @pytest.mark.anyio
    async def test_search_no_results(self, client: AsyncClient) -> None:
        response = await client.get(
            "/api/cities/search",
            params={"query": "ZZZZNONEXISTENT12345"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 0


# ---------------------------------------------------------------------------
# Weather metadata — integration with real configuration
# ---------------------------------------------------------------------------


class TestWeatherMetadataIntegration:
    """Weather metadata endpoints with real service layer."""

    @pytest.mark.anyio
    async def test_metrics_list_has_required_fields(self, client: AsyncClient) -> None:
        response = await client.get("/api/weather/metrics")
        assert response.status_code == status.HTTP_200_OK
        metrics = response.json()["metrics"]
        required_metrics = [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
        ]
        for m in required_metrics:
            assert m in metrics, f"Missing metric: {m}"
            assert "name" in metrics[m]
            assert "unit" in metrics[m]

    @pytest.mark.anyio
    async def test_regions_returns_structure(self, client: AsyncClient) -> None:
        response = await client.get("/api/weather/regions")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert "regions" in body

    @pytest.mark.anyio
    async def test_query_types_returns_structure(self, client: AsyncClient) -> None:
        response = await client.get("/api/weather/query-types")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert "query_types" in body
