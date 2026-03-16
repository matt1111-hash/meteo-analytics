#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

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


def _resolve_category(
    value: float, categories: list[tuple[float, str]], fallback: str
) -> str:
    """Resolve the first matching category for a numeric value."""
    for threshold, label in categories:
        if value >= threshold:
            return label
    return fallback


def get_temperature_category(self, temp: float) -> str:
    """
    Temperature categorization.

    Args:
        self: HeatmapCalendarChart instance
        temp: Hőmérséklet érték

    Returns:
        str: Kategória leírás
    """
    return _resolve_category(
        temp,
        [
            (35, "🔥 Extrém forró"),
            (30, "🌞 Forró"),
            (25, "☀️ Meleg"),
            (20, "🌤️ Kellemes"),
            (15, "🌥️ Hűvös"),
            (10, "🌫️ Hideg"),
            (0, "❄️ Fagyos"),
        ],
        "🧊 Extrém hideg",
    )


def get_precipitation_category(self, precip: float) -> str:
    """
    Precipitation categorization.

    Args:
        self: HeatmapCalendarChart instance
        precip: Csapadék érték

    Returns:
        str: Kategória leírás
    """
    return _resolve_category(
        precip,
        [
            (50, "⛈️ Viharos zápo"),
            (20, "🌧️ Erős esőzés"),
            (10, "🌦️ Közepes esőzés"),
            (2, "🌦️ Gyenge esőzés"),
            (0.5, "💧 Szitálás"),
        ],
        "☀️ Száraz időjárás",
    )


def get_wind_category(self, wind: float) -> str:
    """
    Wind speed categorization.

    Args:
        self: HeatmapCalendarChart instance
        wind: Szélsebesség érték

    Returns:
        str: Kategória leírás
    """
    return _resolve_category(
        wind,
        [
            (119, "🌪️ Orkán erősségű szél"),
            (90, "💨 Viharos szél"),
            (61, "🌬️ Erős szél"),
            (43, "🍃 Élénk szél"),
            (20, "🌿 Mérsékelt szél"),
            (10, "🕊️ Gyenge szél"),
        ],
        "🌅 Szélcsend",
    )
