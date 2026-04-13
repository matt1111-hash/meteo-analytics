# mypy: ignore-errors
from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import QObject, Signal

from .interfaces import IMapAnalyticsBridge
from .map_analytics_bridge_support import (
    apply_analysis_update,
    apply_full_refresh,
    run_sync_operation,
)


class MapAnalyticsBridge(QObject, IMapAnalyticsBridge):
    """
    Bridge for synchronizing analytics data with the map.
    Handles parameter updates and triggers map refreshes.
    """

    # Signals to communicate status updates back to the UI
    analytics_sync_completed = Signal(str)  # type of sync
    sync_error_occurred = Signal(str)  # error message
    status_update_requested = Signal(str, str)  # label, color

    def __init__(self, parent=None):  # noqa: D107
        super().__init__(parent)
        self.map_visualizer = None
        self.location_selector = None
        self.multi_city_engine = None
        self.sync_in_progress = False

        # State memory
        self.last_analysis_parameters: dict[str, Any] = {}
        self.last_weather_parameters: dict[str, Any] = {}
        self.last_date_parameters: dict[str, Any] = {}

        self.current_analytics_result = None
        self.current_weather_overlay = None
        self.auto_weather_refresh_enabled = True

    def set_components(self, map_visualizer, location_selector, multi_city_engine):
        """Inject dependencies."""
        self.map_visualizer = map_visualizer
        self.location_selector = location_selector
        self.multi_city_engine = multi_city_engine

    def sync_analysis_parameters(self, params: dict[str, Any]) -> None:
        """Sync analysis parameters from Control Panel to map."""

        def operation() -> None:
            apply_analysis_update(self, params)
            self.last_analysis_parameters = params.copy()
            if self.auto_weather_refresh_enabled and self.current_analytics_result:
                pass

        run_sync_operation(self, "analysis", "analysis_parameters", operation)

    def sync_weather_parameters(self, params: dict[str, Any]) -> None:
        """Sync weather parameters from Control Panel to map."""
        if self.sync_in_progress:
            return

        try:
            self.sync_in_progress = True
            self._emit_status("weather", "in_progress")

            provider = params.get("provider", "auto")
            cache = params.get("cache", True)

            self._refresh_weather_overlays(provider, cache)

            self.last_weather_parameters = params.copy()
            self._emit_status("weather", "success")
            self.analytics_sync_completed.emit("weather_parameters")

        except Exception as e:
            self._emit_status("weather", "error")
            self.sync_error_occurred.emit(f"Weather sync error: {e}")
        finally:
            self.sync_in_progress = False

    def update_date_range(self, start_date: str, end_date: str) -> None:
        """Sync date range from Control Panel to map."""
        if self.sync_in_progress:
            return

        try:
            self.sync_in_progress = True
            self._emit_status("date", "in_progress")

            self._refresh_temporal_data(start_date, end_date)

            self.last_date_parameters = {
                "start_date": start_date,
                "end_date": end_date,
                "timestamp": datetime.now().isoformat(),
            }

            self._emit_status("date", "success")
            self.analytics_sync_completed.emit("date_range")

        except Exception as e:
            self._emit_status("date", "error")
            self.sync_error_occurred.emit(f"Date sync error: {e}")
        finally:
            self.sync_in_progress = False

    def refresh_with_new_parameters(self, bundle: dict[str, Any]) -> None:
        """Comprehensive map refresh with full parameter bundle."""
        if self.sync_in_progress:
            return

        try:
            self.sync_in_progress = True
            self._emit_status("full", "in_progress")

            analysis = bundle.get("analysis", {})
            weather = bundle.get("weather", {})
            date = bundle.get("date", {})

            self._full_map_refresh(analysis, weather, date)

            self.last_analysis_parameters = analysis.copy()
            self.last_weather_parameters = weather.copy()
            self.last_date_parameters = date.copy()

            self._emit_status("full", "success")
            self.analytics_sync_completed.emit("parameter_bundle")

        except Exception as e:
            self._emit_status("full", "error")
            self.sync_error_occurred.emit(f"Bundle sync error: {e}")
        finally:
            self.sync_in_progress = False

    # --- Internal Helpers ---

    def _update_map_for_single_location(self, location: dict[str, Any]) -> None:
        if self.map_visualizer:
            lat = location.get("latitude")
            lon = location.get("longitude")
            name = location.get("display_name", location.get("name", "Unknown"))

            if lat is not None and lon is not None:
                bounds = (lon - 0.1, lat - 0.1, lon + 0.1, lat + 0.1)
                self.map_visualizer.update_map_bounds(bounds)
                if hasattr(self.map_visualizer, "add_location_marker"):
                    self.map_visualizer.add_location_marker(lat, lon, name)

    def _update_map_for_region(self, region: str) -> None:
        if self.location_selector:
            self.location_selector.set_region(region)

    def _update_map_for_county(self, county: str) -> None:
        if self.location_selector:
            self.location_selector.set_county(county)

    def _refresh_weather_overlays(self, provider: str, cache: bool) -> None:
        if not self.multi_city_engine:
            return

        if hasattr(self.multi_city_engine, "set_provider"):
            self.multi_city_engine.set_provider(provider)

        if hasattr(self.multi_city_engine, "set_cache_enabled"):
            self.multi_city_engine.set_cache_enabled(cache)

    def _refresh_temporal_data(self, start_date: str, end_date: str) -> None:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            if start_dt > end_dt:
                return
        except ValueError:
            return

        if self.multi_city_engine and hasattr(self.multi_city_engine, "set_date_range"):
            self.multi_city_engine.set_date_range(start_date, end_date)

    def _full_map_refresh(self, analysis: dict, weather: dict, date: dict) -> None:
        apply_full_refresh(self, analysis, weather, date)

    def _emit_status(self, sync_type: str, status: str) -> None:
        labels = {
            "analysis": "Analysis",
            "weather": "Weather",
            "date": "Date",
            "full": "Full",
        }
        status_text = {
            "in_progress": ("Sync...", "#F39C12"),
            "success": ("Sync OK", "#27AE60"),
            "error": ("Sync Error", "#E74C3C"),
        }

        label = labels.get(sync_type, sync_type)
        text, color = status_text.get(status, ("?", "#95A5A6"))
        self.status_update_requested.emit(f"{label} {text}", color)
