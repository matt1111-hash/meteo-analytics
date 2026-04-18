# mypy: ignore-errors
"""Transform and statistics service for analytics results."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from datetime import datetime
from typing import Any

from src.domain.analytics.models import CityWeatherData
from src.domain.analytics.services.analytics_statistics import (
    calculate_statistics_for_results_none_safe as _calc_stats,
)
from src.domain.analytics.services.analytics_statistics import (
    create_empty_analytics_result as _create_empty,
)
from src.domain.analytics.services.analytics_statistics import (
    get_provider_stats as _get_provider_stats,
)
from src.domain.entities.analytics_models import AnalyticsQuestion, AnalyticsResult
from src.domain.entities.weather import CityWeatherResult
from src.domain.value_objects.enums import AnalyticsMetric

logger = logging.getLogger(__name__)


class AnalyticsTransformService:
    """Handle weather result transformation, sorting, and statistics."""

    def __init__(self, query_types: dict[str, dict[str, Any]]) -> None:
        """Initialize with query type configuration mapping."""
        if not query_types:
            raise ValueError("query_types mapping is required")
        self.query_types = query_types

    # ------------------------------------------------------------------
    # Query config helpers
    # ------------------------------------------------------------------

    def _require_query_config(self, query_type: str) -> dict[str, Any]:
        config = self.query_types.get(query_type)
        if not config:
            raise ValueError(f"Ismeretlen query_type: {query_type}")
        return config

    # ------------------------------------------------------------------
    # Transform
    # ------------------------------------------------------------------

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
        if metric_value is not None:
            return float(metric_value)
        return self._resolve_fallback_value(city_data, metric_enum)

    # ------------------------------------------------------------------
    # Processing pipeline
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_temperature_ranges(weather_data: list[CityWeatherData], metric: str) -> None:
        """Compute temperature range for eligible records."""
        if metric != "temperature_range":
            return

        for city_data in weather_data:
            if not city_data.fetch_success:
                continue
            temp_max = city_data.temperature_2m_max
            temp_min = city_data.temperature_2m_min
            if temp_max is None or temp_min is None:
                continue
            try:
                city_data.temperature_range = temp_max - temp_min
            except (TypeError, ValueError):
                city_data.temperature_range = None

    @staticmethod
    def _aggregate_by_city(
        weather_data: list[CityWeatherData], metric: str
    ) -> list[CityWeatherData]:
        """Aggregate weather data by city using max metric value."""
        city_aggregates: dict[str, CityWeatherData] = {}
        for city_data in weather_data:
            city_key = city_data.city
            current_value = getattr(city_data, metric, None)
            existing_data = city_aggregates.get(city_key)
            if existing_data is None:
                city_aggregates[city_key] = city_data
                continue

            existing_value = getattr(existing_data, metric, None)
            if current_value is not None and (
                existing_value is None or current_value > existing_value
            ):
                city_aggregates[city_key] = city_data

        return list(city_aggregates.values())

    @staticmethod
    def _log_filtered_records(aggregated_data: list[CityWeatherData], metric: str) -> None:
        """Log records removed from result candidates."""
        for item in aggregated_data:
            metric_value = getattr(item, metric, None)
            if item.fetch_success and metric_value is not None:
                continue
            logger.warning(
                "FILTERED OUT: date=%s city=%s fetch_success=%s %s=%s",
                item.date,
                item.city,
                item.fetch_success,
                metric,
                metric_value,
            )

    @staticmethod
    def _filter_valid_records(
        aggregated_data: list[CityWeatherData], metric: str
    ) -> list[CityWeatherData]:
        """Keep only records with successful fetch and sortable metric."""
        return [
            item
            for item in aggregated_data
            if item.fetch_success and getattr(item, metric, None) is not None
        ]

    @staticmethod
    def _sort_records(
        valid_data: list[CityWeatherData], metric: str, sort_desc: bool
    ) -> list[CityWeatherData]:
        """Sort records by selected metric."""

        def get_sort_value(city: CityWeatherData) -> float:
            value = getattr(city, metric, None)
            if value is None:
                return float("-inf") if sort_desc else float("inf")
            try:
                return float(value)
            except (ValueError, TypeError):
                return float("-inf") if sort_desc else float("inf")

        try:
            return sorted(valid_data, key=get_sort_value, reverse=sort_desc)
        except Exception as exc:
            logger.error("Rendezesi hiba: %s", exc, exc_info=True)
            return valid_data

    def process_weather_results(
        self,
        weather_data: list[CityWeatherData],
        query_type: str,
        aggregate: bool = True,
    ) -> list[CityWeatherData]:
        """Sort and enrich weather data with computed temperature range.

        Args:
            aggregate: If True, aggregates multi-day data per city by taking max value.
                      If False, returns all daily records without aggregation.
        """
        logger.info(
            "WEATHER RESULT PROCESSING: %d total records (aggregate=%s)",
            len(weather_data),
            aggregate,
        )
        query_config = self._require_query_config(query_type)
        metric = query_config["metric"]
        sort_desc = query_config["sort_desc"]
        self._compute_temperature_ranges(weather_data, metric)
        if aggregate:
            aggregated_data = self._aggregate_by_city(weather_data, metric)
            logger.info("AGGREGATED TO: %d unique cities", len(aggregated_data))
        else:
            aggregated_data = weather_data
            logger.info("NO AGGREGATION: Returning all %d daily records", len(aggregated_data))
        self._log_filtered_records(aggregated_data, metric)
        valid_data = self._filter_valid_records(aggregated_data, metric)
        if not valid_data:
            logger.error("NO VALID DATA for metric '%s'", metric)
            return []
        sorted_data = self._sort_records(valid_data, metric, sort_desc)

        if query_type == "windiest_today":
            logger.info(
                "TOP WINDIEST CITIES: %s",
                [(c.city, getattr(c, metric, None)) for c in sorted_data[:3]],
            )

        return sorted_data

    # ------------------------------------------------------------------
    # Statistics (delegated to analytics_statistics module)
    # ------------------------------------------------------------------

    def calculate_statistics_for_results_none_safe(
        self, results: list[CityWeatherResult]
    ) -> dict[str, float]:
        """Compute none-safe statistics from CityWeatherResult list."""
        return _calc_stats(results)

    def get_provider_stats(self, weather_data: Iterable[CityWeatherData]) -> dict[str, int]:
        """Count provider usage from CityWeatherData list."""
        return _get_provider_stats(weather_data)

    def create_empty_analytics_result(
        self,
        question: AnalyticsQuestion | None,
        error_msg: str = "Ismeretlen hiba",
    ) -> AnalyticsResult:
        """Create fallback AnalyticsResult when processing fails."""
        return _create_empty(question, error_msg)
