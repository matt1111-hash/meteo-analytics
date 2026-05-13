"""Statistics and result factory functions for analytics."""

from __future__ import annotations

import logging
from collections.abc import Iterable

from src.domain.analytics.models import CityWeatherData
from src.domain.analytics.statistics import (
    safe_mean,
    safe_median,
    safe_min_max,
    safe_stdev,
)
from src.domain.entities.analytics_models import AnalyticsQuestion, AnalyticsResult
from src.domain.entities.weather import CityWeatherResult
from src.domain.value_objects.enums import AnalyticsMetric, QuestionType, RegionScope

logger = logging.getLogger(__name__)


def calculate_statistics_for_results_none_safe(
    results: list[CityWeatherResult],
) -> dict[str, float]:
    """Compute none-safe statistics from CityWeatherResult list."""
    logger.info("NONE-SAFE STATS: %d results", len(results))
    all_values = [r.value for r in results]
    if not all_values:
        logger.error("No values for statistics")
        return {}

    stats: dict[str, float] = {}
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


def get_provider_stats(weather_data: Iterable[CityWeatherData]) -> dict[str, int]:
    """Count provider usage from CityWeatherData list."""
    stats: dict[str, int] = {}
    for item in weather_data:
        source = item.data_source or "unknown"
        stats[source] = stats.get(source, 0) + 1
    return stats


def create_empty_analytics_result(
    question: AnalyticsQuestion | None,
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
