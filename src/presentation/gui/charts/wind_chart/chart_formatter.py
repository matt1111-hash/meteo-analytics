#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wind Chart Formatter - Format wind chart with theme integration.
"""

from typing import TYPE_CHECKING

import pandas as pd
from matplotlib.dates import DateFormatter, MonthLocator

from ..theme_manager import get_current_colors
from .wind_categories import calculate_y_axis_max

if TYPE_CHECKING:
    from .core import WindChart


class WindChartFormatter:
    """Format wind chart with theme integration."""

    def __init__(self, chart: 'WindChart'):
        """
        Initialize wind chart formatter.

        Args:
            chart: WindChart instance
        """
        self.chart = chart

    def format(self, df: pd.DataFrame) -> None:
        """
        Format wind chart with theme colors.

        Args:
            df: DataFrame with wind data
        """
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')

        # Set labels and title
        self.chart.ax.set_title(
            self.chart.chart_title,
            fontweight='bold',
            pad=20,
            color=text_color
        )
        self.chart.ax.set_xlabel(self.chart.x_label, color=text_color)
        self.chart.ax.set_ylabel(self.chart.y_label, color=text_color)

        # Tick colors
        self.chart.ax.tick_params(colors=text_color)

        # Date formatting
        self.chart.ax.xaxis.set_major_locator(MonthLocator())
        self.chart.ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))

        # Y-axis range - optimized for Hungarian thresholds
        max_wind = df['windspeed'].max() if not df.empty else 50
        y_max = calculate_y_axis_max(max_wind)
        self.chart.ax.set_ylim(0, y_max)

        # Grid and legend
        self._apply_grid_and_legend(current_colors)

        # Layout optimization
        self.chart.figure.autofmt_xdate()
        self.chart.figure.tight_layout()

    def _apply_grid_and_legend(self, current_colors: dict) -> None:
        """
        Apply grid and legend with theme colors.

        Args:
            current_colors: Current theme color dictionary
        """
        # Grid
        if self.chart.grid_enabled:
            grid_color = current_colors.get('border', '#d1d5db')
            grid_alpha = 0.3 if self.chart.theme_manager.get_current_theme() == "light" else 0.2
            self.chart.ax.grid(
                True,
                alpha=grid_alpha,
                linestyle='-',
                linewidth=0.5,
                color=grid_color
            )

        # Legend
        if self.chart.legend_enabled:
            legend = self.chart.ax.legend(loc='upper left', framealpha=0.9)
            legend.get_frame().set_facecolor(current_colors.get('surface', '#ffffff'))
            legend.get_frame().set_edgecolor(current_colors.get('border', '#d1d5db'))
