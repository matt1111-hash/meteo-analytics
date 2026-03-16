# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for AnalyticsTransformService."""

from __future__ import annotations

from .analytics_transform_service_support import *


class AnalyticsTransformServicePart2Mixin:
    @staticmethod
    def _compute_temperature_ranges(
        weather_data: List[CityWeatherData], metric: str
    ) -> None:
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
        weather_data: List[CityWeatherData], metric: str
    ) -> List[CityWeatherData]:
        """Aggregate weather data by city using max metric value."""
        city_aggregates: Dict[str, CityWeatherData] = {}
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
    def _log_filtered_records(
        aggregated_data: List[CityWeatherData], metric: str
    ) -> None:
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
        aggregated_data: List[CityWeatherData], metric: str
    ) -> List[CityWeatherData]:
        """Keep only records with successful fetch and sortable metric."""
        return [
            item
            for item in aggregated_data
            if item.fetch_success and getattr(item, metric, None) is not None
        ]

    @staticmethod
    def _sort_records(
        valid_data: List[CityWeatherData], metric: str, sort_desc: bool
    ) -> List[CityWeatherData]:
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
            logger.error("Rendezési hiba: %s", exc, exc_info=True)
            return valid_data

    def process_weather_results(
        self,
        weather_data: List[CityWeatherData],
        query_type: str,
        aggregate: bool = True,
    ) -> List[CityWeatherData]:
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
            logger.info(
                "NO AGGREGATION: Returning all %d daily records", len(aggregated_data)
            )
        self._log_filtered_records(aggregated_data, metric)
        valid_data = self._filter_valid_records(aggregated_data, metric)
        if not valid_data:
            logger.error("NO VALID DATA for metric '%s'", metric)
            return weather_data[:5]
        sorted_data = self._sort_records(valid_data, metric, sort_desc)

        if query_type == "windiest_today":
            logger.info(
                "TOP WINDIEST CITIES: %s",
                [(c.city, getattr(c, metric, None)) for c in sorted_data[:3]],
            )

        return sorted_data

    def calculate_statistics_for_results_none_safe(
        self, results: List[CityWeatherResult]
    ) -> Dict[str, float]:
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

    def get_provider_stats(
        self, weather_data: Iterable[CityWeatherData]
    ) -> Dict[str, int]:
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
