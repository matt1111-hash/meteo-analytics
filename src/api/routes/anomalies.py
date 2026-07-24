"""Anomaly detection API route."""

from __future__ import annotations  # noqa: I001

import logging
from dataclasses import asdict
from typing import Any, Dict, List  # noqa: UP035

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator
from starlette.concurrency import run_in_threadpool

from src.api.dependencies import ServiceRegistry, get_services
from src.api.dto.weather_request import WeatherAnalysisRequest
from src.api.dto.weather_request import validate_date_span, validate_iso_date
from src.application.use_cases import AnalyzeMultiCityUseCase, DetectAnomaliesUseCase

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/weather", tags=["anomalies"])


class AnomalyThresholds(BaseModel):
    """Anomaly detection thresholds."""

    temp_hot: float = Field(default=30.0, description="Hot temperature threshold (°C)")
    temp_cold: float = Field(default=0.0, description="Cold temperature threshold (°C)")
    precip_high: float = Field(default=50.0, description="High precipitation threshold (mm)")
    precip_low: float = Field(default=1.0, description="Low precipitation threshold (mm)")
    wind_normal: float = Field(default=20.0, description="Normal wind speed threshold (km/h)")
    wind_strong: float = Field(default=40.0, description="Strong wind threshold (km/h)")
    wind_extreme: float = Field(default=60.0, description="Extreme wind threshold (km/h)")
    wind_hurricane: float = Field(default=100.0, description="Hurricane wind threshold (km/h)")


class AnomalyDetectionRequest(BaseModel):
    """Request for anomaly detection."""

    city: str = Field(..., min_length=1, description="City name to analyze")
    start: str = Field(..., description="Start date (YYYY-MM-DD)")
    end: str = Field(..., description="End date (YYYY-MM-DD)")
    thresholds: AnomalyThresholds | None = Field(
        default=None,
        description="Custom thresholds (defaults provided if not specified)",
    )

    @field_validator("start", "end")
    @classmethod
    def _check_date_format(cls, value: str) -> str:
        return validate_iso_date(value)

    @model_validator(mode="after")
    def _check_date_span(self) -> AnomalyDetectionRequest:
        validate_date_span(self.start, self.end)
        return self


anomaly_use_case = DetectAnomaliesUseCase()


def _serialize_anomaly(anomaly: Any) -> Dict[str, Any] | None:  # noqa: UP006
    """Convert ClimateAnomaly to JSON-serializable dict."""
    if anomaly is None:
        return None
    data = asdict(anomaly)
    # Convert date to ISO string
    if "date" in data and data["date"]:  # noqa: RUF019
        data["date"] = data["date"].isoformat()
    return data


def _get_city_or_404(
    weather_use_case: AnalyzeMultiCityUseCase, city_name: str
) -> List[Dict[str, Any]]:  # noqa: UP006
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
    cities: List[Dict[str, Any]],  # noqa: UP006
) -> List[Any]:  # noqa: UP006
    """Fetch raw weather data or raise 404."""
    region_config = weather_use_case.regions.get("Global", {})
    raw_weather_data = weather_use_case.weather_fetch_service.fetch_weather_data_dual_api_batch(
        cities=cities,
        date=start,
        region_config=region_config,
        start_date=start,
        end_date=end,
    )
    if raw_weather_data:
        return raw_weather_data
    raise HTTPException(status_code=404, detail=f"No weather data found for {city_name}")


def _build_weather_metric_lists(
    raw_weather_data: List[Any],  # noqa: UP006
) -> Dict[str, List[float | None]]:  # noqa: UP006
    """Build metric lists for anomaly detection."""
    return {
        "temperature_2m_max": [item.temperature_2m_max for item in raw_weather_data],
        "temperature_2m_min": [item.temperature_2m_min for item in raw_weather_data],
        "precipitation_sum": [item.precipitation_sum for item in raw_weather_data],
        "windspeed_10m_max": [item.windspeed_10m_max for item in raw_weather_data],
    }


def _resolve_thresholds(request: AnomalyDetectionRequest) -> Dict[str, Any]:  # noqa: UP006
    """Resolve custom or default anomaly thresholds."""
    if request.thresholds:
        return request.thresholds.model_dump()
    return AnomalyThresholds().model_dump()


@router.post("/anomalies")
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    services: ServiceRegistry = Depends(get_services),
) -> dict:
    """Detect weather anomalies for a city over a date range.

    Returns:
        Anomaly detection results for temperature, precipitation, and wind.
    """
    try:
        weather_use_case = services.analyze_multi_city_use_case
        WeatherAnalysisRequest(
            cities=[request.city],
            date_range={"start": request.start, "end": request.end},
        )
        cities = _get_city_or_404(weather_use_case, request.city)
        raw_weather_data = await run_in_threadpool(
            lambda: _fetch_weather_or_404(
                weather_use_case, request.city, request.start, request.end, cities
            )
        )
        weather_data = _build_weather_metric_lists(raw_weather_data)
        thresholds_dict = _resolve_thresholds(request)
        result = await run_in_threadpool(
            lambda: anomaly_use_case.execute(
                weather_data=weather_data,
                thresholds=thresholds_dict,
                location_name=request.city,
            )
        )
        anomalies: dict[str, Any] = result
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
