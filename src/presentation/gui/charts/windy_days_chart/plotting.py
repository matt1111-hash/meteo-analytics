#!/usr/bin/env python3
# mypy: ignore-errors

"""
Windy Days Chart - Plotting

📈 Chart rajzolás

Képességek:
- Fő chart rajzolás
- Bar chart létrehozás

Fájl: src/presentation/gui/charts/windy_days_chart/plotting.py
"""

import logging
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _plot_windy_days_chart(self) -> None:
    """
    Szeles napok oszlopdiagram rajzolása.

    Args:
        self: WindyDaysChart instance
    """
    from .helpers import _plot_error_message, _plot_no_data_message  # noqa: PLC0415
    from .interactivity import _setup_chart_interactivity  # noqa: PLC0415
    from .styling import (  # noqa: PLC0415
        _add_value_labels,
        _apply_chart_styling,
        _get_bar_colors,
        _setup_chart_axes,
        _setup_chart_labels,
    )

    try:
        # Canvas tisztítása
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Adatok kinyerése
        months = self.chart_data.get("months", [])
        counts = self.chart_data.get("counts", [])
        percentages = self.chart_data.get("percentages", [])

        if not months or not counts:
            _plot_no_data_message(self)
            return

        # Színpaletta a szeles napok számának megfelelően
        colors = _get_bar_colors(self, counts)

        # X tengely pozíciók
        x_positions = np.arange(len(months))

        # Oszlopdiagram
        bars = ax.bar(
            x_positions,
            counts,
            color=colors,
            alpha=0.8,
            edgecolor="white",
            linewidth=1.2,
        )

        # Értékek megjelenítése az oszlopok tetején
        _add_value_labels(self, ax, bars, counts, percentages)

        # Tengelyek beállítása
        _setup_chart_axes(self, ax, months, counts)

        # Chart címe és címkék
        _setup_chart_labels(self, ax)

        # Grid és stílus
        _apply_chart_styling(self, ax)

        # Theme alkalmazása
        self._apply_theme_to_chart()

        # Interaktivitás
        _setup_chart_interactivity(self, bars, months, counts, percentages)

        # Canvas frissítése - 🚨 JAVÍTVA: self.draw() használata self.canvas.draw() helyett
        self.draw()

        logger.info("Szeles napok oszlopdiagram sikeresen rajzolva")

    except Exception as e:
        logger.error(f"Hiba a szeles napok chart rajzolásában: {e}")
        _plot_error_message(self, str(e))
