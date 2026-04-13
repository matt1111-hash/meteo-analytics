#!/usr/bin/env python3
# mypy: ignore-errors

"""
ChartContainer Core - Main ChartsContainer class.
"""

from datetime import datetime
from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from ..charts import (
    EnhancedTemperatureChart,
    HeatmapCalendarChart,
    MultiYearComparisonChart,
    PrecipitationChart,
    WindChart,
    WindRoseChart,
)
from ..theme_manager import get_theme_manager, register_widget_for_theming
from .chart_manager import ChartManager
from .theme_handler import ThemeHandler
from .toggle_handlers import ToggleHandlers
from .ui_builder import UIBuilder


class ChartsContainer(QWidget):
    """
    Grafikonok fő konténer widget - PROFESSIONAL CHARTS + DUPLICATION BUGFIX.

    🔄 FÁZIS 4: Professzionális nagy chartok integrálása
    📊 CHARTOK: Enhanced Temperature, Heatmap Calendar, Wind Rose, Multi-Year
    🔧 KRITIKUS JAVÍTÁS: Toggle funkciók optimalizálása duplikáció nélkül
    🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ
    🌪️ WIND GUSTS KRITIKUS JAVÍTÁS
    """

    # Signals
    chart_exported = Signal(str, bool)  # filepath, success
    chart_settings_changed = Signal(dict)  # settings dict

    def __init__(self, parent: QWidget | None = None):
        """
        Initialize ChartsContainer.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # SimplifiedThemeManager integration
        self.theme_manager = get_theme_manager()
        self.current_data: dict[str, Any] | None = None

        # Charts collection
        self.temp_chart: EnhancedTemperatureChart = None
        self.precip_chart: PrecipitationChart = None
        self.wind_chart: WindChart = None
        self.heatmap_chart: HeatmapCalendarChart = None
        self.windrose_chart: WindRoseChart = None
        self.comparison_chart: MultiYearComparisonChart = None
        self.tabs = None

        # UI components
        self.grid_check = None
        self.legend_check = None

        # Helper components
        self._ui_builder = UIBuilder(self)
        self._chart_manager = ChartManager(self)
        self._toggle_handlers = ToggleHandlers(self)
        self._theme_handler = ThemeHandler(self)

        # Initialize UI and connect signals
        self._ui_builder.build()
        self._connect_signals()

        # Register for theming
        register_widget_for_theming(self, "container")

        print("✅ DEBUG: ChartsContainer initialized with refactored chart modules")

    def _connect_signals(self) -> None:
        """Connect all chart signals."""
        charts = [
            self.temp_chart,
            self.precip_chart,
            self.wind_chart,
            self.heatmap_chart,
            self.windrose_chart,
            self.comparison_chart,
        ]

        for chart in charts:
            chart.chart_clicked.connect(self._on_chart_clicked)

        # Theme change detection
        self.theme_manager.theme_changed.connect(self._theme_handler.on_theme_changed)

        print("✅ DEBUG: ChartsContainer signals connected")

    def _on_chart_clicked(self, x: float, y: float) -> None:
        """Handle chart click."""
        print(f"Chart clicked at: {x}, {y}")

    # === PUBLIC API DELEGATED TO HELPERS ===

    def update_charts(self, data: dict[str, Any]) -> None:
        """Update all charts with new data."""
        self._chart_manager.update_all(data)

    def clear_charts(self) -> None:
        """Clear all charts."""
        self._chart_manager.clear_all()

    def _toggle_grid_optimized(self, enabled: bool) -> None:
        """Toggle grid display."""
        self._toggle_handlers.toggle_grid(enabled)

    def _toggle_legend_optimized(self, enabled: bool) -> None:
        """Toggle legend display."""
        self._toggle_handlers.toggle_legend(enabled)

    def _on_theme_changed(self, theme_name: str) -> None:
        """Handle theme change."""
        self._theme_handler.on_theme_changed(theme_name)

    def _export_current_chart(self) -> None:
        """Export current chart."""
        current_widget = self.tabs.currentWidget()
        if hasattr(current_widget, "export_chart"):
            chart_name = self.tabs.tabText(self.tabs.currentIndex()).replace(" ", "_")
            filepath = f"chart_{chart_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            success = current_widget.export_chart(filepath)
            self.chart_exported.emit(filepath, success)

    def apply_theme(self, dark_theme: bool) -> None:
        """
        🎨 DEPRECATED: Use SimplifiedThemeManager instead.

        Args:
            dark_theme: Dark theme flag (DEPRECATED)
        """
        print("⚠️ DEBUG: apply_theme() DEPRECATED - use SimplifiedThemeManager.set_theme()")
        theme_name = "dark" if dark_theme else "light"
        self.theme_manager.set_theme(theme_name)
