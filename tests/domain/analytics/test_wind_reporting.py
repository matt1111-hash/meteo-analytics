#!/usr/bin/env python3
"""
Tests for src/domain/analytics/wind_reporting.py
Wind analysis reporting helpers
"""

import datetime

from src.domain.analytics.wind_models import (
    WINDY_DAY_THRESHOLD_KMH,
    WindAnalysisResult,
    WindyDayStats,
)
from src.domain.analytics.wind_reporting import (
    format_wind_analysis_summary,
    get_chart_data_for_monthly_windy_days,
)


def create_test_analysis_result(
    location_name: str = "Test Location",
    total_days: int = 10,
    total_windy_days: int = 3,
    monthly_stats: list | None = None,
    windiest_month: WindyDayStats | None = None,
    calmest_month: WindyDayStats | None = None,
    threshold_kmh: float = WINDY_DAY_THRESHOLD_KMH,
) -> WindAnalysisResult:
    """Helper to create test WindAnalysisResult."""
    return WindAnalysisResult(
        location_name=location_name,
        analysis_period=(datetime.date(2026, 1, 1), datetime.date(2026, 1, 31)),
        threshold_kmh=threshold_kmh,
        monthly_stats=monthly_stats or [],
        total_windy_days=total_windy_days,
        total_days=total_days,
        overall_windy_percentage=(total_windy_days / total_days * 100)
        if total_days > 0
        else 0.0,
        windiest_month=windiest_month,
        calmest_month=calmest_month,
    )


def create_test_monthly_stat(
    year: int = 2026,
    month: int = 1,
    windy_days_count: int = 3,
    total_days: int = 31,
) -> WindyDayStats:
    """Helper to create test WindyDayStats."""
    return WindyDayStats(
        year=year,
        month=month,
        month_name="Január" if month == 1 else "Február",
        windy_days_count=windy_days_count,
        total_days=total_days,
        windy_percentage=(windy_days_count / total_days * 100)
        if total_days > 0
        else 0.0,
        max_wind_speed=80.0,
        avg_wind_speed=50.0,
        windy_days_list=[],
    )


class TestFormatWindAnalysisSummary:
    """Test format_wind_analysis_summary function."""

    def test_returns_message_for_no_data(self) -> None:
        """Should return message when no monthly stats."""
        analysis = create_test_analysis_result(monthly_stats=[])
        result = format_wind_analysis_summary(analysis)
        assert "Nincs elérhető szélsebességi adat" in result

    def test_includes_location_name(self) -> None:
        """Should include location name in summary."""
        monthly = create_test_monthly_stat()
        analysis = create_test_analysis_result(
            location_name="Budapest",
            monthly_stats=[monthly],
        )
        result = format_wind_analysis_summary(analysis)
        assert "Budapest" in result

    def test_includes_total_days(self) -> None:
        """Should include total days in summary."""
        monthly = create_test_monthly_stat()
        analysis = create_test_analysis_result(
            total_days=30,
            monthly_stats=[monthly],
        )
        result = format_wind_analysis_summary(analysis)
        assert "30" in result

    def test_includes_windy_days_count(self) -> None:
        """Should include windy days count."""
        monthly = create_test_monthly_stat()
        analysis = create_test_analysis_result(
            total_windy_days=5,
            monthly_stats=[monthly],
        )
        result = format_wind_analysis_summary(analysis)
        assert "5" in result

    def test_includes_threshold(self) -> None:
        """Should include threshold in summary."""
        monthly = create_test_monthly_stat()
        analysis = create_test_analysis_result(
            monthly_stats=[monthly],
            threshold_kmh=50.0,
        )
        result = format_wind_analysis_summary(analysis)
        assert "50" in result or "43" in result  # Default or custom

    def test_includes_windiest_month(self) -> None:
        """Should include windiest month info."""
        monthly = create_test_monthly_stat()
        analysis = create_test_analysis_result(
            monthly_stats=[monthly],
            windiest_month=monthly,
        )
        result = format_wind_analysis_summary(analysis)
        assert "Legszélesebb" in result or "Január" in result

    def test_includes_calmest_month(self) -> None:
        """Should include calmest month info."""
        monthly = create_test_monthly_stat()
        analysis = create_test_analysis_result(
            monthly_stats=[monthly],
            calmest_month=monthly,
        )
        result = format_wind_analysis_summary(analysis)
        assert "Legcsendesebb" in result or "Január" in result


class TestGetChartDataForMonthlyWindyDays:
    """Test get_chart_data_for_monthly_windy_days function."""

    def test_returns_empty_for_no_stats(self) -> None:
        """Should return empty data when no monthly stats."""
        analysis = create_test_analysis_result(monthly_stats=[])
        result = get_chart_data_for_monthly_windy_days(analysis)
        assert result["months"] == []
        assert result["counts"] == []
        assert result["percentages"] == []
        assert result["labels"] == []

    def test_returns_months_list(self) -> None:
        """Should return months list."""
        monthly = create_test_monthly_stat()
        analysis = create_test_analysis_result(monthly_stats=[monthly])
        result = get_chart_data_for_monthly_windy_days(analysis)
        assert len(result["months"]) == 1
        assert "Január" in result["months"][0]

    def test_returns_counts_list(self) -> None:
        """Should return counts list."""
        monthly = create_test_monthly_stat(windy_days_count=5)
        analysis = create_test_analysis_result(monthly_stats=[monthly])
        result = get_chart_data_for_monthly_windy_days(analysis)
        assert result["counts"] == [5]

    def test_returns_percentages_list(self) -> None:
        """Should return percentages list."""
        monthly = create_test_monthly_stat(windy_days_count=5, total_days=31)
        analysis = create_test_analysis_result(monthly_stats=[monthly])
        result = get_chart_data_for_monthly_windy_days(analysis)
        assert len(result["percentages"]) == 1
        assert abs(result["percentages"][0] - 16.13) < 0.5

    def test_returns_labels_list(self) -> None:
        """Should return labels list."""
        monthly = create_test_monthly_stat(windy_days_count=5)
        analysis = create_test_analysis_result(monthly_stats=[monthly])
        result = get_chart_data_for_monthly_windy_days(analysis)
        assert len(result["labels"]) == 1
        assert "5" in result["labels"][0]

    def test_handles_multiple_months(self) -> None:
        """Should handle multiple months."""
        jan = create_test_monthly_stat(month=1, windy_days_count=5)
        feb = create_test_monthly_stat(month=2, windy_days_count=3)
        analysis = create_test_analysis_result(monthly_stats=[jan, feb])
        result = get_chart_data_for_monthly_windy_days(analysis)
        assert len(result["months"]) == 2
        assert len(result["counts"]) == 2

    def test_sorts_by_year_and_month(self) -> None:
        """Should sort results by year and month."""
        feb = create_test_monthly_stat(month=2)
        jan = create_test_monthly_stat(month=1)
        analysis = create_test_analysis_result(monthly_stats=[feb, jan])
        result = get_chart_data_for_monthly_windy_days(analysis)
        # Should be sorted: Jan first, then Feb
        assert "Január" in result["months"][0]

    def test_includes_year_for_multi_year_data(self) -> None:
        """Should include year for multi-year data."""
        jan_2025 = create_test_monthly_stat(year=2025, month=1)
        jan_2026 = create_test_monthly_stat(year=2026, month=1)
        analysis = create_test_analysis_result(monthly_stats=[jan_2025, jan_2026])
        result = get_chart_data_for_monthly_windy_days(analysis)
        # Should include year in label for multi-year data
        assert any("2025" in m or "2026" in m for m in result["months"])

    def test_handles_zero_windy_days(self) -> None:
        """Should handle months with zero windy days."""
        monthly = create_test_monthly_stat(windy_days_count=0)
        analysis = create_test_analysis_result(monthly_stats=[monthly])
        result = get_chart_data_for_monthly_windy_days(analysis)
        assert result["counts"] == [0]
        assert "0" in result["labels"][0]
