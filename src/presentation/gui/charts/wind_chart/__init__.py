#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wind Chart - Széllökés grafikon widget.
🌪️ MAGYAR METEOROLÓGIAI SZABVÁNY: 43-61-90-119 km/h küszöbök
"""

# Core class
from .core import WindChart

# Wind categories
from .wind_categories import (
    HUNGARIAN_WIND_THRESHOLDS,
    get_wind_category,
    get_wind_recommendations,
    calculate_y_axis_max,
)

__all__ = [
    "WindChart",
    "HUNGARIAN_WIND_THRESHOLDS",
    "get_wind_category",
    "get_wind_recommendations",
    "calculate_y_axis_max",
]
