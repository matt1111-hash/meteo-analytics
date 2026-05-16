"""Compatibility wrapper for wind analysis orchestration."""

from __future__ import annotations

import logging

import pandas as pd

from src.application.services.wind_extractors import (
    extract_daily_wind_data,
    identify_windy_days,
)
from src.application.services.wind_pattern_analyzer import (
    _build_analysis_period,
    _calculate_wind_summary,
    _create_empty_analysis_result,
    _resolve_extreme_months,
)
from src.application.services.wind_statistics import calculate_monthly_windy_stats
from src.domain.analytics.wind_models import (
    WINDY_DAY_THRESHOLD_KMH,
    WindAnalysisResult,
    WindyDayStats,
)

logger = logging.getLogger(__name__)


def _log_wind_speed_range(daily_wind: pd.DataFrame) -> None:
    """Log extracted wind speed range when data exists."""
    wind_speeds = daily_wind["max_wind_speed_kmh"].dropna()
    if len(wind_speeds) > 0:
        logger.info(
            "Extracted wind speed range: %.1f - %.1f km/h",
            wind_speeds.min(),
            wind_speeds.max(),
        )


def _log_analysis_completion(
    total_windy_days: int,
    total_days: int,
    overall_windy_percentage: float,
    windiest_month: WindyDayStats | None,
    calmest_month: WindyDayStats | None,
) -> None:
    """Log final wind analysis summary."""
    logger.info(
        "Wind analysis completed: %s/%s windy days (%.1f%%)",
        total_windy_days,
        total_days,
        overall_windy_percentage,
    )
    if windiest_month:
        logger.info(
            "Windiest month: %s (%s days)",
            windiest_month.month_name,
            windiest_month.windy_days_count,
        )
    if calmest_month:
        logger.info(
            "Calmest month: %s (%s days)",
            calmest_month.month_name,
            calmest_month.windy_days_count,
        )


def analyze_wind_patterns(
    weather_data: pd.DataFrame,
    location_name: str = "Ismeretlen helyszín",
    threshold_kmh: float = WINDY_DAY_THRESHOLD_KMH,
) -> WindAnalysisResult:
    """
    Analyze wind patterns from weather data.

    This compatibility implementation keeps historical patch points in this
    module while the application layer owns the same orchestration logic.
    """
    try:
        if weather_data.empty:
            logger.warning("Weather data is empty")
            return _create_empty_analysis_result(location_name, threshold_kmh)

        daily_wind = extract_daily_wind_data(weather_data)
        if daily_wind.empty:
            logger.warning("No processable wind speed data found")
            return _create_empty_analysis_result(location_name, threshold_kmh)

        _log_wind_speed_range(daily_wind)
        windy_days = identify_windy_days(daily_wind, threshold_kmh)
        monthly_stats = calculate_monthly_windy_stats(windy_days)
        total_windy_days, total_days, overall_windy_percentage = _calculate_wind_summary(windy_days)
        windiest_month, calmest_month = _resolve_extreme_months(monthly_stats)

        result = WindAnalysisResult(
            location_name=location_name,
            analysis_period=_build_analysis_period(daily_wind),
            threshold_kmh=threshold_kmh,
            monthly_stats=monthly_stats,
            total_windy_days=total_windy_days,
            total_days=total_days,
            overall_windy_percentage=overall_windy_percentage,
            windiest_month=windiest_month,
            calmest_month=calmest_month,
        )

        _log_analysis_completion(
            total_windy_days,
            total_days,
            overall_windy_percentage,
            windiest_month,
            calmest_month,
        )
        return result
    except Exception:
        logger.exception("Failed to analyze wind patterns")
        return _create_empty_analysis_result(location_name, threshold_kmh)


__all__ = [
    "_build_analysis_period",
    "_calculate_wind_summary",
    "_create_empty_analysis_result",
    "_log_analysis_completion",
    "_log_wind_speed_range",
    "_resolve_extreme_months",
    "analyze_wind_patterns",
    "extract_daily_wind_data",
]
