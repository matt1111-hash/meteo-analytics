#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Precipitation Chart - Formatting

🎨 Chart formázás

Képességek:
- Chart formázás
- Statisztikai információk

Fájl: src/presentation/gui/charts/precipitation_chart/formatting.py
"""

from typing import TYPE_CHECKING

from matplotlib.dates import DateFormatter, MonthLocator

if TYPE_CHECKING:
    pass

from src.presentation.gui.theme_manager import get_current_colors


def _format_precipitation_chart(self, df) -> None:
    """
    Csapadék chart formázása + SIMPLIFIED THEMEMANAGER.

    Args:
        self: PrecipitationChart instance
        df: DataFrame with precipitation data
    """
    # 🔧 SIMPLIFIED THEMEMANAGER SZÍNEK
    current_colors = get_current_colors()
    text_color = current_colors.get("on_surface", "#1f2937")

    self.ax.set_title(self.chart_title, fontweight="bold", pad=20, color=text_color)
    self.ax.set_xlabel(self.x_label, color=text_color)
    self.ax.set_ylabel(self.y_label, color=text_color)

    # Tick színek
    self.ax.tick_params(colors=text_color)

    # Dátum formázás
    self.ax.xaxis.set_major_locator(MonthLocator())
    self.ax.xaxis.set_major_formatter(DateFormatter("%Y-%m"))

    # Y tengely formázás
    max_precip = df["precipitation"].max() if not df.empty else 50
    self.ax.set_ylim(0, max_precip * 1.1)

    # Grid + SIMPLIFIED THEMEMANAGER
    if self.grid_enabled:
        grid_color = current_colors.get("border", "#d1d5db")
        grid_alpha = 0.3 if self.theme_manager.get_current_theme() == "light" else 0.2
        self.ax.grid(
            True,
            alpha=grid_alpha,
            axis="y",
            linestyle="-",
            linewidth=0.5,
            color=grid_color,
        )

    # Statisztika szöveg hozzáadása + SIMPLIFIED THEMEMANAGER
    total_precip = df["precipitation"].sum()
    avg_precip = df["precipitation"].mean()
    self.ax.text(
        0.02,
        0.98,
        f"Összesen: {total_precip:.1f} mm\nÁtlag: {avg_precip:.1f} mm/nap",
        transform=self.ax.transAxes,
        verticalalignment="top",
        color=text_color,
        bbox=dict(
            boxstyle="round",
            facecolor=current_colors.get("surface_variant", "#f9fafb"),
            edgecolor=current_colors.get("border", "#d1d5db"),
            alpha=0.8,
        ),
    )

    # Layout optimalizálás
    self.figure.autofmt_xdate()
    self.figure.tight_layout()

    print("✅ DEBUG: Precipitation chart formázva + TOOLTIP READY")
