#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Formatting Module - Wind Helpers - Wind-specific formatting.
"""

from typing import Any

from src.presentation.gui.utils.constants import AnomalyConstants


def format_wind_gusts(value: float, unit: str = "km/h", include_category: bool = False) -> str:
    """Format wind gusts values with category."""
    if value is None:
        return "N/A"

    formatted = f"{value:.1f} {unit}"

    if include_category:
        category = get_wind_gusts_category(value)
        if category:
            formatted += f" ({category['emoji']} {category['label']})"

    return formatted


def get_wind_gusts_category(value: float) -> dict[str, Any] | None:
    """Get wind gusts category for value."""
    if value is None:
        return None

    for category_data in AnomalyConstants.WIND_GUSTS_CATEGORIES.values():
        if category_data["threshold"] <= value < category_data["max"]:
            return category_data

    return AnomalyConstants.WIND_GUSTS_CATEGORIES["CATASTROPHIC"]


def is_wind_gusts_extreme(value: float) -> bool:
    """Check if wind gusts is extreme."""
    if value is None:
        return False
    return value >= AnomalyConstants.WIND_GUSTS_EXTREME


def is_wind_gusts_hurricane(value: float) -> bool:
    """Check if wind gusts is hurricane strength."""
    if value is None:
        return False
    return value >= AnomalyConstants.WIND_GUSTS_HURRICANE


def is_wind_gusts_catastrophic(value: float) -> bool:
    """Check if wind gusts is catastrophic."""
    if value is None:
        return False
    return value >= AnomalyConstants.WIND_GUSTS_CATASTROPHIC


def get_wind_gusts_icon(value: float) -> str:
    """Get icon for wind gusts value."""
    if value is None:
        return "❓"

    category = get_wind_gusts_category(value)
    if category:
        return category["emoji"]

    return "💨"


def get_wind_gusts_color(value: float) -> str:
    """Get color code for wind gusts value."""
    if value is None:
        return AnomalyConstants.WIND_GUSTS_COLORS["normal"]

    category = get_wind_gusts_category(value)
    if category:
        return category["color"]

    return AnomalyConstants.WIND_GUSTS_COLORS["normal"]
