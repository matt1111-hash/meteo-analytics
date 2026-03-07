"""Single city time series API route."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.analytics.multi_city_engine_core import MultiCityEngine
from src.analytics.multi_city_types import HUNGARIAN_REGIONAL_MAPPING, REGIONS
from src.api.adapters.weather_adapter import to_multi_city_query
from src.api.dto.weather_request import WeatherAnalysisRequest
from src.application.use_cases import AnalyzeMultiCityUseCase
from src.domain.analytics.services import (
    AnalyticsTransformService,
    RegionResolverService,
    WeatherFetchService,
)
from src.domain.ports import CityRepositoryPort
from src.infrastructure.container import get_city_repository_port

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


def _build_use_case() -> AnalyzeMultiCityUseCase:
    """Build use case with dependencies (CA compliant - uses ports)."""
    engine = MultiCityEngine()
    city_repo: CityRepositoryPort = get_city_repository_port()
    return AnalyzeMultiCityUseCase(
        region_resolver=RegionResolverService(),
        city_repository=city_repo,
        weather_fetch_service=WeatherFetchService(
            weather_client=engine.weather_client,
            max_workers=engine.max_workers,
            request_timeout=engine.request_timeout,
            max_retries=engine.max_retries,
            retry_delay=engine.retry_delay,
        ),
        analytics_transform_service=AnalyticsTransformService(
            MultiCityEngine.QUERY_TYPES
        ),
        query_types=MultiCityEngine.QUERY_TYPES,
        regions=REGIONS,
        hungarian_mapping=HUNGARIAN_REGIONAL_MAPPING,
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
async def analyze_single_city_timeseries(request: SingleCityRequest) -> dict:
    """Analyze single city with daily time series breakdown (NO aggregation).

    Returns:
        Daily weather data for the specified date range without aggregation.
        Each day is a separate record in the results.
    """
    try:
        use_case = _build_use_case()
        # Map metric to query_type
        query_type = _metric_to_query_type(request.metric)

        # Convert to multi-city request format (reuse existing logic)
        multi_city_request = WeatherAnalysisRequest(
            cities=[request.city],
            date_range={"start": request.start, "end": request.end},
        )

        # Execute analysis WITHOUT aggregation (daily time series)
        query = to_multi_city_query(multi_city_request)

        # Override query_type with metric-specific one
        from dataclasses import replace

        query = replace(query, query_type=query_type)

        result = use_case.execute(query, aggregate=False)

        # Return RAW daily data WITHOUT aggregation
        response = result.to_dict()

        # Add metadata
        response["requested_metrics"] = [request.metric]
        response["daily_breakdown"] = True

        return response

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Unexpected error in single-city analysis: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
