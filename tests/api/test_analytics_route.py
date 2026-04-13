"""Tests for analytics API routes."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from src.api.dto.trend_request import TrendAnalysisRequest
from src.api.routes import analytics


@pytest.mark.asyncio
async def test_calculate_trend_builds_use_case_with_injected_ports(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Route should construct the use case with outer-layer dependencies."""
    weather_client = MagicMock()
    city_manager = MagicMock()
    result = MagicMock()
    result.to_dict.return_value = {"location_name": "Budapest"}
    use_case_instance = MagicMock()
    use_case_instance.execute.return_value = result
    use_case_factory = MagicMock(return_value=use_case_instance)
    monkeypatch.setattr(
        analytics, "get_weather_client_port", MagicMock(return_value=weather_client)
    )
    monkeypatch.setattr(analytics, "get_city_manager_port", MagicMock(return_value=city_manager))
    monkeypatch.setattr(analytics, "CalculateTrendUseCase", use_case_factory)
    request = TrendAnalysisRequest(location="Budapest", time_periods=[5])

    response = await analytics.calculate_trend(request)

    use_case_factory.assert_called_once_with(
        weather_client=weather_client,
        city_manager=city_manager,
    )
    use_case_instance.execute.assert_called_once_with(request)
    assert response == {"location_name": "Budapest"}


@pytest.mark.asyncio
async def test_calculate_trend_maps_value_error_to_http_400(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Route should return HTTP 400 for invalid requests."""
    use_case_instance = MagicMock()
    use_case_instance.execute.side_effect = ValueError("bad request")
    monkeypatch.setattr(analytics, "get_weather_client_port", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(analytics, "get_city_manager_port", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(
        analytics, "CalculateTrendUseCase", MagicMock(return_value=use_case_instance)
    )
    request = TrendAnalysisRequest(location="Budapest", time_periods=[5])

    with pytest.raises(HTTPException, match="bad request") as exc_info:
        await analytics.calculate_trend(request)

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_calculate_trend_maps_unexpected_error_to_http_500(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Route should return HTTP 500 for unexpected failures."""
    use_case_instance = MagicMock()
    use_case_instance.execute.side_effect = RuntimeError("boom")
    monkeypatch.setattr(analytics, "get_weather_client_port", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(analytics, "get_city_manager_port", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(
        analytics, "CalculateTrendUseCase", MagicMock(return_value=use_case_instance)
    )
    request = TrendAnalysisRequest(location="Budapest", time_periods=[5])

    with pytest.raises(HTTPException, match="Trend calculation failed: boom") as exc_info:
        await analytics.calculate_trend(request)

    assert exc_info.value.status_code == 500
