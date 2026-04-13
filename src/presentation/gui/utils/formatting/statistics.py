#!/usr/bin/env python3
# mypy: ignore-errors

"""
Formatting Module - Statistics - Statistical calculations.
"""

import logging
import statistics
from typing import Any, cast

from src.presentation.gui.utils.constants import AnomalyConstants
from src.presentation.gui.utils.formatting.wind_helpers import get_wind_gusts_category

logger = logging.getLogger(__name__)


def _clean_numeric_data(data: list[float]) -> list[float]:
    """Return cleaned numeric values."""
    return [value for value in data if value is not None]


def _clean_non_negative_numeric_data(data: list[float]) -> list[float]:
    """Return cleaned non-negative numeric values."""
    return [value for value in data if isinstance(value, int | float) and value >= 0]


def _calculate_std_dev(clean_data: list[float]) -> float:
    """Calculate standard deviation safely."""
    return statistics.stdev(clean_data) if len(clean_data) > 1 else 0


def _count_values_at_or_above(clean_data: list[float], threshold: float) -> int:
    """Count values meeting or exceeding a threshold."""
    return len([value for value in clean_data if value >= threshold])


def calculate_statistics(data: list[float]) -> dict[str, float]:
    """Calculate basic statistics."""
    if not data:
        return {}

    clean_data = _clean_numeric_data(data)

    if not clean_data:
        return {}

    try:
        return {
            "count": len(clean_data),
            "min": min(clean_data),
            "max": max(clean_data),
            "mean": statistics.mean(clean_data),
            "median": statistics.median(clean_data),
            "std_dev": _calculate_std_dev(clean_data),
            "sum": sum(clean_data),
        }
    except Exception as e:
        logger.error(f"Statisztikai számítás hiba: {e}")
        return {}


def calculate_wind_gusts_statistics(data: list[float]) -> dict[str, Any]:
    """Calculate wind gusts specific statistics."""
    if not data:
        return {}

    clean_data = _clean_non_negative_numeric_data(data)

    if not clean_data:
        return {}

    try:
        basic_stats = calculate_statistics(clean_data)
        basic_stats.update(
            {
                **_build_wind_gusts_counters(clean_data),
                "category_distribution": _build_category_distribution(clean_data),
                "max_category": get_wind_gusts_category(max(clean_data)),
            }
        )
        return basic_stats

    except Exception as e:
        logger.error(f"Széllökés statisztikai számítás hiba: {e}")
        return {}


def _build_wind_gusts_counters(clean_data: list[float]) -> dict[str, int]:
    """Build severity counters for wind gust values."""
    return {
        "extreme_days": _count_values_at_or_above(clean_data, AnomalyConstants.WIND_GUSTS_EXTREME),
        "hurricane_days": _count_values_at_or_above(
            clean_data, AnomalyConstants.WIND_GUSTS_HURRICANE
        ),
        "catastrophic_days": _count_values_at_or_above(
            clean_data, AnomalyConstants.WIND_GUSTS_CATASTROPHIC
        ),
    }


def _build_category_distribution(clean_data: list[float]) -> dict[str, int]:
    """Build category histogram for wind gust values."""
    category_distribution: dict[str, int] = {}
    for category_name, category_data in AnomalyConstants.WIND_GUSTS_CATEGORIES.items():
        threshold = cast(float, category_data["threshold"])
        maximum = cast(float, category_data["max"])
        category_distribution[category_name] = len(
            [value for value in clean_data if threshold <= value < maximum]
        )
    return category_distribution
