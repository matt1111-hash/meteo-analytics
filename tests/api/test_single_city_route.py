"""Tests for single-city API route."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app
from src.api.routes import single_city
from src.domain.analytics.models import MultiCityQuery


@pytest.mark.anyio
async def test_analyze_single_city_timeseries_returns_daily_breakdown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Single-city endpoint should return raw daily data and metadata."""
    use_case = MagicMock()
    use_case.execute.return_value = MagicMock(
        to_dict=MagicMock(
            return_value={"city_results": [{"date": "2024-01-01", "value": 12.0}]}
        )
    )
    monkeypatch.setattr(
        single_city, "_build_use_case", MagicMock(return_value=use_case)
    )
    monkeypatch.setattr(
        single_city,
        "to_multi_city_query",
        MagicMock(
            return_value=MultiCityQuery(
                query_type="hottest_today",
                region="Global",
                date="2024-01-01",
            )
        ),
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/weather/single-city",
            json={
                "city": "Budapest",
                "start": "2024-01-01",
                "end": "2024-01-03",
                "metric": "windspeed_10m_max",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["city_results"] == [{"date": "2024-01-01", "value": 12.0}]
    assert data["requested_metrics"] == ["windspeed_10m_max"]
    assert data["daily_breakdown"] is True
    executed_query = use_case.execute.call_args.args[0]
    assert executed_query.query_type == "windiest_today"
    assert use_case.execute.call_args.kwargs["aggregate"] is False


@pytest.mark.anyio
async def test_analyze_single_city_uses_default_mapping_for_unknown_metric(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unknown metrics should fall back to hottest_today query type."""
    use_case = MagicMock()
    use_case.execute.return_value = MagicMock(
        to_dict=MagicMock(return_value={"city_results": []})
    )
    monkeypatch.setattr(
        single_city, "_build_use_case", MagicMock(return_value=use_case)
    )
    monkeypatch.setattr(
        single_city,
        "to_multi_city_query",
        MagicMock(
            return_value=MultiCityQuery(
                query_type="hottest_today",
                region="Global",
                date="2024-01-01",
            )
        ),
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/weather/single-city",
            json={
                "city": "Budapest",
                "start": "2024-01-01",
                "end": "2024-01-03",
                "metric": "unknown_metric",
            },
        )

    assert response.status_code == 200
    assert use_case.execute.call_args.args[0].query_type == "hottest_today"


@pytest.mark.anyio
async def test_analyze_single_city_maps_value_error_to_http_400(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Value errors should map to HTTP 400."""
    use_case = MagicMock()
    use_case.execute.side_effect = ValueError("bad request")
    monkeypatch.setattr(
        single_city, "_build_use_case", MagicMock(return_value=use_case)
    )
    monkeypatch.setattr(
        single_city,
        "to_multi_city_query",
        MagicMock(
            return_value=MultiCityQuery(
                query_type="hottest_today",
                region="Global",
                date="2024-01-01",
            )
        ),
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/weather/single-city",
            json={"city": "Budapest", "start": "2024-01-01", "end": "2024-01-03"},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "bad request"


@pytest.mark.anyio
async def test_analyze_single_city_maps_unexpected_error_to_http_500(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unexpected errors should map to HTTP 500."""
    monkeypatch.setattr(
        single_city,
        "_build_use_case",
        MagicMock(side_effect=RuntimeError("boom")),
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/weather/single-city",
            json={"city": "Budapest", "start": "2024-01-01", "end": "2024-01-03"},
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
