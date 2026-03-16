# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Multi-Year Comparison Chart
Több év összehasonlító chart widget trend elemzéssel.

📊 MULTI-YEAR COMPARISON CHART: Azonos időszakok összehasonlítása különböző évekből
🎨 TÉMA INTEGRÁCIÓ: ColorPalette trend elemzési színek használata
🔧 KRITIKUS JAVÍTÁS: Duplikáció-mentes frissítés + SIMPLIFIED THEMEMANAGER
✅ Piros (#C43939) téma támogatás
✅ Trend vonalak minden évhez
✅ Szezonális vonalak (tavasz, nyár, ősz, tél)
✅ Statisztikai információk
✅ Optimális legend pozícionálás
"""

from typing import Any, Dict, Optional

import pandas as pd
from PySide6.QtWidgets import QWidget

from src.presentation.gui.theme_manager import get_current_colors

from .base_chart import WeatherChart


def build_temp_mean_fallback(
    temp_max: list[Any], temp_min: list[Any], temp_mean: list[Any]
) -> list[Any]:
    """Return API mean series or compute a fallback from min/max values."""
    if temp_mean:
        return temp_mean
    if not temp_max or not temp_min or len(temp_max) != len(temp_min):
        return []

    result: list[Any] = []
    for t_max, t_min in zip(temp_max, temp_min):
        if t_max is None or t_min is None:
            result.append(None)
            continue
        result.append(round((t_max + t_min) / 2, 1))
    return result


def has_complete_temperature_payload(
    dates: list[Any], temp_max: list[Any], temp_min: list[Any], temp_mean: list[Any]
) -> bool:
    """Return whether all yearly temperature series are present."""
    return bool(dates and temp_max and temp_min and temp_mean)


def has_matching_temperature_lengths(
    dates: list[Any], temp_max: list[Any], temp_min: list[Any], temp_mean: list[Any]
) -> bool:
    """Return whether all yearly temperature series share the same length."""
    expected_length = len(dates)
    return (
        expected_length == len(temp_max)
        and expected_length == len(temp_min)
        and expected_length == len(temp_mean)
    )
