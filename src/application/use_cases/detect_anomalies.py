"""Use case for running anomaly detection from GUI-facing data."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Callable, Dict, List, Optional

from src.domain.entities.climate_anomaly import ClimateAnomaly
from src.domain.services.anomaly_detector import AnomalyDetectorService
from src.domain.value_objects.anomaly_threshold import AnomalyThresholdSet

# pylint: disable=too-few-public-methods

logger = logging.getLogger(__name__)


class DetectAnomaliesUseCase:
    """Application layer orchestrator for anomaly detection."""

    def __init__(self, today_provider: Optional[Callable[[], date]] = None) -> None:
        self.today_provider = today_provider or date.today

    def execute(
        self,
        weather_data: Dict[str, List[Any]],
        thresholds: Dict[str, Any],
        location_name: str = "current_location",
    ) -> Dict[str, Optional[ClimateAnomaly]]:
        """Run anomaly detection for temperature, precipitation, and wind."""
        if weather_data is None:
            raise ValueError("weather_data is required")
        threshold_set = self._build_thresholds(thresholds)
        service = AnomalyDetectorService(threshold_set)
        analysis_date = self.today_provider()

        temperature_anomaly = service.detect_temperature_anomaly(
            location_name=location_name,
            analysis_date=analysis_date,
            max_temps=self._safe_float_list(weather_data.get("temperature_2m_max")),
            min_temps=self._safe_float_list(weather_data.get("temperature_2m_min")),
        )
        precipitation_anomaly = service.detect_precipitation_anomaly(
            location_name=location_name,
            analysis_date=analysis_date,
            precipitation_values=self._safe_float_list(
                weather_data.get("precipitation_sum")
            ),
        )
        wind_anomaly = service.detect_wind_anomaly(
            location_name=location_name,
            analysis_date=analysis_date,
            wind_speeds=self._collect_wind_values(weather_data),
        )

        return {
            "temperature": temperature_anomaly,
            "precipitation": precipitation_anomaly,
            "wind": wind_anomaly,
        }

    def _build_thresholds(self, thresholds: Dict[str, Any]) -> AnomalyThresholdSet:
        required_keys = [
            "temp_hot",
            "temp_cold",
            "precip_high",
            "precip_low",
            "wind_normal",
            "wind_strong",
            "wind_extreme",
            "wind_hurricane",
        ]
        missing = [key for key in required_keys if key not in thresholds]
        if missing:
            raise ValueError(f"Hiányzó threshold kulcsok: {', '.join(missing)}")
        try:
            return AnomalyThresholdSet(
                temp_hot=float(thresholds["temp_hot"]),
                temp_cold=float(thresholds["temp_cold"]),
                precip_high=float(thresholds["precip_high"]),
                precip_low=float(thresholds["precip_low"]),
                wind_normal=float(thresholds["wind_normal"]),
                wind_strong=float(thresholds["wind_strong"]),
                wind_extreme=float(thresholds["wind_extreme"]),
                wind_hurricane=float(thresholds["wind_hurricane"]),
            )
        except (TypeError, ValueError) as exc:
            logger.error("Invalid threshold values: %s", thresholds)
            raise ValueError("Threshold values must be numeric") from exc

    def _collect_wind_values(
        self, weather_data: Dict[str, List[Any]]
    ) -> List[Optional[float]]:
        wind_fields = ["wind_speed_10m_max", "wind_gusts_10m_max", "windspeed_10m_max"]
        for field in wind_fields:
            values = self._safe_float_list(weather_data.get(field))
            if values:
                return values
        return []

    def _safe_float_list(self, values: Optional[List[Any]]) -> List[Optional[float]]:
        if not values:
            return []
        result: List[Optional[float]] = []
        for value in values:
            if value is None:
                result.append(None)
                continue
            try:
                result.append(float(value))
            except (TypeError, ValueError):
                continue
        return result
