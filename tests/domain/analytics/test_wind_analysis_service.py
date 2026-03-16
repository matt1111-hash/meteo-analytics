#!/usr/bin/env python3
"""
Tests for src/domain/analytics/wind_analysis_service.py
Wind analysis orchestration logic
"""

import datetime

import pandas as pd

from src.domain.analytics.wind_analysis_service import (
    _create_empty_analysis_result,
    analyze_wind_patterns,
)
from src.domain.analytics.wind_models import WINDY_DAY_THRESHOLD_KMH, WindAnalysisResult


class TestAnalyzeWindPatterns:
    """Test analyze_wind_patterns function."""

    def test_returns_empty_result_for_empty_input(self) -> None:
        """Should return empty result for empty DataFrame."""
        df = pd.DataFrame()
        result = analyze_wind_patterns(df)
        assert isinstance(result, WindAnalysisResult)
        assert result.total_days == 0
        assert result.total_windy_days == 0

    def test_uses_default_location_name(self) -> None:
        """Should use default location name."""
        df = pd.DataFrame()
        result = analyze_wind_patterns(df)
        assert result.location_name == "Ismeretlen helyszín"

    def test_accepts_custom_location_name(self) -> None:
        """Should accept custom location name."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-02-01"]),
                "wind_gusts_max": [60.0],
            }
        )
        result = analyze_wind_patterns(df, location_name="Budapest")
        assert result.location_name == "Budapest"

    def test_uses_default_threshold(self) -> None:
        """Should use default threshold."""
        df = pd.DataFrame()
        result = analyze_wind_patterns(df)
        assert result.threshold_kmh == WINDY_DAY_THRESHOLD_KMH

    def test_accepts_custom_threshold(self) -> None:
        """Should accept custom threshold."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-02-01"]),
                "wind_gusts_max": [40.0],
            }
        )
        result = analyze_wind_patterns(df, threshold_kmh=30.0)
        assert result.threshold_kmh == 30.0

    def test_counts_windy_days_correctly(self) -> None:
        """Should count windy days correctly."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-02-01", "2026-02-02", "2026-02-03"]),
                "wind_gusts_max": [30.0, 60.0, 70.0],  # 2 windy days at threshold 50
            }
        )
        result = analyze_wind_patterns(df, threshold_kmh=50.0)
        assert result.total_windy_days == 2

    def test_calculates_total_days(self) -> None:
        """Should calculate total days correctly."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-02-01", "2026-02-02", "2026-02-03"]),
                "wind_gusts_max": [30.0, 40.0, 50.0],
            }
        )
        result = analyze_wind_patterns(df)
        assert result.total_days == 3

    def test_calculates_overall_percentage(self) -> None:
        """Should calculate overall percentage correctly."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    ["2026-02-01", "2026-02-02", "2026-02-03", "2026-02-04"]
                ),
                "wind_gusts_max": [30.0, 60.0, 70.0, 40.0],  # 2/4 = 50%
            }
        )
        result = analyze_wind_patterns(df, threshold_kmh=50.0)
        assert abs(result.overall_windy_percentage - 50.0) < 0.1

    def test_identifies_windiest_month(self) -> None:
        """Should identify windiest month."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    [
                        "2026-01-15",
                        "2026-01-16",  # 2 windy
                        "2026-02-10",  # 1 windy
                    ]
                ),
                "wind_gusts_max": [60.0, 70.0, 60.0],
            }
        )
        result = analyze_wind_patterns(df, threshold_kmh=50.0)
        assert result.windiest_month is not None
        assert result.windiest_month.month == 1

    def test_identifies_calmest_month(self) -> None:
        """Should identify calmest month."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    [
                        "2026-01-15",
                        "2026-01-16",  # 2 windy
                        "2026-02-10",  # 1 windy
                    ]
                ),
                "wind_gusts_max": [60.0, 70.0, 60.0],
            }
        )
        result = analyze_wind_patterns(df, threshold_kmh=50.0)
        assert result.calmest_month is not None
        assert result.calmest_month.month == 2

    def test_sets_analysis_period(self) -> None:
        """Should set analysis period from data."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-01-15", "2026-02-20"]),
                "wind_gusts_max": [60.0, 70.0],
            }
        )
        result = analyze_wind_patterns(df)
        assert result.analysis_period[0] == datetime.date(2026, 1, 15)
        assert result.analysis_period[1] == datetime.date(2026, 2, 20)

    def test_returns_monthly_stats(self) -> None:
        """Should return monthly stats."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-01-15", "2026-02-10"]),
                "wind_gusts_max": [60.0, 70.0],
            }
        )
        result = analyze_wind_patterns(df)
        assert len(result.monthly_stats) >= 2


class TestCreateEmptyAnalysisResult:
    """Test _create_empty_analysis_result function."""

    def test_creates_empty_result(self) -> None:
        """Should create empty result."""
        result = _create_empty_analysis_result("Test Location", 50.0)
        assert isinstance(result, WindAnalysisResult)
        assert result.location_name == "Test Location"
        assert result.threshold_kmh == 50.0
        assert result.total_days == 0
        assert result.total_windy_days == 0
        assert result.overall_windy_percentage == 0.0
        assert result.monthly_stats == []
        assert result.windiest_month is None
        assert result.calmest_month is None

    def test_sets_today_as_analysis_period(self) -> None:
        """Should set today as analysis period."""
        result = _create_empty_analysis_result("Test", 50.0)
        today = datetime.date.today()
        assert result.analysis_period[0] == today
        assert result.analysis_period[1] == today
