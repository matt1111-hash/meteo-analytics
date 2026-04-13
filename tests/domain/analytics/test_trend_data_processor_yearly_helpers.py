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


class TestExtractYears(TestTrendDataProcessor):
    """Test extract_years method."""

    def test_extracts_unique_years(self, processor: TrendDataProcessor) -> None:
        """Should extract unique years."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01", "2025-01-01", "2025-06-01", "2026-01-01"]),
                "avg_value": [10.0, 11.0, 12.0, 13.0],
            }
        )
        result = processor.extract_years(df)
        assert result == [2024, 2025, 2026]

    def test_returns_sorted_years(self, processor: TrendDataProcessor) -> None:
        """Should return sorted years."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-01-01", "2024-01-01", "2025-01-01"]),
                "avg_value": [10.0, 11.0, 12.0],
            }
        )
        result = processor.extract_years(df)
        assert result == [2024, 2025, 2026]


class TestCalculateYearlyMeans(TestTrendDataProcessor):
    """Test calculate_yearly_means method."""

    def test_calculates_yearly_means(self, processor: TrendDataProcessor) -> None:
        """Should calculate yearly means."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01", "2024-06-01", "2025-01-01"]),
                "avg_value": [10.0, 20.0, 15.0],
            }
        )
        result = processor.calculate_yearly_means(df)
        assert len(result) == 2
        assert result[0] == 15.0
        assert result[1] == 15.0


class TestCalculateYearlyDates(TestTrendDataProcessor):
    """Test calculate_yearly_dates method."""

    def test_calculates_yearly_dates(self, processor: TrendDataProcessor) -> None:
        """Should calculate yearly dates."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01", "2024-06-01", "2025-03-15"]),
                "avg_value": [10.0, 20.0, 15.0],
            }
        )
        result = processor.calculate_yearly_dates(df)
        assert len(result) == 2
        assert "2024-01-01" in result
        assert "2025-03-15" in result

    def test_returns_strings(self, processor: TrendDataProcessor) -> None:
        """Should return string dates."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01"]),
                "avg_value": [10.0],
            }
        )
        result = processor.calculate_yearly_dates(df)
        assert all(isinstance(d, str) for d in result)
