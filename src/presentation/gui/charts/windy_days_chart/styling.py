#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Windy Days Chart - Styling

🎨 Stílus és színkezelés

Képességek:
- Bar színek
- Érték címkék
- Tengelyek beállítása
- Chart címkék
- Stílus alkalmazás

Fájl: src/presentation/gui/charts/windy_days_chart/styling.py
"""

import logging
from typing import TYPE_CHECKING, List

import matplotlib.pyplot as plt

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _get_bar_colors(self, counts: List[int]) -> List[str]:
    """
    Oszlopok színeinek meghatározása a szeles napok száma alapján.

    Args:
        self: WindyDaysChart instance
        counts: Szeles napok számai

    Returns:
        Lista hex színkódokkal
    """
    from src.presentation.gui.theme_manager import ProfessionalThemeManager

    try:
        if not counts:
            return []

        theme_manager = ProfessionalThemeManager()

        # Színkategóriák a szeles napok száma alapján
        max_count = max(counts) if counts else 1

        colors = []
        for count in counts:
            if count == 0:
                # Nincs szeles nap - szürke
                color = theme_manager.get_color("muted")
            elif count <= max_count * 0.3:
                # Kevés szeles nap - zöld
                color = theme_manager.get_color("success")
            elif count <= max_count * 0.6:
                # Közepes szeles nap - sárga
                color = theme_manager.get_color("warning")
            else:
                # Sok szeles nap - piros
                color = theme_manager.get_color("danger")

            colors.append(color)

        return colors

    except Exception as e:
        logger.error(f"Hiba a színek meghatározásában: {e}")
        # Fallback szín
        return ["#3498db"] * len(counts)


def _add_value_labels(
    self, ax, bars, counts: List[int], percentages: List[float]
) -> None:
    """
    Értékek hozzáadása az oszlopok tetejére.

    Args:
        self: WindyDaysChart instance
        ax: Matplotlib axis
        bars: Bar chart
        counts: Szeles napok számai
        percentages: Százalékok
    """
    try:
        for bar, count, percentage in zip(bars, counts, percentages):
            height = bar.get_height()

            # Érték szöveg
            if count > 0:
                label_text = f"{count}\n({percentage:.1f}%)"
            else:
                label_text = "0"

            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + max(counts) * 0.02,
                label_text,
                ha="center",
                va="bottom",
                fontsize=9,
                weight="bold",
            )

    except Exception as e:
        logger.error(f"Hiba az értékcímkék hozzáadásában: {e}")


def _setup_chart_axes(self, ax, months: List[str], counts: List[int]) -> None:
    """
    Chart tengelyek beállítása.

    Args:
        self: WindyDaysChart instance
        ax: Matplotlib axis
        months: Hónapok
        counts: Szeles napok számai
    """
    try:
        # X tengely
        ax.set_xticks(range(len(months)))
        ax.set_xticklabels(months, rotation=45, ha="right")
        ax.set_xlabel("Hónap", fontweight="bold")

        # Y tengely
        max_count = max(counts) if counts else 10
        ax.set_ylim(0, max_count * 1.2)
        ax.set_ylabel("Szeles Napok Száma", fontweight="bold")

        # Y tengely egész számok
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    except Exception as e:
        logger.error(f"Hiba a tengelyek beállításában: {e}")


def _setup_chart_labels(self, ax) -> None:
    """
    Chart cím és címkék beállítása.

    Args:
        self: WindyDaysChart instance
        ax: Matplotlib axis
    """
    try:
        # Főcím
        title = f"Havi Szeles Napok - {self.location_name}"
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

        # Alcím a küszöbértékkel
        subtitle = f"Küszöbérték: {self.threshold_kmh} km/h"
        ax.text(
            0.5,
            0.98,
            subtitle,
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=10,
            style="italic",
        )

    except Exception as e:
        logger.error(f"Hiba a címkék beállításában: {e}")


def _apply_chart_styling(self, ax) -> None:
    """
    Chart stílus és grid alkalmazása.

    Args:
        self: WindyDaysChart instance
        ax: Matplotlib axis
    """
    try:
        # Grid
        ax.grid(True, alpha=0.3, linestyle="--")
        ax.set_axisbelow(True)

        # Spines styling
        for spine in ax.spines.values():
            spine.set_color("#cccccc")
            spine.set_linewidth(0.8)

        # Tight layout
        self.figure.tight_layout()

    except Exception as e:
        logger.error(f"Hiba a chart stílus alkalmazásában: {e}")
