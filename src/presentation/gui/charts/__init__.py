#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Charts Package
Professzionális chart widget-ek moduláris package-je.

🎨 MODULÁRIS ARCHITEKTÚRA: Minden chart típus saját modulban
🔧 CLEAN CODE: Single Responsibility Principle
🚀 EASY IMPORT: Centralizált chart import rendszer
✅ Piros (#C43939) téma támogatás minden chart-ban
✅ SimplifiedThemeManager integráció
✅ ColorPalette API használata
✅ Duplikáció bugfix minden chart-ban
✅ Wind gusts támogatás
✅ Professional styling és formázás

Ez a package tartalmazza:
- BaseChart: Alap chart osztály ColorPalette integrációval
- EnhancedTemperatureChart: Fejlett hőmérséklet vizualizáció
- PrecipitationChart: Csapadék oszlopdiagram
- WindChart: Széllökés trend chart
- WindRoseChart: Széllökés rózsadiagram
- HeatmapCalendarChart: Hőmérséklet naptár heatmap
- MultiYearComparisonChart: Évek összehasonlító chart

HASZNÁLAT:
```python
from .charts import (
    WeatherChart, EnhancedTemperatureChart, PrecipitationChart,
    WindChart, WindRoseChart, HeatmapCalendarChart, MultiYearComparisonChart
)
```

VAGY:
```python
from .charts.temperature_chart import EnhancedTemperatureChart
from .charts.wind_chart import WindChart
# stb.
```
"""

# === CHART OSZTÁLYOK EXPORTÁLÁSA ===

# Base chart osztály
from .base_chart import WeatherChart
from .comparison_chart import MultiYearComparisonChart
from .heatmap_chart import HeatmapCalendarChart
from .precipitation_chart import PrecipitationChart

# Specifikus chart típusok
from .temperature_chart import EnhancedTemperatureChart
from .wind_chart import WindChart
from .wind_rose_chart import WindRoseChart

# === PACKAGE METADATA ===

__version__ = "1.0.0"
__author__ = "Global Weather Analyzer Team"
__description__ = "Professional weather chart widgets with ColorPalette integration"

# === PUBLIKUS API ===

__all__ = [
    # Base chart
    "WeatherChart",
    # Specific chart types
    "EnhancedTemperatureChart",
    "PrecipitationChart",
    "WindChart",
    "WindRoseChart",
    "HeatmapCalendarChart",
    "MultiYearComparisonChart",
]

# === CHART TÍPUSOK REGISTRY ===

CHART_TYPES = {
    "temperature": EnhancedTemperatureChart,
    "precipitation": PrecipitationChart,
    "wind": WindChart,
    "wind_rose": WindRoseChart,
    "heatmap": HeatmapCalendarChart,
    "comparison": MultiYearComparisonChart,
}

# === UTILITY FÜGGVÉNYEK ===


def get_available_chart_types():
    """
    Elérhető chart típusok listája.

    Returns:
        List[str]: Chart típusok nevei
    """
    return list(CHART_TYPES.keys())


def create_chart(chart_type: str, parent=None):
    """
    Chart factory függvény.

    Args:
        chart_type: Chart típus neve ('temperature', 'precipitation', stb.)
        parent: Szülő widget

    Returns:
        WeatherChart: Chart instance

    Raises:
        ValueError: Ha ismeretlen chart típus
    """
    if chart_type not in CHART_TYPES:
        available = ", ".join(CHART_TYPES.keys())
        raise ValueError(f"Ismeretlen chart típus: {chart_type}. Elérhető: {available}")

    chart_class = CHART_TYPES[chart_type]
    return chart_class(parent=parent)


def get_chart_info():
    """
    Részletes információk az összes chart típusról.

    Returns:
        Dict[str, Dict]: Chart típusok és tulajdonságaik
    """
    return {
        "temperature": {
            "class": "EnhancedTemperatureChart",
            "description": "Fejlett hőmérséklet vizualizáció trend vonalakkal",
            "icon": "🌡️",
            "features": ["trend_lines", "zones", "annotations", "statistics"],
        },
        "precipitation": {
            "class": "PrecipitationChart",
            "description": "Csapadék oszlopdiagram színkódolással",
            "icon": "🌧️",
            "features": ["color_coding", "statistics", "bar_chart"],
        },
        "wind": {
            "class": "WindChart",
            "description": "Széllökés trend chart kritikus küszöbökkel",
            "icon": "🌪️",
            "features": ["wind_gusts", "thresholds", "annotations", "categories"],
        },
        "wind_rose": {
            "class": "WindRoseChart",
            "description": "Széllökés rózsadiagram 16 iránnyal",
            "icon": "🌹",
            "features": ["polar_plot", "direction_analysis", "speed_categories"],
        },
        "heatmap": {
            "class": "HeatmapCalendarChart",
            "description": "Hőmérséklet naptár heatmap tetszőleges időszakhoz",
            "icon": "📅",
            "features": ["calendar_view", "heatmap", "colorbar", "date_range"],
        },
        "comparison": {
            "class": "MultiYearComparisonChart",
            "description": "Évek összehasonlító chart szezonális vonalakkal",
            "icon": "📊",
            "features": ["multi_year", "trend_analysis", "seasonal_markers"],
        },
    }


# === DEBUG INFORMÁCIÓK ===

print(f"✅ DEBUG: Charts package loaded - {len(__all__)} chart types available")
print("🎨 DEBUG: All charts support ColorPalette API + Piros (#C43939) téma")
print("🔧 DEBUG: Duplikáció bugfix applied to all charts")
print("🌪️ DEBUG: Wind gusts support: WindChart + WindRoseChart")
print(f"📈 DEBUG: Available chart types: {', '.join(get_available_chart_types())}")
