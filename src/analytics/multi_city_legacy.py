#!/usr/bin/env python3
"""
Multi-City Analytics Engine - Legacy Wrappers
Backward compatibility wrappers for statistics functions
"""

from typing import List, Optional, Tuple

from src.domain.analytics.statistics import (
    safe_mean as _safe_mean,
    safe_median as _safe_median,
    safe_min_max as _safe_min_max,
    safe_stdev as _safe_stdev,
)

Number = float | int
NumberOrNone = Number | None


def safe_mean(values: List[NumberOrNone]) -> Optional[float]:
    """Legacy wrapper → domain safe_mean."""
    return _safe_mean(values)


def safe_statistics_mean(values: List[NumberOrNone]) -> Optional[float]:
    """Legacy wrapper → domain safe_mean."""
    return safe_mean(values)


def safe_median(values: List[NumberOrNone]) -> Optional[float]:
    """Legacy wrapper → domain safe_median."""
    return _safe_median(values)


def safe_statistics_median(values: List[NumberOrNone]) -> Optional[float]:
    """Legacy wrapper → domain safe_median."""
    return safe_median(values)


def safe_stdev(values: List[NumberOrNone]) -> Optional[float]:
    """Legacy wrapper → domain safe_stdev."""
    return _safe_stdev(values)


def safe_statistics_stdev(values: List[NumberOrNone]) -> Optional[float]:
    """Legacy wrapper → domain safe_stdev."""
    return safe_stdev(values)


def safe_min_max(values: List[NumberOrNone]) -> Tuple[Optional[float], Optional[float]]:
    """Legacy wrapper → domain safe_min_max."""
    return _safe_min_max(values)


__all__ = [
    'safe_mean',
    'safe_statistics_mean',
    'safe_median',
    'safe_statistics_median',
    'safe_stdev',
    'safe_statistics_stdev',
    'safe_min_max'
]
