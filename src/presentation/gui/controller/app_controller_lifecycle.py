# mypy: ignore-errors
"""Lifecycle helpers for the GUI app controller."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .app_controller import AppController


class AppControllerLifecycleMixin:
    """Lifecycle, state access, and shutdown helpers."""

    def get_current_city(self: AppController) -> dict[str, Any] | None:
        """Return the currently selected city."""
        return self.current_city_data.copy() if self.current_city_data else None

    def get_current_weather_data(self: AppController) -> dict[str, Any] | None:
        """Return the current weather data payload."""
        return self.weather_data_handler.get_current_weather_data()

    def cancel_all_operations(self: AppController) -> None:
        """Cancel active operations and broadcast status updates."""
        try:
            self._logger.info("🛑 Cancelling all operations...")
            if self.is_analysis_running():
                self.stop_current_analysis()
            self.worker_manager.cancel_all()
            self.status_updated.emit("🛑 Műveletek megszakítva")
            self._logger.info("✅ Összes művelet megszakítva")
        except Exception as exc:
            self._logger.error(f"Műveletek megszakítási hiba: {exc}")

    def shutdown(self: AppController) -> None:
        """Shutdown the controller and clean up resources."""
        try:
            self._logger.info("🛑 AppController leállítása...")
            self.cancel_all_operations()

            from .analysis_handler.state_management import _cleanup_analysis_state

            _cleanup_analysis_state(self.analysis_handler)
            self.worker_manager.shutdown()
            self.provider_routing.save_preferences()
            self.current_city_data = None
            self.current_weather_data = None
            self.active_search_query = None
            self._logger.info("✅ AppController leállítva (CLEAN ARCHITECTURE REFACTORED)")
        except Exception as exc:
            self._logger.warning(f"⚠️ Controller leállítási hiba: {exc}")
            import traceback

            traceback.print_exc()

    def _load_user_preferences(self: AppController) -> None:
        """Load saved user preferences and emit state signals."""
        try:
            prefs_data = self.provider_routing.load_user_preferences()
            self.provider_selected.emit(prefs_data["selected_provider"])
            self.provider_usage_updated.emit(prefs_data["usage_data"])
            if prefs_data["warning_data"]:
                self.provider_warning.emit(*prefs_data["warning_data"])
            self._logger.info("✅ User preferences betöltve és signalok elküldve")
        except Exception as exc:
            self._logger.error(f"User preferences betöltési hiba: {exc}")
