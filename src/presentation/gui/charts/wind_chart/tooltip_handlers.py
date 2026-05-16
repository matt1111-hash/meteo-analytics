# mypy: ignore-errors
"""Wind Chart Tooltip Handlers - Tooltip formatting and positioning."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from src.presentation.gui.theme_manager import get_current_colors

from .wind_categories import get_wind_category, get_wind_recommendations


class WindTooltipHandler:
    """
    Handle tooltip display for wind chart.

    WIND TOOLTIP:
    - Magyar szelkategoriak es Beaufort skala
    - Szeljaras leirasok
    - Meteorologiai hatasok
    - Smart positioning
    """

    def __init__(self, ax, hover_tolerance: int = 15):
        """
        Initialize tooltip handler.

        Args:
            ax: Matplotlib axes
            hover_tolerance: Pixel distance tolerance for hover detection
        """
        self.ax = ax
        self._hover_tolerance = hover_tolerance
        self._tooltip_annotation = None
        self._tooltip_visible = False

    def find_closest_point(self, event, df: pd.DataFrame) -> dict[str, Any] | None:
        """
        Find closest data point to mouse event.

        Args:
            event: Mouse event
            df: Current data DataFrame

        Returns:
            Point data dictionary or None
        """
        try:
            if df is None or df.empty:
                return None

            if "date" not in df.columns or "windspeed" not in df.columns:
                return None

            import matplotlib.dates as mdates  # noqa: PLC0415

            plot_dates = mdates.date2num(df["date"])
            windspeeds = df["windspeed"]
            mouse_coords = self.ax.transData.transform((event.xdata, event.ydata))
            closest_idx, min_distance = self._find_closest_index(
                plot_dates, windspeeds, mouse_coords
            )

            # Tolerance check
            if closest_idx is not None and min_distance <= self._hover_tolerance:
                point_data = {
                    "index": closest_idx,
                    "date": df.iloc[closest_idx]["date"],
                    "windspeed": df.iloc[closest_idx]["windspeed"],
                    "pixel_distance": min_distance,
                    "data_source": df.iloc[closest_idx]["_data_source"]
                    if "_data_source" in df.columns
                    else "unknown",
                }
                return point_data

        except Exception as e:
            print(f"DEBUG: Wind point calculation error: {e}")

        return None

    def _find_closest_index(
        self, plot_dates: Any, windspeeds: Any, mouse_coords: tuple[float, float]
    ) -> tuple[int | None, float]:
        """Find closest visible wind point."""
        mouse_x_display, mouse_y_display = mouse_coords
        closest_idx: int | None = None
        min_distance = float("inf")
        for index, (x_val, y_val) in enumerate(zip(plot_dates, windspeeds, strict=False)):
            if pd.isna(y_val):
                continue
            point_x_display, point_y_display = self.ax.transData.transform((x_val, y_val))
            distance = np.sqrt(
                (mouse_x_display - point_x_display) ** 2 + (mouse_y_display - point_y_display) ** 2
            )
            if distance < min_distance:
                min_distance = distance
                closest_idx = index
        return closest_idx, min_distance

    def format_tooltip_text(self, point_data: dict[str, Any]) -> str:
        """
        Format tooltip text for wind data.

        Args:
            point_data: Point data dictionary

        Returns:
            Formatted tooltip text
        """
        date = point_data["date"]
        windspeed = point_data["windspeed"]
        data_source = point_data.get("data_source", "unknown")

        # Date formatting
        if isinstance(date, datetime):
            date_str = date.strftime("%Y-%m-%d (%A)")
        else:
            date_str = str(date)

        # Get wind category
        category = get_wind_category(windspeed)
        recommendations = get_wind_recommendations(windspeed)

        # Measurement type
        measurement_type = (
            "Szellokesek" if data_source == "wind_gusts_10m_max" else "Szelsebesseg (atlag)"
        )

        # Build tooltip lines
        tooltip_lines = [
            f"{date_str}",
            "",
            f"{category['icon']} {measurement_type}: {windspeed:.1f} km/h",
            f"{category['name']}",
            f"Beaufort skala: {category['beaufort']}",
            f"{category['description']}",
            "",
            f"Intenzitas: {category['intensity']}",
            category["effects"],
        ]

        # Add recommendations
        if recommendations:
            tooltip_lines.append("")
            tooltip_lines.extend(recommendations)

        # Fallback indicator
        if data_source == "windspeed_10m_max":
            tooltip_lines.extend(["", "Fallback adatforras (atlag szelsebesseg)"])

        return "\n".join(tooltip_lines)

    def show_tooltip(
        self,
        event,  # noqa: ARG002
        point_data: dict[str, Any],
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
                print(f"DEBUG: Wind tooltip remove error: {e}")

            self._tooltip_annotation = None
            self._tooltip_visible = False

            if draw_idle_callback:
                draw_idle_callback()
