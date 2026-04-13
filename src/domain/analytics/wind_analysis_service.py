"""Wind analysis orchestration logic."""

from __future__ import annotations

import datetime
import logging

import pandas as pd
from src.domain.analytics.wind_extractors import (
    extract_daily_wind_data,
    identify_windy_days,
)
from src.domain.analytics.wind_models import (
    WINDY_DAY_THRESHOLD_KMH,
    WindAnalysisResult,
    WindyDayStats,
)
from src.domain.analytics.wind_statistics import calculate_monthly_windy_stats

logger = logging.getLogger(__name__)


def _log_analysis_start(
    weather_data: pd.DataFrame, location_name: str, threshold_kmh: float
) -> None:
    """Log wind analysis inputs."""
    logger.info(f"🌪️ Szél analízis kezdés: {location_name}, küszöb: {threshold_kmh} km/h")
    logger.info(
        f"📊 Bemeneti weather_data: {len(weather_data)} sor, oszlopok: {list(weather_data.columns)}"
    )


def _log_wind_speed_range(daily_wind: pd.DataFrame) -> None:
    """Log extracted wind speed range when data exists."""
    wind_speeds = daily_wind["max_wind_speed_kmh"].dropna()
    if len(wind_speeds) > 0:
        logger.info(
            "🔧 KAPOTT WIND_SPEED (ResultsPanel konvertálta): "
            f"{wind_speeds.min():.1f} - {wind_speeds.max():.1f} km/h"
        )


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
    windiest_month = max(monthly_stats, key=lambda x: x.windy_days_count)
    calmest_month = min(monthly_stats, key=lambda x: x.windy_days_count)
    return windiest_month, calmest_month


def _build_analysis_period(
    daily_wind: pd.DataFrame,
) -> tuple[datetime.date, datetime.date]:
    """Build analysis period from extracted daily wind data."""
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


def _log_analysis_completion(
    total_windy_days: int,
    total_days: int,
    overall_windy_percentage: float,
    windiest_month: WindyDayStats | None,
    calmest_month: WindyDayStats | None,
) -> None:
    """Log final wind analysis summary."""
    logger.info(
        "✅ Szél analízis befejezve: "
        f"{total_windy_days}/{total_days} szeles nap "
        f"({overall_windy_percentage:.1f}%)"
    )
    if windiest_month:
        logger.info(
            "🌪️ Legszélesebb hónap: "
            f"{windiest_month.month_name} ({windiest_month.windy_days_count} nap)"
        )
    if calmest_month:
        logger.info(
            "🌅 Legcsendesebb hónap: "
            f"{calmest_month.month_name} ({calmest_month.windy_days_count} nap)"
        )


def analyze_wind_patterns(
    weather_data: pd.DataFrame,
    location_name: str = "Ismeretlen helyszín",
    threshold_kmh: float = WINDY_DAY_THRESHOLD_KMH,
) -> WindAnalysisResult:
    """
    🔥 DUPLA JAVÍTÁS: Teljes szél minta analízis HELYES ADATOKKAL.

    VÁLTOZÁSOK:
    1. Helyes oszlop használata (széllökések prioritás)
    2. Teljes hónapos lista generálása

    Args:
        weather_data: Weather DataFrame
        location_name: Helyszín neve
        threshold_kmh: Szeles nap küszöbérték

    Returns:
        WindAnalysisResult objektum az eredményekkel
    """
    try:
        if weather_data.empty:
            logger.warning("⚠️ Üres weather_data")
            return _create_empty_analysis_result(location_name, threshold_kmh)

        _log_analysis_start(weather_data, location_name, threshold_kmh)
        daily_wind = extract_daily_wind_data(weather_data)

        if daily_wind.empty:
            logger.warning("⚠️ Nincs feldolgozható szélsebességi adat")
            return _create_empty_analysis_result(location_name, threshold_kmh)

        _log_wind_speed_range(daily_wind)
        windy_days = identify_windy_days(daily_wind, threshold_kmh)
        monthly_stats = calculate_monthly_windy_stats(windy_days)
        total_windy_days, total_days, overall_windy_percentage = _calculate_wind_summary(windy_days)
        windiest_month, calmest_month = _resolve_extreme_months(monthly_stats)
        analysis_period = _build_analysis_period(daily_wind)

        result = WindAnalysisResult(
            location_name=location_name,
            analysis_period=analysis_period,
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

    except Exception as e:
        logger.error(f"❌ Hiba a szél analízisben: {e}")
        import traceback

        traceback.print_exc()
        return _create_empty_analysis_result(location_name, threshold_kmh)


def _create_empty_analysis_result(location_name: str, threshold_kmh: float) -> WindAnalysisResult:
    """Üres analízis eredmény létrehozása hiba esetén."""
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
