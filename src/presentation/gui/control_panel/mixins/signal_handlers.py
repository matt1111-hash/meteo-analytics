#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Control Panel - Widget Signal Handlers Mixin
Kezeli az összes widget signal routingot a ControlPanel-ben.
"""

from typing import Any


class SignalHandlersMixin:
    """
    Signal handling mixin a ControlPanel számára.
    Kezeli az összes widget belső signalját és routingot.
    """

    def _connect_widget_signals(self) -> None:
        """Widget signalok összekötése - CLEAN SIGNAL ROUTING + MULTI-CITY."""

        # === 1. ANALYSIS TYPE WIDGET ===
        self.analysis_type_widget.analysis_type_changed.connect(self._on_analysis_type_changed)

        # === 2. LOCATION WIDGET ===
        # Kompatibilitási signalok (AppController számára)
        self.location_widget.search_requested.connect(self.search_requested.emit)
        self.location_widget.city_selected.connect(self.city_selected.emit)

        # Internal handling
        self.location_widget.location_changed.connect(self._on_location_changed)

        # 🏙️ === 3. MULTI-CITY WIDGET (ÚJ) ===
        self.multi_city_widget.selection_changed.connect(self._on_multi_city_selection_changed)

        # === 4. DATE RANGE WIDGET ===
        self.date_range_widget.date_range_changed.connect(self._on_date_range_changed)
        self.date_range_widget.date_mode_changed.connect(self._on_date_mode_changed)

        # === 5. PROVIDER WIDGET ===
        self.provider_widget.provider_changed.connect(self._on_provider_changed)

        # === 6. API SETTINGS WIDGET ===
        self.api_settings_widget.api_settings_changed.connect(self._on_api_settings_changed)

        # === 7. QUERY CONTROL WIDGET ===
        self.query_control_widget.fetch_requested.connect(self._on_fetch_requested)
        self.query_control_widget.cancel_requested.connect(self._on_cancel_requested)

        print(
            "🎯 Clean signal routing connected + MULTI-CITY signals - Single analysis_requested signal"
        )

    def _on_analysis_type_changed(self, analysis_type: str) -> None:
        """
        🔧 KRITIKUS FIX: Analysis type változás kezelése + WIDGET STATE PRESERVATION + MULTI-CITY.

        Args:
            analysis_type: Új analysis type ("single_location", "region", "county")
        """
        print(
            f"🎯 DEBUG: Analysis type changed from '{self._last_analysis_type}' to '{analysis_type}'"
        )

        # 1. WIDGET STATES MEGŐRZÉSE (analysis type váltás előtt)
        self._preserve_widget_states()

        # 2. UI FRISSÍTÉSE - JAVÍTOTT VERZIÓ MULTI-CITY TÁMOGATÁSSAL
        self._update_ui_for_analysis_type_fixed(analysis_type)

        # 3. WIDGET STATES VISSZAÁLLÍTÁSA (analysis type váltás után)
        self._restore_widget_states(analysis_type)

        # 4. FETCH BUTTON STATE ÚJRAÉRTÉKELÉSE
        self._update_fetch_button_state_comprehensive()

        # 5. LAST ANALYSIS TYPE TRACKING
        self._last_analysis_type = analysis_type

        print(f"✅ DEBUG: Analysis type change completed: {analysis_type}")

    def _on_location_changed(self, location) -> None:
        """Location változás kezelése."""
        print(f"🌍 Location changed: {location}")

        # Fetch button state frissítése
        self._update_fetch_button_state_comprehensive()

    def _on_multi_city_selection_changed(self, selection_data: dict[str, Any]) -> None:
        """
        🏙️ ÚJ: Multi-city selection változás kezelése.

        Args:
            selection_data: {"mode": "region", "selected": [...], "count": 3, "is_valid": True}
        """
        mode = selection_data.get("mode", "unknown")
        count = selection_data.get("count", 0)
        selected = selection_data.get("selected", [])

        print(f"🏙️ Multi-city selection changed: {mode} mode, {count} items selected")
        print(f"📋 Selected items: {selected[:3]}{'...' if len(selected) > 3 else ''}")  # noqa: PLR2004

        # Fetch button state frissítése
        self._update_fetch_button_state_comprehensive()

    def _on_date_range_changed(self, start_date: str, end_date: str) -> None:
        """Date range változás kezelése."""
        print(f"📅 Date range changed: {start_date} → {end_date}")

        # Fetch button state frissítése
        self._update_fetch_button_state_comprehensive()

    def _on_date_mode_changed(self, date_mode: str) -> None:
        """Date mode változás kezelése."""
        print(f"📅 Date mode changed: {date_mode}")

        # Fetch button state frissítése
        self._update_fetch_button_state_comprehensive()

    def _on_provider_changed(self, provider: str) -> None:
        """Provider változás kezelése."""
        print(f"🎛️ Provider changed: {provider}")

        # Fetch button state frissítése
        self._update_fetch_button_state_comprehensive()

    def _on_api_settings_changed(self, settings: dict[str, Any]) -> None:
        """API settings változás kezelése."""
        print(f"⚙️ API settings changed: {settings}")

        # Fetch button state frissítése
        self._update_fetch_button_state_comprehensive()

    def _on_fetch_requested(self) -> None:
        """
        🎯 FETCH REQUEST KEZELÉSE - FŐSIGNAL KIBOCSÁTÁS + MULTI-CITY TÁMOGATÁS

        Ez a CLEAN ARCHITECTURE központi pontja:
        1. Widget state aggregálás (+ multi-city)
        2. Analysis request building
        3. Validálás
        4. analysis_requested(dict) signal emit
        """
        print("🚀 Fetch requested - generating clean analysis request + multi-city support")

        # Comprehensive analysis request összeállítása
        analysis_request = self._build_analysis_request()

        if self._validate_analysis_request(analysis_request):
            # Fetch state beállítása
            self.query_control_widget.set_fetching_state(True)

            # 🎯 FŐSIGNAL KIBOCSÁTÁSA - CLEAN ARCHITECTURE
            self.analysis_requested.emit(analysis_request)

            print(f"🎯 CLEAN: analysis_requested emitted → {analysis_request['analysis_type']}")

            # 🔧 AUTO-RESET FETCH STATE - Error esetére timeout
            from PySide6.QtCore import QTimer  # noqa: PLC0415

            QTimer.singleShot(2000, self._auto_reset_fetch_state)  # 2 sec után reset

        else:
            print("❌ ERROR: Invalid analysis request")
            # 🔧 FETCH STATE RESET on validation failure
            self.query_control_widget.set_fetching_state(False)
            self.local_error_occurred.emit("Hiányos vagy érvénytelen beállítások")

    def _on_cancel_requested(self) -> None:
        """Cancel request kezelése."""
        print("⛔ Cancel requested")

        # Worker manager stop
        if self.worker_manager:
            self.worker_manager.stop_all_workers()

        # UI reset
        self.query_control_widget.set_fetching_state(False)
        self._update_fetch_button_state_comprehensive()

    def _on_theme_changed(self, theme_name: str) -> None:
        """Theme változás kezelése."""
        print(f"🎨 Theme changed to: {theme_name}")
        # Widget-ek saját maguk kezelik a theme változást
