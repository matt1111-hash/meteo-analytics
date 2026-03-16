# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for TemperatureTooltipHandlerMixin."""

from __future__ import annotations

from .tooltip_handler_support import *


class TemperatureTooltipHandlerMixinPart2Mixin:
    @staticmethod
    def _format_date_label(date: Any) -> str:
        """Format tooltip date label."""
        if isinstance(date, datetime):
            return date.strftime("%Y-%m-%d (%A)")
        return str(date)

    @staticmethod
    def _categorize_temperature(primary_temp: float) -> str:
        """Categorize temperature value for tooltip."""
        if primary_temp > 35:
            return "Extrém forró"
        if primary_temp > 30:
            return "Forró nap"
        if primary_temp > 25:
            return "Meleg nap"
        if primary_temp > 15:
            return "Mérsékelt nap"
        if primary_temp > 0:
            return "Hideg nap"
        if primary_temp > -10:
            return "Fagyos nap"
        return "Extrém hideg"

    @staticmethod
    def _build_temperature_lines(
        point_data: Dict[str, Any], closest_line: str
    ) -> list[str]:
        """Build tooltip lines for temperature values."""
        line_names = {
            "temp_max": "Maximum",
            "temp_min": "Minimum",
            "temp_mean": "Átlag",
        }
        line_icons = {"temp_max": "🔺", "temp_min": "🔻", "temp_mean": "🎯"}
        lines: list[str] = []
        if closest_line in point_data:
            lines.append(
                f"➤ {line_icons.get(closest_line, '🌡️')} {line_names.get(closest_line, closest_line)}: "
                f"{point_data[closest_line]:.1f}°C ← HOVER"
            )
        for column in ["temp_max", "temp_min", "temp_mean"]:
            if column in point_data and column != closest_line:
                lines.append(
                    f"  {line_icons.get(column, '🌡️')} {line_names.get(column, column)}: "
                    f"{point_data[column]:.1f}°C"
                )
        return lines

    def _format_tooltip_text(self, point_data: Dict[str, Any]) -> str:
        """
        📝 ENHANCED MULTI-LINE TOOLTIP FORMÁZÁS

        🌡️ INTELLIGENT TOOLTIP:
        - Kiemeli a legközelebbi vonalat (closest_line)
        - Összes hőmérséklet adat megjelenítése
        - Magyar weather ikonok és kategóriák
        - Professional formatting
        """
        date = point_data["date"]
        primary_temp = point_data["primary_temp"]
        closest_line = point_data.get("closest_line", "temp_mean")
        date_str = self._format_date_label(date)
        category = self._categorize_temperature(primary_temp)
        tooltip_lines = [
            f"📅 {date_str}",
            "",
        ]
        tooltip_lines.extend(self._build_temperature_lines(point_data, closest_line))

        if "temp_max" in point_data and "temp_min" in point_data:
            temp_range = point_data["temp_max"] - point_data["temp_min"]
            tooltip_lines.append(f"📊 Napi hőingás: {temp_range:.1f}°C")

        tooltip_lines.extend(["", f"🏷️ {category}"])
        return "\n".join(tooltip_lines)
