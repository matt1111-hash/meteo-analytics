"""Weather analysis API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query

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


@router.post("/multi-city")
async def analyze_multi_city(
    request: WeatherAnalysisRequest,
    aggregate: bool = Query(
        default=True,
        description="Aggregate multi-day data per city (True) or return daily time series (False)",
    ),
) -> dict:
    """Run multi-city analysis with defaults derived from request.

    Args:
        request: Weather analysis request parameters
        aggregate: If True (default), aggregates multi-day data per city.
                  If False, returns all daily records as time series.
    """
    try:
        use_case = _build_use_case()
        query = to_multi_city_query(request)
        result = use_case.execute(query, aggregate=aggregate)
        return result.to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - safety net
        logger.error("Unexpected error in analyze_multi_city: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
