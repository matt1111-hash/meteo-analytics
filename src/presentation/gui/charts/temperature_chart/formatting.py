#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

        # Cím és címkék
        self.ax.set_title(
            self.chart_title,
            fontweight="bold",
            pad=25,
            fontsize=18,
            color=current_colors.get("on_surface", "#1f2937"),
        )
        self.ax.set_xlabel(
            self.x_label,
            fontsize=14,
            fontweight="500",
            color=current_colors.get("on_surface", "#1f2937"),
        )
        self.ax.set_ylabel(
            self.y_label,
            fontsize=14,
            fontweight="500",
            color=current_colors.get("on_surface", "#1f2937"),
        )

        # Dátum formázás - INTELLIGENS
        total_days = len(df)
        if total_days <= 31:  # Egy hónap vagy kevesebb
            self.ax.xaxis.set_major_locator(
                DayLocator(interval=max(1, total_days // 10))
            )
            self.ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
        else:  # Több hónap
            self.ax.xaxis.set_major_locator(MonthLocator())
            self.ax.xaxis.set_major_formatter(DateFormatter("%Y-%m"))

        # Y tengely formázás - INTELLIGENS TARTOMÁNY
        temp_min = df["temp_min"].min()
        temp_max = df["temp_max"].max()
        temp_range = temp_max - temp_min
        padding = max(2, temp_range * 0.1)  # 10% padding vagy minimum 2°C

        self.ax.set_ylim(temp_min - padding, temp_max + padding)
        self.ax.yaxis.set_major_locator(plt.MaxNLocator(10))

        # Grid és legend - PROFESSZIONÁLIS + KRITIKUS JAVÍTÁS + SIMPLIFIED THEMEMANAGER SZÍNEK
        if self.grid_enabled:
            grid_color = current_colors.get("border", "#d1d5db")
            grid_alpha = (
                0.3 if self.theme_manager.get_current_theme() == "light" else 0.2
            )
            self.ax.grid(
                True, alpha=grid_alpha, linestyle="-", linewidth=0.8, color=grid_color
            )
            self.ax.set_axisbelow(True)  # Grid a háttérben

        if self.legend_enabled:
            # 🎯 KRITIKUS JAVÍTÁS: Legend kívülre helyezése chart területen kívülre
            # bbox_to_anchor=(1.05, 1) - jobb oldalra, felső szélhez igazítva
            # ncol=1 - egy oszlop a jobb áttekinthetőségért
            legend = self.ax.legend(
                bbox_to_anchor=(1.05, 1),
                loc="upper left",
                framealpha=0.95,
                fancybox=True,
                shadow=True,
                ncol=1,
                fontsize=11,
            )

            # 🎨 LEGEND SZÍNEK SIMPLIFIED THEMEMANAGER-REL
            legend.get_frame().set_facecolor(current_colors.get("surface", "#ffffff"))
            legend.get_frame().set_edgecolor(current_colors.get("border", "#d1d5db"))

            print(
                "🎯 DEBUG: Legend pozíció javítva - kívülre helyezve (1.05, 1) + SimplifiedThemeManager színek"
            )

        # Layout optimalizálás - EXTRA HELY A LEGEND-NEK
        # bbox_inches='tight' automatikusan alkalmazkodik a kívülre helyezett legend-hez
        self.figure.tight_layout(
            rect=[0, 0, 0.85, 1]
        )  # 85%-ig a figure, 15% a legend-nek

        print(
            "✅ DEBUG: Enhanced temperature chart formázva - LEGEND NEM FEDI EL A TARTALMAT + SIMPLIFIED THEMEMANAGER + TOOLTIP READY"
        )
