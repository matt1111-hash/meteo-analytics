#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - GUI Formatting Module.
Adatformázó és ikon generáló függvények.

🎨 FORMATTING FUNCTIONS:
✅ Hőmérséklet, csapadék, szél formázás
✅ Széllökés specifikus formázás kategóriával
✅ Időjárás ikonok generálása
✅ Széllökés ikonok és színek

🌪️ WIND GUSTS SUPPORT:
✅ Széllökés kategória meghatározás
✅ Ikgenerálás széllökés értékhez
✅ Színkód lekérdezés kategória alapján
"""

import logging
from typing import Any, Dict, List, Optional

from .constants import AnomalyConstants

logger = logging.getLogger(__name__)


def format_temperature(value: float, unit: str = "°C") -> str:
    """
    Hőmérséklet értékek formázása.

    Args:
        value: Hőmérséklet érték
        unit: Mértékegység

    Returns:
        Formázott string
    """
    if value is None:
        return "N/A"
    return f"{value:.1f} {unit}"


def format_precipitation(value: float, unit: str = "mm") -> str:
    """
    Csapadék értékek formázása.

    Args:
        value: Csapadék érték
        unit: Mértékegység

    Returns:
        Formázott string
    """
    if value is None or value < 0.1:
        return "0.0 mm"
    return f"{value:.1f} {unit}"


def format_wind_speed(value: float, unit: str = "km/h") -> str:
    """
    Szélsebesség értékek formázása.

    Args:
        value: Szélsebesség érték
        unit: Mértékegység

    Returns:
        Formázott string
    """
    if value is None:
        return "N/A"
    return f"{value:.1f} {unit}"


def format_wind_gusts(value: float, unit: str = "km/h", include_category: bool = False) -> str:
    """
    🌪️ KRITIKUS JAVÍTÁS: Széllökés értékek formázása kategóriával.

    Args:
        value: Széllökés érték
        unit: Mértékegység
        include_category: Kategória megjelenítése

    Returns:
        Formázott string
    """
    if value is None:
        return "N/A"

    formatted = f"{value:.1f} {unit}"

    if include_category:
        category = get_wind_gusts_category(value)
        if category:
            formatted += f" ({category['emoji']} {category['label']})"

    return formatted


def get_wind_gusts_category(value: float) -> Optional[Dict[str, Any]]:
    """
    🌪️ KRITIKUS JAVÍTÁS: Széllökés kategória meghatározása.

    Args:
        value: Széllökés érték km/h-ban

    Returns:
        Kategória dictionary vagy None
    """
    if value is None:
        return None

    for category_name, category_data in AnomalyConstants.WIND_GUSTS_CATEGORIES.items():
        if category_data["threshold"] <= value < category_data["max"]:
            return category_data

    # Ha minden kategórián felül van, akkor katasztrofális
    return AnomalyConstants.WIND_GUSTS_CATEGORIES["CATASTROPHIC"]


def is_wind_gusts_extreme(value: float) -> bool:
    """
    🌪️ KRITIKUS JAVÍTÁS: Extrém széllökés ellenőrzése.

    Args:
        value: Széllökés érték km/h-ban

    Returns:
        Extrém széllökés-e
    """
    if value is None:
        return False

    return value >= AnomalyConstants.WIND_GUSTS_EXTREME


def is_wind_gusts_hurricane(value: float) -> bool:
    """
    🌪️ KRITIKUS JAVÍTÁS: Hurrikán erősségű széllökés ellenőrzése.

    Args:
        value: Széllökés érték km/h-ban

    Returns:
        Hurrikán erősségű-e
    """
    if value is None:
        return False

    return value >= AnomalyConstants.WIND_GUSTS_HURRICANE


def is_wind_gusts_catastrophic(value: float) -> bool:
    """
    🌪️ KRITIKUS JAVÍTÁS: Katasztrofális széllökés ellenőrzése.

    Args:
        value: Széllökés érték km/h-ban

    Returns:
        Katasztrofális szintű-e
    """
    if value is None:
        return False

    return value >= AnomalyConstants.WIND_GUSTS_CATASTROPHIC


def get_weather_icon(weather_code: int) -> str:
    """
    Időjárási kód alapján emoji ikon visszaadása.

    Args:
        weather_code: WMO időjárási kód

    Returns:
        Emoji string
    """
    weather_icons = {
        0: "☀️",    # Clear sky
        1: "🌤️",   # Mainly clear
        2: "⛅",    # Partly cloudy
        3: "☁️",    # Overcast
        45: "🌫️",  # Fog
        48: "🌫️",  # Depositing rime fog
        51: "🌦️",  # Light drizzle
        53: "🌦️",  # Moderate drizzle
        55: "🌧️",  # Dense drizzle
        61: "🌧️",  # Slight rain
        63: "🌧️",  # Moderate rain
        65: "🌧️",  # Heavy rain
        71: "🌨️",  # Slight snow
        73: "🌨️",  # Moderate snow
        75: "❄️",   # Heavy snow
        77: "❄️",   # Snow grains
        80: "🌦️",  # Slight rain showers
        81: "🌧️",  # Moderate rain showers
        82: "⛈️",   # Violent rain showers
        85: "🌨️",  # Slight snow showers
        86: "❄️",   # Heavy snow showers
        95: "⛈️",   # Thunderstorm
        96: "⛈️",   # Thunderstorm with hail
        99: "⛈️"    # Heavy thunderstorm with hail
    }

    return weather_icons.get(weather_code, "🌡️")


def get_wind_gusts_icon(value: float) -> str:
    """
    🌪️ KRITIKUS JAVÍTÁS: Széllökés érték alapján emoji ikon.

    Args:
        value: Széllökés érték km/h-ban

    Returns:
        Emoji string
    """
    if value is None:
        return "❓"

    category = get_wind_gusts_category(value)
    if category:
        return category["emoji"]

    return "💨"  # Default szél emoji


def get_wind_gusts_color(value: float) -> str:
    """
    🌪️ KRITIKUS JAVÍTÁS: Széllökés érték alapján szín visszaadása.

    Args:
        value: Széllökés érték km/h-ban

    Returns:
        Hex színkód
    """
    if value is None:
        return AnomalyConstants.WIND_GUSTS_COLORS["normal"]

    category = get_wind_gusts_category(value)
    if category:
        return category["color"]

    return AnomalyConstants.WIND_GUSTS_COLORS["normal"]


def calculate_statistics(data: List[float]) -> Dict[str, float]:
    """
    Alapvető statisztikák számítása.

    Args:
        data: Számértékek listája

    Returns:
        Statisztikák dictionary-je
    """
    if not data:
        return {}

    import statistics

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
    """
    🌪️ KRITIKUS JAVÍTÁS: Széllökés specifikus statisztikák számítása.

    Args:
        data: Széllökés értékek listája

    Returns:
        Bővített statisztikák dictionary-je
    """
    if not data:
        return {}

    clean_data = [x for x in data if x is not None and x >= 0]

    if not clean_data:
        return {}

    try:
        basic_stats = calculate_statistics(clean_data)

        # Széllökés specifikus statisztikák
        extreme_days = len([x for x in clean_data if x >= AnomalyConstants.WIND_GUSTS_EXTREME])
        hurricane_days = len([x for x in clean_data if x >= AnomalyConstants.WIND_GUSTS_HURRICANE])
        catastrophic_days = len([x for x in clean_data if x >= AnomalyConstants.WIND_GUSTS_CATASTROPHIC])

        # Kategóriák szerinti eloszlás
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


__all__ = [
    "format_temperature",
    "format_precipitation",
    "format_wind_speed",
    "format_wind_gusts",
    "get_wind_gusts_category",
    "is_wind_gusts_extreme",
    "is_wind_gusts_hurricane",
    "is_wind_gusts_catastrophic",
    "get_weather_icon",
    "get_wind_gusts_icon",
    "get_wind_gusts_color",
    "calculate_statistics",
    "calculate_wind_gusts_statistics",
]
