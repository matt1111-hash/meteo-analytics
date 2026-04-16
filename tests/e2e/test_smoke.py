"""
E2E smoke tests — critical user flows.

These tests verify that the full stack (FastAPI routes → services → data layer)
works end-to-end without starting a real HTTP server. External weather APIs are
mocked so the tests are deterministic and offline-safe.

Critical flow: backend health → city search → weather data → metadata.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

# ---------------------------------------------------------------------------
# 1. Health check
# ---------------------------------------------------------------------------


class TestHealthCheck:
    """Backend health endpoint must be reachable without auth."""

    @pytest.mark.anyio
    async def test_health_returns_ok(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body.get("status") == "ok"


# ---------------------------------------------------------------------------
# 2. City search — the entry point for every user interaction
# ---------------------------------------------------------------------------


class TestCitySearch:
    """City autocomplete must return results from the local database."""

    @pytest.mark.anyio
    async def test_search_budapest(self, client: AsyncClient) -> None:
        response = await client.get(
            "/api/cities/search",
            params={"query": "Budapest", "limit": 5},
        )
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["count"] >= 1
        assert any(c["name"] == "Budapest" for c in body["cities"]), (
            f"Budapest not found in: {[c['name'] for c in body['cities']]}"
        )

    @pytest.mark.anyio
    async def test_search_returns_coordinates(self, client: AsyncClient) -> None:
        response = await client.get(
            "/api/cities/search",
            params={"query": "Budapest", "limit": 1},
        )
        assert response.status_code == status.HTTP_200_OK
        city = response.json()["cities"][0]
        assert city["coordinates"] is not None
        assert "lat" in city["coordinates"]
        assert "lon" in city["coordinates"]

    @pytest.mark.anyio
    async def test_search_empty_query_returns_4xx(self, client: AsyncClient) -> None:
        response = await client.get(
            "/api/cities/search",
            params={"query": "", "limit": 5},
        )
        assert response.status_code in {
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        }


# ---------------------------------------------------------------------------
# 3. Weather data — single city (mocked external API)
# ---------------------------------------------------------------------------

MOCK_SINGLE_CITY_RESPONSE = {
    "city_results": [
        {
            "city_name": "Budapest",
            "date": "2024-01-15",
            "value": 3.5,
            "metric": "temperature_2m_max",
        },
        {
            "city_name": "Budapest",
            "date": "2024-01-16",
            "value": 4.1,
            "metric": "temperature_2m_max",
        },
    ],
}


class TestSingleCityWeather:
    """Single-city weather endpoint must return data with correct structure."""

    @pytest.mark.anyio
    async def test_single_city_returns_data(self, client: AsyncClient) -> None:
        mock_result = MagicMock()
        mock_result.to_dict.return_value = MOCK_SINGLE_CITY_RESPONSE

        mock_use_case = MagicMock()
        mock_use_case.execute = MagicMock(return_value=mock_result)

        with patch(
            "src.api.routes.single_city._build_use_case",
            return_value=mock_use_case,
        ):
            response = await client.post(
                "/api/weather/single-city",
                json={
                    "city": "Budapest",
                    "start": "2024-01-15",
                    "end": "2024-01-16",
                    "metric": "temperature_2m_max",
                },
            )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert "city_results" in body
        assert len(body["city_results"]) == 2
        assert body["city_results"][0]["value"] == 3.5

    @pytest.mark.anyio
    async def test_single_city_missing_city_returns_4xx(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/weather/single-city",
            json={
                "city": "",
                "start": "2024-01-15",
                "end": "2024-01-16",
                "metric": "temperature_2m_max",
            },
        )
        assert response.status_code in {
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        }


# ---------------------------------------------------------------------------
# 4. Metadata — metrics and regions must be available
# ---------------------------------------------------------------------------


class TestMetadata:
    """Weather metadata endpoints must return non-empty lists."""

    @pytest.mark.anyio
    async def test_metrics_endpoint(self, client: AsyncClient) -> None:
        response = await client.get("/api/weather/metrics")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert "metrics" in body
        assert len(body["metrics"]) > 0
        # Verify at least one well-known metric exists
        assert "temperature_2m_max" in body["metrics"]

    @pytest.mark.anyio
    async def test_regions_endpoint(self, client: AsyncClient) -> None:
        response = await client.get("/api/weather/regions")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert "regions" in body

    @pytest.mark.anyio
    async def test_query_types_endpoint(self, client: AsyncClient) -> None:
        response = await client.get("/api/weather/query-types")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert "query_types" in body


# ---------------------------------------------------------------------------
# 5. Provider status — must list available weather providers
# ---------------------------------------------------------------------------


class TestProviders:
    """Provider management endpoints must list providers."""

    @pytest.mark.anyio
    async def test_provider_list(self, client: AsyncClient) -> None:
        response = await client.get("/api/providers/list")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert "providers" in body
        assert len(body["providers"]) > 0

    @pytest.mark.anyio
    async def test_provider_status(self, client: AsyncClient) -> None:
        response = await client.get("/api/providers/status")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert isinstance(body, list)
        assert len(body) > 0
        assert "provider_id" in body[0]
        assert "status" in body[0]
