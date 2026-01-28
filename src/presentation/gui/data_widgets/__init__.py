#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Data Widgets Module
Táblázatos adatmegjelenítés modulja - ThemeManager integrált verzió.

🎨 THEMEMANAGER INTEGRÁCIÓ:
- Hardcoded CSS-ek eltávolítva
- Manual dark theme logika lecserélve ThemeManager-re
- Widget regisztrációk automatikus styling-hoz

🔧 KRITIKUS JAVÍTÁS:
- _convert_to_dataframe() robust hibakezelés
- Adathossz validálás
- Üres adatok kezelése
"""

# Public API export
from .core import WeatherDataTable
from .items import NumericTableWidgetItem
from .table_model import WeatherTableModel

# Re-export for backward compatibility
__all__ = [
    "WeatherDataTable",
    "WeatherTableModel",
    "NumericTableWidgetItem",
]
