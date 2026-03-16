#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Windy Days Chart - Helpers

🛠️ Segédfüggvények

Képességek:
- No data üzenet
- Error üzenet
- Export
- Chart info

Fájl: src/presentation/gui/charts/windy_days_chart/helpers.py
"""

import logging
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _plot_no_data_message(self) -> None:
    """
    Üzenet megjelenítése ha nincs adat.

    Args:
        self: WindyDaysChart instance
    """
    try:
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.text(
            0.5,
            0.5,
            f"Nincs elérhető szélsebességi adat\n\n"
            f"Küszöbérték: {self.threshold_kmh} km/h\n"
            f"Helyszín: {self.location_name}",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=12,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.5),
        )

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        # 🚨 JAVÍTVA: self.draw() használata self.canvas.draw() helyett
        self.draw()

    except Exception as e:
        logger.error(f"Hiba a 'nincs adat' üzenet rajzolásában: {e}")


def _plot_error_message(self, error_msg: str) -> None:
    """
    Hibaüzenet megjelenítése.

    Args:
        self: WindyDaysChart instance
        error_msg: Hibaüzenet
    """
    try:
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.text(
            0.5,
            0.5,
            f"Hiba történt a chart rajzolásában:\n\n{error_msg}",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=10,
            color="red",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="mistyrose", alpha=0.7),
        )

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        # 🚨 JAVÍTVA: self.draw() használata self.canvas.draw() helyett
        self.draw()

    except Exception as e:
        logger.error(f"Hiba a hibaüzenet rajzolásában: {e}")


def clear_chart(self) -> None:
    """
    Chart törlése.

    Args:
        self: WindyDaysChart instance
    """
    try:
        self.figure.clear()
        # 🚨 JAVÍTVA: self.draw() használata self.canvas.draw() helyett
        self.draw()

        # Adatok törlése
        self.chart_data = {"months": [], "counts": [], "percentages": [], "labels": []}

        logger.info("WindyDaysChart törölve")

    except Exception as e:
        logger.error(f"Hiba a chart törlésében: {e}")


def export_chart(self, file_path: str, dpi: int = 300) -> bool:
    """
    Chart exportálása fájlba.

    Args:
        self: WindyDaysChart instance
        file_path: Export fájl útvonala
        dpi: Felbontás DPI-ben

    Returns:
        True ha sikeres, False egyébként
    """
    try:
        if not self._has_valid_data():
            logger.warning("Nincs exportálható adat")
            return False

        self.figure.savefig(
            file_path, dpi=dpi, bbox_inches="tight", facecolor="white", edgecolor="none"
        )

        logger.info(f"WindyDaysChart exportálva: {file_path}")
        return True

    except Exception as e:
        logger.error(f"Hiba a chart exportálásában: {e}")
        return False


def get_chart_info(self) -> Dict[str, Any]:
    """
    Chart információk lekérdezése.

    Args:
        self: WindyDaysChart instance

    Returns:
        Dict: Chart információk
    """
    return {
        "type": "windy_days",
        "title": self.chart_title,
        "has_data": self._has_valid_data(),
        "data_points": len(self.chart_data.get("months", [])),
        "threshold_kmh": self.threshold_kmh,
        "location": self.location_name,
    }
