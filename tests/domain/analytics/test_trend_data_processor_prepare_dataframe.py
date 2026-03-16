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


class TestPrepareDataframe(TestTrendDataProcessor):
    """Test prepare_dataframe method."""

    def test_returns_none_for_empty_input(self, processor: TrendDataProcessor) -> None:
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

    def test_sorts_by_date(self, processor: TrendDataProcessor) -> None:
        """Should sort data by date."""
        data = [
            {"date": "2026-01-03", "temperature": 15.0},
            {"date": "2026-01-01", "temperature": 10.0},
            {"date": "2026-01-02", "temperature": 12.0},
        ]
        result = processor.prepare_dataframe(data, "temperature")
        assert result is not None
        assert result["date"].iloc[0] < result["date"].iloc[1]

    def test_converts_date_to_datetime(self, processor: TrendDataProcessor) -> None:
        """Should convert date strings to datetime."""
        data = [{"date": "2026-01-01", "temperature": 10.0}]
        result = processor.prepare_dataframe(data, "temperature")
        assert result is not None
        assert pd.api.types.is_datetime64_any_dtype(result["date"])

    def test_converts_value_to_float(self, processor: TrendDataProcessor) -> None:
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
            {"temperature": 12.0},
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
            {"date": "2026-01-02"},
            {"date": "2026-01-03", "temperature": 14.0},
        ]
        result = processor.prepare_dataframe(data, "temperature")
        assert result is not None
        assert len(result) == 2

    def test_drops_na_values(self, processor: TrendDataProcessor) -> None:
        """Should drop NaN values."""
        data = [
            {"date": "2026-01-01", "temperature": 10.0},
            {"date": "2026-01-02", "temperature": float("nan")},
            {"date": "2026-01-03", "temperature": 14.0},
        ]
        result = processor.prepare_dataframe(data, "temperature")
        assert result is not None
        assert len(result) == 2
