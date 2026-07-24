#!/usr/bin/env python3
"""
Tests for src/domain/analytics/services/trend_statistics.py
Trend statistics calculator for linear regression analysis
"""

import numpy as np
import pandas as pd
import pytest
from src.infrastructure.analytics.trend_statistics import TrendStatisticsCalculator


class TestTrendStatisticsCalculator:
    """Test TrendStatisticsCalculator class."""

    @pytest.fixture
    def calculator(self) -> TrendStatisticsCalculator:
        """Create a TrendStatisticsCalculator instance."""
        return TrendStatisticsCalculator()

    @pytest.fixture
    def monthly_df(self) -> pd.DataFrame:
        """Create a sample monthly DataFrame."""
        # 12 months of data
        dates = pd.date_range("2024-01-01", periods=12, freq="MS")
        # Increasing trend
        values = [10.0 + i * 0.5 for i in range(12)]
        return pd.DataFrame(
            {
                "date": dates,
                "avg_value": values,
            }
        )


class TestCalculateLinearRegression(TestTrendStatisticsCalculator):
    """Test calculate_linear_regression method."""

    def test_returns_dict_with_required_keys(
        self, calculator: TrendStatisticsCalculator, monthly_df: pd.DataFrame
    ) -> None:
        """Should return dict with required keys."""
        result = calculator.calculate_linear_regression(monthly_df)
        assert result is not None
        required_keys = [
            "slope",
            "intercept",
            "r_squared",
            "p_value",
            "std_error",
            "slope_per_decade",
            "confidence_interval",
        ]
        for key in required_keys:
            assert key in result

    def test_calculates_slope(
        self, calculator: TrendStatisticsCalculator, monthly_df: pd.DataFrame
    ) -> None:
        """Should calculate slope."""
        result = calculator.calculate_linear_regression(monthly_df)
        assert result is not None
        # Data has 0.5 increase per month
        assert result["slope"] > 0

    def test_calculates_r_squared(
        self, calculator: TrendStatisticsCalculator, monthly_df: pd.DataFrame
    ) -> None:
        """Should calculate r_squared as r_value**2 (scipy path, no sklearn)."""
        result = calculator.calculate_linear_regression(monthly_df)
        assert result is not None
        # The fixture is perfectly linear (10.0 + i*0.5), so r_squared ~= 1.0.
        # This locks in r_squared == r_value**2 from scipy.stats.linregress.
        assert 0 <= result["r_squared"] <= 1
        assert result["r_squared"] > 0.99

    def test_calculates_p_value(
        self, calculator: TrendStatisticsCalculator, monthly_df: pd.DataFrame
    ) -> None:
        """Should calculate p_value."""
        result = calculator.calculate_linear_regression(monthly_df)
        assert result is not None
        assert 0 <= result["p_value"] <= 1

    def test_calculates_confidence_interval(
        self, calculator: TrendStatisticsCalculator, monthly_df: pd.DataFrame
    ) -> None:
        """Should calculate confidence interval."""
        result = calculator.calculate_linear_regression(monthly_df)
        assert result is not None
        ci = result["confidence_interval"]
        assert isinstance(ci, tuple)
        assert len(ci) == 2
        assert ci[0] <= 0 <= ci[1]  # CI should contain 0 for predictions

    def test_calculates_slope_per_decade(
        self, calculator: TrendStatisticsCalculator, monthly_df: pd.DataFrame
    ) -> None:
        """Should calculate slope per decade."""
        result = calculator.calculate_linear_regression(monthly_df)
        assert result is not None
        # slope_per_decade = slope * 12 months * 10 years
        expected = result["slope"] * 12 * 10
        assert abs(result["slope_per_decade"] - expected) < 0.01

    def test_handles_constant_values(self, calculator: TrendStatisticsCalculator) -> None:
        """Should handle constant values."""
        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=12, freq="MS"),
                "avg_value": [10.0] * 12,  # All same values
            }
        )
        result = calculator.calculate_linear_regression(df)
        assert result is not None
        assert result["slope"] == 0

    def test_handles_negative_trend(self, calculator: TrendStatisticsCalculator) -> None:
        """Should handle negative trend."""
        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=12, freq="MS"),
                "avg_value": [20.0 - i * 0.5 for i in range(12)],  # Decreasing
            }
        )
        result = calculator.calculate_linear_regression(df)
        assert result is not None
        assert result["slope"] < 0


class TestCalculateConfidenceInterval(TestTrendStatisticsCalculator):
    """Test _calculate_confidence_interval method."""

    def test_returns_tuple(self, calculator: TrendStatisticsCalculator) -> None:
        """Should return a tuple."""
        X = np.arange(12).reshape(-1, 1)
        y = np.array([10.0 + i * 0.5 for i in range(12)])
        y_pred = y.copy()

        result = calculator._calculate_confidence_interval(X, y, y_pred)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_lower_less_than_upper(self, calculator: TrendStatisticsCalculator) -> None:
        """Lower bound should be less than upper bound."""
        X = np.arange(12).reshape(-1, 1)
        y = np.array([10.0 + i * 0.5 for i in range(12)])
        y_pred = y.copy()

        result = calculator._calculate_confidence_interval(X, y, y_pred)
        assert result[0] <= result[1]
