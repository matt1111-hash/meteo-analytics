#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Control Panel - External Handlers Mixin
External signal handlers, geocoding, progress updates.
"""

from typing import Any, Dict, List


class ExternalHandlersMixin:
    """
    External handlers mixin a ControlPanel számára.
    Kezeli a külső signalokat és callbackeket.
    """

    # === EXTERNAL SIGNAL HANDLERS (UNCHANGED) ===

    def _auto_reset_fetch_state(self) -> None:
        """🔧 AUTO-RESET: Fetch state reset timeout esetére."""
        if self.query_control_widget._state.is_fetching:
            print("🔧 DEBUG: Auto-resetting fetch state after timeout")
            self.query_control_widget.set_fetching_state(False)
            # 🔥 KRITIKUS FIX: set_progress_text → update_progress
            self.query_control_widget.update_progress("⏰ Timeout - próbálja újra")
            self._update_fetch_button_state_comprehensive()

    def on_weather_data_completed(self) -> None:
        """Weather data lekérdezés befejezése külső jelzés alapján."""
        self.query_control_widget.set_fetching_state(False)
        # 🔥 KRITIKUS FIX: set_progress_text → update_progress
        self.query_control_widget.update_progress("✅ Adatok sikeresen lekérdezve")
        self._update_fetch_button_state_comprehensive()

        print("✅ Weather data completed - UI updated")

    def on_controller_error(self, error_message: str) -> None:
        """Hiba kezelése külső jelzés alapján."""
        self.query_control_widget.set_fetching_state(False)
        # 🔥 KRITIKUS FIX: set_progress_text → update_progress
        self.query_control_widget.update_progress(f"❌ Hiba: {error_message}")
        self._update_fetch_button_state_comprehensive()

        self.local_error_occurred.emit(error_message)

        print(f"❌ Controller error: {error_message}")

    def update_progress(self, worker_type: str, progress: int) -> None:
        """Progress frissítése külső jelzés alapján."""
        if 0 <= progress <= 100:
            self.query_control_widget.set_progress_value(progress)
            # 🔥 KRITIKUS FIX: set_progress_text → update_progress
            self.query_control_widget.update_progress(f"⏳ {worker_type}: {progress}%")

        if progress >= 100:
            # 🔥 KRITIKUS FIX: set_progress_text → update_progress
            self.query_control_widget.update_progress("✅ Befejezve")

    def update_status_from_controller(self, message: str) -> None:
        """Status frissítése külső controller-ből."""
        # 🔥 KRITIKUS FIX: set_progress_text → update_progress
        self.query_control_widget.update_progress(message)
        print(f"📊 Status update: {message}")

    # === GEOCODING COMPATIBILITY HANDLERS (UNCHANGED) ===

    def _on_geocoding_completed(self, results: List[Dict[str, Any]]) -> None:
        """Geocoding eredmények fogadása - LocationWidget-re továbbítás."""
        if hasattr(self.location_widget, "update_search_results"):
            self.location_widget.update_search_results(results)

        print(f"🔍 Geocoding completed: {len(results)} results")

    def _on_geocoding_error(self, error_message: str) -> None:
        """Geocoding hiba fogadása."""
        self.local_error_occurred.emit(f"Keresési hiba: {error_message}")
        print(f"❌ Geocoding error: {error_message}")

    # === CLEANUP ===

    def cleanup(self) -> None:
        """ControlPanel cleanup - widget cleanup-ok hívása + MULTI-CITY."""
        # Provider widget cleanup (timer leállítása)
        if hasattr(self.provider_widget, "cleanup"):
            self.provider_widget.cleanup()

        # 🏙️ Multi-city widget cleanup (ha van)
        if hasattr(self.multi_city_widget, "cleanup"):
            self.multi_city_widget.cleanup()

        print("🧹 ControlPanel cleanup completed + MultiCityWidget")

    def __del__(self):
        """Destruktor."""
        try:
            self.cleanup()
        except Exception:
            pass
