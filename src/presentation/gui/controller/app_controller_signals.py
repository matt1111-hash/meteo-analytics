# mypy: ignore-errors
"""Signal wiring and external request handlers for the app controller."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Slot

if TYPE_CHECKING:
    from .app_controller import AppController


class AppControllerSignalsMixin:
    """Signal registration and lightweight forwarding methods."""

    def _connect_geocoding_signals(self: AppController) -> None:
        """Connect geocoding handler signals."""
        self.geocoding_handler.geocoding_results_ready.connect(self.geocoding_results_ready)
        self.geocoding_handler.city_saved_to_db.connect(self.city_saved_to_db)
        self.geocoding_handler.error_occurred.connect(self.error_occurred)
        self.geocoding_handler.status_updated.connect(self.status_updated)

    def _connect_weather_data_signals(self: AppController) -> None:
        """Connect weather data handler signals."""
        self.weather_data_handler.weather_data_ready.connect(self.weather_data_ready)
        self.weather_data_handler.weather_saved_to_db.connect(self.weather_saved_to_db)
        self.weather_data_handler.error_occurred.connect(self.error_occurred)
        self.weather_data_handler.status_updated.connect(self.status_updated)

    def _connect_analysis_signals(self: AppController) -> None:
        """Connect analysis and worker manager signals."""
        self.analysis_handler.analysis_started.connect(self.analysis_started)
        self.analysis_handler.analysis_progress.connect(self.analysis_progress)
        self.analysis_handler.analysis_completed.connect(self._on_analysis_completed_forward)
        self.analysis_handler.analysis_failed.connect(self.analysis_failed)
        self.analysis_handler.analysis_cancelled.connect(self.analysis_cancelled)
        self.analysis_handler.status_updated.connect(self.status_updated)

        self.worker_manager.weather_data_completed.connect(
            self.weather_data_handler.on_weather_data_completed
        )
        self.worker_manager.error_occurred.connect(self.error_occurred)
        self.worker_manager.progress_updated.connect(self.progress_updated.emit)

    @Slot(str)
    def handle_search_request(self: AppController, search_query: str) -> None:
        """Pass a geocoding search to the dedicated handler."""
        self.geocoding_handler.handle_search_request(search_query)

    @Slot(str, float, float, dict)
    def handle_city_selection(
        self: AppController,
        city_name: str,
        latitude: float,
        longitude: float,
        metadata: dict[str, Any],
    ) -> None:
        """Update the current city and weather context from a selection."""
        self.current_city_data = self.geocoding_handler.handle_city_selection(
            city_name,
            latitude,
            longitude,
            metadata,
        )
        self.weather_data_handler.set_current_city(self.current_city_data)

    @Slot(str)
    def handle_provider_change(self: AppController, provider_name: str) -> None:
        """Handle provider changes initiated by the GUI."""
        status_msg = self.provider_routing.handle_provider_change(provider_name)
        self.provider_selected.emit(provider_name)
        self.status_updated.emit(status_msg)

    def get_provider_info(self: AppController) -> dict[str, Any]:
        """Return provider information for the GUI."""
        return self.provider_routing.get_provider_info()
