#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Formatting Module - Statistics - Statistical calculations.
"""

import logging
from typing import Any, Dict, List

import statistics

from src.presentation.gui.utils.constants import AnomalyConstants

logger = logging.getLogger(__name__)


def calculate_statistics(data: List[float]) -> Dict[str, float]:
    """Calculate basic statistics."""
    if not data:
        return {}

    clean_data = [x for x in data if x is not None]

    if not clean_data:
        return {}

    try:
        return {
            "count": len(clean_data),
            "min": min(clean_data),
            "max": max(clean_data),
            "mean": statistics.mean(clean_data),
            "median": statistics.median(clean_data),
            "std_dev": statistics.stdev(clean_data) if len(clean_data) > 1 else 0,
            "sum": sum(clean_data)
        }
    except Exception as e:
        logger.error(f"Statisztikai számítás hiba: {e}")
        return {}


def calculate_wind_gusts_statistics(data: List[float]) -> Dict[str, Any]:
    """Calculate wind gusts specific statistics."""
    if not data:
        return {}

    clean_data = [x for x in data if x is not None and x >= 0]

    if not clean_data:
        return {}

    try:
        basic_stats = calculate_statistics(clean_data)

        extreme_days = len([x for x in clean_data if x >= AnomalyConstants.WIND_GUSTS_EXTREME])
        hurricane_days = len([x for x in clean_data if x >= AnomalyConstants.WIND_GUSTS_HURRICANE])
        catastrophic_days = len([x for x in clean_data if x >= AnomalyConstants.WIND_GUSTS_CATASTROPHIC])

        category_distribution = {}
        for category_name, category_data in AnomalyConstants.WIND_GUSTS_CATEGORIES.items():
            count = len([x for x in clean_data if category_data["threshold"] <= x < category_data["max"]])
            category_distribution[category_name] = count

        basic_stats.update({
            "extreme_days": extreme_days,
            "hurricane_days": hurricane_days,
            "catastrophic_days": catastrophic_days,
            "category_distribution": category_distribution,
            "max_category": get_wind_gusts_category(max(clean_data)) if clean_data else None
        })

        return basic_stats

    except Exception as e:
        logger.error(f"Széllökés statisztikai számítás hiba: {e}")
        return {}
