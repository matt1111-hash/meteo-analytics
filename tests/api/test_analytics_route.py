"""Tests for analytics API routes."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from src.api.dto.trend_request import TrendAnalysisRequest
from src.application.commands.trend_command import TrendAnalysisCommand


@pytest.mark.asyncio
async def test_calculate_trend_uses_injected_use_case() -> None:
    """Route should use the pre-built use case from the service registry."""
    result = MagicMock()
    result.to_dict.return_value = {"location_name": "Budapest"}
    use_case_instance = MagicMock()
    use_case_instance.execute.return_value = result

    mock_services = MagicMock()
    mock_services.calculate_trend_use_case = use_case_instance

    from src.api.routes import analytics  # noqa: PLC0415

    request = TrendAnalysisRequest(location="Budapest", time_periods=[5])
    response = await analytics.calculate_trend(request, services=mock_services)

    called_cmd = use_case_instance.execute.call_args[0][0]
    assert isinstance(called_cmd, TrendAnalysisCommand)
    assert called_cmd.location == "Budapest"
    assert response == {"location_name": "Budapest"}


@pytest.mark.asyncio
async def test_calculate_trend_maps_value_error_to_http_400() -> None:
    """Route should return HTTP 400 for invalid requests."""
    use_case_instance = MagicMock()
    use_case_instance.execute.side_effect = ValueError("bad request")

    mock_services = MagicMock()
    mock_services.calculate_trend_use_case = use_case_instance

    from src.api.routes import analytics  # noqa: PLC0415

    request = TrendAnalysisRequest(location="Budapest", time_periods=[5])

    with pytest.raises(HTTPException, match="bad request") as exc_info:
        await analytics.calculate_trend(request, services=mock_services)

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_calculate_trend_maps_unexpected_error_to_http_500() -> None:
    """Route should return HTTP 500 for unexpected failures."""
    use_case_instance = MagicMock()
    use_case_instance.execute.side_effect = RuntimeError("boom")

    mock_services = MagicMock()
    mock_services.calculate_trend_use_case = use_case_instance

    from src.api.routes import analytics  # noqa: PLC0415

    request = TrendAnalysisRequest(location="Budapest", time_periods=[5])

    with pytest.raises(HTTPException, match="Trend calculation failed") as exc_info:
        await analytics.calculate_trend(request, services=mock_services)

    assert exc_info.value.status_code == 500
    assert "boom" not in exc_info.value.detail
