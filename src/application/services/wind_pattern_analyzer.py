"""Wind analysis orchestration logic."""

from __future__ import annotations

import datetime
import logging

import pandas as pd

from src.application.services.wind_extractors import (
    extract_daily_wind_data,
    identify_windy_days,
)
from src.application.services.wind_statistics import calculate_monthly_windy_stats
from src.domain.analytics.wind_models import (
    WINDY_DAY_THRESHOLD_KMH,
    WindAnalysisResult,
    WindyDayStats,
)

logger = logging.getLogger(__name__)


def _calculate_wind_summary(windy_days: pd.DataFrame) -> tuple[int, int, float]:
    """Calculate overall windy-day totals and percentage."""
    if windy_days.empty:
        return 0, 0, 0.0

    total_windy_days = windy_days["is_windy"].sum()
    total_days = len(windy_days)
    overall_windy_percentage = (total_windy_days / total_days) * 100 if total_days > 0 else 0.0
    return total_windy_days, total_days, overall_windy_percentage


def _resolve_extreme_months(
    monthly_stats: list[WindyDayStats],
) -> tuple[WindyDayStats | None, WindyDayStats | None]:
    """Resolve windiest and calmest months."""
    if not monthly_stats:
        return None, None
    windiest_month = max(monthly_stats, key=lambda item: item.windy_days_count)
    calmest_month = min(monthly_stats, key=lambda item: item.windy_days_count)
    return windiest_month, calmest_month


def _build_analysis_period(
    daily_wind: pd.DataFrame,
) -> tuple[datetime.date, datetime.date]:
    """Build the analysis period from extracted daily wind data."""
    if daily_wind.empty:
        today = datetime.date.today()
        return today, today

    start_date = daily_wind["date"].min()
    end_date = daily_wind["date"].max()
    if hasattr(start_date, "date"):
        start_date = start_date.date()
    if hasattr(end_date, "date"):
        end_date = end_date.date()
    return start_date, end_date


def analyze_wind_patterns(
    weather_data: pd.DataFrame,
    location_name: str = "Ismeretlen helyszín",
    threshold_kmh: float = WINDY_DAY_THRESHOLD_KMH,
) -> WindAnalysisResult:
    """
    Analyze wind patterns from weather data.

    Args:
        weather_data: Weather dataframe.
        location_name: Display name of the analyzed location.
        threshold_kmh: Windy-day threshold in km/h.

    Returns:
        Wind analysis result.
    """
    try:
        if weather_data.empty:
            logger.warning("Weather data is empty")
            return _create_empty_analysis_result(location_name, threshold_kmh)

        logger.info("Starting wind analysis: %s, threshold %.1f km/h", location_name, threshold_kmh)
        daily_wind = extract_daily_wind_data(weather_data)

        if daily_wind.empty:
            logger.warning("No processable wind speed data found")
            return _create_empty_analysis_result(location_name, threshold_kmh)

        windy_days = identify_windy_days(daily_wind, threshold_kmh)
        monthly_stats = calculate_monthly_windy_stats(windy_days)
        total_windy_days, total_days, overall_windy_percentage = _calculate_wind_summary(windy_days)
        windiest_month, calmest_month = _resolve_extreme_months(monthly_stats)

        return WindAnalysisResult(
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
    except Exception:
        logger.exception("Failed to analyze wind patterns")
        return _create_empty_analysis_result(location_name, threshold_kmh)


def _create_empty_analysis_result(location_name: str, threshold_kmh: float) -> WindAnalysisResult:
    """Create an empty analysis result for missing or invalid data."""
    today = datetime.date.today()
    return WindAnalysisResult(
        location_name=location_name,
        analysis_period=(today, today),
        threshold_kmh=threshold_kmh,
        monthly_stats=[],
        total_windy_days=0,
        total_days=0,
        overall_windy_percentage=0.0,
        windiest_month=None,
        calmest_month=None,
    )


__all__ = ["_create_empty_analysis_result", "analyze_wind_patterns"]
