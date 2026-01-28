#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Formatting Module - Icons - Icon generation.
"""

def get_weather_icon(weather_code: int) -> str:
    """Get weather icon for WMO code."""
    weather_icons = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️", 45: "🌫️", 48: "🌫️",
        51: "🌦️", 53: "🌦️", 55: "🌧️", 61: "🌧️", 63: "🌧️", 65: "🌧️",
        71: "🌨️", 73: "🌨️", 75: "❄️", 77: "❄️", 80: "🌦️", 81: "🌧️",
        82: "⛈️", 85: "🌨️", 86: "❄️", 95: "⛈️", 96: "⛈️", 99: "⛈️"
    }
    return weather_icons.get(weather_code, "🌡️")
