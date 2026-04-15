#!/usr/bin/env python3
# mypy: ignore-errors

"""
Wind Chart Core - Main WindChart class.
🌪️ Széllökés grafikon widget - MAGYAR METEOROLÓGIAI SZABVÁNY
"""

from typing import Any

from PySide6.QtWidgets import QWidget

from ..base_chart import WeatherChart
from ..tooltip_mixin import WeatherTooltipMixin
from .chart_formatter import WindChartFormatter
from .data_extractor import WindDataExtractor
from .tooltip_handlers import WindTooltipHandler
from .wind_plotter import WindPlotter


class WindChart(WeatherChart, WeatherTooltipMixin):
    """
    🌪️ Wind Chart - Hungarian meteorological standards.

    🌪️ MAGYAR METEOROLÓGIAI SZABVÁNY:
    - Erős szél (43 km/h)
    - Viharos szél (61 km/h)
    - Erős vihar (90 km/h)
    - Orkán (119 km/h)

    ✅ wind_gusts_10m_max prioritás → windspeed_10m_max fallback
    🎨 ThemeManager integráció
    🎯 Interactive tooltip magyar szélkategóriákkal
    """

    def __init__(self, parent: QWidget | None = None):
        """
        Initialize WindChart.

        Args:
            parent: Parent widget
        """
        super().__init__(figsize=(12, 6), parent=parent)

        # Default labels
        self.chart_title = "🌪️ Széllökések változása"
        self.y_label = "Széllökések (km/h)"

        # Data extractor
        self._data_extractor = WindDataExtractor()

        # Plotter and formatter (initialized later with ax)
        self._plotter = None
        self._formatter = None

        # Tooltip handler (initialized later with ax)
        self._tooltip_handler = None

        # Enable tooltips
        self.enable_tooltips(hover_tolerance=15)

    def update_data(self, data: dict[str, Any]) -> None:
        """
        Update wind chart with new data.

        Args:
            data: API response dictionary with daily weather data
        """
        try:
            if self._is_updating:
                return

            self._is_updating = True

            # Extract wind data
            df = self._data_extractor.extract(data)

            if df.empty:
                self.clear_chart()
                self._is_updating = False
                return

            # Update current data
            self.current_data = df

            # Update chart title and y_label from extractor
            self.chart_title = self._data_extractor.chart_title
            self.y_label = self._data_extractor.y_label

            # Clear figure
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)

            # Initialize plotter and formatter
            self._plotter = WindPlotter(self)
            self._formatter = WindChartFormatter(self)
            self._tooltip_handler = WindTooltipHandler(self.ax, self._hover_tolerance)

            # Apply theme
            self._apply_theme_to_chart()

            # Plot wind data
            self._plotter.plot(df)

            # Format chart
            self._formatter.format(df)

            # Draw
            self.draw()

            self._is_updating = False

        except Exception:
            self._is_updating = False
            self.clear_chart()

    def _find_closest_chart_point(self, event) -> dict[str, Any] | None:
        """
        Find closest chart point to mouse event.

        Args:
            event: Mouse event

        Returns:
            Point data dictionary or None
        """
        if self._tooltip_handler is None:
            return None
        return self._tooltip_handler.find_closest_point(event, self.current_data)

    def _format_tooltip_text(self, point_data: dict[str, Any]) -> str:
        """
        Format tooltip text for wind data.

        Args:
            point_data: Point data dictionary

        Returns:
            Formatted tooltip text
        """
        if self._tooltip_handler is None:
            return ""
        return self._tooltip_handler.format_tooltip_text(point_data)

    def _show_tooltip(self, event, point_data: dict[str, Any]) -> None:
        """
        Show tooltip for wind data point.

        Args:
            event: Mouse event
            point_data: Point data dictionary
        """
        if self._tooltip_handler is None:
            return
        self._tooltip_handler.show_tooltip(event, point_data, self.draw_idle)

    def _hide_tooltip(self) -> None:
        """Hide tooltip."""
        if self._tooltip_handler is None:
            return
        self._tooltip_handler.hide_tooltip(self.draw_idle)
