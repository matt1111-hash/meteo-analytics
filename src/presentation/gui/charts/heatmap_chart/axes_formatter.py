#!/usr/bin/env python3
# mypy: ignore-errors

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
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from ...theme_manager import get_current_colors

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _get_hungarian_months() -> list[str]:
    """Return Hungarian short month labels."""
    return [
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


def _build_month_ticks(
    min_date: pd.Timestamp, total_days: int, first_day_weekday: int
) -> tuple[list[int], list[str]]:
    """Build month tick positions for visible week boundaries."""
    x_ticks: list[int] = []
    x_labels: list[str] = []
    seen_months: set[tuple[int, int]] = set()
    hungarian_months = _get_hungarian_months()
    for week_idx in range(53):
        days_from_start = week_idx * 7 - first_day_weekday
        if days_from_start < 0 or days_from_start >= total_days:
            continue
        week_date = min_date + pd.Timedelta(days=days_from_start)
        month_key = (week_date.year, week_date.month)
        if month_key in seen_months or week_idx % 4 != 0:
            continue
        seen_months.add(month_key)
        x_ticks.append(week_idx)
        month_name = hungarian_months[week_date.month]
        x_labels.append(
            f"{month_name}\n{week_date.year}" if week_date.year != min_date.year else month_name
        )
    return x_ticks, x_labels


def _build_fallback_ticks(
    min_date: pd.Timestamp, total_days: int, first_day_weekday: int
) -> tuple[Any, list[str]]:
    """Build fallback month ticks when month transitions are sparse."""
    x_ticks = np.arange(6, 53, 8)
    labels: list[str] = []
    hungarian_months = _get_hungarian_months()
    for week_idx in x_ticks:
        days_from_start = week_idx * 7 - first_day_weekday
        if 0 <= days_from_start < total_days:
            week_date = min_date + pd.Timedelta(days=days_from_start)
            labels.append(hungarian_months[week_date.month])
        else:
            labels.append(f"H{week_idx}")
    return x_ticks, labels


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
    x_ticks, x_labels = _build_month_ticks(min_date, total_days, self._first_day_weekday)
    if len(x_ticks) < 3:  # noqa: PLR2004
        x_ticks, x_labels = _build_fallback_ticks(min_date, total_days, self._first_day_weekday)

    self.ax.set_xticks(x_ticks)
    self.ax.set_xticklabels(x_labels, color=text_color, rotation=0, ha="center")
    self.ax.set_xlabel("Valódi hónapok (helyes pozíciók)", color=text_color, fontsize=12)

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
    self,  # noqa: ARG001
    min_date: pd.Timestamp,
    max_date: pd.Timestamp,
    total_days: int,
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
    years = sorted({min_date.year, max_date.year})
    if len(years) == 1:
        if (
            min_date.month == 1
            and min_date.day == 1
            and max_date.month == 12  # noqa: PLR2004
            and max_date.day == 31  # noqa: PLR2004
        ):
            return f" ({years[0]})"
        return f" ({min_date.strftime('%Y.%m.%d')} - {max_date.strftime('%m.%d')})"
    return f" ({min_date.strftime('%Y.%m')} - {max_date.strftime('%Y.%m')}, {total_days} nap)"
