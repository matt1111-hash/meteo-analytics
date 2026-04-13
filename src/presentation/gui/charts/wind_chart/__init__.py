#!/usr/bin/env python3
# mypy: ignore-errors

"""
Wind Chart - Széllökés grafikon widget.
🌪️ MAGYAR METEOROLÓGIAI SZABVÁNY: 43-61-90-119 km/h küszöbök
"""

# Core class
from .core import WindChart

# Wind categories
from .wind_categories import (
    HUNGARIAN_WIND_THRESHOLDS,
    calculate_y_axis_max,
    get_wind_category,
    get_wind_recommendations,
)

__all__ = [
    "HUNGARIAN_WIND_THRESHOLDS",
    "WindChart",
    "calculate_y_axis_max",
    "get_wind_category",
    "get_wind_recommendations",
]
