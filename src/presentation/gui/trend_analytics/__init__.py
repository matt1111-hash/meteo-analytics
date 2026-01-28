#!/usr/bin/env python3
"""
Trend Analytics Package

🚀 Enhanced Trend Analytics - Professional Dashboard Implementation

This package contains modular components for trend analytics visualization:
- TrendDataProcessor: API-alapú trend adatfeldolgozás
- DashboardStatsCard: KPI kártya komponens
- InteractiveTrendChart: Plotly-alapú interaktív chart
- EnhancedStatisticsPanel: Dashboard layout statisztikákhoz
- TrendAnalyticsWorker: Háttérszálas API hívás kezelő
- TrendAnalyticsTab: Fő koordinátor widget

Fájl: src/presentation/gui/trend_analytics/__init__.py
"""

# Re-export all classes for backward compatibility
from .trend_analytics_tab import TrendAnalyticsTab, register_trend_analytics_theme
from .trend_data_processor import TrendDataProcessor
from .trend_widgets import (
    DashboardStatsCard,
    EnhancedStatisticsPanel,
    InteractiveTrendChart,
)
from .trend_worker import TrendAnalyticsWorker

__all__ = [
    "TrendDataProcessor",
    "DashboardStatsCard",
    "InteractiveTrendChart",
    "EnhancedStatisticsPanel",
    "TrendAnalyticsWorker",
    "TrendAnalyticsTab",
    "register_trend_analytics_theme",
]
