#!/usr/bin/env python3
# mypy: ignore-errors

"""
WeatherTooltipMixin Event Handlers - Handle mouse events.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import WeatherTooltipMixin


class EventHandlers:
    """Handle mouse events for tooltips."""

    def __init__(self, mixin: "WeatherTooltipMixin"):
        """
        Initialize event handlers.

        Args:
            mixin: WeatherTooltipMixin instance
        """
        self._mixin = mixin

    def on_figure_leave(self, event) -> None:  # noqa: ARG002
        """
        Handle mouse leaving figure.

        Args:
            event: Figure leave event
        """
        if not self._mixin._tooltip_enabled:
            return

        self._mixin._hide_tooltip()

    def on_mouse_move(self, event) -> None:
        """
        Handle mouse move event - tooltip hover logic.

        Args:
            event: Mouse move event
        """
        if not self._mixin._tooltip_enabled:
            return

        if not hasattr(self._mixin, "ax") or event.inaxes != self._mixin.ax:
            self._mixin._hide_tooltip()
            return

        if event.xdata is None or event.ydata is None:
            self._mixin._hide_tooltip()
            return

        # Find closest data point
        closest_point = self._mixin._find_closest_chart_point(event)

        if closest_point:
            print(f"🎯 DEBUG: Tooltip FOUND point - index: {closest_point.get('index')}")

            if not self._mixin._last_tooltip_point or self._mixin._last_tooltip_point.get(
                "index"
            ) != closest_point.get("index"):
                print("🎯 DEBUG: Tooltip megjelenítés indul...")
                self._mixin._show_tooltip(event, closest_point)
                self._mixin._last_tooltip_point = closest_point
            else:
                print("🔄 DEBUG: Tooltip ugyanaz a pont - skip update")
        else:
            print("🚫 DEBUG: Tooltip nincs közeli pont")
            if self._mixin._tooltip_visible:
                print("🙈 DEBUG: Tooltip elrejtése...")
                self._mixin._hide_tooltip()
                self._mixin._last_tooltip_point = None

    def on_mouse_click(self, event) -> None:
        """
        Handle mouse click event - log detailed info.

        Args:
            event: Mouse click event
        """
        if not self._mixin._tooltip_enabled:
            return

        if not hasattr(self._mixin, "ax") or event.inaxes != self._mixin.ax:
            return

        closest_point = self._mixin._find_closest_chart_point(event)
        if closest_point:
            self._mixin._log_detailed_point_info(closest_point)
