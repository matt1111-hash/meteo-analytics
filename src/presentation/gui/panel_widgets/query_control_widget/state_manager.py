"""
State management for QueryControlWidget.

Ez a modul felelős a QueryControlWidget állapotkezelésért.
"""

from typing import Optional
from datetime import datetime
from PySide6.QtCore import QTimer, Signal
import logging

logger = logging.getLogger(__name__)


class QueryControlStateManager:
    """
    QueryControlWidget állapotkezelő.

    Kezeli az idle/fetching/error/success állapotokat és a timer-eket.
    """

    # States
    STATE_IDLE = "idle"
    STATE_FETCHING = "fetching"
    STATE_ERROR = "error"
    STATE_SUCCESS = "success"

    def __init__(self, ui_builder, state_changed_signal: Signal):
        """
        State manager inicializálása.

        Args:
            ui_builder: UI builder objektum
            state_changed_signal: Állapot változás signal
        """
        self._ui = ui_builder
        self._state_changed = state_changed_signal

        # State variables
        self._current_state: str = self.STATE_IDLE
        self._is_fetching: bool = False
        self._fetch_start_time: Optional[datetime] = None
        self._progress_dots: int = 0
        self._cancel_requested: bool = False

        # Timers
        self._auto_reset_timer: Optional[QTimer] = QTimer()
        self._auto_reset_timer.setSingleShot(True)
        self._auto_reset_timer.timeout.connect(self._on_auto_reset)

        self._progress_update_timer: Optional[QTimer] = QTimer()
        self._progress_update_timer.timeout.connect(self._update_progress_animation)

    @property
    def current_state(self) -> str:
        """Jelenlegi állapot."""
        return self._current_state

    @property
    def is_fetching(self) -> bool:
        """Fetching állapotban van-e."""
        return self._is_fetching

    @property
    def cancel_requested(self) -> bool:
        """Megszakítás lett-e kérve."""
        return self._cancel_requested

    @cancel_requested.setter
    def cancel_requested(self, value: bool) -> None:
        """Megszakítás kérés beállítása."""
        self._cancel_requested = value

    @property
    def fetch_start_time(self) -> Optional[datetime]:
        """Lekérdezés kezdési időpontja."""
        return self._fetch_start_time

    def set_state(self, new_state: str) -> None:
        """
        Állapot beállítása és UI frissítése.

        Args:
            new_state: idle/fetching/error/success
        """
        if self._current_state == new_state:
            return

        logger.debug(f"State change: {self._current_state} -> {new_state}")

        self._current_state = new_state

        # State specific actions
        if new_state == self.STATE_IDLE:
            self._set_idle_state()
        elif new_state == self.STATE_FETCHING:
            self._set_fetching_state()
        elif new_state == self.STATE_ERROR:
            self._set_error_state()
        elif new_state == self.STATE_SUCCESS:
            self._set_success_state()

        self._state_changed.emit(new_state)

    def _set_idle_state(self) -> None:
        """Idle állapot beállítása."""
        self._is_fetching = False
        self._cancel_requested = False
        self._fetch_start_time = None

        if self._ui.status_label:
            self._ui.status_label.setText("✅ Kész a lekérdezésre")
            self._ui.status_label.setStyleSheet("color: #16a34a; font-weight: bold;")

        if self._ui.progress_text_label:
            self._ui.progress_text_label.setText("")
            self._ui.progress_text_label.setVisible(False)

        self._stop_progress_timer()
        logger.debug("Set to idle state")

    def _set_fetching_state(self) -> None:
        """Fetching állapot beállítása."""
        self._is_fetching = True
        self._cancel_requested = False
        self._fetch_start_time = datetime.now()
        self._progress_dots = 0

        if self._ui.status_label:
            self._ui.status_label.setText("⏳ Adatok lekérdezése...")
            self._ui.status_label.setStyleSheet("color: #2563eb; font-weight: bold;")

        if self._ui.progress_text_label:
            self._ui.progress_text_label.setText("📄 Kapcsolódás...")
            self._ui.progress_text_label.setVisible(True)

        self._start_progress_timer()
        logger.debug("Set to fetching state")

    def _set_error_state(self) -> None:
        """Error állapot beállítása."""
        self._is_fetching = False

        if self._ui.status_label:
            self._ui.status_label.setText("❌ Hiba történt")
            self._ui.status_label.setStyleSheet("color: #dc2626; font-weight: bold;")

        if self._ui.progress_text_label:
            self._ui.progress_text_label.setText("")
            self._ui.progress_text_label.setVisible(False)

        self._stop_progress_timer()
        self._start_auto_reset(5000)  # 5 seconds
        logger.debug("Set to error state")

    def _set_success_state(self) -> None:
        """Success állapot beállítása."""
        self._is_fetching = False

        if self._ui.status_label:
            self._ui.status_label.setText("✅ Sikeres lekérdezés")
            self._ui.status_label.setStyleSheet("color: #16a34a; font-weight: bold;")

        if self._ui.progress_text_label:
            self._ui.progress_text_label.setText("")
            self._ui.progress_text_label.setVisible(False)

        self._stop_progress_timer()
        self._start_auto_reset(3000)  # 3 seconds
        logger.debug("Set to success state")

    # Timer management

    def _start_auto_reset(self, delay_ms: int) -> None:
        """Auto-reset timer indítása."""
        if self._auto_reset_timer:
            if self._auto_reset_timer.isActive():
                self._auto_reset_timer.stop()
            self._auto_reset_timer.start(delay_ms)
            logger.debug(f"Auto-reset timer started: {delay_ms}ms")
        else:
            logger.warning("Auto-reset timer is None - cannot start")

    def _on_auto_reset(self) -> None:
        """Auto-reset timer timeout kezelése."""
        logger.debug("Auto-reset triggered")
        self.set_state(self.STATE_IDLE)

    def _start_progress_timer(self) -> None:
        """Progress timer indítása."""
        if self._progress_update_timer:
            self._progress_update_timer.start(500)  # 500ms intervals

    def _stop_progress_timer(self) -> None:
        """Progress timer leállítása."""
        if self._progress_update_timer and self._progress_update_timer.isActive():
            self._progress_update_timer.stop()

    def _update_progress_animation(self) -> None:
        """Progress animáció frissítése."""
        if not self._is_fetching:
            return

        self._progress_dots = (self._progress_dots + 1) % 4
        dots = "." * self._progress_dots

        elapsed_time = ""
        if self._fetch_start_time:
            elapsed = datetime.now() - self._fetch_start_time
            elapsed_seconds = int(elapsed.total_seconds())
            elapsed_time = f" ({elapsed_seconds}s)"

        if self._ui.progress_text_label:
            self._ui.progress_text_label.setText(f"📄 Adatok letöltése{dots}{elapsed_time}")

    def cleanup(self) -> None:
        """Timer-ek takarítása."""
        if self._auto_reset_timer:
            if self._auto_reset_timer.isActive():
                self._auto_reset_timer.stop()
            self._auto_reset_timer.deleteLater()
            self._auto_reset_timer = None

        if self._progress_update_timer:
            if self._progress_update_timer.isActive():
                self._progress_update_timer.stop()
            self._progress_update_timer.deleteLater()
            self._progress_update_timer = None
