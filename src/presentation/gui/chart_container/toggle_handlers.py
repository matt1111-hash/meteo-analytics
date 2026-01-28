#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChartContainer Toggle Handlers - Handle grid and legend toggles.
"""

from typing import TYPE_CHECKING

from ..theme_manager import get_current_colors

if TYPE_CHECKING:
    from .core import ChartsContainer


class ToggleHandlers:
    """Handle grid and legend toggle operations."""

    def __init__(self, container: 'ChartsContainer'):
        """
        Initialize toggle handlers.

        Args:
            container: ChartsContainer instance
        """
        self._container = container

    def toggle_grid(self, enabled: bool) -> None:
        """
        Toggle grid display on all charts.

        Args:
            enabled: Whether grid should be enabled
        """
        print(f"🔧 DEBUG: _toggle_grid_optimized({enabled})")

        try:
            charts = [
                self._container.temp_chart, self._container.precip_chart,
                self._container.wind_chart, self._container.heatmap_chart,
                self._container.windrose_chart, self._container.comparison_chart
            ]

            for chart in charts:
                chart.grid_enabled = enabled

                if hasattr(chart, 'ax') and chart.ax:
                    if enabled:
                        current_colors = get_current_colors()
                        grid_color = current_colors.get('border', '#d1d5db')
                        grid_alpha = 0.3 if self._container.theme_manager.get_current_theme() == "light" else 0.2
                        chart.ax.grid(True, alpha=grid_alpha, linestyle='-', linewidth=0.8, color=grid_color)
                    else:
                        chart.ax.grid(False)

                    chart.draw()

            print(f"✅ DEBUG: Grid toggle optimalizálva: {enabled}")

        except Exception as e:
            print(f"❌ DEBUG: Grid toggle hiba: {e}")

    def toggle_legend(self, enabled: bool) -> None:
        """
        Toggle legend display on all charts.

        Args:
            enabled: Whether legend should be enabled
        """
        print(f"🔧 DEBUG: _toggle_legend_optimized({enabled})")

        try:
            charts = [
                self._container.temp_chart, self._container.precip_chart,
                self._container.wind_chart, self._container.heatmap_chart,
                self._container.windrose_chart, self._container.comparison_chart
            ]

            current_colors = get_current_colors()

            for chart in charts:
                chart.legend_enabled = enabled

                if hasattr(chart, 'ax') and chart.ax:
                    if enabled:
                        legend = chart.ax.get_legend()
                        if legend:
                            legend.set_visible(True)
                            legend.get_frame().set_facecolor(current_colors.get('surface', '#ffffff'))
                            legend.get_frame().set_edgecolor(current_colors.get('border', '#d1d5db'))
                        else:
                            legend = chart.ax.legend(
                                bbox_to_anchor=(1.05, 1), loc='upper left',
                                framealpha=0.95, fancybox=True, shadow=True, fontsize=11
                            )
                            legend.get_frame().set_facecolor(current_colors.get('surface', '#ffffff'))
                            legend.get_frame().set_edgecolor(current_colors.get('border', '#d1d5db'))
                    else:
                        legend = chart.ax.get_legend()
                        if legend:
                            legend.set_visible(False)

                    chart.draw()

            print(f"✅ DEBUG: Legend toggle optimalizálva: {enabled}")

        except Exception as e:
            print(f"❌ DEBUG: Legend toggle hiba: {e}")
