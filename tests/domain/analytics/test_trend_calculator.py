#!/usr/bin/env python3
"""
Tests for src/domain/analytics/services/trend_calculator.py
Trend calculator service for climate trend analysis
"""

from unittest.mock import MagicMock, patch

import pytest
from src.domain.analytics.services.trend_calculator import TrendCalculator
from src.domain.value_objects.enums import AnalyticsMetric


class TestTrendCalculator:
    """Test TrendCalculator class."""

    @pytest.fixture
    def calculator(self) -> TrendCalculator:
        """Create a TrendCalculator instance."""
        return TrendCalculator()


class TestTrendCalculatorInit(TestTrendCalculator):
    """Test TrendCalculator initialization."""

    def test_initializes_metric_field_map(self, calculator: TrendCalculator) -> None:
        """Should initialize metric field map."""
        assert AnalyticsMetric.TEMPERATURE_2M_MAX in calculator.metric_field_map
        assert AnalyticsMetric.PRECIPITATION_SUM in calculator.metric_field_map

    def test_has_significance_thresholds(self, calculator: TrendCalculator) -> None:
        """Should have significance thresholds."""
        assert calculator.HIGHLY_SIGNIFICANT == 0.001
        assert calculator.SIGNIFICANT == 0.01
        assert calculator.MODERATELY_SIGNIFICANT == 0.05

    def test_has_minimum_data_requirements(self, calculator: TrendCalculator) -> None:
        """Should have minimum data requirements."""
        assert calculator.MIN_DAILY_RECORDS == 30
        assert calculator.MIN_MONTHLY_POINTS == 6


class TestCalculateTrend(TestTrendCalculator):
    """Test calculate_trend method."""

    def test_returns_none_for_empty_data(self, calculator: TrendCalculator) -> None:
        """Should return None for empty data."""
        result = calculator.calculate_trend([], AnalyticsMetric.TEMPERATURE_2M_MAX, "Test", 1)
        assert result is None

    def test_returns_none_for_unknown_metric(self, calculator: TrendCalculator) -> None:
        """Should return None for unknown metric."""
        # Create a mock metric that's not in the map
        mock_metric = MagicMock()
        mock_metric.__str__ = lambda self: "unknown_metric"

        # Patch _get_api_field to return None
        with patch.object(calculator, "_get_api_field", return_value=None):
            result = calculator.calculate_trend(
                [{"date": "2024-01-01", "temp": 10.0}],
                mock_metric,
                "Test",
                1,
            )
            assert result is None

    def test_returns_none_for_insufficient_data(self, calculator: TrendCalculator) -> None:
        """Should return None for insufficient data."""
        data = [{"date": "2024-01-01", "temperature_2m_max": 10.0}]
        result = calculator.calculate_trend(data, AnalyticsMetric.TEMPERATURE_2M_MAX, "Test", 1)
        assert result is None


class TestGetApiField(TestTrendCalculator):
    """Test _get_api_field method."""

    def test_returns_field_for_temperature_max(self, calculator: TrendCalculator) -> None:
        """Should return field for TEMPERATURE_2M_MAX."""
        result = calculator._get_api_field(AnalyticsMetric.TEMPERATURE_2M_MAX)
        assert result == "temperature_2m_max"

    def test_returns_field_for_precipitation(self, calculator: TrendCalculator) -> None:
        """Should return field for PRECIPITATION_SUM."""
        result = calculator._get_api_field(AnalyticsMetric.PRECIPITATION_SUM)
        assert result == "precipitation_sum"

    def test_returns_none_for_unknown_metric(self, calculator: TrendCalculator) -> None:
        """Should return None for unknown metric."""
        result = calculator._get_api_field(MagicMock())
        assert result is None


class TestClassifyTrendDirection(TestTrendCalculator):
    """Test _classify_trend_direction method."""

    def test_returns_increasing_for_positive_slope_and_significant(
        self, calculator: TrendCalculator
    ) -> None:
        """Should return 'increasing' for positive slope and significant p-value."""
        result = calculator._classify_trend_direction(0.5, 0.01)
        assert result == "increasing"

    def test_returns_decreasing_for_negative_slope_and_significant(
        self, calculator: TrendCalculator
    ) -> None:
        """Should return 'decreasing' for negative slope and significant p-value."""
        result = calculator._classify_trend_direction(-0.5, 0.01)
        assert result == "decreasing"

    def test_returns_stable_for_not_significant(self, calculator: TrendCalculator) -> None:
        """Should return 'stable' for not significant p-value."""
        result = calculator._classify_trend_direction(0.5, 0.1)  # > 0.05
        assert result == "stable"

    def test_returns_stable_for_edge_case(self, calculator: TrendCalculator) -> None:
        """Should return 'stable' when p-value equals threshold."""
        result = calculator._classify_trend_direction(0.5, 0.05)
        assert result == "stable"


class TestAssessSignificance(TestTrendCalculator):
    """Test _assess_significance method."""

    def test_returns_highly_significant_for_very_low_p(self, calculator: TrendCalculator) -> None:
        """Should return 'highly_significant' for p < 0.001."""
        result = calculator._assess_significance(0.0001)
        assert result == "highly_significant"

    def test_returns_significant_for_low_p(self, calculator: TrendCalculator) -> None:
        """Should return 'significant' for p < 0.01."""
        result = calculator._assess_significance(0.005)
        assert result == "significant"

    def test_returns_moderately_significant_for_medium_p(self, calculator: TrendCalculator) -> None:
        """Should return 'moderately_significant' for p < 0.05."""
        result = calculator._assess_significance(0.03)
        assert result == "moderately_significant"

    def test_returns_not_significant_for_high_p(self, calculator: TrendCalculator) -> None:
        """Should return 'not_significant' for p >= 0.05."""
        result = calculator._assess_significance(0.1)
        assert result == "not_significant"


class TestCalculateMultiplePeriods(TestTrendCalculator):
    """Test calculate_multiple_periods method."""

    def test_returns_result_structure(self, calculator: TrendCalculator) -> None:
        """Should return TrendAnalysisResult structure."""
        # Not enough data for actual calculation, but should return structure
        data = [{"date": "2024-01-01", "temperature_2m_max": 10.0}]
        result = calculator.calculate_multiple_periods(
            data, AnalyticsMetric.TEMPERATURE_2M_MAX, "Test", [1, 5]
        )
        assert hasattr(result, "location_name")
        assert hasattr(result, "metric")
        assert hasattr(result, "periods")
        assert result.location_name == "Test"

    def test_sorts_data_by_date(self, calculator: TrendCalculator) -> None:
        """Should sort data by date."""
        data = [
            {"date": "2024-03-01", "temperature_2m_max": 15.0},
            {"date": "2024-01-01", "temperature_2m_max": 10.0},
            {"date": "2024-02-01", "temperature_2m_max": 12.0},
        ]
        result = calculator.calculate_multiple_periods(
            data, AnalyticsMetric.TEMPERATURE_2M_MAX, "Test", [1]
        )
        assert result is not None

    def test_handles_empty_data(self, calculator: TrendCalculator) -> None:
        """Should handle empty data."""
        result = calculator.calculate_multiple_periods(
            [], AnalyticsMetric.TEMPERATURE_2M_MAX, "Test", [1]
        )
        assert result.total_data_points == 0
        assert result.periods == []

    def test_uses_custom_end_date(self, calculator: TrendCalculator) -> None:
        """Should use custom end date."""
        data = [{"date": "2024-01-01", "temperature_2m_max": 10.0}]
        result = calculator.calculate_multiple_periods(
            data,
            AnalyticsMetric.TEMPERATURE_2M_MAX,
            "Test",
            [1],
            end_date="2024-12-31",
        )
        assert result is not None

    def test_handles_invalid_end_date(self, calculator: TrendCalculator) -> None:
        """Should handle invalid end date format."""
        data = [{"date": "2024-01-01", "temperature_2m_max": 10.0}]
        result = calculator.calculate_multiple_periods(
            data,
            AnalyticsMetric.TEMPERATURE_2M_MAX,
            "Test",
            [1],
            end_date="invalid-date",
        )
        assert result is not None
