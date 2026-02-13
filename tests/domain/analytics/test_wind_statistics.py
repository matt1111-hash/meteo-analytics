#!/usr/bin/env python3
"""
Tests for src/domain/analytics/wind_statistics.py
Wind monthly statistics calculations
"""


import pandas as pd

from src.domain.analytics.wind_models import MONTHS_HU, WindyDayStats
from src.domain.analytics.wind_statistics import calculate_monthly_windy_stats


class TestCalculateMonthlyWindyStats:
    """Test calculate_monthly_windy_stats function."""

    def test_returns_empty_list_for_empty_input(self) -> None:
        """Should return empty list for empty DataFrame."""
        df = pd.DataFrame()
        result = calculate_monthly_windy_stats(df)
        assert result == []

    def test_calculates_stats_for_single_month(self) -> None:
        """Should calculate stats for a single month."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-02-01", "2026-02-02", "2026-02-03"]),
            "is_windy": [True, False, True],
            "max_wind_speed_kmh": [60.0, 30.0, 70.0],
        })
        result = calculate_monthly_windy_stats(df)
        assert len(result) == 1
        assert result[0].year == 2026
        assert result[0].month == 2
        assert result[0].windy_days_count == 2
        assert result[0].total_days == 3
        assert abs(result[0].windy_percentage - 66.67) < 0.1

    def test_calculates_stats_for_multiple_months(self) -> None:
        """Should calculate stats for multiple months."""
        df = pd.DataFrame({
            "date": pd.to_datetime([
                "2026-01-15", "2026-01-20",
                "2026-02-10", "2026-02-15",
            ]),
            "is_windy": [True, False, True, True],
            "max_wind_speed_kmh": [60.0, 30.0, 70.0, 55.0],
        })
        result = calculate_monthly_windy_stats(df)
        assert len(result) == 2

    def test_fills_missing_months_with_zeros(self) -> None:
        """Should fill missing months in the range with zero stats."""
        # Only January and March data
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-01-15", "2026-03-15"]),
            "is_windy": [True, True],
            "max_wind_speed_kmh": [60.0, 70.0],
        })
        result = calculate_monthly_windy_stats(df)
        # Should have January, February, March
        assert len(result) == 3
        months = [stat.month for stat in result]
        assert 1 in months
        assert 2 in months
        assert 3 in months

    def test_uses_hungarian_month_names(self) -> None:
        """Should use Hungarian month names."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-01-15"]),
            "is_windy": [True],
            "max_wind_speed_kmh": [60.0],
        })
        result = calculate_monthly_windy_stats(df)
        assert result[0].month_name == "Január"

    def test_calculates_max_wind_speed(self) -> None:
        """Should calculate max wind speed per month."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-02-01", "2026-02-02"]),
            "is_windy": [True, True],
            "max_wind_speed_kmh": [50.0, 80.0],
        })
        result = calculate_monthly_windy_stats(df)
        assert result[0].max_wind_speed == 80.0

    def test_calculates_avg_wind_speed(self) -> None:
        """Should calculate average wind speed per month."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-02-01", "2026-02-02", "2026-02-03"]),
            "is_windy": [True, True, True],
            "max_wind_speed_kmh": [50.0, 60.0, 70.0],
        })
        result = calculate_monthly_windy_stats(df)
        assert result[0].avg_wind_speed == 60.0

    def test_creates_windy_days_list(self) -> None:
        """Should create list of windy days."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-02-01", "2026-02-02", "2026-02-03"]),
            "is_windy": [True, False, True],
            "max_wind_speed_kmh": [60.0, 30.0, 70.0],
        })
        result = calculate_monthly_windy_stats(df)
        assert len(result[0].windy_days_list) == 2

    def test_sorts_results_by_date(self) -> None:
        """Should sort results by year and month."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-03-01", "2026-01-01", "2026-02-01"]),
            "is_windy": [True, True, True],
            "max_wind_speed_kmh": [50.0, 50.0, 50.0],
        })
        result = calculate_monthly_windy_stats(df)
        assert result[0].month == 1
        assert result[1].month == 2
        assert result[2].month == 3

    def test_converts_string_dates(self) -> None:
        """Should convert string dates to datetime."""
        df = pd.DataFrame({
            "date": ["2026-02-01", "2026-02-02"],
            "is_windy": [True, False],
            "max_wind_speed_kmh": [60.0, 30.0],
        })
        result = calculate_monthly_windy_stats(df)
        assert len(result) == 1

    def test_handles_year_boundary(self) -> None:
        """Should handle data spanning year boundary."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2025-12-15", "2026-01-15"]),
            "is_windy": [True, True],
            "max_wind_speed_kmh": [60.0, 70.0],
        })
        result = calculate_monthly_windy_stats(df)
        assert len(result) == 2
        years = [stat.year for stat in result]
        assert 2025 in years
        assert 2026 in years

    def test_returns_windy_day_stats_objects(self) -> None:
        """Should return list of WindyDayStats objects."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-02-01"]),
            "is_windy": [True],
            "max_wind_speed_kmh": [60.0],
        })
        result = calculate_monthly_windy_stats(df)
        assert all(isinstance(stat, WindyDayStats) for stat in result)

    def test_calculates_windy_percentage_correctly(self) -> None:
        """Should calculate windy percentage correctly."""
        df = pd.DataFrame({
            "date": pd.to_datetime([
                "2026-02-01", "2026-02-02", "2026-02-03", "2026-02-04"
            ]),
            "is_windy": [True, True, True, False],
            "max_wind_speed_kmh": [60.0, 70.0, 80.0, 30.0],
        })
        result = calculate_monthly_windy_stats(df)
        assert abs(result[0].windy_percentage - 75.0) < 0.1

    def test_handles_month_with_no_windy_days(self) -> None:
        """Should handle month with no windy days."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-02-01", "2026-02-02"]),
            "is_windy": [False, False],
            "max_wind_speed_kmh": [20.0, 30.0],
        })
        result = calculate_monthly_windy_stats(df)
        assert result[0].windy_days_count == 0
        assert result[0].windy_percentage == 0.0
        assert result[0].windy_days_list == []

    def test_handles_all_hungarian_months(self) -> None:
        """Should have Hungarian names for all months."""
        df = pd.DataFrame({
            "date": pd.to_datetime([f"2026-{i:02d}-15" for i in range(1, 13)]),
            "is_windy": [True] * 12,
            "max_wind_speed_kmh": [50.0] * 12,
        })
        result = calculate_monthly_windy_stats(df)
        month_names = [stat.month_name for stat in result]
        for i, hungarian_name in enumerate(MONTHS_HU):
            assert hungarian_name in month_names, f"Missing {hungarian_name}"
