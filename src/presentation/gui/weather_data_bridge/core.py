# mypy: ignore-errors
"""Weather Data Bridge - Multi-City Engine to Folium Map Integration."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from src.domain.entities.analytics_models import AnalyticsResult
from src.domain.entities.weather import CityWeatherResult
from src.domain.value_objects.enums import AnalyticsMetric
from src.presentation.gui.weather_data_bridge.constants import (
    DISPLAY_PARAMETER_MAP,
    METRIC_MAP,
    OVERLAY_CONFIGS,
)
from src.presentation.gui.weather_data_bridge.data import WeatherOverlayData
from src.presentation.gui.weather_data_bridge.folium_bridge import (
    debug_metric_mapping as _debug_metric_mapping,
)
from src.presentation.gui.weather_data_bridge.folium_bridge import (
    get_folium_heatmap_data as _get_folium_heatmap_data,
)
from src.presentation.gui.weather_data_bridge.folium_bridge import (
    get_folium_marker_data as _get_folium_marker_data,
)

logger = logging.getLogger(__name__)


class WeatherDataBridge:
    """
    Weather Data Bridge - Analytics Engine to Folium Map Integration.

    Responsibilities:
    - AnalyticsResult to Folium overlay format conversion
    - 4 weather types supported (temperature, precipitation, wind, wind_gusts)
    - Coordinates + values extraction
    - Metric-based overlay type auto-detection
    - Min/max values calculation for color scales
    """

    METRIC_MAP = METRIC_MAP
    METRIC_TO_OVERLAY = METRIC_MAP
    OVERLAY_CONFIGS = OVERLAY_CONFIGS

    def __init__(self) -> None:  # noqa: D107
        logger.info("Weather Data Bridge initialized with METRIC_MAP")

    def convert_analytics_result(
        self, analytics_result: AnalyticsResult, display_parameter: str | None = None
    ) -> dict[str, Any]:
        """Convert analytics result based on display_parameter."""
        try:
            if not analytics_result or not analytics_result.city_results:
                logger.warning("Empty analytics result")
                return {}

            metric = analytics_result.question.metric

            if display_parameter:
                detected_parameter = self._normalize_display_parameter(display_parameter)
            else:
                detected_parameter = self.METRIC_MAP.get(metric)
                if not detected_parameter:
                    logger.error(f"Unknown metric: {metric}")
                    return {}

            result_data = {detected_parameter: {}}

            for city_result in analytics_result.city_results:
                if self._is_valid_city_result(city_result):
                    city_data = {
                        "coordinates": [city_result.latitude, city_result.longitude],
                        "value": float(city_result.value),
                    }
                    if detected_parameter in ["wind_speed", "wind_gusts"]:
                        city_data["speed"] = float(city_result.value)
                        city_data["direction"] = 0
                    result_data[detected_parameter][city_result.city_name] = city_data

            if not result_data[detected_parameter]:
                return {}

            return result_data

        except Exception as e:
            logger.error(f"Error in analytics result conversion: {e}", exc_info=True)
            return {}

    def _normalize_display_parameter(self, display_parameter: str) -> str:
        """Display parameter normalizalasa belso formatumra"""
        normalized = DISPLAY_PARAMETER_MAP.get(display_parameter, display_parameter.lower())
        return normalized

    def convert_analytics_to_weather_overlay(
        self, analytics_result: AnalyticsResult
    ) -> WeatherOverlayData | None:
        """AnalyticsResult to WeatherOverlayData conversion."""
        try:
            if not analytics_result or not analytics_result.city_results:
                return None

            metric = analytics_result.question.metric
            overlay_type = self.METRIC_MAP.get(metric)

            if not overlay_type:
                return None

            weather_data = {}
            values = []

            for city_result in analytics_result.city_results:
                if self._is_valid_city_result(city_result):
                    city_data = {
                        "coordinates": [city_result.latitude, city_result.longitude],
                        "value": float(city_result.value),
                        "city_name": city_result.city_name,
                        "country": city_result.country,
                        "country_code": city_result.country_code,
                        "population": city_result.population,
                        "rank": getattr(city_result, "rank", 0),
                        "quality_score": city_result.quality_score,
                    }
                    if overlay_type in ["wind_speed", "wind_gusts"]:
                        city_data["speed"] = float(city_result.value)
                        city_data["direction"] = 0
                    weather_data[city_result.city_name] = city_data
                    values.append(float(city_result.value))

            if not weather_data:
                return None

            metadata = self._create_overlay_metadata(overlay_type, values, analytics_result)

            return WeatherOverlayData(
                overlay_type=overlay_type, data=weather_data, metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error in overlay conversion: {e}", exc_info=True)
            return None

    def get_display_parameter_for_metric(self, metric: AnalyticsMetric) -> str | None:
        """Metrika alapjan display parameter lekerdezese"""
        return self.METRIC_MAP.get(metric)

    def get_supported_metrics(self) -> list[AnalyticsMetric]:
        """Tamogatott metrikak listaja"""
        return list(self.METRIC_MAP.keys())

    def is_metric_supported(self, metric: AnalyticsMetric) -> bool:
        """Metrika tamogatottsag ellenorzese"""
        return metric in self.METRIC_MAP

    def _is_valid_city_result(self, city_result: CityWeatherResult) -> bool:
        """Ellenorzi hogy a varos eredmeny ervenyes-e overlay-hez"""
        is_valid = (
            city_result.latitude is not None
            and city_result.longitude is not None
            and city_result.value is not None
            and isinstance(city_result.value, int | float)
            and not (city_result.value == 0 and city_result.city_name == "")
        )
        return is_valid

    def _create_overlay_metadata(
        self, overlay_type: str, values: list[float], analytics_result: AnalyticsResult
    ) -> dict[str, Any]:
        """Overlay metadata letrehozasa."""
        config = self.OVERLAY_CONFIGS[overlay_type]

        value_min = min(values) if values else 0
        value_max = max(values) if values else 1

        if overlay_type == "temperature":
            abs_max = max(abs(value_min), abs(value_max))
            scale_min = -abs_max if value_min < 0 else min(value_min, 0)
            scale_max = abs_max if value_max > 0 else max(value_max, 0)
        else:
            scale_min = 0
            scale_max = value_max * 1.1

        return {
            "overlay_type": overlay_type,
            "name": config["name"],
            "unit": config["unit"],
            "icon": config["icon"],
            "color_scale": config["color_scale"],
            "value_min": value_min,
            "value_max": value_max,
            "scale_min": scale_min,
            "scale_max": scale_max,
            "total_cities": len(values),
            "analytics_question": analytics_result.question.question_text,
            "execution_time": analytics_result.execution_time,
            "data_sources": [source.value for source in analytics_result.data_sources_used],
            "statistics": analytics_result.statistics,
            "generated_at": datetime.now().isoformat(),
            "metric": analytics_result.question.metric.value,
        }

    def get_overlay_legend_data(self, overlay_data: WeatherOverlayData) -> dict[str, Any]:
        """Legend adatok generalasa a Folium terrekephez"""
        metadata = overlay_data.metadata

        return {
            "title": f"{metadata['icon']} {metadata['name']}",
            "unit": metadata["unit"],
            "min_value": metadata["scale_min"],
            "max_value": metadata["scale_max"],
            "color_scale": metadata["color_scale"],
            "total_cities": metadata["total_cities"],
            "value_range": f"{metadata['value_min']:.1f} - {metadata['value_max']:.1f}",
            "question": metadata["analytics_question"],
            "metric": metadata.get("metric", "unknown"),
        }

    def create_multiple_overlays_from_analytics(
        self, analytics_results: list[AnalyticsResult]
    ) -> dict[str, WeatherOverlayData]:
        """Tobb analytics eredmenyekbol tobb overlay letrehozasa"""
        overlays = {}

        for result in analytics_results:
            overlay_data = self.convert_analytics_to_weather_overlay(result)
            if overlay_data:
                overlays[overlay_data.overlay_type] = overlay_data

        return overlays

    def get_folium_heatmap_data(self, overlay_data: WeatherOverlayData) -> list[list[float]]:
        """Convert overlay data to Folium HeatMap format."""
        return _get_folium_heatmap_data(overlay_data)

    def get_folium_marker_data(self, overlay_data: WeatherOverlayData) -> list[dict[str, Any]]:
        """Convert overlay data to Folium CircleMarker format."""
        return _get_folium_marker_data(overlay_data)

    def debug_metric_mapping(self) -> dict[str, Any]:
        """Return debug information about metric mapping."""
        return _debug_metric_mapping()
