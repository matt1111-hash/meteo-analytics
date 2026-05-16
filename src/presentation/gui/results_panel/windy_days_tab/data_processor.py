#!/usr/bin/env python3
# mypy: ignore-errors

"""
Windy Days Tab - Data Processor

Adatkezelő metódusok a szeles napok analízis tab-hoz.

Fájl: src/presentation/gui/results_panel/windy_days_tab/data_processor.py
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pandas as pd

from src.domain.analytics.wind_models import WINDY_DAY_THRESHOLD_KMH

if TYPE_CHECKING:
    from src.presentation.gui.results_panel.windy_days_tab.core import WindyDaysTab

logger = logging.getLogger(__name__)


def update_data(
    self: WindyDaysTab,
    weather_data: pd.DataFrame,
    location: str = "Ismeretlen helyszín",
) -> None:
    """
    Adatok frissítése - MEGBÍZIK A RESULTSPANEL-BEN!

    Args:
        weather_data: Pandas DataFrame időjárási adatokkal (ResultsPanel KONVERTÁLTA km/h-ra)
        location: Helyszín neve
    """
    try:
        logger.info(f"WindyDaysTab adatok frissítése: {location}")
        logger.info(
            f"BEJÖVŐ ADATOK (ResultsPanel konvertálta): {len(weather_data)} sor, oszlopok: {list(weather_data.columns)}"
        )

        # Wind speed ellenőrzés
        if not weather_data.empty and "wind_speed" in weather_data.columns:
            wind_speeds = weather_data["wind_speed"].dropna()
            if len(wind_speeds) > 0:
                logger.info(
                    f"KAPOTT WIND_SPEED (km/h): {wind_speeds.min():.1f} - {wind_speeds.max():.1f}"
                )
            else:
                logger.warning("ÜRES WIND_SPEED OSZLOP")

        # ADATOK TÁROLÁSA (ResultsPanel már konvertálta)
        self.current_weather_data = weather_data
        self.current_location = location

        # Automatikus analízis ha be van kapcsolva
        auto_update = getattr(self, "auto_update_checkbox", None)
        if auto_update and auto_update.isChecked() and not weather_data.empty:
            logger.info("AUTOMATIKUS ANALÍZIS INDÍTÁSA (DUPLA KONVERZIÓ NÉLKÜL)")
            _start_auto_analysis(self)

    except Exception as e:
        logger.error(f"Hiba az adatok frissítésében: {e}")
        self.error_occurred.emit(f"Adatok frissítési hiba: {e}")


def clear_data(self: WindyDaysTab) -> None:
    """Adatok és UI tartalom törlése."""
    try:
        logger.info("WindyDaysTab adatok törlése")

        # Adatok nullázása
        self.current_weather_data = None
        self.current_location = "Ismeretlen helyszín"
        self.current_analysis_result = None

        # Chart törlése
        if self.chart:
            self.chart.clear_chart()

        # Summary törlése
        _set_initial_summary_message(self)

        # UI elemek állapotának visszaállítása
        if self.export_button:
            self.export_button.setEnabled(False)

        if self.threshold_spinbox:
            self.threshold_spinbox.setValue(int(WINDY_DAY_THRESHOLD_KMH))

    except Exception as e:
        logger.error(f"Hiba az adatok törlésében: {e}")


def get_current_threshold(self: WindyDaysTab) -> float:
    """Aktuális küszöbérték lekérdezése."""
    if self.threshold_spinbox:
        return float(self.threshold_spinbox.value())
    return WINDY_DAY_THRESHOLD_KMH


def set_threshold(self: WindyDaysTab, threshold: float) -> None:
    """Küszöbérték beállítása."""
    if self.threshold_spinbox:
        self.threshold_spinbox.setValue(int(threshold))


def _start_auto_analysis(self: WindyDaysTab) -> None:
    """Automatikus analízis indítása (késleltetve)."""
    try:
        from src.presentation.gui.results_panel.windy_days_tab.handlers import (  # noqa: PLC0415
            _start_analysis,
        )

        _start_analysis(self)
    except Exception as e:
        logger.error(f"Hiba az automatikus analízis indításában: {e}")


def _set_initial_summary_message(self: WindyDaysTab) -> None:
    """Kezdeti üzenet beállítása az összefoglalóban."""
    try:
        initial_message = """
Szeles Napok Analízis

Még nem futott analízis.

Kattints az "Analízis Futtatása" gombra
az időjárási adatok elemzéséhez.

Beállítható paraméterek:
- Küszöbérték: szélsebesség limit
- Automatikus frissítés: ki/bekapcsolás

A rendszer megszámolja azokat a napokat,
amikor a maximális szélsebesség meghaladja
a beállított küszöbértéket.

MEGBÍZIK A RESULTSPANEL KONVERZIÓJÁBAN!
DUPLA KONVERZIÓ ELTÁVOLÍTVA!
        """.strip()

        if self.summary_text:
            self.summary_text.setPlainText(initial_message)

    except Exception as e:
        logger.error(f"Hiba a kezdeti üzenet beállításában: {e}")
