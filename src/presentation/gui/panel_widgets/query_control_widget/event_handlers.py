"""
Event handlers for QueryControlWidget.

Ez a modul tartalmazza a QueryControlWidget eseménykezelőit.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from PySide6.QtCore import Signal
import logging

logger = logging.getLogger(__name__)


class QueryControlEventHandlers:
    """
    QueryControlWidget eseménykezelők.

    Kezeli a widget eseményeit: kattintások, változások, stb.
    """

    def __init__(self, validator, state_manager, ui_builder):
        """
        Event handlers inicializálása.

        Args:
            validator: Query validator objektum
            state_manager: State manager objektum
            ui_builder: UI builder objektum
        """
        self._validator = validator
        self._state = state_manager
        self._ui = ui_builder

        # Query params
        self._last_query_params: Optional[Dict[str, Any]] = None

        # Widgets (ezeket kívülről kell beállítani)
        self.location_widget = None
        self.date_range_widget = None
        self.parameters_widget = None
        self.provider_widget = None

        # Signals (ezeket kívülről kell beállítani)
        self.query_requested: Optional[Signal] = None
        self.fetch_requested: Optional[Signal] = None
        self.location_changed: Optional[Signal] = None
        self.cancel_requested: Optional[Signal] = None
        self.validation_changed: Optional[Signal] = None

    def connect_widget_signals(self) -> None:
        """Widget signalok csatlakoztatása."""
        logger.debug("QueryControlEventHandlers.connect_widget_signals() START")

        # Location changes
        if self.location_widget:
            self.location_widget.location_selected.connect(self._on_location_changed)
            if hasattr(self.location_widget, 'selection_changed'):
                self.location_widget.selection_changed.connect(self._on_location_changed_simple)

        # Date range changes
        if self.date_range_widget:
            self.date_range_widget.date_range_changed.connect(self._on_date_range_changed)

        # Parameters changes
        if self.parameters_widget:
            self.parameters_widget.parameters_changed.connect(self._on_parameters_changed)

        # Provider changes
        if self.provider_widget:
            self.provider_widget.provider_changed.connect(self._on_provider_changed)

        logger.debug("QueryControlEventHandlers.connect_widget_signals() BEFEJEZVE")

    def _on_location_changed(self, city: str, country: str, lat: float, lon: float) -> None:
        """Helység változás kezelése."""
        logger.debug(f"Location changed: {city}, {country} ({lat}, {lon})")
        if self.location_changed:
            self.location_changed.emit(city, country, lat, lon)
        self._update_button_states()
        self._emit_validation_state()

    def _on_location_changed_simple(self, location: str) -> None:
        """Egyszerű helység változás kezelése."""
        logger.debug(f"Location changed (simple): {location}")
        self._update_button_states()
        self._emit_validation_state()

    def _on_date_range_changed(self, start_date: object, end_date: object) -> None:
        """Dátum tartomány változás kezelése."""
        logger.debug(f"Date range changed: {start_date} - {end_date}")
        self._update_button_states()
        self._emit_validation_state()

    def _on_parameters_changed(self, parameters: list) -> None:
        """Paraméterek változás kezelése."""
        logger.debug(f"Parameters changed: {parameters}")
        self._update_button_states()
        self._emit_validation_state()

    def _on_provider_changed(self, provider: str) -> None:
        """Provider változás kezelése."""
        logger.debug(f"Provider changed: {provider}")
        self._update_button_states()
        self._emit_validation_state()

    def on_query_clicked(self) -> None:
        """Lekérdezés gomb kattintás kezelése."""
        logger.info("Query button clicked - starting data fetch")

        if not self._validator.is_query_valid():
            logger.warning("Query validation failed")
            print("🚨 DEBUG: Query clicked but validation failed!")
            return

        if self._state.is_fetching:
            logger.warning("Already fetching - ignoring query click")
            return

        query_params = self._build_query_parameters()

        if query_params:
            self._last_query_params = query_params
            self._state.set_state(self._state.STATE_FETCHING)
            if self.query_requested:
                self.query_requested.emit(query_params)
            if self.fetch_requested:
                self.fetch_requested.emit(query_params)
            logger.info(f"Query started with params: {query_params}")
        else:
            logger.error("Failed to build query parameters")
            self._state.set_state(self._state.STATE_ERROR)

    def on_cancel_clicked(self) -> None:
        """Megszakítás gomb kattintás kezelése."""
        logger.info("Cancel button clicked - requesting cancellation")

        self._state.cancel_requested = True
        if self.cancel_requested:
            self.cancel_requested.emit()

        # Immediate UI feedback
        if self._ui.status_label:
            self._ui.status_label.setText("🚫 Megszakítás...")
            self._ui.status_label.setStyleSheet("color: #f59e0b; font-weight: bold;")

        # Auto-reset after cancellation
        self._state._start_auto_reset(2000)  # 2 seconds

    def _build_query_parameters(self) -> Optional[Dict[str, Any]]:
        """Lekérdezési paraméterek összeállítása."""
        try:
            params = {}

            # Location data
            if self.location_widget:
                city = self.location_widget.get_current_city()
                coordinates = self.location_widget.get_current_coordinates()
                params["city"] = city
                params["latitude"] = coordinates[0]
                params["longitude"] = coordinates[1]
                print(f"📍 DEBUG: Query params location - city: {city}, coords: {coordinates}")

            # Date range
            if self.date_range_widget:
                start_date, end_date = self.date_range_widget.get_date_range()
                params["start_date"] = start_date
                params["end_date"] = end_date
                print(f"📅 DEBUG: Query params date range - {start_date} to {end_date}")

            # Parameters
            if self.parameters_widget:
                parameters = self.parameters_widget.get_selected_parameters()
                params["parameters"] = parameters
                print(f"🌡️ DEBUG: Query params parameters - {len(parameters)} items")

            # Provider
            if self.provider_widget:
                provider = self.provider_widget.get_current_provider()
                params["provider"] = provider
                print(f"🌐 DEBUG: Query params provider - {provider}")

            # Timestamp
            params["timestamp"] = datetime.now()

            print(f"✅ DEBUG: Query parameters built successfully: {list(params.keys())}")
            return params

        except Exception as e:
            logger.error(f"Query parameters build error: {e}")
            print(f"❌ DEBUG: Query parameters build error: {e}")
            return None

    def _update_button_states(self) -> None:
        """Gomb állapotok frissítése."""
        try:
            is_valid = self._validator.is_query_valid()
            is_fetching = self._state.is_fetching

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

            logger.debug(f"Button states updated: valid={is_valid}, fetching={is_fetching}")

        except Exception as e:
            logger.error(f"Button state update error: {e}")

    def _emit_validation_state(self) -> None:
        """Validálási állapot jelzése."""
        if self.validation_changed:
            is_valid = self._validator.is_query_valid()
            self.validation_changed.emit(is_valid)

    @property
    def last_query_params(self) -> Optional[Dict[str, Any]]:
        """Utolsó query paraméterek."""
        return self._last_query_params

    @last_query_params.setter
    def last_query_params(self, value: Optional[Dict[str, Any]]) -> None:
        """Utolsó query paraméterek beállítása."""
        self._last_query_params = value
