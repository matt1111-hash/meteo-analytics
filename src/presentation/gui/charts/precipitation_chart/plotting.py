#!/usr/bin/env python3
# mypy: ignore-errors

"""
Precipitation Chart - Plotting

📈 Chart rajzolás

Képességek:
- Csapadék grafikon rajzolása
- Színkódolás

Fájl: src/presentation/gui/charts/precipitation_chart/plotting.py
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from src.presentation.gui.theme_manager import get_current_colors


def _build_precipitation_colors(chart) -> dict[str, str]:
    """Build precipitation palette colors from theme sources."""
    precip_colors = {
        "none": chart.color_palette.get_color("surface_variant", "base") or "#f3f4f6",
        "light": chart.color_palette.get_color("info", "light") or "#93c5fd",
        "moderate": chart.color_palette.get_color("info", "base") or "#3b82f6",
        "heavy": chart.color_palette.get_color("info", "dark") or "#1e40af",
    }
    precip_colors["moderate"] = chart.weather_colors.get("precipitation", "#3b82f6")
    return precip_colors


def _resolve_bar_color(precipitation: float, precip_colors: dict[str, str]) -> str:
    """Resolve bar color based on precipitation amount."""
    if precipitation > 20:  # noqa: PLR2004
        return precip_colors["heavy"]
    if precipitation > 10:  # noqa: PLR2004
        return precip_colors["moderate"]
    if precipitation > 1:
        return precip_colors["light"]
    return precip_colors["none"]


def _store_bar_data(chart, index: int, date, precipitation: float) -> None:
    """Store bar metadata for tooltip handling."""
    chart.bar_data.append(
        {
            "index": index,
            "date": date,
            "precipitation": precipitation,
            "bar": chart.bars[index],
        }
    )


def _plot_precipitation(self, df) -> None:
    """
    Csapadék grafikon rajzolása - DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER.
    🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ: ColorPalette precipitation színek használata

    Args:
        self: PrecipitationChart instance
        df: DataFrame with precipitation data
    """
    from .formatting import _format_precipitation_chart

    print("🎨 DEBUG: _plot_precipitation() - DUPLIKÁCIÓ MENTES + SIMPLIFIED THEMEMANAGER")

    # 🔧 KRITIKUS JAVÍTÁS: HELYES API HASZNÁLAT - csapadék színek
    precip_colors = _build_precipitation_colors(self)
    current_colors = get_current_colors()

    print(f"🎨 DEBUG: Using SimplifiedThemeManager precipitation colors: {precip_colors}")

    # Oszlopdiagram alapszín
    self.bars = self.ax.bar(
        df["date"],
        df["precipitation"],
        color=precip_colors["moderate"],
        alpha=0.7,
        edgecolor=current_colors.get("border", "#d1d5db"),
        linewidth=0.5,
    )

    # 🎯 TOOLTIP TRACKING: Bar objektumok tárolása
    self.bar_data = []  # Bar-hoz tartozó adatok tooltip-hoz

    # Színkódolás csapadék mennyiség alapján + SIMPLIFIED THEMEMANAGER
    for i, (date, precip) in enumerate(zip(df["date"], df["precipitation"], strict=False)):
        _store_bar_data(self, i, date, precip)
        self.bars[i].set_color(_resolve_bar_color(precip, precip_colors))

    # Formázás
    _format_precipitation_chart(self, df)
