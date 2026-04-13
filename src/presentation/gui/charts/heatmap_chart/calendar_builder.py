#!/usr/bin/env python3
# mypy: ignore-errors

"""
Heatmap Chart - Calendar Builder

🗓️ Kalendár mátrix építés

Képességek:
- 7x53 kalendár mátrix építése
- Hét pozíció számítás
- NaN kezelés

Fájl: src/presentation/gui/charts/heatmap_chart/calendar_builder.py
"""

import logging
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def build_calendar_matrix(self, values: np.ndarray, start_date: pd.Timestamp) -> np.ndarray:
    """
    Build 7x53 calendar matrix, considering the start day's weekday.

    Args:
        self: HeatmapCalendarChart instance
        values: Értékek tömb
        start_date: Kezdő dátum

    Returns:
        np.ndarray: 7x53 kalendár mátrix
    """
    # A hét első napjának megkeresése (0=Hétfő, 6=Vasárnap)
    first_day_weekday = start_date.weekday()

    # A teljes naptár mérete: az eltolás + az adatok hossza
    total_cells = first_day_weekday + len(values)

    # Feltöltjük a teljes listát NaN-okkal
    full_year_values = np.full(total_cells, np.nan)

    # Beillesztjük a valódi adatokat a megfelelő helyre
    full_year_values[first_day_weekday:] = values

    # Létrehozzuk a 7x53-as mátrixot
    calendar_matrix = np.full((7, 53), np.nan)

    num_weeks = (total_cells + 6) // 7

    for week in range(min(num_weeks, 53)):
        start_idx = week * 7
        end_idx = start_idx + 7
        week_data = full_year_values[start_idx:end_idx]

        # Biztosítjuk, hogy a hét adatai 7 eleműek legyenek
        padded_week_data = np.pad(
            week_data, (0, 7 - len(week_data)), "constant", constant_values=np.nan
        )
        calendar_matrix[:, week] = padded_week_data

    if "precipitation" in self.parameter or "wind" in self.parameter:
        calendar_matrix = np.nan_to_num(calendar_matrix, nan=0.0)

    logger.debug(
        f"🗓️ OKOS Kalendár mátrix: {calendar_matrix.shape}, első nap: {start_date.strftime('%A')}"
    )
    return calendar_matrix
