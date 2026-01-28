#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Heatmap Chart - Categories

🏷️ Kategorizálási függvények

Képességek:
- Hőmérséklet kategóriák
- Csapadék kategóriák
- Szél kategóriák

Fájl: src/presentation/gui/charts/heatmap_chart/categories.py
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def get_temperature_category(self, temp: float) -> str:
    """
    Temperature categorization.

    Args:
        self: HeatmapCalendarChart instance
        temp: Hőmérséklet érték

    Returns:
        str: Kategória leírás
    """
    if temp >= 35:
        return "🔥 Extrém forró"
    elif temp >= 30:
        return "🌞 Forró"
    elif temp >= 25:
        return "☀️ Meleg"
    elif temp >= 20:
        return "🌤️ Kellemes"
    elif temp >= 15:
        return "🌥️ Hűvös"
    elif temp >= 10:
        return "🌫️ Hideg"
    elif temp >= 0:
        return "❄️ Fagyos"
    else:
        return "🧊 Extrém hideg"


def get_precipitation_category(self, precip: float) -> str:
    """
    Precipitation categorization.

    Args:
        self: HeatmapCalendarChart instance
        precip: Csapadék érték

    Returns:
        str: Kategória leírás
    """
    if precip >= 50:
        return "⛈️ Viharos zápo"
    elif precip >= 20:
        return "🌧️ Erős esőzés"
    elif precip >= 10:
        return "🌦️ Közepes esőzés"
    elif precip >= 2:
        return "🌦️ Gyenge esőzés"
    elif precip >= 0.5:
        return "💧 Szitálás"
    else:
        return "☀️ Száraz időjárás"


def get_wind_category(self, wind: float) -> str:
    """
    Wind speed categorization.

    Args:
        self: HeatmapCalendarChart instance
        wind: Szélsebesség érték

    Returns:
        str: Kategória leírás
    """
    if wind >= 119:
        return "🌪️ Orkán erősségű szél"
    elif wind >= 90:
        return "💨 Viharos szél"
    elif wind >= 61:
        return "🌬️ Erős szél"
    elif wind >= 43:
        return "🍃 Élénk szél"
    elif wind >= 20:
        return "🌿 Mérsékelt szél"
    elif wind >= 10:
        return "🕊️ Gyenge szél"
    else:
        return "🌅 Szélcsend"
