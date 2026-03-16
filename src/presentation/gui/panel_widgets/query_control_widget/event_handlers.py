# mypy: ignore-errors
"""
Event handlers for QueryControlWidget (SIMPLIFIED).

Egyszerűsített verzió: csak a vezérlőgombokat kezeli.
A widget validáció és state aggregation a ControlPanel-ben történik.
"""

import logging
from typing import Any, Dict, Optional

from PySide6.QtCore import Signal

logger = logging.getLogger(__name__)


class QueryControlEventHandlers:
    """
    QueryControlWidget eseménykezelők (egyszerűsített).

    Csak a gombokat kezeli - a validáció a ControlPanel-ben történik.
    """

    def __init__(self, state_manager, ui_builder):
        """
        Event handlers inicializálása.

        Args:
            state_manager: State manager objektum
            ui_builder: UI builder objektum
        """
        self._state = state_manager
        self._ui = ui_builder

        # Query params (külsőleg beállítva)
        self._last_query_params: Optional[Dict[str, Any]] = None

        # Signals (külsőleg beállítva)
        self.query_requested: Optional[Signal] = None
        self.fetch_requested: Optional[Signal] = None
        self.cancel_requested: Optional[Signal] = None

    def on_query_clicked(self) -> None:
        """Lekérdezés gomb kattintás kezelése."""
        logger.info("Query button clicked")

        if self._state.is_fetching:
            logger.warning("Already fetching - ignoring query click")
            return

        # Emit signals - ControlPanel végzi a validációt
        self._state.set_state(self._state.STATE_FETCHING)

        if self.query_requested:
            self.query_requested.emit(self._last_query_params or {})
        if self.fetch_requested:
            self.fetch_requested.emit(self._last_query_params or {})

        logger.info("Query started")

    def on_cancel_clicked(self) -> None:
        """Megszakítás gomb kattintás kezelése."""
        logger.info("Cancel button clicked")

        self._state.cancel_requested = True
        if self.cancel_requested:
            self.cancel_requested.emit()

        # Immediate UI feedback
        if self._ui.status_label:
            self._ui.status_label.setText("🚫 Megszakítás...")
            self._ui.status_label.setStyleSheet("color: #f59e0b; font-weight: bold;")

        # Auto-reset after cancellation
        self._state._start_auto_reset(2000)  # 2 seconds

    def update_button_states(self, is_valid: bool, is_fetching: bool) -> None:
        """Gomb állapotok frissítése (külső hívásra)."""
        try:
            # Query button state
            if self._ui.query_button:
                self._ui.query_button.setEnabled(is_valid and not is_fetching)
                if is_fetching:
                    self._ui.query_button.setText("⏳ Lekérdezés folyamatban...")
                else:
                    self._ui.query_button.setText("🚀 Lekérdezés Indítása")

            # Cancel button state
            if self._ui.cancel_button:
                self._ui.cancel_button.setVisible(is_fetching)

            # Progress bar state
            if self._ui.progress_bar:
                self._ui.progress_bar.setVisible(is_fetching)

            # Progress text state
            if self._ui.progress_text_label:
                self._ui.progress_text_label.setVisible(is_fetching)

        except Exception as e:
            logger.error(f"Button state update error: {e}")

    @property
    def last_query_params(self) -> Optional[Dict[str, Any]]:
        """Utolsó query paraméterek."""
        return self._last_query_params

    @last_query_params.setter
    def last_query_params(self, value: Optional[Dict[str, Any]]) -> None:
        """Utolsó query paraméterek beállítása."""
        self._last_query_params = value
