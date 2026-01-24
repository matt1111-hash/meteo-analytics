"""None-safe statistical helper functions for multi-city analytics."""
from __future__ import annotations

from statistics import mean, median, stdev, StatisticsError
from typing import List, Optional, Tuple, Union

Number = Union[float, int]
NumberOrNone = Union[Number, None]


def safe_mean(values: List[NumberOrNone]) -> Optional[float]:
    """Return mean ignoring None and non-numeric entries."""
    clean_values = _filtered(values)
    if not clean_values:
        return None
    try:
        return mean(clean_values)
    except StatisticsError:
        return None


def safe_median(values: List[NumberOrNone]) -> Optional[float]:
    """Return median ignoring None and non-numeric entries."""
    clean_values = _filtered(values)
    if not clean_values:
        return None
    try:
        return median(clean_values)
    except StatisticsError:
        return None


def safe_stdev(values: List[NumberOrNone]) -> Optional[float]:
    """Return stdev ignoring None; returns 0.0 if insufficient data."""
    clean_values = _filtered(values)
    if len(clean_values) < 2:
        return 0.0
    try:
        return stdev(clean_values)
    except StatisticsError:
        return 0.0


def safe_min_max(
    values: List[NumberOrNone],
) -> Tuple[Optional[float], Optional[float]]:
    """Return (min, max) ignoring None and non-numeric entries."""
    clean_values = _filtered(values)
    if not clean_values:
        return None, None
    try:
        return min(clean_values), max(clean_values)
    except (ValueError, TypeError):
        return None, None


def _filtered(values: List[NumberOrNone]) -> List[float]:
    return [float(v) for v in values if isinstance(v, (int, float))]
