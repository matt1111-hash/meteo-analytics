#!/usr/bin/env python3
# mypy: ignore-errors

"""
ChartContainer UI Builder - Build UI components.
"""

from typing import TYPE_CHECKING

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..charts import (
    EnhancedTemperatureChart,
    HeatmapCalendarChart,
    MultiYearComparisonChart,
    PrecipitationChart,
    WindChart,
    WindRoseChart,
)
from ..theme_manager import register_widget_for_theming

if TYPE_CHECKING:
    from .core import ChartsContainer


class UIBuilder:
    """Build UI components for ChartsContainer."""

    def __init__(self, container: "ChartsContainer"):
        """
        Initialize UI builder.

        Args:
            container: ChartsContainer instance
        """
        self._container = container

    def build(self) -> None:
        """Build complete UI."""
        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(5, 5, 5, 5)

        # Controls
        controls = self._create_controls()
        layout.addWidget(controls)

        # Chart tabs
        self._create_chart_tabs(layout)

    def _create_controls(self) -> QWidget:
        """Create control panel."""
        controls = QWidget()
        controls.setMaximumHeight(50)
        layout = QHBoxLayout(controls)

        # Register for theming
        register_widget_for_theming(controls, "container")

        # Chart title
        title = QLabel("📈 Részletes Grafikonok")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        register_widget_for_theming(title, "text")
        layout.addWidget(title)

        layout.addStretch()

        # Grid toggle
        self._container.grid_check = QCheckBox("Rácsvonalak")
        self._container.grid_check.setChecked(True)
        self._container.grid_check.toggled.connect(self._container._toggle_grid_optimized)
        register_widget_for_theming(self._container.grid_check, "input")
        layout.addWidget(self._container.grid_check)

        # Legend toggle
        self._container.legend_check = QCheckBox("Jelmagyarázat")
        self._container.legend_check.setChecked(True)
        self._container.legend_check.toggled.connect(self._container._toggle_legend_optimized)
        register_widget_for_theming(self._container.legend_check, "input")
        layout.addWidget(self._container.legend_check)

        # Export button
        export_btn = QPushButton("💾 Export")
        export_btn.clicked.connect(self._container._export_current_chart)
        register_widget_for_theming(export_btn, "button")
        layout.addWidget(export_btn)

        return controls

    def _create_chart_tabs(self, layout: QVBoxLayout) -> None:
        """Create chart tabs."""
        self._container.tabs = QTabWidget()
        register_widget_for_theming(self._container.tabs, "container")

        # 1. Temperature chart
        self._container.temp_chart = EnhancedTemperatureChart()
        self._container.tabs.addTab(self._container.temp_chart, "🌡️ Hőmérséklet")

        # 2. Precipitation chart
        self._container.precip_chart = PrecipitationChart()
        self._container.tabs.addTab(self._container.precip_chart, "🌧️ Csapadék")

        # 3. Wind chart
        self._container.wind_chart = WindChart()
        self._container.tabs.addTab(self._container.wind_chart, "🌪️ Széllökések")

        # 4. Heatmap chart
        self._container.heatmap_chart = HeatmapCalendarChart()
        self._container.tabs.addTab(self._container.heatmap_chart, "📅 Naptár")

        # 5. Wind Rose chart
        self._container.windrose_chart = WindRoseChart()
        self._container.tabs.addTab(self._container.windrose_chart, "🌹 Széllökés Rózsa")

        # 6. Comparison chart
        self._container.comparison_chart = MultiYearComparisonChart()
        self._container.tabs.addTab(self._container.comparison_chart, "📊 Évek")

        layout.addWidget(self._container.tabs)
