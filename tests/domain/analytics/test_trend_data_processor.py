#!/usr/bin/env python3
"""
Tests for src/domain/analytics/services/trend_data_processor.py
Trend data processor for DataFrame preparation and aggregation
"""


import pandas as pd
import pytest

from src.domain.analytics.services.trend_data_processor import TrendDataProcessor


class TestTrendDataProcessor:
    """Test TrendDataProcessor class."""

    @pytest.fixture
    def processor(self) -> TrendDataProcessor:
        """Create a TrendDataProcessor instance."""
        return TrendDataProcessor()


class TestPrepareDataframe(TestTrendDataProcessor):
    """Test prepare_dataframe method."""

    def test_returns_none_for_empty_input(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should return None for empty input."""
        result = processor.prepare_dataframe([], "temperature")
        assert result is None

    def test_returns_none_when_no_valid_records(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should return None when no valid records."""
        data = [
            {"date": None, "temperature": 10.0},
            {"date": "2026-01-01", "temperature": None},
        ]
        result = processor.prepare_dataframe(data, "temperature")
        assert result is None

    def test_creates_dataframe_from_valid_data(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should create DataFrame from valid data."""
        data = [
            {"date": "2026-01-01", "temperature": 10.0},
            {"date": "2026-01-02", "temperature": 12.0},
        ]
        result = processor.prepare_dataframe(data, "temperature")
        assert result is not None
        assert len(result) == 2
        assert "date" in result.columns
        assert "value" in result.columns

    def test_sorts_by_date(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should sort data by date."""
        data = [
            {"date": "2026-01-03", "temperature": 15.0},
            {"date": "2026-01-01", "temperature": 10.0},
            {"date": "2026-01-02", "temperature": 12.0},
        ]
        result = processor.prepare_dataframe(data, "temperature")
        assert result is not None
        assert result["date"].iloc[0] < result["date"].iloc[1]

    def test_converts_date_to_datetime(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should convert date strings to datetime."""
        data = [{"date": "2026-01-01", "temperature": 10.0}]
        result = processor.prepare_dataframe(data, "temperature")
        assert result is not None
        assert pd.api.types.is_datetime64_any_dtype(result["date"])

    def test_converts_value_to_float(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should convert values to float."""
        data = [{"date": "2026-01-01", "temperature": 10}]
        result = processor.prepare_dataframe(data, "temperature")
        assert result is not None
        assert result["value"].dtype in [float, "float64"]

    def test_skips_records_with_missing_date(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should skip records with missing date."""
        data = [
            {"date": "2026-01-01", "temperature": 10.0},
            {"temperature": 12.0},  # Missing date
            {"date": "2026-01-02", "temperature": 14.0},
        ]
        result = processor.prepare_dataframe(data, "temperature")
        assert result is not None
        assert len(result) == 2

    def test_skips_records_with_missing_value(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should skip records with missing value."""
        data = [
            {"date": "2026-01-01", "temperature": 10.0},
            {"date": "2026-01-02"},  # Missing temperature
            {"date": "2026-01-03", "temperature": 14.0},
        ]
        result = processor.prepare_dataframe(data, "temperature")
        assert result is not None
        assert len(result) == 2

    def test_drops_na_values(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should drop NaN values."""
        data = [
            {"date": "2026-01-01", "temperature": 10.0},
            {"date": "2026-01-02", "temperature": float("nan")},
            {"date": "2026-01-03", "temperature": 14.0},
        ]
        result = processor.prepare_dataframe(data, "temperature")
        assert result is not None
        assert len(result) == 2


class TestAggregateMonthly(TestTrendDataProcessor):
    """Test aggregate_monthly method."""

    def test_returns_none_for_insufficient_data(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should return None for insufficient data."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-01-01"]),
            "value": [10.0],
        })
        result = processor.aggregate_monthly(df)
        assert result is None

    def test_aggregates_to_monthly(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should aggregate data to monthly level."""
        # Need at least 6 months with 5+ days each
        dates = pd.date_range("2026-01-01", periods=10)
        dates2 = pd.date_range("2026-02-01", periods=10)
        dates3 = pd.date_range("2026-03-01", periods=10)
        dates4 = pd.date_range("2026-04-01", periods=10)
        dates5 = pd.date_range("2026-05-01", periods=10)
        dates6 = pd.date_range("2026-06-01", periods=10)

        all_dates = list(dates) + list(dates2) + list(dates3) + list(dates4) + list(dates5) + list(dates6)
        values = list(range(60))

        df = pd.DataFrame({
            "date": all_dates,
            "value": values,
        })
        result = processor.aggregate_monthly(df)
        assert result is not None
        assert len(result) == 6

    def test_creates_required_columns(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should create required columns."""
        dates = pd.date_range("2026-01-01", periods=10)
        dates2 = pd.date_range("2026-02-01", periods=10)
        dates3 = pd.date_range("2026-03-01", periods=10)
        dates4 = pd.date_range("2026-04-01", periods=10)
        dates5 = pd.date_range("2026-05-01", periods=10)
        dates6 = pd.date_range("2026-06-01", periods=10)

        all_dates = list(dates) + list(dates2) + list(dates3) + list(dates4) + list(dates5) + list(dates6)
        values = list(range(60))

        df = pd.DataFrame({"date": all_dates, "value": values})
        result = processor.aggregate_monthly(df)
        assert result is not None
        required_cols = ["year_month", "avg_value", "min_value", "max_value", "day_count", "date"]
        for col in required_cols:
            assert col in result.columns

    def test_calculates_monthly_avg(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should calculate monthly average."""
        dates = pd.date_range("2026-01-01", periods=10)
        dates2 = pd.date_range("2026-02-01", periods=10)
        dates3 = pd.date_range("2026-03-01", periods=10)
        dates4 = pd.date_range("2026-04-01", periods=10)
        dates5 = pd.date_range("2026-05-01", periods=10)
        dates6 = pd.date_range("2026-06-01", periods=10)

        all_dates = list(dates) + list(dates2) + list(dates3) + list(dates4) + list(dates5) + list(dates6)
        # All values are 10, so avg should be 10
        values = [10.0] * 60

        df = pd.DataFrame({"date": all_dates, "value": values})
        result = processor.aggregate_monthly(df)
        assert result is not None
        assert all(result["avg_value"] == 10.0)

    def test_filters_months_with_insufficient_days(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should filter months with less than MIN_DAYS_PER_MONTH days."""
        # 6 months with varying days
        dates = pd.date_range("2026-01-01", periods=10)  # 10 days
        dates2 = pd.date_range("2026-02-01", periods=3)   # 3 days (should be filtered)
        dates3 = pd.date_range("2026-03-01", periods=10)  # 10 days
        dates4 = pd.date_range("2026-04-01", periods=10)  # 10 days
        dates5 = pd.date_range("2026-05-01", periods=10)  # 10 days
        dates6 = pd.date_range("2026-06-01", periods=10)  # 10 days
        dates7 = pd.date_range("2026-07-01", periods=10)  # 10 days

        all_dates = list(dates) + list(dates2) + list(dates3) + list(dates4) + list(dates5) + list(dates6) + list(dates7)
        values = list(range(63))

        df = pd.DataFrame({"date": all_dates, "value": values})
        result = processor.aggregate_monthly(df)
        assert result is not None
        # February should be filtered out (3 days < 5)
        assert len(result) == 6  # 7 months - 1 filtered


class TestExtractYears(TestTrendDataProcessor):
    """Test extract_years method."""

    def test_extracts_unique_years(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should extract unique years."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01", "2025-01-01", "2025-06-01", "2026-01-01"]),
            "avg_value": [10.0, 11.0, 12.0, 13.0],
        })
        result = processor.extract_years(df)
        assert result == [2024, 2025, 2026]

    def test_returns_sorted_years(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should return sorted years."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-01-01", "2024-01-01", "2025-01-01"]),
            "avg_value": [10.0, 11.0, 12.0],
        })
        result = processor.extract_years(df)
        assert result == [2024, 2025, 2026]


class TestCalculateYearlyMeans(TestTrendDataProcessor):
    """Test calculate_yearly_means method."""

    def test_calculates_yearly_means(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should calculate yearly means."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01", "2024-06-01", "2025-01-01"]),
            "avg_value": [10.0, 20.0, 15.0],
        })
        result = processor.calculate_yearly_means(df)
        assert len(result) == 2
        assert result[0] == 15.0  # Mean of 10 and 20
        assert result[1] == 15.0


class TestCalculateYearlyDates(TestTrendDataProcessor):
    """Test calculate_yearly_dates method."""

    def test_calculates_yearly_dates(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should calculate yearly dates."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01", "2024-06-01", "2025-03-15"]),
            "avg_value": [10.0, 20.0, 15.0],
        })
        result = processor.calculate_yearly_dates(df)
        assert len(result) == 2
        assert "2024-01-01" in result
        assert "2025-03-15" in result

    def test_returns_strings(
        self, processor: TrendDataProcessor
    ) -> None:
        """Should return string dates."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01"]),
            "avg_value": [10.0],
        })
        result = processor.calculate_yearly_dates(df)
        assert all(isinstance(d, str) for d in result)
