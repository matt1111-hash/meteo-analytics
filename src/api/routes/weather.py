"""Weather analysis API routes."""

from __future__ import annotations  # noqa: I001

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.concurrency import run_in_threadpool

from src.api.adapters.weather_adapter import to_multi_city_query
from src.api.dependencies import ServiceRegistry, get_services
from src.api.dto.weather_request import WeatherAnalysisRequest
from src.api.error_handling import raise_for_use_case_result

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.post("/multi-city")
async def analyze_multi_city(
    request: WeatherAnalysisRequest,
    aggregate: bool = Query(
        default=True,
        description="Aggregate multi-day data per city (True) or return daily time series (False)",
    ),
    services: ServiceRegistry = Depends(get_services),
) -> dict:
    """Run multi-city analysis with defaults derived from request."""
    try:
        query = to_multi_city_query(request)
        uc_result = await run_in_threadpool(
            lambda: services.analyze_multi_city_use_case.execute(query, aggregate=aggregate)
        )
        raise_for_use_case_result(uc_result)
        assert uc_result.data is not None
        return uc_result.data.to_dict()
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - safety net
        logger.error("Unexpected error in analyze_multi_city: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
