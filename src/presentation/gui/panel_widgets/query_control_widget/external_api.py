# mypy: ignore-errors
"""
External API methods for QueryControlWidget (SIMPLIFIED).

Egyszerűsített verzió: csak az állapotkezelő API-k maradnak.
"""

import logging
from typing import Any

from PySide6.QtCore import QTimer

logger = logging.getLogger(__name__)


class QueryControlExternalAPI:
    """
    QueryControlWidget külső API (egyszerűsített).

    Csak az állapotkezelő metódusok maradnak.
    """

    def __init__(self, state_manager, ui_builder, event_handlers):
        """
        External API inicializálása.

        Args:
            state_manager: State manager objektum
            ui_builder: UI builder objektum
            event_handlers: Event handlers objektum
        """
        self._state = state_manager
        self._ui = ui_builder
        self._events = event_handlers

    def set_fetching_state(self, is_fetching: bool, message: str = "") -> None:
        """
        Külső fetching állapot beállítása.

        Args:
            is_fetching: Fetching állapot
            message: Opcionális üzenet
        """
        if is_fetching:
            self._state.set_state(self._state.STATE_FETCHING)
            if message and self._ui.progress_text_label:
                self._ui.progress_text_label.setText(message)
        elif self._state.cancel_requested:
            self._state.set_state(self._state.STATE_IDLE)
        else:
            self._state.set_state(self._state.STATE_SUCCESS)

        logger.debug(f"External fetching state set: {is_fetching}")

    def set_error_state(self, error_message: str) -> None:
        """
        Külső error állapot beállítása.

        Args:
            error_message: Hiba üzenet
        """
        self._state.set_state(self._state.STATE_ERROR)

        if self._ui.status_label:
            self._ui.status_label.setText(f"❌ {error_message[:50]}...")

        logger.debug(f"External error state set: {error_message}")

    def update_progress(self, message: str) -> None:
        """
        Progress üzenet frissítése.

        Args:
            message: Progress üzenet
        """
        if self._state.is_fetching and self._ui.progress_text_label:
            self._ui.progress_text_label.setText(message)

        logger.debug(f"Progress updated: {message}")

    def force_reset(self) -> None:
        """
        Kényszerített reset idle állapotba.
        """
        logger.warning("QueryControlWidget force reset triggered")

        # Timer cleanup
        if self._state._auto_reset_timer and self._state._auto_reset_timer.isActive():
            self._state._auto_reset_timer.stop()

        if self._state._progress_update_timer and self._state._progress_update_timer.isActive():
            self._state._progress_update_timer.stop()

        self._state.set_state(self._state.STATE_IDLE)
        self._state.cancel_requested = False

        logger.warning("QueryControlWidget force reset completed")

    def emergency_cancel(self) -> None:
        """
        Emergency cancel - azonnali megszakítás.
        """
        logger.warning("Emergency cancel triggered")

        if self._state.is_fetching:
            self._events.on_cancel_clicked()

        # Force reset after emergency
        QTimer.singleShot(1000, self.force_reset)

    # === State API ===

    def is_fetching(self) -> bool:
        """Fetching állapot lekérdezése."""
        return self._state.is_fetching

    def get_state(self) -> str:
        """Jelenlegi állapot lekérdezése."""
        return self._state.current_state

    def get_last_query_params(self) -> dict[str, Any] | None:
        """Utolsó query paraméterek lekérdezése."""
        return self._events.last_query_params

    def set_last_query_params(self, params: dict[str, Any]) -> None:
        """Utolsó query paraméterek beállítása."""
        self._events.last_query_params = params

    def save_state(self) -> dict[str, Any]:
        """Állapot mentése."""
        return {
            "current_state": self._state.current_state,
            "is_fetching": self._state.is_fetching,
            "last_query_params": self._events.last_query_params,
            "cancel_requested": self._state.cancel_requested,
        }

    def restore_state(self, state: dict[str, Any]) -> bool:
        """Állapot visszaállítása."""
        try:
            if "current_state" in state:
                self._state.set_state(state["current_state"])
            if "cancel_requested" in state:
                self._state.cancel_requested = state["cancel_requested"]
            if "last_query_params" in state:
                self._events.last_query_params = state["last_query_params"]
            return True
        except Exception as e:
            logger.error(f"State restore failed: {e}")
            return False

    def get_debug_info(self) -> dict[str, Any]:
        """Debug információk lekérdezése."""
        return {
            "state": self._state.current_state,
            "is_fetching": self._state.is_fetching,
            "cancel_requested": self._state.cancel_requested,
            "fetch_start_time": self._state.fetch_start_time.isoformat()
            if self._state.fetch_start_time
            else None,
            "auto_reset_timer_active": self._state._auto_reset_timer.isActive()
            if self._state._auto_reset_timer
            else False,
            "progress_timer_active": self._state._progress_update_timer.isActive()
            if self._state._progress_update_timer
            else False,
            "last_query_params": self._events.last_query_params,
        }
