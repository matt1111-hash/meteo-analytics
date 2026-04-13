"""None-safe statistical helper functions for multi-city analytics."""

from __future__ import annotations

from statistics import StatisticsError, mean, median, stdev
from typing import Union

Number = Union[float, int]  # noqa: UP007
NumberOrNone = Union[Number, None]  # noqa: UP007


def safe_mean(values: list[NumberOrNone]) -> float | None:
    """Return mean ignoring None and non-numeric entries."""
    clean_values = _filtered(values)
    if not clean_values:
        return None
    try:
        return mean(clean_values)
    except StatisticsError:
        return None


def safe_median(values: list[NumberOrNone]) -> float | None:
    """Return median ignoring None and non-numeric entries."""
    clean_values = _filtered(values)
    if not clean_values:
        return None
    try:
        return median(clean_values)
    except StatisticsError:
        return None


def safe_stdev(values: list[NumberOrNone]) -> float | None:
    """Return stdev ignoring None; returns 0.0 if insufficient data."""
    clean_values = _filtered(values)
    if len(clean_values) < 2:  # noqa: PLR2004
        return 0.0
    try:
        return stdev(clean_values)
    except StatisticsError:
        return 0.0


def safe_min_max(
    values: list[NumberOrNone],
) -> tuple[float | None, float | None]:
    """Return (min, max) ignoring None and non-numeric entries."""
    clean_values = _filtered(values)
    if not clean_values:
        return None, None
    try:
        return min(clean_values), max(clean_values)
    except (ValueError, TypeError):
        return None, None


def _filtered(values: list[NumberOrNone]) -> list[float]:
    return [float(v) for v in values if isinstance(v, int | float)]
