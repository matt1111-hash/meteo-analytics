"""
External API methods for QueryControlWidget.

Ez a modul tartalmazza a QueryControlWidget külső API metódusait.
"""

from typing import Optional, Dict, Any
from PySide6.QtCore import QTimer
import logging

logger = logging.getLogger(__name__)


class QueryControlExternalAPI:
    """
    QueryControlWidget külső API.

    Ezeket a metódusokat külső komponensek hívják (pl. AppController).
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

        Ez a metódus az AppController-től jön.

        Args:
            is_fetching: Fetching állapot
            message: Opcionális üzenet
        """
        if is_fetching:
            self._state.set_state(self._state.STATE_FETCHING)
            if message and self._ui.progress_text_label:
                self._ui.progress_text_label.setText(message)
        else:
            if self._state.cancel_requested:
                self._state.set_state(self._state.STATE_IDLE)
            else:
                self._state.set_state(self._state.STATE_SUCCESS)

        logger.debug(f"External fetching state set: {is_fetching}, message: {message}")

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

        Emergency esetekre.
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

        Ez a metódus Ctrl+Shift+C shortcut-hoz.
        """
        logger.warning("Emergency cancel triggered")

        if self._state.is_fetching:
            self._events.on_cancel_clicked()

        # Force reset after emergency
        QTimer.singleShot(1000, self.force_reset)

    # Public API methods

    def get_current_query_params(self) -> Optional[Dict[str, Any]]:
        """
        Jelenlegi query paraméterek lekérdezése.

        Returns:
            dict: Query paraméterek vagy None
        """
        return self._events.last_query_params

    def get_current_location(self) -> Optional[tuple]:
        """
        Jelenlegi helység lekérdezése.

        Returns:
            tuple: (city, country, lat, lon) vagy None
        """
        if self._events.location_widget:
            city = self._events.location_widget.get_current_city()
            coordinates = self._events.location_widget.get_current_coordinates()
            return (city, "Hungary", coordinates[0], coordinates[1])
        return None

    def is_valid(self) -> bool:
        """
        Widget validálása.

        Returns:
            bool: True ha minden adat valid
        """
        return self._events._validator.is_query_valid()

    def is_fetching(self) -> bool:
        """
        Fetching állapot lekérdezése.

        Returns:
            bool: True ha fetching állapotban
        """
        return self._state.is_fetching

    def get_state(self) -> str:
        """
        Jelenlegi állapot lekérdezése.

        Returns:
            str: idle/fetching/error/success
        """
        return self._state.current_state

    # State persistence

    def save_state(self) -> Dict[str, Any]:
        """
        Állapot mentése.

        Returns:
            dict: Widget állapot
        """
        state = {
            "current_state": self._state.current_state,
            "is_fetching": self._state.is_fetching,
            "last_query_params": self._events.last_query_params,
            "cancel_requested": self._state.cancel_requested
        }

        # Widget states
        if self._events.location_widget:
            state["location"] = self._events.location_widget.get_current_city()

        if self._events.date_range_widget:
            state["date_range"] = self._events.date_range_widget.get_date_range()

        if self._events.parameters_widget:
            state["parameters"] = self._events.parameters_widget.get_selected_parameters()

        if self._events.provider_widget:
            state["provider"] = self._events.provider_widget.get_current_provider()

        return state

    def restore_state(self, state: Dict[str, Any]) -> bool:
        """
        Állapot visszaállítása.

        Args:
            state: Widget állapot

        Returns:
            bool: Sikeres volt-e
        """
        try:
            # Restore basic state
            if "current_state" in state:
                self._state.set_state(state["current_state"])

            if "cancel_requested" in state:
                self._state.cancel_requested = state["cancel_requested"]

            if "last_query_params" in state:
                self._events.last_query_params = state["last_query_params"]

            logger.debug("QueryControlWidget state restored")
            return True

        except Exception as e:
            logger.error(f"QueryControlWidget state restore failed: {e}")
            return False

    # Debug support

    def get_debug_info(self, widget_availability: Dict[str, bool]) -> Dict[str, Any]:
        """
        Debug információk lekérdezése.

        Args:
            widget_availability: Widget elérhetőségi info

        Returns:
            dict: Debug adatok
        """
        return {
            "state": self._state.current_state,
            "is_fetching": self._state.is_fetching,
            "cancel_requested": self._state.cancel_requested,
            "fetch_start_time": self._state.fetch_start_time.isoformat() if self._state.fetch_start_time else None,
            "auto_reset_timer_active": self._state._auto_reset_timer.isActive() if self._state._auto_reset_timer else False,
            "progress_timer_active": self._state._progress_update_timer.isActive() if self._state._progress_update_timer else False,
            "last_query_params": self._events.last_query_params,
            "is_valid": self._events._validator.is_query_valid(),
            "widget_availability": widget_availability
        }
