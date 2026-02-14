#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wind Chart Tooltip Handlers - Tooltip formatting and positioning.
🎯 WIND CHART SPECIFIKUS TOOLTIP: Magyar szélkategóriák és Beaufort skála
"""

from datetime import datetime
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from src.presentation.gui.theme_manager import get_current_colors

from .wind_categories import get_wind_category, get_wind_recommendations


class WindTooltipHandler:
    """
    Handle tooltip display for wind chart.

    💨 PROFESSIONAL WIND TOOLTIP:
    - Magyar szélkategóriák és Beaufort skála
    - Széljárás leírások
    - Meteorológiai hatások
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

    def find_closest_point(self, event, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
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

            import matplotlib.dates as mdates

            plot_dates = mdates.date2num(df["date"])
            windspeeds = df["windspeed"]

            # Mouse position in display coordinates
            mouse_x_display, mouse_y_display = self.ax.transData.transform(
                (event.xdata, event.ydata)
            )

            closest_idx = None
            min_distance = float("inf")

            # Find closest point
            for i, (x_val, y_val) in enumerate(zip(plot_dates, windspeeds)):
                if pd.isna(y_val):
                    continue

                point_x_display, point_y_display = self.ax.transData.transform(
                    (x_val, y_val)
                )

                # Pixel distance
                distance = np.sqrt(
                    (mouse_x_display - point_x_display) ** 2
                    + (mouse_y_display - point_y_display) ** 2
                )

                if distance < min_distance:
                    min_distance = distance
                    closest_idx = i

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
            print(f"⚠️ DEBUG: Wind point calculation error: {e}")

        return None

    def format_tooltip_text(self, point_data: Dict[str, Any]) -> str:
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
            "Széllökések"
            if data_source == "wind_gusts_10m_max"
            else "Szélsebesség (átlag)"
        )

        # Build tooltip lines
        tooltip_lines = [
            f"📅 {date_str}",
            "",
            f"{category['icon']} {measurement_type}: {windspeed:.1f} km/h",
            f"🏷️ {category['name']}",
            f"📊 Beaufort skála: {category['beaufort']}",
            f"🌬️ {category['description']}",
            "",
            f"📈 Intenzitás: {category['intensity']}",
            category["effects"],
        ]

        # Add recommendations
        if recommendations:
            tooltip_lines.append("")
            tooltip_lines.extend(recommendations)

        # Fallback indicator
        if data_source == "windspeed_10m_max":
            tooltip_lines.extend(["", "ℹ️ Fallback adatforrás (átlag szélsebesség)"])

        return "\n".join(tooltip_lines)

    def show_tooltip(
        self, event, point_data: Dict[str, Any], draw_idle_callback
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
        import matplotlib.dates as mdates

        x_pos = mdates.date2num(point_data["date"])
        y_pos = point_data["windspeed"]

        # Smart positioning
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        x_relative = (x_pos - xlim[0]) / (xlim[1] - xlim[0])
        y_relative = (y_pos - ylim[0]) / (ylim[1] - ylim[0])

        # Dynamic offset calculation
        if y_relative > 0.7:
            offset_y = -80
            va_align = "top"
        else:
            offset_y = 50
            va_align = "bottom"

        if x_relative > 0.8:
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
            bbox=dict(
                boxstyle="round,pad=1.0",
                facecolor="lightblue",
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
