"""Wind analysis compatibility wrapper."""

from __future__ import annotations

from src.domain.analytics.wind_models import (
    MONTHS_HU,
    WINDY_DAY_THRESHOLD_KMH,
    WindAnalysisResult,
    WindChartData,
    WindyDayStats,
)
from src.domain.analytics.wind_reporting import (
    format_wind_analysis_summary,
    get_chart_data_for_monthly_windy_days,
)
from src.infrastructure.analytics.wind_analysis_service import analyze_wind_patterns
from src.infrastructure.analytics.wind_extractors import (
    extract_daily_wind_data,
    identify_windy_days,
)
from src.infrastructure.analytics.wind_statistics import calculate_monthly_windy_stats

__all__ = [
    "MONTHS_HU",
    "WINDY_DAY_THRESHOLD_KMH",
    "WindAnalysisResult",
    "WindChartData",
    "WindyDayStats",
    "analyze_wind_patterns",
    "calculate_monthly_windy_stats",
    "extract_daily_wind_data",
    "format_wind_analysis_summary",
    "get_chart_data_for_monthly_windy_days",
    "identify_windy_days",
]
