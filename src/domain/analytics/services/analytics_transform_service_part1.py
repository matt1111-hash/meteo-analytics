# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for AnalyticsTransformService."""

from __future__ import annotations

from .analytics_transform_service_support import *


class AnalyticsTransformServicePart1Mixin:  # noqa: D101
    def __init__(self, query_types: Dict[str, Dict[str, Any]]) -> None:  # noqa: D107
        if not query_types:
            raise ValueError("query_types mapping is required")
        self.query_types = query_types

    def transform_to_city_weather_result(
        self,
        city_data: CityWeatherData,
        query_type: str,
    ) -> CityWeatherResult:
        """Convert CityWeatherData to CityWeatherResult using query config."""
        query_config = self._require_query_config(query_type)
        metric_name = query_config["metric"]
        metric_enum = query_config["metric_enum"]
        metric_value = self._extract_metric_value(city_data, metric_name)
        self._log_transform_inputs(city_data, metric_name, metric_value)
        final_value = self._resolve_final_metric_value(city_data, metric_value, metric_enum)

        return CityWeatherResult(
            city_name=city_data.city,
            country=city_data.country,
            country_code=city_data.country_code,
            latitude=city_data.lat,
            longitude=city_data.lon,
            value=final_value,
            metric=metric_enum,
            date=datetime.strptime(city_data.date, "%Y-%m-%d").date()
            if city_data.date
            else datetime.now().date(),
            population=city_data.population,
            quality_score=city_data.data_quality_score
            if city_data.data_quality_score is not None
            else 0.0,
        )

    @staticmethod
    def _extract_metric_value(city_data: CityWeatherData, metric_name: str) -> Any:
        """Extract metric value from city weather data."""
        if metric_name == "temperature_range":
            return city_data.temperature_range
        return getattr(city_data, metric_name, None)

    @staticmethod
    def _log_transform_inputs(
        city_data: CityWeatherData, metric_name: str, metric_value: Any
    ) -> None:
        """Log inputs used for transformation."""
        logger.info(
            "TRANSFORM DEBUG: %s - %s=%s (type: %s)",
            city_data.city,
            metric_name,
            metric_value,
            type(metric_value),
        )
        logger.info(
            "RAW DATA: temp_max=%s, temp_min=%s, precip=%s, windspeed=%s",
            city_data.temperature_2m_max,
            city_data.temperature_2m_min,
            city_data.precipitation_sum,
            city_data.windspeed_10m_max,
        )

    @staticmethod
    def _resolve_fallback_value(city_data: CityWeatherData, metric_enum: AnalyticsMetric) -> float:
        """Resolve fallback metric value."""
        if metric_enum == AnalyticsMetric.PRECIPITATION_SUM:
            return 0.0

        fallback_value = (
            city_data.temperature_2m_max
            or city_data.temperature_2m_min
            or city_data.windspeed_10m_max
            or 0.0
        )
        logger.warning(
            "NULL metric value for %s, using fallback: %s",
            city_data.city,
            fallback_value,
        )
        return float(fallback_value)

    def _resolve_final_metric_value(
        self,
        city_data: CityWeatherData,
        metric_value: Any,
        metric_enum: AnalyticsMetric,
    ) -> float:
        """Resolve final numeric metric value."""
        if metric_value is not None and metric_value != 0:
            return float(metric_value)
        return self._resolve_fallback_value(city_data, metric_enum)
