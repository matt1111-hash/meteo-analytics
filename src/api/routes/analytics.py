"""Analytics API routes for trend analysis."""

from __future__ import annotations  # noqa: I001

import logging

from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool

from src.api.dto.trend_request import TrendAnalysisRequest
from src.application.commands.trend_command import TrendAnalysisCommand
from src.application.use_cases.calculate_trend import CalculateTrendUseCase
from src.infrastructure.container import get_city_manager_port, get_weather_client_port

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.post("/trend")
async def calculate_trend(request: TrendAnalysisRequest) -> dict:
    """Calculate climate trend analysis for a location.

    Provides linear regression trend statistics for multiple time periods
    (5, 10, 25, 55 years) with confidence intervals and significance testing.

    Request body:
        location: City name (e.g., "Budapest", "Pécs")
        metric: Weather metric (temperature_2m_max, precipitation_sum, etc.)
        time_periods: List of periods in years (default: [5, 10, 25, 55])
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)

    Returns:
        TrendAnalysisResult with:
        - Period results: slope, R², p-value, trend direction
        - Confidence intervals and significance levels
        - Chart data for visualization
        - KPI dashboard metrics

    Example:
        POST /api/analytics/trend
        {
            "location": "Budapest",
            "metric": "temperature_2m_max",
            "time_periods": [5, 10, 25, 55]
        }
    """
    try:
        use_case = CalculateTrendUseCase(
            weather_client=get_weather_client_port(),
            city_manager=get_city_manager_port(),
        )
        result = await run_in_threadpool(
            lambda: use_case.execute(
                TrendAnalysisCommand(
                    location=request.location,
                    metric=request.metric.value,
                    time_periods=request.time_periods,
                    start_date=request.start_date,
                    end_date=request.end_date,
                )
            )
        )
        return result.to_dict()

    except ValueError as e:
        logger.warning("Invalid trend request: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e

    except Exception as e:
        logger.error("Error calculating trend: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Trend calculation failed",
        ) from e


__all__ = ["router"]
