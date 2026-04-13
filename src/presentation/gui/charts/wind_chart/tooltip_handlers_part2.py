# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for WindTooltipHandler."""

from __future__ import annotations

from .tooltip_handlers_support import *


class WindTooltipHandlerPart2Mixin:  # noqa: D101
    def show_tooltip(
        self,
        event,  # noqa: ARG002
        point_data: Dict[str, Any],
        draw_idle_callback,
    ) -> None:
        """
        Show tooltip with smart positioning.

        Args:
            event: Mouse event
            point_data: Point data dictionary
            draw_idle_callback: Callback to redraw canvas
        """
        # Hide previous tooltip
        self.hide_tooltip(draw_idle_callback)

        # Format tooltip text
        tooltip_text = self.format_tooltip_text(point_data)

        # Get coordinates
        import matplotlib.dates as mdates  # noqa: PLC0415

        x_pos = mdates.date2num(point_data["date"])
        y_pos = point_data["windspeed"]

        # Smart positioning
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        x_relative = (x_pos - xlim[0]) / (xlim[1] - xlim[0])
        y_relative = (y_pos - ylim[0]) / (ylim[1] - ylim[0])

        # Dynamic offset calculation
        if y_relative > 0.7:  # noqa: PLR2004
            offset_y = -80
            va_align = "top"
        else:
            offset_y = 50
            va_align = "bottom"

        if x_relative > 0.8:  # noqa: PLR2004
            offset_x = -120
            ha_align = "right"
        else:
            offset_x = 40
            ha_align = "left"

        # Current colors
        current_colors = get_current_colors()

        # Create tooltip annotation
        self.tooltip_annotation = self.ax.annotate(
            tooltip_text,
            xy=(x_pos, y_pos),
            xytext=(offset_x, offset_y),
            textcoords="offset points",
            bbox={
                "boxstyle": "round,pad=1.0",
                "facecolor": "lightblue",
                "edgecolor": current_colors.get("border", "#34495E"),
                "linewidth": 2,
                "alpha": 0.95,
            },
            arrowprops={
                "arrowstyle": "->",
                "color": current_colors.get("border", "#34495E"),
                "lw": 2,
                "alpha": 0.8,
            },
            fontsize=10,
            fontweight="bold",
            ha=ha_align,
            va=va_align,
            zorder=1000,
        )

        self._tooltip_visible = True
        self._tooltip_annotation = self.tooltip_annotation

        # Redraw canvas
        if draw_idle_callback:
            draw_idle_callback()

    def hide_tooltip(self, draw_idle_callback=None) -> None:
        """
        Hide tooltip.

        Args:
            draw_idle_callback: Callback to redraw canvas
        """
        if hasattr(self, "_tooltip_annotation") and self._tooltip_annotation:
            try:
                self._tooltip_annotation.remove()
            except Exception as e:
                print(f"⚠️ DEBUG: Wind tooltip remove error: {e}")

            self._tooltip_annotation = None
            self._tooltip_visible = False

            if draw_idle_callback:
                draw_idle_callback()
