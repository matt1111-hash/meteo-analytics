#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Analytics Module.
Multi-city régió elemzések dashboard modul.

🎯 REFAKTORÁLT KONSTANS HEATMAP ANALYTICS VIEW:
✅ KÖZPONTI SIGNAL RENDSZER - multi_city_query_requested
✅ 4 KONSTANS HEATMAP TAB - hőmérséklet, csapadék, szél, széllökés
✅ 2 DEDICATED WIND CHART - WindChart, WindRoseChart
✅ BEAUFORT 13 FOKOZAT - progresszív színátmenet
✅ KOMPAKT KÁRTYÁS STATISZTIKÁK
✅ MULTI-CITY RÉGIÓ ELEMZÉS

📁 MODUL STRUKTÚRA:
- analytics_helpers.py: MeteorologicalColorMaps, safe_* helpers
- analytics_widgets.py: RecordCard, RecordSummaryCard
- analytics_tabs.py: Tab widgetek (4 heatmap + 2 dedicated wind chart)
- analytics_statistics.py: Statisztika számítások
- analytics_view.py: Fő AnalyticsView osztály
"""

# Main AnalyticsView class
from .analytics_view.core import AnalyticsView

# Color maps
from .analytics_helpers import MeteorologicalColorMaps

# Widgets
from .analytics_widgets import RecordCard, RecordSummaryCard

# Tabs
from .analytics_tabs import (
    TemperatureTabWidget,
    PrecipitationTabWidget,
    WindTabWidget,
    WindGustTabWidget,
    ClimateTabWidget,
)

# Statistics
from .analytics_statistics import AnalyticsStatistics


__all__ = [
    # Main class
    'AnalyticsView',
    # Color maps
    'MeteorologicalColorMaps',
    # Widgets
    'RecordCard',
    'RecordSummaryCard',
    # Tabs
    'TemperatureTabWidget',
    'PrecipitationTabWidget',
    'WindTabWidget',
    'WindGustTabWidget',
    'ClimateTabWidget',
    # Statistics
    'AnalyticsStatistics',
]
