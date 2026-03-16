#!/usr/bin/env python3
# mypy: ignore-errors
"""
Trend Widgets Module

🎨 Dashboard widget components for trend analytics visualization

Képességek:
- DashboardStatsCard: KPI kártya komponens
- InteractiveTrendChart: Plotly-alapú interaktív chart
- EnhancedStatisticsPanel: Dashboard layout statisztikákhoz

Fájl: src/presentation/gui/trend_analytics/trend_widgets/__init__.py
"""

# Re-export for backward compatibility
from .stats_card import DashboardStatsCard
from .stats_panel import EnhancedStatisticsPanel
from .trend_chart import InteractiveTrendChart

__all__ = [
    "DashboardStatsCard",
    "InteractiveTrendChart",
    "EnhancedStatisticsPanel",
]
