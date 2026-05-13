"""Analytics API routes for trend analysis."""

from __future__ import annotations  # noqa: I001

import logging

from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool

from src.api.dependencies import ServiceRegistry, get_services
from src.api.dto.trend_request import TrendAnalysisRequest
from src.application.commands.trend_command import TrendAnalysisCommand

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.post("/trend")
async def calculate_trend(
    request: TrendAnalysisRequest,
    services: ServiceRegistry = Depends(get_services),
) -> dict:
    """Calculate climate trend analysis for a location.

    Provides linear regression trend statistics for multiple time periods
    (5, 10, 25, 55 years) with confidence intervals and significance testing.
    """
    try:
        result = await run_in_threadpool(
            lambda: services.calculate_trend_use_case.execute(
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
