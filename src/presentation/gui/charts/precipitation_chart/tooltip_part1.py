# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from tooltip.py."""

from __future__ import annotations

from .tooltip_support import *


def _get_mouse_chart_coordinates(event) -> tuple[float, float] | None:
    """Return mouse chart coordinates when available."""
    if event.xdata is None or event.ydata is None:
        return None
    return event.xdata, event.ydata


def _build_date_positions(bar_data: list[dict[str, Any]]) -> list[tuple[int, float]]:
    """Build date-number pairs for tooltip matching."""
    import matplotlib.dates as mdates

    return [
        (index, mdates.date2num(bar_info["date"]))
        for index, bar_info in enumerate(bar_data)
    ]


def _find_nearest_bar(
    mouse_x: float, date_positions: list[tuple[int, float]]
) -> tuple[int, float]:
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
    🎯 BAR CHART SPECIFIKUS PONT KERESÉS - TOOLTIP MIXIN OVERRIDE

    🔧 PRECIPITATION BAR CHART KOMPATIBILITÁS:
    - Bar objektumok hit detection
    - X koordináta alapú oszlop keresés
    - Professional precipitation tooltip adatok

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
        day_tolerance = 0.5  # Fél nap tolerance

        if min_distance > day_tolerance:
            return None

        bar_info = self.bar_data[closest_idx]
        return _build_precipitation_point(bar_info, closest_idx, min_distance)

    except Exception as e:
        print(f"⚠️ DEBUG: Precipitation point calculation error: {e}")

    return None
