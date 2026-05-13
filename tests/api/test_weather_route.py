"""Tests for weather analysis API routes."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from src.api.dependencies import ServiceRegistry, get_services
from src.api.main import app
from src.application.use_cases.use_case_result import ResultStatus, UseCaseResult
from src.domain.analytics.models import MultiCityQuery


def _setup_services(monkeypatch: pytest.MonkeyPatch, use_case: MagicMock) -> MagicMock:
    """Create mock service registry with the given use case."""
    mock_services = MagicMock(spec=ServiceRegistry)
    mock_services.analyze_multi_city_use_case = use_case
    app.dependency_overrides[get_services] = lambda: mock_services
    return mock_services


@pytest.mark.anyio
async def test_analyze_multi_city_returns_result_and_passes_aggregate_flag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Multi-city endpoint should build query and forward aggregate flag."""
    use_case = MagicMock()
    use_case.execute.return_value = UseCaseResult(
        status=ResultStatus.SUCCESS,
        data=MagicMock(to_dict=MagicMock(return_value={"city_results": [{"city": "Budapest"}]})),
    )
    query = MultiCityQuery(
        query_type="windiest_today",
        region="Global",
        date="2024-01-01",
    )
    _setup_services(monkeypatch, use_case)
    from src.api.routes import weather  # noqa: PLC0415

    monkeypatch.setattr(weather, "to_multi_city_query", MagicMock(return_value=query))

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
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
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_analyze_multi_city_maps_value_error_to_http_400(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Route should expose validation failures as HTTP 400."""
    _setup_services(monkeypatch, MagicMock())
    from src.api.routes import weather  # noqa: PLC0415

    monkeypatch.setattr(
        weather,
        "to_multi_city_query",
        MagicMock(side_effect=ValueError("bad date range")),
    )

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
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
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_analyze_multi_city_maps_unexpected_error_to_http_500(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unexpected failures should return HTTP 500."""
    mock_services = MagicMock(spec=ServiceRegistry)
    mock_services.analyze_multi_city_use_case = property(
        lambda self: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    app.dependency_overrides[get_services] = lambda: mock_services

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
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
    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_502_does_not_leak_internal_error_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Failed use-case result must not expose internal error_message to client."""
    use_case = MagicMock()
    use_case.execute.return_value = UseCaseResult(
        status=ResultStatus.ERROR,
        error_message="Database connection refused: postgres://secret@internal-host:5432",
    )
    query = MultiCityQuery(
        query_type="hottest_today",
        region="Global",
        date="2024-01-01",
    )
    _setup_services(monkeypatch, use_case)
    from src.api.routes import weather  # noqa: PLC0415

    monkeypatch.setattr(weather, "to_multi_city_query", MagicMock(return_value=query))

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/weather/multi-city",
                json={
                    "cities": ["Budapest"],
                    "date_range": {"start": "2024-01-01", "end": "2024-01-03"},
                    "metric": "temperature_2m_max",
                },
            )

        assert response.status_code == 502
        detail = response.json()["detail"]
        assert detail == "Upstream error"
        assert "postgres" not in detail
        assert "secret" not in detail
    finally:
        app.dependency_overrides.clear()
