#!/usr/bin/env python3
# mypy: ignore-errors

"""
Progress Manager - Progress tracking és loading indicator kezelése

Kezeli a loading indicator megjelenítését, elrejtését,
timeout kezelést és a progress frissítéseket.
"""

import logging
from contextlib import suppress

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QLabel


class ProgressManager(QObject):
    """
    Progress tracking és loading indicator kezelése.

    Felelőségek:
    - Loading indicator megjelenítés/elrejtés
    - Progress üzenetek frissítése
    - Timeout kezelés (30 sec)
    - State management (is_loading)
    """

    # Signalok
    progress_changed = Signal(str)  # progress üzenet változás
    loading_state_changed = Signal(bool)  # loading állapot változás

    def __init__(self, parent=None):
        """
        ProgressManager inicializálása.

        Args:
            parent: Szülő QObject
        """
        super().__init__(parent)
        self._logger = logging.getLogger(__name__)

        # Állapot változók
        self._is_loading: bool = False
        self._loading_timer: QTimer | None = None
        self._progress_text: str = ""

    def initialize(self, progress_indicator: QLabel) -> None:
        """
        Progress manager inicializálása UI komponensekkel.

        Args:
            progress_indicator: QLabel a progress megjelenítéshez
        """
        self._progress_indicator = progress_indicator

        # Timer létrehozása
        if not self._loading_timer:
            self._loading_timer = QTimer()
            self._loading_timer.setSingleShot(True)
            self._loading_timer.timeout.connect(self._on_loading_timeout)

    def show_loading(self, message: str = "⏳ Adatok betöltése...") -> None:
        """
        Loading indicator megjelenítése.

        Args:
            message: Megjelenítendő üzenet
        """
        self._logger.debug(f"ResultsPanel loading indicator: {message}")

        self._is_loading = True
        self._progress_text = message
        self._progress_indicator.setText(message)
        self._progress_indicator.setVisible(True)

        # Signal küldése
        self.progress_changed.emit(message)
        self.loading_state_changed.emit(True)

        # Auto-timeout beállítása (30 sec)
        if self._loading_timer:
            self._loading_timer.start(30000)

        self._logger.debug(f"📊 DEBUG: ResultsPanel loading indicator shown - {message}")

    def hide_loading(self) -> None:
        """Loading indicator elrejtése."""
        self._logger.debug("ResultsPanel loading indicator hide")

        self._is_loading = False
        self._progress_text = ""
        self._progress_indicator.setVisible(False)
        self._progress_indicator.setText("")

        # Signal küldése
        self.loading_state_changed.emit(False)

        # Timer leállítása
        if self._loading_timer and self._loading_timer.isActive():
            self._loading_timer.stop()

        self._logger.debug("📊 DEBUG: ResultsPanel loading indicator hidden")

    def update_progress(self, message: str) -> None:
        """
        Loading progress frissítése.

        Args:
            message: Aktuális progress üzenet
        """
        if self._is_loading:
            self._progress_text = message
            self._progress_indicator.setText(message)
            self.progress_changed.emit(message)
            self._logger.debug(f"📊 DEBUG: ResultsPanel progress updated - {message}")

    def _on_loading_timeout(self) -> None:
        """Loading timeout kezelése."""
        self._logger.warning("ResultsPanel loading timeout - forcing hide")
        self.hide_loading()
        self.timeout_occurred.emit()

    def force_hide(self) -> None:
        """Loading indicator kényszerített elrejtése."""
        if self._is_loading:
            self.hide_loading()
            self._logger.debug("🚨 DEBUG: Force hide loading indicator")

    def is_loading(self) -> bool:
        """
        Loading állapot lekérdezése.

        Returns:
            bool: True ha loading állapotban van
        """
        return self._is_loading

    def get_progress_text(self) -> str:
        """
        Jelenlegi progress üzenet lekérdezése.

        Returns:
            str: Progress üzenet
        """
        return self._progress_text

    def cleanup(self) -> None:
        """Cleanup - timer törlése."""
        timer = self._loading_timer
        if timer:
            with suppress(RuntimeError):
                if timer.isActive():
                    timer.stop()
            with suppress(RuntimeError):
                timer.deleteLater()
            self._loading_timer = None
        self._is_loading = False


class ProgressManagerWithTimeout(ProgressManager):
    """
    ProgressManager timeout signallal.

    Kiegészíti az alap ProgressManager-t timeout signallal,
    hogy a külső komponensek is kezelhessék a timeout-ot.
    """

    timeout_occurred = Signal()  # Timeout történt

    def _on_loading_timeout(self) -> None:
        """Loading timeout kezelése signal kíséretében."""
        super()._on_loading_timeout()
        self.timeout_occurred.emit()
