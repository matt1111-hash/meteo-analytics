#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


def _plot_precipitation(self, df) -> None:
    """
    Csapadék grafikon rajzolása - DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER.
    🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ: ColorPalette precipitation színek használata

    Args:
        self: PrecipitationChart instance
        df: DataFrame with precipitation data
    """
    from .formatting import _format_precipitation_chart

    print(
        "🎨 DEBUG: _plot_precipitation() - DUPLIKÁCIÓ MENTES + SIMPLIFIED THEMEMANAGER"
    )

    # 🔧 KRITIKUS JAVÍTÁS: HELYES API HASZNÁLAT - csapadék színek
    precip_colors = {
        "none": self.color_palette.get_color("surface_variant", "base") or "#f3f4f6",
        "light": self.color_palette.get_color("info", "light") or "#93c5fd",
        "moderate": self.color_palette.get_color("info", "base") or "#3b82f6",
        "heavy": self.color_palette.get_color("info", "dark") or "#1e40af",
    }

    # Weather színpaletta integrálása
    weather_precip_color = self.weather_colors.get("precipitation", "#3b82f6")
    precip_colors["moderate"] = weather_precip_color

    current_colors = get_current_colors()

    print(
        f"🎨 DEBUG: Using SimplifiedThemeManager precipitation colors: {precip_colors}"
    )

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
    for i, (date, precip) in enumerate(zip(df["date"], df["precipitation"])):
        # Bar-hoz tartozó adat tárolása
        self.bar_data.append(
            {"index": i, "date": date, "precipitation": precip, "bar": self.bars[i]}
        )

        if precip > 20:  # Erős csapadék
            self.bars[i].set_color(precip_colors["heavy"])
        elif precip > 10:  # Közepes csapadék
            self.bars[i].set_color(precip_colors["moderate"])
        elif precip > 1:  # Gyenge csapadék
            self.bars[i].set_color(precip_colors["light"])
        else:  # Száraz
            self.bars[i].set_color(precip_colors["none"])

    # Formázás
    _format_precipitation_chart(self, df)
