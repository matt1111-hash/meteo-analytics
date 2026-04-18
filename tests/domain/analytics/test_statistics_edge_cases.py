"""Tests for statistics helpers — edge cases covering exception branches."""

from __future__ import annotations

from statistics import StatisticsError
from unittest.mock import patch

from src.domain.analytics.statistics import (
    safe_mean,
    safe_median,
    safe_min_max,
    safe_stdev,
)


class TestSafeMeanExceptionBranch:
    """Cover the StatisticsError except branch in safe_mean."""

    @patch("src.domain.analytics.statistics.mean", side_effect=StatisticsError)
    def test_returns_none_on_statistics_error(self, _mock_mean: object) -> None:
        assert safe_mean([1.0, 2.0]) is None


class TestSafeMedianExceptionBranch:
    """Cover the StatisticsError except branch in safe_median."""

    @patch("src.domain.analytics.statistics.median", side_effect=StatisticsError)
    def test_returns_none_on_statistics_error(self, _mock_median: object) -> None:
        assert safe_median([1.0, 2.0]) is None


class TestSafeStdevExceptionBranch:
    """Cover the StatisticsError except branch in safe_stdev."""

    @patch("src.domain.analytics.statistics.stdev", side_effect=StatisticsError)
    def test_returns_zero_on_statistics_error(self, _mock_stdev: object) -> None:
        assert safe_stdev([1.0, 2.0]) == 0.0


class TestSafeMinMaxExceptionBranch:
    """Cover the ValueError/TypeError except branch in safe_min_max."""

    def test_returns_none_tuple_on_exception(self) -> None:
        """safe_min_max returns (None, None) when min/max raises."""
        with patch("src.domain.analytics.statistics.min", side_effect=ValueError):
            result = safe_min_max([1.0])
            assert result == (None, None)
