#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChartContainer Theme Handler - Handle theme changes.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import ChartsContainer


class ThemeHandler:
    """Handle theme change events."""

    def __init__(self, container: "ChartsContainer"):
        """
        Initialize theme handler.

        Args:
            container: ChartsContainer instance
        """
        self._container = container

    def on_theme_changed(self, theme_name: str) -> None:
        """
        Handle theme change event.

        Args:
            theme_name: New theme name
        """
        print(f"🎨 DEBUG: ChartsContainer theme changing to: {theme_name}")

        charts = [
            self._container.temp_chart,
            self._container.precip_chart,
            self._container.wind_chart,
            self._container.heatmap_chart,
            self._container.windrose_chart,
            self._container.comparison_chart,
        ]

        for chart in charts:
            if hasattr(chart, "_redraw_with_new_theme"):
                try:
                    chart._redraw_with_new_theme()
                except Exception as e:
                    print(
                        f"⚠️ DEBUG: Chart theme update error for {chart.__class__.__name__}: {e}"
                    )

        print(f"✅ DEBUG: ChartsContainer theme updated: {theme_name}")
