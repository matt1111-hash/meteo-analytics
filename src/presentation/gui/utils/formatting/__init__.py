#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Formatting Module - Data formatting and icon generation.
"""

# Value formatting
from .formatters import (
    format_precipitation,
    format_temperature,
    format_wind_speed,
)

# Icons
from .icons import (
    get_weather_icon,
)

# Statistics
from .statistics import (
    calculate_statistics,
    calculate_wind_gusts_statistics,
)

# Wind-specific formatting
from .wind_helpers import (
    format_wind_gusts,
    get_wind_gusts_category,
    get_wind_gusts_color,
    get_wind_gusts_icon,
    is_wind_gusts_catastrophic,
    is_wind_gusts_extreme,
    is_wind_gusts_hurricane,
)

__all__ = [
    # Formatters
    "format_temperature",
    "format_precipitation",
    "format_wind_speed",
    # Wind helpers
    "format_wind_gusts",
    "get_wind_gusts_category",
    "is_wind_gusts_extreme",
    "is_wind_gusts_hurricane",
    "is_wind_gusts_catastrophic",
    "get_wind_gusts_icon",
    "get_wind_gusts_color",
    # Statistics
    "calculate_statistics",
    "calculate_wind_gusts_statistics",
    # Icons
    "get_weather_icon",
]
