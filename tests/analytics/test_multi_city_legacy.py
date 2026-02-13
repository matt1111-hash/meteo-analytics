#!/usr/bin/env python3
"""
Tests for src/analytics/multi_city_legacy.py
Legacy wrapper functions for statistics
"""


from src.analytics.multi_city_legacy import (
    safe_mean,
    safe_median,
    safe_min_max,
    safe_statistics_mean,
    safe_statistics_median,
    safe_statistics_stdev,
    safe_stdev,
)


class TestSafeMean:
    """Test safe_mean legacy wrapper."""

    def test_returns_none_for_empty_list(self) -> None:
        """Empty list should return None."""
        result = safe_mean([])
        assert result is None

    def test_returns_mean_for_integers(self) -> None:
        """Should calculate mean of integers."""
        result = safe_mean([1, 2, 3, 4, 5])
        assert result == 3.0

    def test_returns_mean_for_floats(self) -> None:
        """Should calculate mean of floats."""
        result = safe_mean([1.5, 2.5, 3.5])
        assert result == 2.5

    def test_ignores_none_values(self) -> None:
        """None values should be ignored."""
        result = safe_mean([1, None, 3, None, 5])
        assert result == 3.0

    def test_returns_none_when_all_none(self) -> None:
        """All None values should return None."""
        result = safe_mean([None, None, None])
        assert result is None

    def test_handles_single_value(self) -> None:
        """Single value should return that value."""
        result = safe_mean([5])
        assert result == 5.0

    def test_handles_negative_values(self) -> None:
        """Should handle negative values."""
        result = safe_mean([-5, 5])
        assert result == 0.0


class TestSafeStatisticsMean:
    """Test safe_statistics_mean legacy wrapper."""

    def test_delegates_to_safe_mean(self) -> None:
        """Should produce same result as safe_mean."""
        data = [1, 2, 3, 4, 5]
        assert safe_statistics_mean(data) == safe_mean(data)

    def test_returns_none_for_empty(self) -> None:
        """Empty list should return None."""
        assert safe_statistics_mean([]) is None


class TestSafeMedian:
    """Test safe_median legacy wrapper."""

    def test_returns_none_for_empty_list(self) -> None:
        """Empty list should return None."""
        result = safe_median([])
        assert result is None

    def test_returns_median_for_odd_count(self) -> None:
        """Odd number of values should return middle value."""
        result = safe_median([1, 2, 3, 4, 5])
        assert result == 3.0

    def test_returns_median_for_even_count(self) -> None:
        """Even number of values should return average of middle two."""
        result = safe_median([1, 2, 3, 4])
        assert result == 2.5

    def test_ignores_none_values(self) -> None:
        """None values should be ignored."""
        result = safe_median([1, None, 3, None, 5])
        assert result == 3.0

    def test_returns_none_when_all_none(self) -> None:
        """All None values should return None."""
        result = safe_median([None, None, None])
        assert result is None

    def test_handles_single_value(self) -> None:
        """Single value should return that value."""
        result = safe_median([5])
        assert result == 5.0


class TestSafeStatisticsMedian:
    """Test safe_statistics_median legacy wrapper."""

    def test_delegates_to_safe_median(self) -> None:
        """Should produce same result as safe_median."""
        data = [1, 2, 3, 4, 5]
        assert safe_statistics_median(data) == safe_median(data)

    def test_returns_none_for_empty(self) -> None:
        """Empty list should return None."""
        assert safe_statistics_median([]) is None


class TestSafeStdev:
    """Test safe_stdev legacy wrapper."""

    def test_returns_zero_for_empty_list(self) -> None:
        """Empty list should return 0.0 (not None, as per domain implementation)."""
        result = safe_stdev([])
        assert result == 0.0

    def test_returns_zero_for_single_value(self) -> None:
        """Single value should return zero stdev."""
        result = safe_stdev([5])
        assert result == 0.0

    def test_returns_zero_for_two_same_values(self) -> None:
        """Two identical values should return zero stdev."""
        result = safe_stdev([5, 5])
        assert result == 0.0

    def test_calculates_sample_stdev(self) -> None:
        """Should calculate sample standard deviation."""
        result = safe_stdev([2, 4, 4, 4, 5, 5, 7, 9])
        # Sample stdev of this data is approximately 2.138
        assert result is not None
        assert abs(result - 2.138) < 0.01

    def test_ignores_none_values(self) -> None:
        """None values should be ignored."""
        result = safe_stdev([2, None, 4, None, 6])
        # Values: 2, 4, 6 - mean=4, stdev=sqrt((4+0+4)/2)=sqrt(4)=2
        assert result == 2.0

    def test_returns_zero_when_all_none(self) -> None:
        """All None values should return 0.0 (not None, as per domain implementation)."""
        result = safe_stdev([None, None, None])
        assert result == 0.0


class TestSafeStatisticsStdev:
    """Test safe_statistics_stdev legacy wrapper."""

    def test_delegates_to_safe_stdev(self) -> None:
        """Should produce same result as safe_stdev."""
        data = [2, 4, 4, 4, 5, 5, 7, 9]
        assert safe_statistics_stdev(data) == safe_stdev(data)

    def test_returns_zero_for_empty(self) -> None:
        """Empty list should return 0.0 (not None)."""
        assert safe_statistics_stdev([]) == 0.0


class TestSafeMinMax:
    """Test safe_min_max legacy wrapper."""

    def test_returns_none_tuple_for_empty_list(self) -> None:
        """Empty list should return (None, None)."""
        result = safe_min_max([])
        assert result == (None, None)

    def test_returns_min_max_for_integers(self) -> None:
        """Should return (min, max) for integers."""
        result = safe_min_max([3, 1, 4, 1, 5, 9, 2, 6])
        assert result == (1.0, 9.0)

    def test_returns_min_max_for_floats(self) -> None:
        """Should return (min, max) for floats."""
        result = safe_min_max([3.5, 1.2, 4.8, 2.1])
        assert result == (1.2, 4.8)

    def test_ignores_none_values(self) -> None:
        """None values should be ignored."""
        result = safe_min_max([3, None, 1, None, 5])
        assert result == (1.0, 5.0)

    def test_returns_none_tuple_when_all_none(self) -> None:
        """All None values should return (None, None)."""
        result = safe_min_max([None, None, None])
        assert result == (None, None)

    def test_handles_single_value(self) -> None:
        """Single value should return same for min and max."""
        result = safe_min_max([5])
        assert result == (5.0, 5.0)

    def test_handles_negative_values(self) -> None:
        """Should handle negative values correctly."""
        result = safe_min_max([-5, -1, -10, -3])
        assert result == (-10.0, -1.0)

    def test_handles_mixed_positive_negative(self) -> None:
        """Should handle mix of positive and negative."""
        result = safe_min_max([-5, 0, 5])
        assert result == (-5.0, 5.0)


class TestExports:
    """Test module exports via __all__."""

    def test_all_exports_exist(self) -> None:
        """All items in __all__ should be accessible."""
        from src.analytics import multi_city_legacy

        expected_exports = [
            "safe_mean",
            "safe_statistics_mean",
            "safe_median",
            "safe_statistics_median",
            "safe_stdev",
            "safe_statistics_stdev",
            "safe_min_max",
        ]
        for export in expected_exports:
            assert hasattr(multi_city_legacy, export), f"Missing export: {export}"

    def test_all_exports_callable(self) -> None:
        """All exported functions should be callable."""
        from src.analytics import multi_city_legacy

        for name in multi_city_legacy.__all__:
            func = getattr(multi_city_legacy, name)
            assert callable(func), f"{name} is not callable"
