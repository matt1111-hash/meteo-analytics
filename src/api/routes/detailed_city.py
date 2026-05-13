"""Detailed single city analysis with multiple metrics API route."""

from __future__ import annotations  # noqa: I001

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from src.api.dependencies import ServiceRegistry, get_services

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/weather", tags=["weather"])


class DetailedCityRequest(BaseModel):
    """Request for detailed single city analysis with multiple metrics."""

    city: str = Field(..., description="City name to analyze")
    start: str = Field(..., description="Start date (YYYY-MM-DD)")
    end: str = Field(..., description="End date (YYYY-MM-DD)")


@router.post("/single-city-detailed")
async def analyze_single_city_detailed(
    request: DetailedCityRequest,
    services: ServiceRegistry = Depends(get_services),
) -> dict:
    """Analyze single city with ALL metrics — single fetch, four metric extractions."""
    try:
        result = await run_in_threadpool(
            lambda: services.detailed_city_use_case.execute(
                city=request.city, start=request.start, end=request.end
            )
        )
        return {
            "city": result.city,
            "start": result.start,
            "end": result.end,
            "temperature_data": result.temperature_data,
            "wind_data": result.wind_data,
            "wind_gusts_data": result.wind_gusts_data,
            "precipitation_data": result.precipitation_data,
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Unexpected error in detailed-city analysis: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
