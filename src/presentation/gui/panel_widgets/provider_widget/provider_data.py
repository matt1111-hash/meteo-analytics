#!/usr/bin/env python3
# mypy: ignore-errors

"""
Provider Widget - Provider Data

📊 Provider adatok és konstansok

Képességek:
- Provider listák
- Status üzenetek

Fájl: src/presentation/gui/panel_widgets/provider_widget/provider_data.py
"""

from typing import Any


def get_providers_list() -> list:
    """
    Provider lista lekérdezése.

    Returns:
        list: Provider tuple lista (value, display)
    """
    return [
        ("open-meteo", "🌍 Open-Meteo (Ingyenes) ⭐ AJÁNLOTT"),
        ("meteostat", "💎 Meteostat (Premium)"),
        ("weatherapi", "🌤️ WeatherAPI (Premium)"),
        ("openweather", "☁️ OpenWeatherMap (Premium)"),
        ("auto", "🤖 Automatikus (Smart Routing)"),
    ]


def get_status_messages() -> dict[str, str]:
    """
    Status üzenetek lekérdezése.

    Returns:
        Dict[str, str]: Provider status üzenetek
    """
    return {
        "open-meteo": "🌍 Open-Meteo aktív - Ingyenes, korlátlan használat ⭐ AJÁNLOTT",
        "meteostat": "💎 Meteostat aktív - Premium API, pay-per-use",
        "weatherapi": "🌤️ WeatherAPI aktív - Premium API, monthly limits",
        "openweather": "☁️ OpenWeatherMap aktív - Premium API, call limits",
        "auto": "🤖 Automatikus routing aktív - Smart provider selection",
    }


def get_default_warning_thresholds() -> dict[str, Any]:
    """
    Alapértelmezett warning thresholdök.

    Returns:
        Dict[str, Any]: Warning thresholdök
    """
    return {
        "usage_warning": 80,  # 80% usage warning
        "usage_critical": 95,  # 95% usage critical
        "cost_warning": 50.0,  # $50/month warning
    }
