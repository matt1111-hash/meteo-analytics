# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 3 for TemperatureTooltipHandlerMixin."""

from __future__ import annotations

from .tooltip_handler_support import *


class TemperatureTooltipHandlerMixinPart3Mixin:
    def _show_tooltip(self, event, point_data: Dict[str, Any]) -> None:
        """
        💬 SMART TOOLTIP POSITIONING - DYNAMIC PLACEMENT

        🎨 INTELLIGENT TOOLTIP:
        - Professional design
        - Weather-specific formatting
        - 🎯 SMART POSITIONING: Automatically avoids chart edges
        """
        if not hasattr(self, "ax"):
            return

        # Előző tooltip törlése
        self._hide_tooltip()

        # Tooltip szöveg formázása
        tooltip_text = self._format_tooltip_text(point_data)

        # Koordináták meghatározása
        import matplotlib.dates as mdates

        x_pos = mdates.date2num(point_data["date"])
        y_pos = point_data["primary_temp"]

        # 🎯 SMART POSITIONING LOGIC
        # Chart területének boundaries
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # Pont pozíciója a chart területen (0-1 scale)
        x_relative = (x_pos - xlim[0]) / (xlim[1] - xlim[0])
        y_relative = (y_pos - ylim[0]) / (ylim[1] - ylim[0])

        # Dynamic offset számítás
        if y_relative > 0.7:  # Felső 30%-ban
            # Tooltip lefelé
            offset_y = -80
            va_align = "top"
            print(f"🔽 DEBUG: Tooltip lefelé - y_relative: {y_relative:.2f}")
        else:
            # Tooltip felfelé (alapértelmezett)
            offset_y = 50
            va_align = "bottom"
            print(f"🔼 DEBUG: Tooltip felfelé - y_relative: {y_relative:.2f}")

        if x_relative > 0.8:  # Jobb 20%-ban
            # Tooltip balra
            offset_x = -100
            ha_align = "right"
            print(f"⬅️ DEBUG: Tooltip balra - x_relative: {x_relative:.2f}")
        else:
            # Tooltip jobbra (alapértelmezett)
            offset_x = 40
            ha_align = "left"
            print(f"➡️ DEBUG: Tooltip jobbra - x_relative: {x_relative:.2f}")

        # Current colors
        current_colors = get_current_colors()

        # ENHANCED TOOLTIP ANNOTATION - SMART POSITIONED
        self.tooltip_annotation = self.ax.annotate(
            tooltip_text,
            xy=(x_pos, y_pos),
            xytext=(offset_x, offset_y),  # 🎯 DYNAMIC OFFSET
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
            ha=ha_align,  # 🎯 DYNAMIC HORIZONTAL ALIGNMENT
            va=va_align,  # 🎯 DYNAMIC VERTICAL ALIGNMENT
            zorder=1000,  # Top layer
        )

        self._tooltip_visible = True
        self._tooltip_annotation = self.tooltip_annotation

        # Canvas frissítése
        if hasattr(self, "draw_idle"):
            self.draw_idle()

    def _hide_tooltip(self) -> None:
        """
        🙈 Tooltip elrejtése - CLEAN HIDING
        """
        if self._tooltip_annotation:
            try:
                self._tooltip_annotation.remove()
            except Exception as e:
                print(f"⚠️ DEBUG: Tooltip remove error: {e}")

            self._tooltip_annotation = None
            self._tooltip_visible = False

            # Canvas frissítése
            if hasattr(self, "draw_idle"):
                self.draw_idle()
