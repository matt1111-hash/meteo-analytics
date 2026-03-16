#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Provider Widget - Provider Data

📊 Provider adatok és konstansok

Képességek:
- Provider listák
- Status üzenetek
- Mock adat generálás

Fájl: src/presentation/gui/panel_widgets/provider_widget/provider_data.py
"""

from typing import Any, Dict


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


def get_status_messages() -> Dict[str, str]:
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


def generate_mock_usage_data() -> Dict[str, Any]:
    """
    Mock usage adatok generálása teszteléshez.

    Returns:
        Dict[str, Any]: Provider usage stats
    """
    import random

    return {
        "open-meteo": {
            "requests": random.randint(100, 1000),
            "limit": float("inf"),  # Korlátlan
            "estimated_cost": 0.0,  # Ingyenes
        },
        "meteostat": {
            "requests": random.randint(50, 500),
            "limit": 1000,
            "estimated_cost": random.uniform(5.0, 25.0),
        },
        "weatherapi": {
            "requests": random.randint(20, 200),
            "limit": 1000000,
            "estimated_cost": random.uniform(10.0, 50.0),
        },
    }


def get_default_warning_thresholds() -> Dict[str, Any]:
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
