# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from tooltip.py."""

from __future__ import annotations

from .tooltip_support import *


def _resolve_bar_tooltip_position(
    self, x_pos: float, y_pos: float
) -> tuple[int, int, str, str, str]:
    """Resolve tooltip offset and alignment for the hovered bar."""
    xlim = self.ax.get_xlim()
    ylim = self.ax.get_ylim()
    x_relative = (x_pos - xlim[0]) / (xlim[1] - xlim[0])
    y_relative = (y_pos - ylim[0]) / (ylim[1] - ylim[0])
    if y_relative > 0.7:  # noqa: PLR2004
        return _resolve_high_bar_position(x_relative)
    return _resolve_standard_bar_position(x_relative)


def _resolve_high_bar_position(x_relative: float) -> tuple[int, int, str, str, str]:
    """Resolve tooltip placement for tall bars."""
    if x_relative > 0.8:  # noqa: PLR2004
        return (
            -120,
            -30,
            "right",
            "top",
            "🔽⬅️ DEBUG: Tooltip balra-lefelé - magas oszlop jobb szélen",
        )
    return 40, -50, "left", "top", "🔽 DEBUG: Tooltip lefelé - magas oszlop"


def _resolve_standard_bar_position(x_relative: float) -> tuple[int, int, str, str, str]:
    """Resolve tooltip placement for regular-height bars."""
    if x_relative > 0.8:  # noqa: PLR2004
        return (
            -120,
            30,
            "right",
            "bottom",
            "🔼⬅️ DEBUG: Tooltip balra-felfelé - jobb szélen",
        )
    return 40, 30, "left", "bottom", "🔼 DEBUG: Tooltip felfelé - oszlop felett"


def _show_tooltip(self, event, point_data: Dict[str, Any]) -> None:  # noqa: ARG001
    """
    💬 PRECIPITATION BAR CHART TOOLTIP POSITIONING

    🎨 BAR CHART SPECIFIC TOOLTIP:
    - Professional design
    - Precipitation-specific formatting
    - 🎯 BAR CHART POSITIONING: Above bars, smart edge detection

    Args:
        self: PrecipitationChart instance
        event: Matplotlib mouse event
        point_data: Point data dict
    """
    if not hasattr(self, "ax"):
        return

    # Előző tooltip törlése
    _hide_tooltip(self)

    # Tooltip szöveg formázása
    tooltip_text = _format_tooltip_text(self, point_data)

    # Koordináták meghatározása - BAR CHART SPECIFIC
    import matplotlib.dates as mdates

    x_pos = mdates.date2num(point_data["date"])
    y_pos = point_data["precipitation"]

    # 🎯 BAR CHART SMART POSITIONING
    offset_x, offset_y, ha_align, va_align, debug_message = _resolve_bar_tooltip_position(
        self, x_pos, y_pos
    )
    print(debug_message)

    # Current colors
    current_colors = get_current_colors()

    # 🌧️ PRECIPITATION THEMED TOOLTIP
    self.tooltip_annotation = self.ax.annotate(
        tooltip_text,
        xy=(x_pos, y_pos),
        xytext=(offset_x, offset_y),  # 🎯 DYNAMIC OFFSET
        textcoords="offset points",
        bbox={
            "boxstyle": "round,pad=1.0",
            "facecolor": "lightcyan",  # 🌧️ Precipitation theme
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

    Args:
        self: PrecipitationChart instance
    """
    if hasattr(self, "_tooltip_annotation") and self._tooltip_annotation:
        try:
            self._tooltip_annotation.remove()
        except Exception as e:
            print(f"⚠️ DEBUG: Precipitation tooltip remove error: {e}")

        self._tooltip_annotation = None
        self._tooltip_visible = False

        # Canvas frissítése
        if hasattr(self, "draw_idle"):
            self.draw_idle()
