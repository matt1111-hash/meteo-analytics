from __future__ import annotations

"""Tests for statistics helpers."""

from math import isclose
from typing import List

import pytest

from src.domain.analytics.statistics import (
    safe_mean,
    safe_median,
    safe_min_max,
    safe_stdev,
)


def test_safe_mean_returns_average_for_numeric_input() -> None:
    """safe_mean returns the arithmetic mean for numeric inputs."""
    values: List[float] = [1.0, 3.0, 5.0]
    assert safe_mean(values) == pytest.approx(3.0)


def test_safe_mean_ignores_none_and_non_numeric() -> None:
    """safe_mean skips None and non-numeric entries."""
    values: List[object] = [None, "x", 2, 4.0]
    assert safe_mean(values) == pytest.approx(3.0)


def test_safe_mean_returns_none_when_no_numeric_input() -> None:
    """safe_mean returns None when no numeric data is present."""
    values: List[object] = ["a", None]
    assert safe_mean(values) is None


def test_safe_median_computes_middle_value() -> None:
    """safe_median returns the median for unsorted numeric input."""
    values: List[int] = [5, 1, 3]
    assert safe_median(values) == 3


def test_safe_median_returns_none_when_empty_after_filtering() -> None:
    """safe_median returns None when only invalid values are provided."""
    assert safe_median([None, "bad"]) is None


def test_safe_stdev_returns_sample_standard_deviation() -> None:
    """safe_stdev returns sample standard deviation for numeric values."""
    values: List[int] = [1, 2, 3]
    assert isclose(safe_stdev(values), 1.0)


def test_safe_stdev_returns_zero_for_single_value() -> None:
    """safe_stdev returns zero when only one numeric value is provided."""
    assert safe_stdev([5]) == 0.0


def test_safe_stdev_returns_zero_when_no_numeric_data() -> None:
    """safe_stdev returns zero when data becomes empty after filtering."""
    assert safe_stdev(["n/a", None]) == 0.0


def test_safe_min_max_returns_bounds_for_valid_numbers() -> None:
    """safe_min_max returns min and max for numeric values."""
    minimum, maximum = safe_min_max([4, 2, 9, 3])
    assert minimum == 2
    assert maximum == 9


def test_safe_min_max_returns_none_tuple_when_no_valid_numbers() -> None:
    """safe_min_max returns (None, None) when filtering removes all entries."""
    assert safe_min_max([None, "x"]) == (None, None)
