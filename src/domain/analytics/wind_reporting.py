"""Wind analysis reporting helpers."""

from __future__ import annotations

import logging

from src.domain.analytics.wind_models import WindAnalysisResult, WindChartData

logger = logging.getLogger(__name__)


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
            return (
                "Nincs elérhető szélsebességi adat a(z) "
                f"{analysis.location_name} helyszínre."
            )

        start_str = analysis.analysis_period[0].strftime("%Y-%m-%d")
        end_str = analysis.analysis_period[1].strftime("%Y-%m-%d")

        summary = f"""
Szél Analízis - {analysis.location_name}
{'=' * 50}

Időszak: {start_str} - {end_str}
Küszöbérték: {analysis.threshold_kmh} km/h

Összegzés:
- Összes nap: {analysis.total_days}
- Szeles napok: {analysis.total_windy_days}
- Szeles napok aránya: {analysis.overall_windy_percentage:.1f}%

Legszélesebb hónap: {analysis.windiest_month.month_name if analysis.windiest_month else 'N/A'} ({analysis.windiest_month.windy_days_count if analysis.windiest_month else 0} nap)
Legcsendesebb hónap: {analysis.calmest_month.month_name if analysis.calmest_month else 'N/A'} ({analysis.calmest_month.windy_days_count if analysis.calmest_month else 0} nap)
"""

        return summary.strip()

    except Exception as e:
        logger.error(f"❌ Hiba az összefoglaló formázásában: {e}")
        return f"Hiba történt az összefoglaló készítésében: {e}"


def get_chart_data_for_monthly_windy_days(analysis: WindAnalysisResult) -> WindChartData:
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

        months = []
        counts = []
        percentages = []
        labels = []

        for stat in sorted_stats:
            unique_years = {s.year for s in sorted_stats}
            if len(unique_years) > 1:
                month_label = f"{stat.year} {stat.month_name}"
            else:
                month_label = stat.month_name

            months.append(month_label)
            counts.append(stat.windy_days_count)
            percentages.append(stat.windy_percentage)

            if stat.windy_days_count > 0:
                label = (
                    f"{month_label}: {stat.windy_days_count} szeles nap "
                    f"({stat.windy_percentage:.1f}%)"
                )
            else:
                label = f"{month_label}: 0 szeles nap"
            labels.append(label)

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
