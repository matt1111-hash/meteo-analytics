#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Heatmap Chart - Axes Formatter

📐 Tengelyek és címkék beállítása

Képességek:
- X tengely (hónapok)
- Y tengely (hétköznapok)
- Magyar lokalizáció

Fájl: src/presentation/gui/charts/heatmap_chart/axes_formatter.py
"""

import logging
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from ...theme_manager import get_current_colors

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def setup_axes_and_labels(self, min_date: pd.Timestamp, max_date: pd.Timestamp) -> None:
    """
    Setup axes VALÓDI DÁTUMOKKAL.

    Args:
        self: HeatmapCalendarChart instance
        min_date: Minimális dátum
        max_date: Maximális dátum
    """
    current_colors = get_current_colors()
    text_color = current_colors.get("on_surface", "#1f2937")

    total_days = (max_date - min_date).days + 1

    # X TENGELY - VALÓDI HÓNAPOK A VALÓDI POZÍCIÓBAN
    x_ticks = []
    x_labels = []

    # Végigmegyünk a heteken és keressük a hónap váltásokat
    seen_months = set()

    hungarian_months = [
        "",
        "Jan",
        "Feb",
        "Már",
        "Ápr",
        "Máj",
        "Jún",
        "Júl",
        "Aug",
        "Sze",
        "Okt",
        "Nov",
        "Dec",
    ]

    # 53 hét végigiterálása
    for week_idx in range(53):
        # Hét első napjának kiszámítása
        days_from_start = week_idx * 7 - self._first_day_weekday

        if days_from_start >= 0 and days_from_start < total_days:
            week_date = min_date + pd.Timedelta(days=days_from_start)
            month_key = (week_date.year, week_date.month)

            # Ha új hónap, jelöljük
            if month_key not in seen_months and week_idx % 4 == 0:  # Minden 4. héten
                seen_months.add(month_key)
                x_ticks.append(week_idx)

                month_name = hungarian_months[week_date.month]
                if week_date.year != min_date.year:
                    x_labels.append(f"{month_name}\n{week_date.year}")
                else:
                    x_labels.append(month_name)

    # Ha túl kevés címke, alapértelmezett
    if len(x_ticks) < 3:
        x_ticks = np.arange(6, 53, 8)
        x_labels = []
        for week_idx in x_ticks:
            days_from_start = week_idx * 7 - self._first_day_weekday
            if days_from_start >= 0 and days_from_start < total_days:
                week_date = min_date + pd.Timedelta(days=days_from_start)
                month_name = hungarian_months[week_date.month]
                x_labels.append(month_name)
            else:
                x_labels.append(f"H{week_idx}")

    self.ax.set_xticks(x_ticks)
    self.ax.set_xticklabels(x_labels, color=text_color, rotation=0, ha="center")
    self.ax.set_xlabel(
        "Valódi hónapok (helyes pozíciók)", color=text_color, fontsize=12
    )

    # Y TENGELY - HÉTKÖZNAPOK
    self.ax.set_yticks(range(7))
    self.ax.set_yticklabels(
        ["Hétfő", "Kedd", "Szerda", "Csütörtök", "Péntek", "Szombat", "Vasárnap"],
        color=text_color,
    )
    self.ax.invert_yaxis()

    self.ax.set_xlim(-0.5, 52.5)
    self.ax.set_ylim(-0.5, 6.5)


def format_period_text(
    self, min_date: pd.Timestamp, max_date: pd.Timestamp, total_days: int
) -> str:
    """
    Format period text for title.

    Args:
        self: HeatmapCalendarChart instance
        min_date: Minimális dátum
        max_date: Maximális dátum
        total_days: Összes napok száma

    Returns:
        str: Formázott időszak szöveg
    """
    years = sorted(set([min_date.year, max_date.year]))

    if len(years) == 1:
        if (
            min_date.month == 1
            and min_date.day == 1
            and max_date.month == 12
            and max_date.day == 31
        ):
            return f" ({years[0]})"
        else:
            return f" ({min_date.strftime('%Y.%m.%d')} - {max_date.strftime('%m.%d')})"
    else:
        return f" ({min_date.strftime('%Y.%m')} - {max_date.strftime('%Y.%m')}, {total_days} nap)"
