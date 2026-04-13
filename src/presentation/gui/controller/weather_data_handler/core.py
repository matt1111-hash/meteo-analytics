# mypy: ignore-errors
"""Weather Data Handler Core."""

import logging
from typing import Any

from PySide6.QtCore import QObject, Signal, Slot
from src.presentation.gui.controller.weather_data_handler.processor import (
    calculate_daily_max_wind_gusts,
    process_weather_data,
)


class WeatherDataHandler(QObject):
    """
    Weather data processing handler.

    Responsibilities:
    - Weather data processing
    - Wind speed and wind gusts handling
    - Daily maximum wind gusts calculation
    - Database persistence
    """

    weather_data_ready = Signal(dict)
    weather_saved_to_db = Signal(bool)
    error_occurred = Signal(str)
    status_updated = Signal(str)

    def __init__(self, database_manager: Any, parent: QObject | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self.database_manager = database_manager
        self._logger = logging.getLogger(__name__)
        self.current_city_data: dict[str, Any] | None = None
        self.current_weather_data: dict[str, Any] | None = None

    def set_current_city(self, city_data: dict[str, Any]) -> None:
        """Set current city."""
        self.current_city_data = city_data

    @Slot(dict)
    def on_weather_data_completed(self, data: dict[str, Any]) -> None:
        """Handle completed weather data (backwards compatibility)."""
        self._logger.info("on_weather_data_completed called")

        try:
            used_provider = data.get("provider", "unknown")
            self._logger.info(f"Weather data from provider: {used_provider}")

            processed_data = process_weather_data(data, self.current_city_data)

            if not processed_data:
                self.error_occurred.emit("No processable weather data")
                return

            processed_data["provider"] = used_provider
            self.current_weather_data = processed_data

            self._save_weather_to_database(processed_data)

            city_name = (
                self.current_city_data.get("name", "Unknown")
                if self.current_city_data
                else "Unknown"
            )
            record_count = len(processed_data.get("daily", {}).get("time", []))

            wind_gusts_info = ""
            if "wind_gusts_max" in processed_data.get("daily", {}):
                wind_gusts_max = processed_data["daily"]["wind_gusts_max"]
                if wind_gusts_max:
                    max_gust = max([g for g in wind_gusts_max if g is not None])
                    wind_gusts_info = f", max gust: {max_gust:.1f} km/h"

            from src.config import ProviderConfig  # noqa: PLC0415

            provider_config = ProviderConfig()
            provider_display = provider_config.PROVIDERS.get(used_provider, {}).get(
                "name", used_provider
            )

            self.status_updated.emit(
                f"Data received ({provider_display}): {city_name} ({record_count} days{wind_gusts_info})"
            )

            self.weather_data_ready.emit(processed_data)

        except Exception as e:
            self._logger.error(f"Weather data processing error: {e}")
            self.error_occurred.emit(f"Processing error: {e}")

    def _process_weather_data(self, raw_data: dict[str, Any]) -> dict[str, Any] | None:
        """Process weather data with wind support."""
        return process_weather_data(raw_data, self.current_city_data)

    def _calculate_daily_max_wind_gusts(
        self, hourly_gusts: list, hourly_times: list, daily_times: list
    ) -> list:
        """Calculate daily maximum wind gusts."""
        return calculate_daily_max_wind_gusts(hourly_gusts, hourly_times, daily_times)

    def _save_weather_to_database(self, weather_data: dict[str, Any]) -> None:
        """Save weather data to database."""
        try:
            success = self.database_manager.save_weather_to_database(
                weather_data, self.current_city_data
            )
            self.weather_saved_to_db.emit(success)
        except Exception as e:
            self._logger.error(f"Database save error: {e}")
            self.weather_saved_to_db.emit(False)

    def get_current_weather_data(self) -> dict[str, Any] | None:
        """Get current weather data."""
        return self.current_weather_data.copy() if self.current_weather_data else None

    def get_current_city_data(self) -> dict[str, Any] | None:
        """Get current city data."""
        return self.current_city_data.copy() if self.current_city_data else None
