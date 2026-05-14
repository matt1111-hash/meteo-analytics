"""Tests for wind_analysis_service — additional coverage for internal helpers."""

from __future__ import annotations

import datetime
from unittest.mock import patch

import pandas as pd
import pytest
from src.domain.analytics.wind_models import WindAnalysisResult, WindyDayStats
from src.infrastructure.analytics.wind_analysis_service import (
    _build_analysis_period,
    _calculate_wind_summary,
    _log_analysis_completion,
    _log_wind_speed_range,
    _resolve_extreme_months,
    analyze_wind_patterns,
)


class TestLogWindSpeedRange:
    """Cover line 36: logging when wind speeds exist."""

    def test_logs_when_data_exists(self) -> None:
        df = pd.DataFrame({"max_wind_speed_kmh": [10.0, 50.0]})
        # Should not raise
        _log_wind_speed_range(df)

    def test_handles_empty_data(self) -> None:
        df = pd.DataFrame({"max_wind_speed_kmh": pd.Series([], dtype=float)})
        # Should not raise
        _log_wind_speed_range(df)


class TestCalculateWindSummary:
    """Cover line 46: empty windy days handling."""

    def test_empty_windy_days_returns_zeros(self) -> None:
        df = pd.DataFrame()
        total, days, pct = _calculate_wind_summary(df)
        assert total == 0
        assert days == 0
        assert pct == 0.0

    def test_with_windy_data(self) -> None:
        df = pd.DataFrame({"is_windy": [True, False, True]})
        total, days, pct = _calculate_wind_summary(df)
        assert total == 2
        assert days == 3
        assert pct == pytest.approx(200.0 / 3)


class TestResolveExtremeMonths:
    """Cover line 59: empty and single-entry edge cases."""

    def test_empty_stats_returns_none_pair(self) -> None:
        windiest, calmest = _resolve_extreme_months([])
        assert windiest is None
        assert calmest is None

    def test_single_entry_returns_same_for_both(self) -> None:
        stat = WindyDayStats(
            year=2024,
            month=1,
            month_name="Jan",
            windy_days_count=5,
            total_days=31,
            max_wind_speed=60.0,
            windy_percentage=16.1,
            avg_wind_speed=30.0,
            windy_days_list=[],
        )
        windiest, calmest = _resolve_extreme_months([stat])
        assert windiest is calmest
        assert windiest.month_name == "Jan"


class TestBuildAnalysisPeriod:
    """Cover lines 70-71, 76, 78: date handling with datetime objects."""

    def test_empty_df_returns_today(self) -> None:
        df = pd.DataFrame()
        start, end = _build_analysis_period(df)
        assert start == datetime.date.today()
        assert end == datetime.date.today()

    def test_datetime_objects_converted_to_date(self) -> None:
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-15", "2024-02-20"]),
            }
        )
        start, end = _build_analysis_period(df)
        assert isinstance(start, datetime.date)
        assert isinstance(end, datetime.date)
        assert start == datetime.date(2024, 1, 15)
        assert end == datetime.date(2024, 2, 20)


class TestLogAnalysisCompletion:
    """Cover lines 95-100: logging with windiest/calmest months."""

    def test_logs_with_both_months(self) -> None:
        windiest = WindyDayStats(
            year=2024,
            month=1,
            month_name="Jan",
            windy_days_count=10,
            total_days=31,
            max_wind_speed=70.0,
            windy_percentage=32.3,
            avg_wind_speed=40.0,
            windy_days_list=[],
        )
        calmest = WindyDayStats(
            year=2024,
            month=6,
            month_name="Jun",
            windy_days_count=2,
            total_days=30,
            max_wind_speed=40.0,
            windy_percentage=6.7,
            avg_wind_speed=20.0,
            windy_days_list=[],
        )
        # Should not raise
        _log_analysis_completion(10, 31, 32.3, windiest, calmest)

    def test_logs_with_none_months(self) -> None:
        _log_analysis_completion(0, 0, 0.0, None, None)


class TestAnalyzeWindPatternsException:
    """Cover lines 168-173: exception handling in main function."""

    def test_exception_returns_empty_result(self) -> None:
        df = pd.DataFrame({"date": ["2024-01-01"]})
        with patch(
            "src.infrastructure.analytics.wind_analysis_service.extract_daily_wind_data",
            side_effect=RuntimeError("test error"),
        ):
            result = analyze_wind_patterns(df)
            assert isinstance(result, WindAnalysisResult)
            assert result.total_days == 0
