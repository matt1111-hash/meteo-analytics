#!/usr/bin/env python3
"""
Tests for src/domain/analytics/wind_extractors.py
Wind analysis extractors and classification helpers
"""


import pandas as pd

from src.domain.analytics.wind_extractors import (
    extract_daily_wind_data,
    identify_windy_days,
)
from src.domain.analytics.wind_models import WINDY_DAY_THRESHOLD_KMH


class TestExtractDailyWindData:
    """Test extract_daily_wind_data function."""

    def test_returns_empty_dataframe_for_empty_input(self) -> None:
        """Should return empty DataFrame for empty input."""
        df = pd.DataFrame()
        result = extract_daily_wind_data(df)
        assert result.empty
        assert "date" in result.columns
        assert "max_wind_speed_kmh" in result.columns

    def test_returns_empty_dataframe_when_no_wind_column(self) -> None:
        """Should return empty DataFrame when no wind column exists."""
        df = pd.DataFrame({"date": ["2026-02-01"], "temperature": [10.0]})
        result = extract_daily_wind_data(df)
        assert result.empty

    def test_uses_wind_gusts_max_column(self) -> None:
        """Should prefer wind_gusts_max column when available."""
        df = pd.DataFrame({
            "date": ["2026-02-01", "2026-02-01", "2026-02-02"],
            "wind_gusts_max": [30.0, 50.0, 40.0],
        })
        result = extract_daily_wind_data(df)
        assert len(result) == 2  # Two days
        assert "max_wind_speed_kmh" in result.columns

    def test_uses_wind_speed_column_as_fallback(self) -> None:
        """Should use wind_speed column when wind_gusts_max not available."""
        df = pd.DataFrame({
            "date": ["2026-02-01", "2026-02-01", "2026-02-02"],
            "wind_speed": [20.0, 30.0, 25.0],
        })
        result = extract_daily_wind_data(df)
        assert len(result) == 2

    def test_uses_windspeed_10m_max_column_as_third_option(self) -> None:
        """Should use windspeed_10m_max as third fallback."""
        df = pd.DataFrame({
            "date": ["2026-02-01", "2026-02-02"],
            "windspeed_10m_max": [35.0, 45.0],
        })
        result = extract_daily_wind_data(df)
        assert len(result) == 2

    def test_calculates_daily_max(self) -> None:
        """Should calculate daily maximum wind speed."""
        df = pd.DataFrame({
            "date": ["2026-02-01", "2026-02-01", "2026-02-01"],
            "wind_gusts_max": [30.0, 50.0, 40.0],
        })
        result = extract_daily_wind_data(df)
        assert len(result) == 1  # One day
        assert result["max_wind_speed_kmh"].iloc[0] == 50.0

    def test_handles_date_conversion(self) -> None:
        """Should convert string dates to datetime."""
        df = pd.DataFrame({
            "date": ["2026-02-01", "2026-02-02"],
            "wind_gusts_max": [30.0, 40.0],
        })
        result = extract_daily_wind_data(df)
        assert len(result) == 2

    def test_returns_empty_when_no_date_column(self) -> None:
        """Should return empty DataFrame when no date column."""
        df = pd.DataFrame({
            "wind_gusts_max": [30.0, 40.0],
        })
        result = extract_daily_wind_data(df)
        assert result.empty

    def test_removes_na_values(self) -> None:
        """Should remove NaN values from wind data."""
        df = pd.DataFrame({
            "date": ["2026-02-01", "2026-02-02", "2026-02-03"],
            "wind_gusts_max": [30.0, None, 40.0],
        })
        result = extract_daily_wind_data(df)
        assert len(result) == 2

    def test_removes_negative_values(self) -> None:
        """Should remove negative wind speed values."""
        df = pd.DataFrame({
            "date": ["2026-02-01", "2026-02-02", "2026-02-03"],
            "wind_gusts_max": [30.0, -5.0, 40.0],
        })
        result = extract_daily_wind_data(df)
        assert len(result) == 2

    def test_fills_na_with_zero(self) -> None:
        """Should fill NaN values with 0.0."""
        df = pd.DataFrame({
            "date": ["2026-02-01"],
            "wind_gusts_max": [30.0],
        })
        result = extract_daily_wind_data(df)
        assert not result["max_wind_speed_kmh"].isna().any()


class TestIdentifyWindyDays:
    """Test identify_windy_days function."""

    def test_returns_empty_dataframe_for_empty_input(self) -> None:
        """Should return empty DataFrame for empty input."""
        df = pd.DataFrame()
        result = identify_windy_days(df)
        assert result.empty
        assert "is_windy" in result.columns

    def test_identifies_windy_days_above_threshold(self) -> None:
        """Should mark days above threshold as windy."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-02-01", "2026-02-02", "2026-02-03"]),
            "max_wind_speed_kmh": [30.0, 60.0, 40.0],
        })
        result = identify_windy_days(df, threshold_kmh=50.0)
        assert not result["is_windy"].iloc[0]
        assert result["is_windy"].iloc[1]
        assert not result["is_windy"].iloc[2]

    def test_uses_default_threshold(self) -> None:
        """Should use WINDY_DAY_THRESHOLD_KMH as default."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-02-01"]),
            "max_wind_speed_kmh": [WINDY_DAY_THRESHOLD_KMH + 1],
        })
        result = identify_windy_days(df)
        assert result["is_windy"].iloc[0]

    def test_custom_threshold(self) -> None:
        """Should accept custom threshold."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-02-01", "2026-02-02"]),
            "max_wind_speed_kmh": [30.0, 40.0],
        })
        result = identify_windy_days(df, threshold_kmh=35.0)
        assert not result["is_windy"].iloc[0]
        assert result["is_windy"].iloc[1]

    def test_counts_windy_days_correctly(self) -> None:
        """Should count windy days correctly."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-02-01", "2026-02-02", "2026-02-03"]),
            "max_wind_speed_kmh": [60.0, 70.0, 30.0],
        })
        result = identify_windy_days(df, threshold_kmh=50.0)
        assert result["is_windy"].sum() == 2

    def test_handles_all_windy_days(self) -> None:
        """Should handle case where all days are windy."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-02-01", "2026-02-02"]),
            "max_wind_speed_kmh": [60.0, 70.0],
        })
        result = identify_windy_days(df, threshold_kmh=50.0)
        assert result["is_windy"].all()

    def test_handles_no_windy_days(self) -> None:
        """Should handle case where no days are windy."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-02-01", "2026-02-02"]),
            "max_wind_speed_kmh": [20.0, 30.0],
        })
        result = identify_windy_days(df, threshold_kmh=50.0)
        assert not result["is_windy"].any()

    def test_preserves_original_columns(self) -> None:
        """Should preserve original columns."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-02-01"]),
            "max_wind_speed_kmh": [60.0],
        })
        result = identify_windy_days(df)
        assert "date" in result.columns
        assert "max_wind_speed_kmh" in result.columns

    def test_boundary_case_exactly_at_threshold(self) -> None:
        """Should not mark day as windy when exactly at threshold."""
        df = pd.DataFrame({
            "date": pd.to_datetime(["2026-02-01"]),
            "max_wind_speed_kmh": [50.0],
        })
        result = identify_windy_days(df, threshold_kmh=50.0)
        # > not >=, so 50.0 should NOT be windy
        assert not result["is_windy"].iloc[0]
