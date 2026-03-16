#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
WeatherTooltipMixin Tooltip Display - Show/hide tooltip annotations.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

import matplotlib.dates as mdates

from ...theme_manager import get_current_colors

if TYPE_CHECKING:
    from .core import WeatherTooltipMixin


class TooltipDisplay:
    """Handle tooltip display and hiding."""

    def __init__(self, mixin: "WeatherTooltipMixin"):
        """
        Initialize tooltip display.

        Args:
            mixin: WeatherTooltipMixin instance
        """
        self._mixin = mixin

    def show(self, event, point_data: Dict[str, Any]) -> None:
        """
        Show tooltip annotation.

        Args:
            event: Mouse event
            point_data: Point data dictionary
        """
        if not hasattr(self._mixin, "ax"):
            return

        # Hide previous tooltip
        self.hide()

        # Format tooltip text
        tooltip_text = self._mixin._format_tooltip_text(point_data)

        # Get coordinates
        if "date" in point_data:
            x_pos = mdates.date2num(point_data["date"])
        else:
            print("⚠️ DEBUG: Nincs 'date' kulcs a point_data-ban")
            return

        # Y coordinate - flexible key search
        y_pos = self._get_y_coordinate(point_data)
        if y_pos is None:
            print("❌ DEBUG: Nem találtunk érvényes Y koordinátát!")
            print(f"📋 DEBUG: point_data kulcsok: {list(point_data.keys())}")
            return

        print(f"🎯 DEBUG: Tooltip koordináták: x={x_pos}, y={y_pos}")

        # Current colors
        current_colors = get_current_colors()

        # Create tooltip annotation
        try:
            self._mixin.tooltip_annotation = self._mixin.ax.annotate(
                tooltip_text,
                xy=(x_pos, y_pos),
                xytext=(40, 50),
                textcoords="offset points",
                bbox=dict(
                    boxstyle="round,pad=1.0",
                    facecolor="lightyellow",
                    edgecolor=current_colors.get("border", "#34495E"),
                    linewidth=2,
                    alpha=0.95,
                ),
                arrowprops=dict(
                    arrowstyle="->",
                    color=current_colors.get("border", "#34495E"),
                    lw=2,
                    alpha=0.8,
                ),
                fontsize=10,
                fontweight="bold",
                ha="left",
                va="bottom",
                zorder=1000,
            )

            self._mixin._tooltip_visible = True
            self._mixin._tooltip_annotation = self._mixin.tooltip_annotation

            print("✅ DEBUG: Tooltip annotation létrehozva!")

            # Force canvas refresh
            self._refresh_canvas()

        except Exception as e:
            print(f"❌ DEBUG: Tooltip annotation létrehozási hiba: {e}")

    def hide(self) -> None:
        """Hide tooltip annotation."""
        if self._mixin._tooltip_annotation:
            try:
                self._mixin._tooltip_annotation.remove()
            except Exception as e:
                print(f"⚠️ DEBUG: Tooltip remove error: {e}")

            self._mixin._tooltip_annotation = None
            self._mixin._tooltip_visible = False

            if hasattr(self._mixin, "draw_idle"):
                self._mixin.draw_idle()

    def _get_y_coordinate(self, point_data: Dict[str, Any]) -> Optional[float]:
        """Get Y coordinate from point data with flexible key search."""
        y_pos = None

        # Temperature chart: 'primary_temp'
        if "primary_temp" in point_data:
            y_pos = point_data["primary_temp"]
            print(f"🌡️ DEBUG: Temperature chart Y pozíció: {y_pos}")
        # Heatmap/Wind/Precipitation: 'value'
        elif "value" in point_data:
            y_pos = point_data["value"]
            print(f"📊 DEBUG: Generic chart Y pozíció: {y_pos}")
        # Fallback: first numeric value
        else:
            for key, value in point_data.items():
                if isinstance(value, (int, float)) and not key.endswith("_index"):
                    y_pos = value
                    print(f"🔍 DEBUG: Fallback Y pozíció ({key}): {y_pos}")
                    break

        return y_pos

    def _refresh_canvas(self) -> None:
        """Force canvas refresh with multiple methods."""
        try:
            if hasattr(self._mixin, "draw_idle"):
                self._mixin.draw_idle()
                print("🔄 DEBUG: draw_idle() hívva")

            if hasattr(self._mixin, "draw"):
                self._mixin.draw()
                print("🔄 DEBUG: draw() force hívva")

            if hasattr(self._mixin.figure, "canvas") and hasattr(
                self._mixin.figure.canvas, "draw"
            ):
                self._mixin.figure.canvas.draw()
                print("🔄 DEBUG: figure.canvas.draw() hívva")

            if hasattr(self._mixin, "update"):
                self._mixin.update()
                print("🔄 DEBUG: widget.update() hívva")

        except Exception as refresh_error:
            print(f"⚠️ DEBUG: Canvas refresh hiba: {refresh_error}")
