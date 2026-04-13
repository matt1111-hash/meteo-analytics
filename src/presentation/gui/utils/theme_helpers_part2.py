# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from theme_helpers.py."""

from __future__ import annotations

from .theme_helpers_support import *


def log_theme_change(from_theme: str, to_theme: str) -> None:
    """
    Téma váltás naplózása.

    Args:
        from_theme: Előző téma neve
        to_theme: Új téma neve
    """
    logger.info(f"THEME CHANGE: {from_theme} → {to_theme}")


def log_wind_gusts_event(value: float, location: str = "Unknown") -> None:
    """
    🌪️ KRITIKUS JAVÍTÁS: Széllökés esemény naplózása.

    Args:
        value: Széllökés érték
        location: Helyszín
    """
    from .formatting import get_wind_gusts_category  # noqa: PLC0415

    category = get_wind_gusts_category(value)
    if category:
        logger.info(
            f"WIND GUSTS: {value:.1f} km/h at {location} - {category['emoji']} {category['label']}"
        )
    else:
        logger.info(f"WIND GUSTS: {value:.1f} km/h at {location}")
