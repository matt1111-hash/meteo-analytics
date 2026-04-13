#!/usr/bin/env python3
# mypy: ignore-errors

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
    # Statistics
    "calculate_statistics",
    "calculate_wind_gusts_statistics",
    "format_precipitation",
    # Formatters
    "format_temperature",
    # Wind helpers
    "format_wind_gusts",
    "format_wind_speed",
    # Icons
    "get_weather_icon",
    "get_wind_gusts_category",
    "get_wind_gusts_color",
    "get_wind_gusts_icon",
    "is_wind_gusts_catastrophic",
    "is_wind_gusts_extreme",
    "is_wind_gusts_hurricane",
]
