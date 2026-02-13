"""Detailed single city analysis with multiple metrics API route."""

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


class DetailedCityRequest(BaseModel):
    """Request for detailed single city analysis with multiple metrics."""

    city: str = Field(..., description="City name to analyze")
    start: str = Field(..., description="Start date (YYYY-MM-DD)")
    end: str = Field(..., description="End date (YYYY-MM-DD)")


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


use_case = _build_use_case()


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


@router.post("/single-city-detailed")
async def analyze_single_city_detailed(request: DetailedCityRequest) -> dict:
    """Analyze single city with ALL metrics for comprehensive analysis.

    Returns:
        Dictionary with separate result sets for each metric category:
        - temperature: temperature_2m_mean data
        - wind: windspeed_10m_max data
        - wind_gusts: windgusts_10m_max data
        - precipitation: precipitation_sum data
    """
    try:
        # Make 4 separate API calls to get each metric separately
        # This prevents data duplication that was happening with aggregate=False
        metrics = {
            "temperature": "temperature_2m_mean",
            "wind": "windspeed_10m_max",
            "wind_gusts": "windgusts_10m_max",
            "precipitation": "precipitation_sum",
        }

        results = {}

        for key, metric in metrics.items():
            query_type = _metric_to_query_type(metric)

            # Convert to multi-city request format
            multi_city_request = WeatherAnalysisRequest(
                cities=[request.city],
                date_range={"start": request.start, "end": request.end},
            )

            query = to_multi_city_query(multi_city_request)

            # Override query_type
            from dataclasses import replace

            query = replace(query, query_type=query_type)

            # Use aggregate=False to get ALL daily records (not just aggregated top results)
            result = use_case.execute(query, aggregate=False)
            results[key] = result.to_dict()["city_results"]

        # Combine all results
        response = {
            "city": request.city,
            "start": request.start,
            "end": request.end,
            "temperature_data": results["temperature"],
            "wind_data": results["wind"],
            "wind_gusts_data": results["wind_gusts"],
            "precipitation_data": results["precipitation"],
        }

        return response

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(
            "Unexpected error in detailed-city analysis: %s", exc, exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error") from exc
