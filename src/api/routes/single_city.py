# mypy: ignore-errors
"""Single city time series API route."""

from __future__ import annotations  # noqa: I001

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from src.api.adapters.weather_adapter import to_multi_city_query
from src.api.dependencies import ServiceRegistry, get_services
from src.api.dto.weather_request import WeatherAnalysisRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/weather", tags=["weather"])


class SingleCityRequest(BaseModel):
    """Request for single city time series analysis."""

    city: str = Field(..., description="City name to analyze")
    start: str = Field(..., description="Start date (YYYY-MM-DD)")
    end: str = Field(..., description="End date (YYYY-MM-DD)")
    metric: str = Field(
        default="temperature_2m_max",
        description="Metric to analyze (temperature_2m_max, windspeed_10m_max, etc.)",
    )


def _metric_to_query_type(metric: str) -> str:
    """Map metric name to query_type for QUERY_TYPES lookup."""
    metric_to_query = {
        "temperature_2m_max": "hottest_today",
        "temperature_2m_min": "coldest_today",
        "temperature_2m_mean": "temperature_mean",
        "precipitation_sum": "wettest_today",
        "windspeed_10m_max": "windiest_today",
        "windgusts_10m_max": "wind_gusts",
        "temperature_range": "temperature_range",
    }
    return metric_to_query.get(metric, "hottest_today")


@router.post("/single-city")
async def analyze_single_city_timeseries(
    request: SingleCityRequest,
    services: ServiceRegistry = Depends(get_services),
) -> dict:
    """Analyze single city with daily time series breakdown (NO aggregation)."""
    try:
        query_type = _metric_to_query_type(request.metric)

        multi_city_request = WeatherAnalysisRequest(
            cities=[request.city],
            date_range={"start": request.start, "end": request.end},
        )

        query = to_multi_city_query(multi_city_request)

        from dataclasses import replace  # noqa: PLC0415

        query = replace(query, query_type=query_type)

        uc_result = await run_in_threadpool(
            lambda: services.analyze_multi_city_use_case.execute(query, aggregate=False)
        )

        if not uc_result.is_success:
            raise HTTPException(status_code=502, detail="Upstream error")

        response = uc_result.data.to_dict()
        response["requested_metrics"] = [request.metric]
        response["daily_breakdown"] = True

        return response

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Unexpected error in single-city analysis: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
