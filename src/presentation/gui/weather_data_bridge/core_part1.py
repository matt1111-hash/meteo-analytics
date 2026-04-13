# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for WeatherDataBridge."""

from __future__ import annotations

from .core_support import *


class WeatherDataBridgePart1Mixin:  # noqa: D101
    def __init__(self) -> None:  # noqa: D107
        logger.info("Weather Data Bridge initialized with METRIC_MAP")

    def convert_analytics_result(
        self, analytics_result: AnalyticsResult, display_parameter: Optional[str] = None
    ) -> Dict[str, Any]:
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
        """Display parameter normalizálása belső formátumra"""
        normalized = DISPLAY_PARAMETER_MAP.get(display_parameter, display_parameter.lower())
        return normalized

    def convert_analytics_to_weather_overlay(
        self, analytics_result: AnalyticsResult
    ) -> Optional[WeatherOverlayData]:
        """AnalyticsResult → WeatherOverlayData conversion."""
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

    def get_display_parameter_for_metric(self, metric: AnalyticsMetric) -> Optional[str]:
        """Metrika alapján display parameter lekérdezése"""
        return self.METRIC_MAP.get(metric)

    def get_supported_metrics(self) -> List[AnalyticsMetric]:
        """Támogatott metrikák listája"""
        return list(self.METRIC_MAP.keys())

    def is_metric_supported(self, metric: AnalyticsMetric) -> bool:
        """Metrika támogatottság ellenőrzése"""
        return metric in self.METRIC_MAP

    def _is_valid_city_result(self, city_result: CityWeatherResult) -> bool:
        """Ellenőrzi hogy a város eredmény érvényes-e overlay-hez"""
        is_valid = (
            city_result.latitude is not None
            and city_result.longitude is not None
            and city_result.value is not None
            and isinstance(city_result.value, int | float)
            and not (city_result.value == 0 and city_result.city_name == "")
        )
        return is_valid

    def _create_overlay_metadata(
        self, overlay_type: str, values: List[float], analytics_result: AnalyticsResult
    ) -> Dict[str, Any]:
        """Overlay metadata létrehozása."""
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
