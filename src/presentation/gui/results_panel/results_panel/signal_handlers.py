#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Results Panel - Signal Handlers

🔌 Signal kezelés és event handlers

Képességek:
- Signal connections
- Event handlers
- Loading state handlers
- WindyDaysTab signal handlers

Fájl: src/presentation/gui/results_panel/results_panel/signal_handlers.py
"""

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def connect_signals(self) -> None:
    """
    Belső signal kapcsolatok beállítása.

    Args:
        self: ResultsPanel instance
    """
    # Progress manager signalok
    self.progress_manager.timeout_occurred.connect(_on_loading_timeout)
    self.progress_manager.loading_state_changed.connect(_on_loading_state_changed)

    # WindyDaysTab signal kapcsolatok
    windy_days_tab = self.tab_manager.get_windy_days_tab()
    if windy_days_tab:
        try:
            if hasattr(windy_days_tab, "analysis_completed"):
                windy_days_tab.analysis_completed.connect(
                    _on_windy_days_analysis_completed
                )
            if hasattr(windy_days_tab, "error_occurred"):
                windy_days_tab.error_occurred.connect(_on_windy_days_error)
            if hasattr(windy_days_tab, "export_requested"):
                windy_days_tab.export_requested.connect(_on_windy_days_export_requested)
            logger.debug("✅ WindyDaysTab signal kapcsolatok beállítva")
        except Exception as e:
            logger.warning(f"⚠️ WindyDaysTab signal kapcsolat hiba: {e}")


def _on_loading_timeout(self) -> None:
    """
    Loading timeout kezelése.

    Args:
        self: ResultsPanel instance
    """
    logger.warning("ResultsPanel loading timeout - handled by ProgressManager")

    # Error message a title-ben
    original_text = self.title_label.text()
    self.title_label.setText("⚠️ Időtúllépés - próbálja újra")

    # Reset after 5 seconds
    QTimer.singleShot(5000, lambda: self.title_label.setText(original_text))


def _on_loading_state_changed(self, is_loading: bool) -> None:
    """
    Loading állapot változás kezelése.

    Args:
        self: ResultsPanel instance
        is_loading: Loading állapot
    """
    # Tab-ok engedélyezése/letiltása
    if self.tab_widget:
        self.tab_widget.setEnabled(not is_loading)

    # Gombok engedélyezése/letiltása
    self.global_export_btn.setEnabled(not is_loading)
    self.extreme_weather_btn.setEnabled(not is_loading)


def _on_extreme_weather_clicked(self) -> None:
    """
    Extreme weather gomb kattintás kezelése.

    Args:
        self: ResultsPanel instance
    """
    logger.info("🔥 Extreme weather button clicked - emitting signal")
    self.extreme_weather_requested.emit()

    # Tab váltás
    from .public_api import switch_to_tab

    switch_to_tab(self, "extreme")


def _on_windy_days_analysis_completed(self, result: dict) -> None:
    """
    WindyDaysTab analízis befejezés kezelése.

    Args:
        self: ResultsPanel instance
        result: Eredmény dictionary
    """
    logger.info("🌪️ WindyDaysTab analízis befejezve")


def _on_windy_days_error(self, error_message: str) -> None:
    """
    WindyDaysTab hiba kezelése.

    Args:
        self: ResultsPanel instance
        error_message: Error message
    """
    logger.error(f"🌪️ WindyDaysTab hiba: {error_message}")

    # Hiba megjelenítése
    original_text = self.title_label.text()
    self.title_label.setText(f"⚠️ Szeles napok hiba: {error_message[:30]}...")

    # Reset 5 másodperc után
    QTimer.singleShot(5000, lambda: self.title_label.setText(original_text))


def _on_windy_days_export_requested(self, file_type: str, file_path: str) -> None:
    """
    WindyDaysTab export kérés kezelése.

    Args:
        self: ResultsPanel instance
        file_type: Fájl típus
        file_path: Fájl útvonal
    """
    logger.info(f"🌪️ WindyDaysTab export kérés: {file_type} -> {file_path}")
    self.export_requested.emit(file_type)
