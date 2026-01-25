"""Transform and statistics service for analytics results."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from src.domain.analytics.statistics import safe_mean, safe_median, safe_min_max, safe_stdev
from src.domain.analytics.models import CityWeatherData
from src.domain.value_objects.enums import AnalyticsMetric, QuestionType, RegionScope
from src.domain.entities.analytics_models import AnalyticsQuestion, AnalyticsResult
from src.domain.entities.weather import CityWeatherResult

logger = logging.getLogger(__name__)


class AnalyticsTransformService:
    """Handle weather result transformation, sorting, and statistics."""

    def __init__(self, query_types: Dict[str, Dict[str, Any]]) -> None:
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

        metric_value = city_data.temperature_range if metric_name == "temperature_range" else getattr(
            city_data, metric_name, None
        )

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

        if metric_value is not None and metric_value != 0:
            final_value = float(metric_value)
        else:
            # Use metric-specific fallback - NEVER use temperature for precipitation!
            if metric_enum == AnalyticsMetric.PRECIPITATION_SUM:
                # For precipitation, prefer zero over wrong temperature data
                fallback_value = 0.0
            else:
                # For temperature metrics, use fallback chain
                fallback_value = (
                    city_data.temperature_2m_max
                    or city_data.temperature_2m_min
                    or city_data.windspeed_10m_max
                    or 0.0
                )
                logger.warning("NULL metric value for %s, using fallback: %s", city_data.city, fallback_value)

            final_value = float(fallback_value) if fallback_value is not None else 0.0

        return CityWeatherResult(
            city_name=city_data.city,
            country=city_data.country,
            country_code=city_data.country_code,
            latitude=city_data.lat,
            longitude=city_data.lon,
            value=final_value,
            metric=metric_enum,
            date=datetime.strptime(city_data.date, "%Y-%m-%d").date() if city_data.date else datetime.now().date(),
            population=city_data.population,
            quality_score=city_data.data_quality_score if city_data.data_quality_score is not None else 0.0,
        )

    def process_weather_results(
        self, weather_data: List[CityWeatherData], query_type: str, aggregate: bool = True
    ) -> List[CityWeatherData]:
        """Sort and enrich weather data with computed temperature range.

        Args:
            aggregate: If True, aggregates multi-day data per city by taking max value.
                      If False, returns all daily records without aggregation.
        """
        logger.info("WEATHER RESULT PROCESSING: %d total records (aggregate=%s)", len(weather_data), aggregate)
        query_config = self._require_query_config(query_type)
        metric = query_config["metric"]
        sort_desc = query_config["sort_desc"]

        # Compute temperature_range for all records
        for city_data in weather_data:
            if metric == "temperature_range" and city_data.fetch_success:
                temp_max = city_data.temperature_2m_max
                temp_min = city_data.temperature_2m_min
                if temp_max is not None and temp_min is not None:
                    try:
                        city_data.temperature_range = temp_max - temp_min
                    except (TypeError, ValueError):
                        city_data.temperature_range = None

        # Conditionally aggregate multi-day data per city
        if aggregate:
            city_aggregates: Dict[str, CityWeatherData] = {}
            for city_data in weather_data:
                city_key = city_data.city
                current_value = getattr(city_data, metric, None)

                if city_key not in city_aggregates:
                    city_aggregates[city_key] = city_data
                else:
                    # Compare and keep the record with higher metric value (for max aggregation)
                    existing_value = getattr(city_aggregates[city_key], metric, None)
                    if current_value is not None and (existing_value is None or current_value > existing_value):
                        city_aggregates[city_key] = city_data

            aggregated_data = list(city_aggregates.values())
            logger.info("AGGREGATED TO: %d unique cities", len(aggregated_data))
        else:
            # No aggregation - return all daily records
            aggregated_data = weather_data
            logger.info("NO AGGREGATION: Returning all %d daily records", len(aggregated_data))

        # DEBUG: Log filtered out records
        for d in aggregated_data:
            if not d.fetch_success or getattr(d, metric, None) is None:
                logger.warning(
                    "FILTERED OUT: date=%s city=%s fetch_success=%s %s=%s",
                    d.date, d.city, d.fetch_success, metric, getattr(d, metric, None)
                )

        valid_data = [
            d for d in aggregated_data if d.fetch_success and getattr(d, metric, None) is not None
        ]
        if not valid_data:
            logger.error("NO VALID DATA for metric '%s'", metric)
            return weather_data[:5]

        def get_sort_value(city: CityWeatherData) -> float:
            value = getattr(city, metric, None)
            if value is None:
                return float("-inf") if sort_desc else float("inf")
            try:
                return float(value)
            except (ValueError, TypeError):
                return float("-inf") if sort_desc else float("inf")

        try:
            sorted_data = sorted(valid_data, key=get_sort_value, reverse=sort_desc)
        except Exception as exc:
            logger.error("Rendezési hiba: %s", exc, exc_info=True)
            sorted_data = valid_data

        if query_type == "windiest_today":
            logger.info("TOP WINDIEST CITIES: %s", [(c.city, getattr(c, metric, None)) for c in sorted_data[:3]])

        return sorted_data

    def calculate_statistics_for_results_none_safe(self, results: List[CityWeatherResult]) -> Dict[str, float]:
        """Compute none-safe statistics from CityWeatherResult list."""
        logger.info("NONE-SAFE STATS: %d results", len(results))
        all_values = [r.value for r in results]
        if not all_values:
            logger.error("No values for statistics")
            return {}

        stats: Dict[str, float] = {}
        mean_val = safe_mean(all_values)
        median_val = safe_median(all_values)
        stdev_val = safe_stdev(all_values)
        min_val, max_val = safe_min_max(all_values)

        if mean_val is not None:
            stats["mean"] = mean_val
        if median_val is not None:
            stats["median"] = median_val
        if stdev_val is not None:
            stats["stdev"] = stdev_val
        if min_val is not None:
            stats["min"] = min_val
        if max_val is not None:
            stats["max"] = max_val
        if min_val is not None and max_val is not None:
            stats["range"] = max_val - min_val

        logger.info("STATS RESULT: %s", stats)
        return stats

    def get_provider_stats(self, weather_data: Iterable[CityWeatherData]) -> Dict[str, int]:
        """Count provider usage from CityWeatherData list."""
        stats: Dict[str, int] = {}
        for item in weather_data:
            source = item.data_source or "unknown"
            stats[source] = stats.get(source, 0) + 1
        return stats

    def create_empty_analytics_result(
        self,
        question: Optional[AnalyticsQuestion],
        error_msg: str = "Ismeretlen hiba",
    ) -> AnalyticsResult:
        """Create fallback AnalyticsResult when processing fails."""
        try:
            fallback_question = question or AnalyticsQuestion(
                question_text=error_msg,
                question_type=QuestionType.TEMPERATURE_MAX,
                region_scope=RegionScope.GLOBAL,
                metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
            )
            return AnalyticsResult(
                question=fallback_question,
                city_results=[],
                execution_time=0.0,
                total_cities_found=0,
                data_sources_used=[],
                statistics={},
                provider_statistics={},
            )
        except Exception as exc:
            logger.error("Critical error creating empty AnalyticsResult: %s", exc)
            raise

    def _require_query_config(self, query_type: str) -> Dict[str, Any]:
        config = self.query_types.get(query_type)
        if not config:
            raise ValueError(f"Ismeretlen query_type: {query_type}")
        return config
