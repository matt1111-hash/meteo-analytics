#!/usr/bin/env python3
"""
Tests for src/domain/analytics/services/trend_data_processor.py
Trend data processor for DataFrame preparation and aggregation
"""

import pandas as pd

from tests.domain.analytics.trend_data_processor_support import (
    TestTrendDataProcessor,
    TrendDataProcessor,
)


class TestAggregateMonthly(TestTrendDataProcessor):
    """Test aggregate_monthly method."""

    def test_returns_none_for_insufficient_data(self, processor: TrendDataProcessor) -> None:
        """Should return None for insufficient data."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-01-01"]),
                "value": [10.0],
            }
        )
        result = processor.aggregate_monthly(df)
        assert result is None

    def test_aggregates_to_monthly(self, processor: TrendDataProcessor) -> None:
        """Should aggregate data to monthly level."""
        dates = pd.date_range("2026-01-01", periods=10)
        dates2 = pd.date_range("2026-02-01", periods=10)
        dates3 = pd.date_range("2026-03-01", periods=10)
        dates4 = pd.date_range("2026-04-01", periods=10)
        dates5 = pd.date_range("2026-05-01", periods=10)
        dates6 = pd.date_range("2026-06-01", periods=10)

        all_dates = (
            list(dates) + list(dates2) + list(dates3) + list(dates4) + list(dates5) + list(dates6)
        )
        values = list(range(60))

        df = pd.DataFrame({"date": all_dates, "value": values})
        result = processor.aggregate_monthly(df)
        assert result is not None
        assert len(result) == 6

    def test_creates_required_columns(self, processor: TrendDataProcessor) -> None:
        """Should create required columns."""
        dates = pd.date_range("2026-01-01", periods=10)
        dates2 = pd.date_range("2026-02-01", periods=10)
        dates3 = pd.date_range("2026-03-01", periods=10)
        dates4 = pd.date_range("2026-04-01", periods=10)
        dates5 = pd.date_range("2026-05-01", periods=10)
        dates6 = pd.date_range("2026-06-01", periods=10)

        all_dates = (
            list(dates) + list(dates2) + list(dates3) + list(dates4) + list(dates5) + list(dates6)
        )
        values = list(range(60))

        df = pd.DataFrame({"date": all_dates, "value": values})
        result = processor.aggregate_monthly(df)
        assert result is not None
        required_cols = [
            "year_month",
            "avg_value",
            "min_value",
            "max_value",
            "day_count",
            "date",
        ]
        for col in required_cols:
            assert col in result.columns

    def test_calculates_monthly_avg(self, processor: TrendDataProcessor) -> None:
        """Should calculate monthly average."""
        dates = pd.date_range("2026-01-01", periods=10)
        dates2 = pd.date_range("2026-02-01", periods=10)
        dates3 = pd.date_range("2026-03-01", periods=10)
        dates4 = pd.date_range("2026-04-01", periods=10)
        dates5 = pd.date_range("2026-05-01", periods=10)
        dates6 = pd.date_range("2026-06-01", periods=10)

        all_dates = (
            list(dates) + list(dates2) + list(dates3) + list(dates4) + list(dates5) + list(dates6)
        )
        values = [10.0] * 60

        df = pd.DataFrame({"date": all_dates, "value": values})
        result = processor.aggregate_monthly(df)
        assert result is not None
        assert all(result["avg_value"] == 10.0)

    def test_filters_months_with_insufficient_days(self, processor: TrendDataProcessor) -> None:
        """Should filter months with less than MIN_DAYS_PER_MONTH days."""
        dates = pd.date_range("2026-01-01", periods=10)
        dates2 = pd.date_range("2026-02-01", periods=3)
        dates3 = pd.date_range("2026-03-01", periods=10)
        dates4 = pd.date_range("2026-04-01", periods=10)
        dates5 = pd.date_range("2026-05-01", periods=10)
        dates6 = pd.date_range("2026-06-01", periods=10)
        dates7 = pd.date_range("2026-07-01", periods=10)

        all_dates = (
            list(dates)
            + list(dates2)
            + list(dates3)
            + list(dates4)
            + list(dates5)
            + list(dates6)
            + list(dates7)
        )
        values = list(range(63))

        df = pd.DataFrame({"date": all_dates, "value": values})
        result = processor.aggregate_monthly(df)
        assert result is not None
        assert len(result) == 6
