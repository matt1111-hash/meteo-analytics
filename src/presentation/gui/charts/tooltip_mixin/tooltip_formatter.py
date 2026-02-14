#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WeatherTooltipMixin Tooltip Formatter - Format tooltip text.
"""

import datetime
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from .core import WeatherTooltipMixin


class TooltipFormatter:
    """Format tooltip text for different chart types."""

    def __init__(self, mixin: "WeatherTooltipMixin"):
        """
        Initialize tooltip formatter.

        Args:
            mixin: WeatherTooltipMixin instance
        """
        self._mixin = mixin

    def format(self, point_data: Dict[str, Any]) -> str:
        """
        Format tooltip text based on chart type.

        Args:
            point_data: Point data dictionary

        Returns:
            Formatted tooltip text
        """
        # Temperature chart specific
        if "primary_temp" in point_data:
            return self._format_temperature(point_data)
        else:
            # Generic for other charts
            return self._format_generic(point_data)

    def _format_temperature(self, point_data: Dict[str, Any]) -> str:
        """
        Format temperature chart tooltip.

        Args:
            point_data: Point data dictionary

        Returns:
            Formatted tooltip text
        """
        date = point_data["date"]
        primary_temp = point_data["primary_temp"]

        # Date formatting
        if isinstance(date, datetime.date):
            date_str = date.strftime("%Y-%m-%d (%A)")
        else:
            date_str = str(date)

        # Temperature category and icon
        if primary_temp > 30:
            temp_icon = "🔥"
            category = "Forró nap"
        elif primary_temp < 0:
            temp_icon = "❄️"
            category = "Fagyos nap"
        elif primary_temp < 10:
            temp_icon = "🧊"
            category = "Hideg nap"
        elif primary_temp > 25:
            temp_icon = "☀️"
            category = "Meleg nap"
        else:
            temp_icon = "🌡️"
            category = "Mérsékelt nap"

        # Base tooltip text
        tooltip_lines = [
            f"📅 {date_str}",
            f"{temp_icon} {point_data['primary_temp_column'].replace('temp_', '').replace('_', ' ').title()}: {primary_temp:.1f}°C",
        ]

        # Add additional temperature columns
        for key, value in point_data.items():
            if key.startswith("temp_") and key != point_data["primary_temp_column"]:
                column_name = key.replace("temp_", "").replace("_", " ").title()
                tooltip_lines.append(f"🌡️ {column_name}: {value:.1f}°C")

        # Add category
        tooltip_lines.extend(["", f"🏷️ {category}"])

        return "\n".join(tooltip_lines)

    def _format_generic(self, point_data: Dict[str, Any]) -> str:
        """
        Format generic tooltip for other chart types.

        Args:
            point_data: Point data dictionary

        Returns:
            Formatted tooltip text
        """
        tooltip_lines = []

        # Add date if available
        if "date" in point_data:
            date = point_data["date"]
            if isinstance(date, datetime.date):
                date_str = date.strftime("%Y-%m-%d (%A)")
            else:
                date_str = str(date)
            tooltip_lines.append(f"📅 {date_str}")

        # Add value if available
        if "value" in point_data:
            parameter = point_data.get("parameter", "Ismeretlen")
            value = point_data["value"]

            # Icon and unit based on parameter
            if "temperature" in parameter:
                icon = "🌡️"
                unit = "°C"
            elif "precipitation" in parameter:
                icon = "🌧️"
                unit = "mm"
            elif "wind" in parameter:
                icon = "💨"
                unit = "km/h"
            else:
                icon = "📊"
                unit = ""

            tooltip_lines.append(f"{icon} Érték: {value:.1f} {unit}")
            tooltip_lines.append(f"📋 Parameter: {parameter}")

        # Fallback: show all key-value pairs
        if not tooltip_lines:
            for key, value in point_data.items():
                if key not in ["index", "pixel_distance"]:
                    tooltip_lines.append(f"{key}: {value}")

        return "\n".join(tooltip_lines) if tooltip_lines else "📊 Chart adat"

    def log_detailed_info(self, point_data: Dict[str, Any]) -> None:
        """Log detailed point info for debugging."""
        print("\n" + "=" * 60)
        print("🎯 TOOLTIP CLICK - RÉSZLETES ADATOK")
        print("=" * 60)

        for key, value in point_data.items():
            if key == "date":
                print(f"📅 Dátum: {value}")
            elif key in ["primary_temp", "value"]:
                print(f"📊 Fő érték ({key}): {value:.1f}")
            elif key.startswith("temp_"):
                print(f"🌡️ {key}: {value:.1f}°C")
            elif key == "parameter":
                print(f"📋 Parameter: {value}")
            elif key == "pixel_distance":
                print(f"🎯 Pixel távolság: {value:.1f}px")
            elif key == "index":
                print(f"📊 Index: {value}")
            else:
                print(f"🔧 {key}: {value}")

        print("=" * 60 + "\n")
