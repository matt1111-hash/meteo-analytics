"""Wind analysis orchestration logic."""

from __future__ import annotations

import datetime
import logging

import pandas as pd

from src.domain.analytics.wind_extractors import (
    extract_daily_wind_data,
    identify_windy_days,
)
from src.domain.analytics.wind_models import WINDY_DAY_THRESHOLD_KMH, WindAnalysisResult
from src.domain.analytics.wind_statistics import calculate_monthly_windy_stats

logger = logging.getLogger(__name__)


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
        logger.info(
            f"🌪️ Szél analízis kezdés: {location_name}, küszöb: {threshold_kmh} km/h"
        )

        if weather_data.empty:
            logger.warning("⚠️ Üres weather_data")
            return _create_empty_analysis_result(location_name, threshold_kmh)

        logger.info(
            f"📊 Bemeneti weather_data: {len(weather_data)} sor, oszlopok: {list(weather_data.columns)}"
        )

        daily_wind = extract_daily_wind_data(weather_data)

        if daily_wind.empty:
            logger.warning("⚠️ Nincs feldolgozható szélsebességi adat")
            return _create_empty_analysis_result(location_name, threshold_kmh)

        wind_speeds = daily_wind["max_wind_speed_kmh"].dropna()
        if len(wind_speeds) > 0:
            logger.info(
                "🔧 KAPOTT WIND_SPEED (ResultsPanel konvertálta): "
                f"{wind_speeds.min():.1f} - {wind_speeds.max():.1f} km/h"
            )

        windy_days = identify_windy_days(daily_wind, threshold_kmh)
        monthly_stats = calculate_monthly_windy_stats(windy_days)

        total_windy_days = windy_days["is_windy"].sum() if not windy_days.empty else 0
        total_days = len(windy_days) if not windy_days.empty else 0
        overall_windy_percentage = (
            (total_windy_days / total_days) * 100 if total_days > 0 else 0.0
        )

        windiest_month = (
            max(monthly_stats, key=lambda x: x.windy_days_count)
            if monthly_stats
            else None
        )
        calmest_month = (
            min(monthly_stats, key=lambda x: x.windy_days_count)
            if monthly_stats
            else None
        )

        if not daily_wind.empty:
            start_date = daily_wind["date"].min()
            end_date = daily_wind["date"].max()
            if hasattr(start_date, "date"):
                start_date = start_date.date()
            if hasattr(end_date, "date"):
                end_date = end_date.date()
            analysis_period = (start_date, end_date)
        else:
            today = datetime.date.today()
            analysis_period = (today, today)

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

        return result

    except Exception as e:
        logger.error(f"❌ Hiba a szél analízisben: {e}")
        import traceback

        traceback.print_exc()
        return _create_empty_analysis_result(location_name, threshold_kmh)


def _create_empty_analysis_result(
    location_name: str, threshold_kmh: float
) -> WindAnalysisResult:
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
