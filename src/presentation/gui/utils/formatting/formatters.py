#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Formatting Module - Formatters - Value formatting functions.
"""


def format_temperature(value: float, unit: str = "°C") -> str:
    """Format temperature values."""
    if value is None:
        return "N/A"
    return f"{value:.1f} {unit}"


def format_precipitation(value: float, unit: str = "mm") -> str:
    """Format precipitation values."""
    if value is None or value < 0.1:
        return "0.0 mm"
    return f"{value:.1f} {unit}"


def format_wind_speed(value: float, unit: str = "km/h") -> str:
    """Format wind speed values."""
    if value is None:
        return "N/A"
    return f"{value:.1f} {unit}"
