#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windy Days Tab - Handlers

Signal handler metódusok a szeles napok analízis tab-hoz.

Fájl: src/presentation/gui/results_panel/windy_days_tab/handlers.py
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFileDialog

from src.domain.analytics.wind_analysis_service import analyze_wind_patterns
from src.domain.analytics.wind_models import WINDY_DAY_THRESHOLD_KMH
from src.domain.analytics.wind_reporting import (
    format_wind_analysis_summary,
    get_chart_data_for_monthly_windy_days,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget
    from pandas import DataFrame

    from src.presentation.gui.results_panel.windy_days_tab.core import WindyDaysTab

logger = logging.getLogger(__name__)


def handle_analyze_clicked(self: "WindyDaysTab") -> None:
    """Analízis gomb kattintás kezelése."""
    try:
        logger.info("Szeles napok analízis indítása")

        if self.current_weather_data is None or self.current_weather_data.empty:
            self.error_occurred.emit("Nincs elérhető időjárási adat az analízishez")
            return

        _start_analysis(self)

    except Exception as e:
        logger.error(f"Hiba az analízis indításában: {e}")
        self.error_occurred.emit(f"Hiba az analízis indításában: {e}")


def handle_export_clicked(self: "WindyDaysTab") -> None:
    """Export gomb kattintás kezelése."""
    try:
        if self.chart and self.current_analysis_result:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Chart Exportálása",
                f"szeles_napok_{self.current_location.replace(' ', '_')}.png",
                "PNG Files (*.png);;PDF Files (*.pdf);;All Files (*)"
            )

            if file_path:
                success = self.chart.export_chart(file_path)
                if success:
                    self.export_requested.emit("chart", file_path)
                else:
                    self.error_occurred.emit("Hiba a chart exportálásában")

    except Exception as e:
        logger.error(f"Hiba az exportálásban: {e}")
        self.error_occurred.emit(f"Export hiba: {e}")


def handle_threshold_changed(self: "WindyDaysTab", value: int) -> None:
    """Küszöbérték változás kezelése."""
    try:
        logger.info(f"Küszöbérték változott: {value} km/h")

        # Automatikus frissítés ha be van kapcsolva
        auto_update = getattr(self, 'auto_update_checkbox', None)
        if (auto_update and
            auto_update.isChecked() and
            self.current_weather_data is not None):
            # Kis késleltetés a túl gyakori frissítés elkerülésére
            QTimer.singleShot(500, lambda: _start_analysis(self))

    except Exception as e:
        logger.error(f"Hiba a küszöbérték változás kezelésében: {e}")


def handle_auto_update_toggled(self: "WindyDaysTab", checked: bool) -> None:
    """Automatikus frissítés toggle kezelése."""
    try:
        logger.info(f"Automatikus frissítés: {'be' if checked else 'ki'}kapcsolva")

    except Exception as e:
        logger.error(f"Hiba az auto update toggle kezelésében: {e}")


def _start_analysis(self: "WindyDaysTab") -> None:
    """
    Analízis indítása - DUPLA KONVERZIÓ NÉLKÜL!

    A ResultsPanel már konvertálta a m/s -> km/h adatokat.
    """
    try:
        # UI állapot
        _set_analysis_state(self, True)

        logger.info("KONVERZIÓ NÉLKÜLI ANALÍZIS: Megbízunk a ResultsPanel km/h konverziójában")

        # Paraméterek
        threshold = self.threshold_spinbox.value() if self.threshold_spinbox else WINDY_DAY_THRESHOLD_KMH
        location = self.current_location

        logger.info(f"ANALÍZIS PARAMÉTEREI: threshold={threshold} km/h, location={location}")
        logger.info(f"WEATHER DATA: {len(self.current_weather_data)} sor, oszlopok: {list(self.current_weather_data.columns)}")

        # Wind speed ellenőrzés
        if 'wind_speed' in self.current_weather_data.columns:
            wind_speeds = self.current_weather_data['wind_speed'].dropna()
            if len(wind_speeds) > 0:
                logger.info(f"KAPOTT WIND_SPEED (ResultsPanel konvertálta): {wind_speeds.min():.1f} - {wind_speeds.max():.1f} km/h")
            else:
                logger.error("ÜRES WIND_SPEED OSZLOP!")
                self.error_occurred.emit("Nincs szélsebesség adat")
                _set_analysis_state(self, False)
                return
        else:
            logger.error("HIÁNYZIK A WIND_SPEED OSZLOP!")
            self.error_occurred.emit("Hiányzik a wind_speed oszlop")
            _set_analysis_state(self, False)
            return

        # ANALÍZIS FUTTATÁSA KÖZVETLENÜL A KAPOTT ADATOKKAL!
        analysis_result = analyze_wind_patterns(
            self.current_weather_data,
            location_name=location,
            threshold_kmh=threshold
        )

        # Chart adatok előkészítése
        chart_data = get_chart_data_for_monthly_windy_days(analysis_result)

        # Eredmények megjelenítése
        _display_analysis_results(self, analysis_result, chart_data, threshold)

        # UI állapot visszaállítása
        _set_analysis_state(self, False)

        # Signal kibocsátása
        self.analysis_completed.emit({
            'analysis_result': analysis_result,
            'chart_data': chart_data,
            'threshold': threshold,
            'location': location
        })

        logger.info("Szeles napok analízis befejezve (DUPLA KONVERZIÓ NÉLKÜL)")

    except Exception as e:
        logger.error(f"Hiba az analízisben: {e}")
        import traceback
        traceback.print_exc()
        _set_analysis_state(self, False)
        self.error_occurred.emit(f"Analízis hiba: {e}")


def _display_analysis_results(
    self: "WindyDaysTab",
    analysis_result,
    chart_data: dict,
    threshold: float
) -> None:
    """Analízis eredmények megjelenítése."""
    try:
        # Chart frissítése
        if self.chart:
            chart_update_data = {
                'chart_data': chart_data,
                'threshold_kmh': threshold,
                'location_name': self.current_location
            }
            self.chart.update_data(chart_update_data)

        # Summary frissítése
        if self.summary_text:
            summary = format_wind_analysis_summary(analysis_result)
            summary_with_fix_info = f"{summary}\n\nJAVÍTÁS: Megbízik a ResultsPanel km/h konverziójában!\nDupla konverzió eltávolítva!"
            self.summary_text.setPlainText(summary_with_fix_info)

        # Export gomb engedélyezése
        if self.export_button:
            self.export_button.setEnabled(True)

        # Eredmény tárolása
        self.current_analysis_result = {
            'analysis_result': analysis_result,
            'chart_data': chart_data,
            'threshold': threshold
        }

        logger.info("Analízis eredmények megjelenítve (DUPLA KONVERZIÓ NÉLKÜL)")

    except Exception as e:
        logger.error(f"Hiba az eredmények megjelenítésében: {e}")


def _set_analysis_state(self: "WindyDaysTab", running: bool) -> None:
    """Analízis állapot UI frissítése."""
    try:
        if self.analyze_button:
            self.analyze_button.setEnabled(not running)
            self.analyze_button.setText("Elemzés..." if running else "Analízis Futtatása")

        if self.progress_bar:
            self.progress_bar.setVisible(running)
            if running:
                self.progress_bar.setRange(0, 0)  # Indeterminate

    except Exception as e:
        logger.error(f"Hiba az analízis állapot beállításában: {e}")
