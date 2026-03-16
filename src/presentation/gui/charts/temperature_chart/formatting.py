#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Temperature Chart - Formatting

📐 Chart formázás és formátum beállítások

Képességek:
- Tengely formázás
- Legend pozicionálás
- Dátum formázás
- Layout optimalizálás

Fájl: src/presentation/gui/charts/temperature_chart/formatting.py
"""

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, DayLocator, MonthLocator

from ...theme_manager import get_current_colors

if TYPE_CHECKING:
    import pandas as pd


def _format_chart_titles(chart, current_colors: dict[str, str]) -> None:
    """Apply title and axis labels to temperature chart."""
    chart.ax.set_title(
        chart.chart_title,
        fontweight="bold",
        pad=25,
        fontsize=18,
        color=current_colors.get("on_surface", "#1f2937"),
    )
    chart.ax.set_xlabel(
        chart.x_label,
        fontsize=14,
        fontweight="500",
        color=current_colors.get("on_surface", "#1f2937"),
    )
    chart.ax.set_ylabel(
        chart.y_label,
        fontsize=14,
        fontweight="500",
        color=current_colors.get("on_surface", "#1f2937"),
    )


def _format_temperature_dates(chart, df: "pd.DataFrame") -> None:
    """Apply smart date locator/formatter selection."""
    total_days = len(df)
    if total_days <= 31:
        chart.ax.xaxis.set_major_locator(DayLocator(interval=max(1, total_days // 10)))
        chart.ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
        return
    chart.ax.xaxis.set_major_locator(MonthLocator())
    chart.ax.xaxis.set_major_formatter(DateFormatter("%Y-%m"))


def _format_temperature_y_axis(chart, df: "pd.DataFrame") -> None:
    """Apply dynamic y-axis range for temperature chart."""
    temp_min = df["temp_min"].min()
    temp_max = df["temp_max"].max()
    temp_range = temp_max - temp_min
    padding = max(2, temp_range * 0.1)
    chart.ax.set_ylim(temp_min - padding, temp_max + padding)
    chart.ax.yaxis.set_major_locator(plt.MaxNLocator(10))


def _apply_temperature_grid(chart, current_colors: dict[str, str]) -> None:
    """Apply themed grid when enabled."""
    if not chart.grid_enabled:
        return
    grid_color = current_colors.get("border", "#d1d5db")
    grid_alpha = 0.3 if chart.theme_manager.get_current_theme() == "light" else 0.2
    chart.ax.grid(
        True, alpha=grid_alpha, linestyle="-", linewidth=0.8, color=grid_color
    )
    chart.ax.set_axisbelow(True)


def _apply_temperature_legend(chart, current_colors: dict[str, str]) -> None:
    """Apply themed external legend when enabled."""
    if not chart.legend_enabled:
        return
    legend = chart.ax.legend(
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
        framealpha=0.95,
        fancybox=True,
        shadow=True,
        ncol=1,
        fontsize=11,
    )
    legend.get_frame().set_facecolor(current_colors.get("surface", "#ffffff"))
    legend.get_frame().set_edgecolor(current_colors.get("border", "#d1d5db"))
    print(
        "🎯 DEBUG: Legend pozíció javítva - kívülre helyezve (1.05, 1) + SimplifiedThemeManager színek"
    )


class TemperatureFormattingMixin:
    """
    📐 Chart formázás keverék osztály.
    """

    def _format_enhanced_temperature_chart(self, df: "pd.DataFrame") -> None:
        """
        Fejlett hőmérséklet chart formázása - PROFESSZIONÁLIS STÍLUS + LEGEND POZÍCIÓ JAVÍTVA + SIMPLIFIED THEMEMANAGER.
        🎯 KRITIKUS JAVÍTÁS: Legend kívülre helyezése, hogy ne fedje el a diagramtartalmat
        🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ: Színek és formázás a centralizált rendszerből
        """
        # 🔧 AKTUÁLIS TÉMA SZÍNEK
        current_colors = get_current_colors()

        _format_chart_titles(self, current_colors)
        _format_temperature_dates(self, df)
        _format_temperature_y_axis(self, df)
        _apply_temperature_grid(self, current_colors)
        _apply_temperature_legend(self, current_colors)
        self.figure.tight_layout(rect=[0, 0, 0.85, 1])

        print(
            "✅ DEBUG: Enhanced temperature chart formázva - LEGEND NEM FEDI EL A TARTALMAT + SIMPLIFIED THEMEMANAGER + TOOLTIP READY"
        )
