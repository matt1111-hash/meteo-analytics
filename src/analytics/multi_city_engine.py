#!/usr/bin/env python3
"""
Multi-City Analytics Engine - Module Entry Point
Re-exports MultiCityEngine and domain types for backward compatibility.
"""

from src.domain.analytics.statistics import (
    safe_mean,
    safe_median,
    safe_min_max,
    safe_stdev,
)
from src.domain.constants.query_types import QUERY_TYPES
from src.domain.constants.regions import HUNGARIAN_REGIONAL_MAPPING, REGIONS

from .multi_city_engine_core import MultiCityEngine

Number = float | int
NumberOrNone = Number | None

safe_statistics_mean = safe_mean
safe_statistics_median = safe_median
safe_statistics_stdev = safe_stdev

__all__ = [
    "HUNGARIAN_REGIONAL_MAPPING",
    "QUERY_TYPES",
    "REGIONS",
    "MultiCityEngine",
    "Number",
    "NumberOrNone",
    "safe_mean",
    "safe_median",
    "safe_min_max",
    "safe_statistics_mean",
    "safe_statistics_median",
    "safe_statistics_stdev",
    "safe_stdev",
]
