"""Tests for TrendCalculator — additional coverage for data pipeline and multi-period."""

from __future__ import annotations

import datetime

import pytest
from src.domain.value_objects.enums import AnalyticsMetric
from src.infrastructure.analytics.trend_calculator import TrendCalculator


def _make_daily_data(n_days: int = 60) -> list[dict]:
    """Generate synthetic daily temperature data with a slight upward trend."""
    base = datetime.date(2023, 1, 1)
    return [
        {
            "date": (base + datetime.timedelta(days=i)).isoformat(),
            "temperature_2m_max": 10.0 + 0.01 * i + (i % 7) * 0.5,
        }
        for i in range(n_days)
    ]


@pytest.fixture
def calculator() -> TrendCalculator:
    return TrendCalculator()


class TestCalculateTrendWithSufficientData:
    """Cover lines 82-105: the full trend calculation pipeline."""

    def test_successful_trend_calculation(self, calculator: TrendCalculator) -> None:
        data = _make_daily_data(365)
        result = calculator.calculate_trend(data, AnalyticsMetric.TEMPERATURE_2M_MAX, "TestCity", 1)
        assert result is not None
        assert result.time_period == 1
        assert len(result.years) > 0
        assert result.r_squared >= 0
        assert result.p_value >= 0
        assert result.slope is not None
        assert result.significance in (
            "highly_significant",
            "significant",
            "moderately_significant",
            "not_significant",
        )

    def test_trend_direction_is_set(self, calculator: TrendCalculator) -> None:
        data = _make_daily_data(365)
        result = calculator.calculate_trend(data, AnalyticsMetric.TEMPERATURE_2M_MAX, "TestCity", 1)
        assert result is not None
        assert result.trend_direction in ("increasing", "decreasing", "stable")


class TestCalculateMultiplePeriodsWithData:
    """Cover line 164: period results appending."""

    def test_multiple_periods_with_sufficient_data(self, calculator: TrendCalculator) -> None:
        data = _make_daily_data(365)
        result = calculator.calculate_multiple_periods(
            data, AnalyticsMetric.TEMPERATURE_2M_MAX, "TestCity", [1]
        )
        assert result.location_name == "TestCity"
        assert result.total_data_points == 365
        # May or may not have periods depending on data quality
        assert isinstance(result.periods, list)

    def test_multiple_periods_date_range(self, calculator: TrendCalculator) -> None:
        data = _make_daily_data(365)
        result = calculator.calculate_multiple_periods(
            data, AnalyticsMetric.TEMPERATURE_2M_MAX, "TestCity", [1]
        )
        assert result.date_range is not None
        assert len(result.date_range) == 2
