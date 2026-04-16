# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Merged part1+part2 definitions from tooltip.py."""

from __future__ import annotations

from .tooltip_support import *


def _get_mouse_chart_coordinates(event) -> tuple[float, float] | None:
    """Return mouse chart coordinates when available."""
    if event.xdata is None or event.ydata is None:
        return None
    return event.xdata, event.ydata


def _build_date_positions(bar_data: list[dict[str, Any]]) -> list[tuple[int, float]]:
    """Build date-number pairs for tooltip matching."""
    import matplotlib.dates as mdates  # noqa: PLC0415

    return [(index, mdates.date2num(bar_info["date"])) for index, bar_info in enumerate(bar_data)]


def _find_nearest_bar(mouse_x: float, date_positions: list[tuple[int, float]]) -> tuple[int, float]:
    """Find the nearest precipitation bar."""
    return min(
        ((index, abs(mouse_x - position)) for index, position in date_positions),
        key=lambda item: item[1],
    )


def _build_precipitation_point(
    bar_info: dict[str, Any], index: int, distance: float
) -> dict[str, Any]:
    """Build tooltip payload for a precipitation bar."""
    return {
        "index": index,
        "date": bar_info["date"],
        "precipitation": bar_info["precipitation"],
        "primary_temp": bar_info["precipitation"],
        "primary_temp_column": "precipitation",
        "pixel_distance": distance,
        "chart_type": "precipitation_bar",
    }


def _find_closest_chart_point(self, event) -> Optional[Dict[str, Any]]:
    """
    Bar chart specific point search - tooltip mixin override.

    Precipitation bar chart compatibility:
    - Bar objects hit detection
    - X coordinate based column search
    - Professional precipitation tooltip data

    Args:
        self: PrecipitationChart instance
        event: Matplotlib mouse event

    Returns:
        Dict with point data or None
    """
    try:
        if (
            not hasattr(self, "current_data")
            or self.current_data is None
            or self.current_data.empty
        ):
            return None

        if not hasattr(self, "bar_data") or not self.bar_data:
            return None

        coordinates = _get_mouse_chart_coordinates(event)
        if coordinates is None:
            return None

        mouse_x, _mouse_y = coordinates
        date_positions = _build_date_positions(self.bar_data)
        closest_idx, min_distance = _find_nearest_bar(mouse_x, date_positions)
        day_tolerance = 0.5

        if min_distance > day_tolerance:
            return None

        bar_info = self.bar_data[closest_idx]
        return _build_precipitation_point(bar_info, closest_idx, min_distance)

    except Exception as e:
        print(f"⚠️ DEBUG: Precipitation point calculation error: {e}")

    return None


PRECIPITATION_CATEGORIES = (
    (50, ("⛈️", "Viharos zápor", "Rendkívül erős")),
    (20, ("🌧️", "Erős esőzés", "Erős")),
    (10, ("🌦️", "Közepes esőzés", "Mérsékelt")),
    (5, ("🌤️", "Gyenge esőzés", "Gyenge")),
    (1, ("💧", "Szitálás", "Nagyon gyenge")),
    (0.1, ("💦", "Harmat/köd", "Minimális")),
)

METEOROLOGICAL_NOTES = (
    (25, "⚠️ Árvízveszély lehetséges"),
    (15, "🚗 Közlekedési nehézségek"),
    (10, "☂️ Esernyő szükséges"),
    (1, "🌱 Jó a növényeknek"),
)


def _format_tooltip_text(self, point_data: Dict[str, Any]) -> str:
    """
    Precipitation chart tooltip formatting.

    Professional precipitation tooltip:
    - Precipitation amount and category
    - Meteorological characteristics
    - Intensity categories
    """
    date = point_data["date"]
    precipitation = point_data["precipitation"]

    date_str = date.strftime("%Y-%m-%d (%A)") if isinstance(date, datetime) else str(date)
    precip_icon, category, intensity = _categorize_precipitation(precipitation)
    meteorological_info = _build_meteorological_info(precipitation)
    contextual_info = _build_precipitation_context(self, precipitation)
    tooltip_lines = [
        f"📅 {date_str}",
        "",
        f"{precip_icon} Csapadék: {precipitation:.1f} mm",
        f"🏷️ {category}",
        f"📊 Intenzitás: {intensity}",
    ]

    if meteorological_info:
        tooltip_lines.append("")
        tooltip_lines.extend(meteorological_info)

    if contextual_info:
        tooltip_lines.append("")
        tooltip_lines.extend(contextual_info)

    return "\n".join(tooltip_lines)


def _categorize_precipitation(precipitation: float) -> tuple[str, str, str]:
    """Categorize precipitation intensity and icon."""
    for threshold, category in PRECIPITATION_CATEGORIES:
        if precipitation > threshold:
            return category
    return "☀️", "Száraz nap", "Nincs csapadék"


def _build_meteorological_info(precipitation: float) -> list[str]:
    """Build meteorological notes for precipitation amount."""
    for threshold, note in METEOROLOGICAL_NOTES:
        if precipitation > threshold:
            return [note]
    return []


def _build_precipitation_context(self, precipitation: float) -> list[str]:
    """Build contextual comparison against mean precipitation."""
    if not hasattr(self, "current_data") or self.current_data.empty:
        return []
    avg_precip = self.current_data["precipitation"].mean()
    if precipitation > avg_precip * 2:
        return [f"📈 Átlag feletti ({avg_precip:.1f} mm)"]
    if precipitation < avg_precip * 0.5:
        return [f"📉 Átlag alatti ({avg_precip:.1f} mm)"]
    return [f"📊 Átlagos tartomány ({avg_precip:.1f} mm)"]
