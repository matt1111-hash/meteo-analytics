#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
WeatherTooltipMixin Core - Main mixin class for chart tooltips.
"""

from typing import Any, Dict

from .event_handlers import EventHandlers
from .event_manager import EventManager
from .point_finder import PointFinder
from .tooltip_display import TooltipDisplay
from .tooltip_formatter import TooltipFormatter


class WeatherTooltipMixin:
    """
    🎯 TOOLTIP MIXIN - Reusable tooltip functionality for charts.

    🛡️ CONSERVATIVE DESIGN:
    - Mixin pattern - opt-in usage
    - Self-contained logic - no external dependencies
    - Clean interface - simple activation
    - Rollback ready - easy to remove
    - Flexible point_data handling - chart-agnostic

    USAGE:
    ```python
    class MyChart(WeatherChart, WeatherTooltipMixin):
        def __init__(self):
            super().__init__()
            self.enable_tooltips()
    ```
    """

    def __init__(self):
        """
        Mixin initialization.

        NOTE: This is a mixin, cannot be called directly!
        """
        # Tooltip state variables
        self._tooltip_enabled = False
        self._tooltip_visible = False
        self._tooltip_annotation = None
        self._last_tooltip_point = None
        self._hover_tolerance = 15  # pixel distance

        # Event connection tracking
        self._tooltip_event_connections = []

        # Helper components
        self._event_manager = EventManager(self)
        self._event_handlers = EventHandlers(self)
        self._point_finder = PointFinder(self)
        self._tooltip_display = TooltipDisplay(self)
        self._tooltip_formatter = TooltipFormatter(self)

    def enable_tooltips(self, hover_tolerance: int = 15) -> None:
        """
        Enable tooltip functionality.

        Args:
            hover_tolerance: Hover sensitivity in pixels (default: 15)
        """
        if self._tooltip_enabled:
            print("⚠️ DEBUG: Tooltips már aktiválva")
            return

        self._hover_tolerance = hover_tolerance
        self._tooltip_enabled = True

        # Connect event handlers
        self._event_manager.connect_events()

        print(f"✅ DEBUG: Tooltips aktiválva - {hover_tolerance}px tolerance")

    def disable_tooltips(self) -> None:
        """Disable tooltip functionality."""
        if not self._tooltip_enabled:
            return

        # Disconnect event handlers
        self._event_manager.disconnect_events()

        # Hide tooltip
        self._tooltip_display.hide()

        self._tooltip_enabled = False
        print("🛑 DEBUG: Tooltips kikapcsolva")

    # Delegate to helper components
    def _find_closest_chart_point(self, event) -> Dict[str, Any]:
        """Find closest chart point to mouse event."""
        return self._point_finder.find_closest(event)

    def _find_closest_temperature_point(self, event) -> Dict[str, Any]:
        """Find closest temperature chart point."""
        return self._point_finder.find_closest_temperature(event)

    def _show_tooltip(self, event, point_data: Dict[str, Any]) -> None:
        """Show tooltip for point data."""
        self._tooltip_display.show(event, point_data)

    def _hide_tooltip(self) -> None:
        """Hide tooltip."""
        self._tooltip_display.hide()

    def _format_tooltip_text(self, point_data: Dict[str, Any]) -> str:
        """Format tooltip text."""
        return self._tooltip_formatter.format(point_data)

    def _on_tooltip_figure_leave(self, event) -> None:
        """Handle mouse leaving figure."""
        self._event_handlers.on_figure_leave(event)

    def _on_tooltip_mouse_move(self, event) -> None:
        """Handle mouse move event."""
        self._event_handlers.on_mouse_move(event)

    def _on_tooltip_mouse_click(self, event) -> None:
        """Handle mouse click event."""
        self._event_handlers.on_mouse_click(event)

    def _log_detailed_point_info(self, point_data: Dict[str, Any]) -> None:
        """Log detailed point info for debugging."""
        self._tooltip_formatter.log_detailed_info(point_data)
