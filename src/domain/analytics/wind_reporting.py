"""Wind analysis reporting helpers."""

from __future__ import annotations

import logging

from src.domain.analytics.wind_models import (
    WindAnalysisResult,
    WindChartData,
    WindyDayStats,
)

logger = logging.getLogger(__name__)


def _build_extreme_month_line(
    label: str,
    month_stat: WindyDayStats | None,
) -> str:
    """Build one extreme-month summary line."""
    if month_stat is None:
        return f"{label}: N/A (0 nap)"
    return f"{label}: {month_stat.month_name} ({month_stat.windy_days_count} nap)"


def _build_summary_body(analysis: WindAnalysisResult) -> str:
    """Build wind analysis summary text."""
    start_str = analysis.analysis_period[0].strftime("%Y-%m-%d")
    end_str = analysis.analysis_period[1].strftime("%Y-%m-%d")
    lines = [
        f"Szél Analízis - {analysis.location_name}",
        "=" * 50,
        "",
        f"Időszak: {start_str} - {end_str}",
        f"Küszöbérték: {analysis.threshold_kmh} km/h",
        "",
        "Összegzés:",
        f"- Összes nap: {analysis.total_days}",
        f"- Szeles napok: {analysis.total_windy_days}",
        f"- Szeles napok aránya: {analysis.overall_windy_percentage:.1f}%",
        "",
        _build_extreme_month_line("Legszélesebb hónap", analysis.windiest_month),
        _build_extreme_month_line("Legcsendesebb hónap", analysis.calmest_month),
    ]
    return "\n".join(lines)


def _build_chart_label(month_label: str, windy_days_count: int, percentage: float) -> str:
    """Build chart label for one month."""
    if windy_days_count <= 0:
        return f"{month_label}: 0 szeles nap"
    return f"{month_label}: {windy_days_count} szeles nap ({percentage:.1f}%)"


def _resolve_month_label(stat: WindyDayStats, has_multiple_years: bool) -> str:
    """Resolve month label with year when needed."""
    return f"{stat.year} {stat.month_name}" if has_multiple_years else stat.month_name


def format_wind_analysis_summary(analysis: WindAnalysisResult) -> str:
    """
    Szél analízis eredmény szöveges összefoglalója.

    Args:
        analysis: WindAnalysisResult objektum

    Returns:
        Formázott szöveges összefoglaló
    """
    try:
        if not analysis.monthly_stats:
            return "Nincs elérhető szélsebességi adat a(z) " f"{analysis.location_name} helyszínre."

        return _build_summary_body(analysis).strip()

    except Exception as e:
        logger.error(f"❌ Hiba az összefoglaló formázásában: {e}")
        return f"Hiba történt az összefoglaló készítésében: {e}"


def get_chart_data_for_monthly_windy_days(
    analysis: WindAnalysisResult,
) -> WindChartData:
    """
    🔥 JAVÍTÁS #2: Chart adatok előkészítése TELJES HÓNAPOS LISTÁVAL.

    VÁLTOZÁS: Most már minden hónap garantált a chart-ban!

    Args:
        analysis: WindAnalysisResult objektum

    Returns:
        Dictionary chart adatokkal (months, counts, percentages) - TELJES LISTA!
    """
    try:
        if not analysis.monthly_stats:
            logger.warning("⚠️ Nincs havi statisztika - üres chart adat")
            return {
                "months": [],
                "counts": [],
                "percentages": [],
                "labels": [],
            }

        sorted_stats = sorted(analysis.monthly_stats, key=lambda x: (x.year, x.month))
        has_multiple_years = len({stat.year for stat in sorted_stats}) > 1
        months = []
        counts = []
        percentages = []
        labels = []

        for stat in sorted_stats:
            month_label = _resolve_month_label(stat, has_multiple_years)
            months.append(month_label)
            counts.append(stat.windy_days_count)
            percentages.append(stat.windy_percentage)
            labels.append(
                _build_chart_label(month_label, stat.windy_days_count, stat.windy_percentage)
            )

        logger.info(f"📊 Chart adatok előkészítve: {len(months)} hónap")
        logger.info(f"📊 Chart hónapok: {months}")
        logger.info(f"📊 Chart értékek: {counts}")

        return {
            "months": months,
            "counts": counts,
            "percentages": percentages,
            "labels": labels,
        }

    except Exception as e:
        logger.error(f"❌ Hiba a chart adatok előkészítésében: {e}")
        import traceback

        traceback.print_exc()
        return {
            "months": [],
            "counts": [],
            "percentages": [],
            "labels": [],
        }
