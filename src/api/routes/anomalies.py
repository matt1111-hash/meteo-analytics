# mypy: ignore-errors
"""Anomaly detection API route."""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.analytics.multi_city_engine_core import MultiCityEngine
from src.analytics.multi_city_types import HUNGARIAN_REGIONAL_MAPPING, REGIONS
from src.api.dto.weather_request import WeatherAnalysisRequest
from src.application.use_cases import AnalyzeMultiCityUseCase, DetectAnomaliesUseCase
from src.domain.analytics.services import (
    AnalyticsTransformService,
    RegionResolverService,
    WeatherFetchService,
)
from src.domain.ports import CityRepositoryPort
from src.infrastructure.container import get_city_repository_port

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/weather", tags=["anomalies"])


class AnomalyThresholds(BaseModel):
    """Anomaly detection thresholds."""

    temp_hot: float = Field(default=30.0, description="Hot temperature threshold (°C)")
    temp_cold: float = Field(default=0.0, description="Cold temperature threshold (°C)")
    precip_high: float = Field(
        default=50.0, description="High precipitation threshold (mm)"
    )
    precip_low: float = Field(
        default=1.0, description="Low precipitation threshold (mm)"
    )
    wind_normal: float = Field(
        default=20.0, description="Normal wind speed threshold (km/h)"
    )
    wind_strong: float = Field(default=40.0, description="Strong wind threshold (km/h)")
    wind_extreme: float = Field(
        default=60.0, description="Extreme wind threshold (km/h)"
    )
    wind_hurricane: float = Field(
        default=100.0, description="Hurricane wind threshold (km/h)"
    )


class AnomalyDetectionRequest(BaseModel):
    """Request for anomaly detection."""

    city: str = Field(..., description="City name to analyze")
    start: str = Field(..., description="Start date (YYYY-MM-DD)")
    end: str = Field(..., description="End date (YYYY-MM-DD)")
    thresholds: Optional[AnomalyThresholds] = Field(
        default=None,
        description="Custom thresholds (defaults provided if not specified)",
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


anomaly_use_case = DetectAnomaliesUseCase()


def _serialize_anomaly(anomaly: Any) -> Optional[Dict[str, Any]]:
    """Convert ClimateAnomaly to JSON-serializable dict."""
    if anomaly is None:
        return None
    data = asdict(anomaly)
    # Convert date to ISO string
    if "date" in data and data["date"]:
        data["date"] = data["date"].isoformat()
    return data


def _get_city_or_404(
    weather_use_case: AnalyzeMultiCityUseCase, city_name: str
) -> List[Dict[str, Any]]:
    """Fetch city records or raise 404."""
    cities = weather_use_case.city_repository.get_cities_by_names([city_name])
    if cities:
        return cities
    raise HTTPException(status_code=404, detail=f"City not found: {city_name}")


def _fetch_weather_or_404(
    weather_use_case: AnalyzeMultiCityUseCase,
    city_name: str,
    start: str,
    end: str,
    cities: List[Dict[str, Any]],
) -> List[Any]:
    """Fetch raw weather data or raise 404."""
    region_config = weather_use_case.regions.get("Global", {})
    raw_weather_data = (
        weather_use_case.weather_fetch_service.fetch_weather_data_dual_api_batch(
            cities=cities,
            date=start,
            region_config=region_config,
            start_date=start,
            end_date=end,
        )
    )
    if raw_weather_data:
        return raw_weather_data
    raise HTTPException(
        status_code=404, detail=f"No weather data found for {city_name}"
    )


def _build_weather_metric_lists(
    raw_weather_data: List[Any],
) -> Dict[str, List[Optional[float]]]:
    """Build metric lists for anomaly detection."""
    return {
        "temperature_2m_max": [item.temperature_2m_max for item in raw_weather_data],
        "temperature_2m_min": [item.temperature_2m_min for item in raw_weather_data],
        "precipitation_sum": [item.precipitation_sum for item in raw_weather_data],
        "windspeed_10m_max": [item.windspeed_10m_max for item in raw_weather_data],
    }


def _resolve_thresholds(request: AnomalyDetectionRequest) -> Dict[str, Any]:
    """Resolve custom or default anomaly thresholds."""
    if request.thresholds:
        return request.thresholds.model_dump()
    return AnomalyThresholds().model_dump()


@router.post("/anomalies")
async def detect_anomalies(request: AnomalyDetectionRequest) -> dict:
    """Detect weather anomalies for a city over a date range.

    Returns:
        Anomaly detection results for temperature, precipitation, and wind.
    """
    try:
        weather_use_case = _build_use_case()
        WeatherAnalysisRequest(
            cities=[request.city],
            date_range={"start": request.start, "end": request.end},
        )
        cities = _get_city_or_404(weather_use_case, request.city)
        raw_weather_data = _fetch_weather_or_404(
            weather_use_case, request.city, request.start, request.end, cities
        )
        weather_data = _build_weather_metric_lists(raw_weather_data)
        thresholds_dict = _resolve_thresholds(request)
        anomalies = anomaly_use_case.execute(
            weather_data=weather_data,
            thresholds=thresholds_dict,
            location_name=request.city,
        )
        return {
            "city": request.city,
            "date_range": {"start": request.start, "end": request.end},
            "anomalies": {
                "temperature": _serialize_anomaly(anomalies["temperature"]),
                "precipitation": _serialize_anomaly(anomalies["precipitation"]),
                "wind": _serialize_anomaly(anomalies["wind"]),
            },
            "thresholds_used": thresholds_dict,
        }

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Unexpected error in anomaly detection: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
