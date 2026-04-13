#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Analytics Sync Core - Main sync methods.

Provides the primary analytics-to-map synchronization methods.
"""

from datetime import datetime
from typing import Any


def _apply_analysis_parameter_update(core: "AnalyticsSyncCore", params: dict[str, Any]) -> None:
    """Apply analysis parameters to the map."""
    analysis_type = params.get("analysis_type", "single_location")
    if analysis_type == "single_location":
        location = params.get("location")
        if location:
            core._update_map_for_single_location(location)
        return
    if analysis_type == "region":
        region = params.get("region")
        if region:
            core._update_map_for_region(region)
        return
    if analysis_type == "county":
        county = params.get("county")
        if county:
            core._update_map_for_county(county)


class AnalyticsSyncCore:
    """
    Core analytics sync functionality.

    Main sync methods for coordinating analytics parameters with map display.
    """

    def update_analysis_parameters(self, params: dict[str, Any]) -> None:
        """
        Sync analysis parameters from Control Panel to map.

        Args:
            params: Analysis parameters dict with keys:
                - analysis_type: "single_location", "region", or "county"
                - location: Location object (for single_location)
                - region: Region name (for region)
                - county: County name (for county)
        """
        if self.sync_in_progress:
            return

        try:
            self.sync_in_progress = True
            self._set_sync_status("analysis", "in_progress")

            _apply_analysis_parameter_update(self, params)
            self.last_analysis_parameters = params.copy()

            if self.auto_weather_refresh_enabled and self.current_analytics_result:
                self._refresh_weather_overlay()

            self._set_sync_status("analysis", "success")
            self.analytics_sync_completed.emit("analysis_parameters")

        except Exception as e:
            self._set_sync_status("analysis", "error")
            self._on_error_occurred(f"Analysis sync error: {e}")
        finally:
            self.sync_in_progress = False

    def update_weather_parameters(self, params: dict[str, Any]) -> None:
        """
        Sync weather parameters from Control Panel to map.

        Args:
            params: Weather parameters dict with keys:
                - provider: "auto", "open-meteo", or "meteostat"
                - timeout: API timeout value
                - cache: Whether caching is enabled
                - timezone: Timezone setting
        """
        if self.sync_in_progress:
            return

        try:
            self.sync_in_progress = True
            self._set_sync_status("weather", "in_progress")

            provider = params.get("provider", "auto")
            cache = params.get("cache", True)

            self._refresh_weather_overlays(provider, cache)

            self.last_weather_parameters = params.copy()
            self._set_sync_status("weather", "success")
            self.analytics_sync_completed.emit("weather_parameters")

        except Exception as e:
            self._set_sync_status("weather", "error")
            self._on_error_occurred(f"Weather sync error: {e}")
        finally:
            self.sync_in_progress = False

    def update_date_range(self, start_date: str, end_date: str) -> None:
        """
        Sync date range from Control Panel to map.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        """
        if self.sync_in_progress:
            return

        try:
            self.sync_in_progress = True
            self._set_sync_status("date", "in_progress")

            self._refresh_temporal_data(start_date, end_date)

            self.last_date_parameters = {
                "start_date": start_date,
                "end_date": end_date,
                "timestamp": datetime.now().isoformat(),
            }

            if self.auto_weather_refresh_enabled and self.current_analytics_result:
                self._refresh_weather_overlay_with_new_dates(start_date, end_date)

            self._set_sync_status("date", "success")
            self.analytics_sync_completed.emit("date_range")

        except Exception as e:
            self._set_sync_status("date", "error")
            self._on_error_occurred(f"Date sync error: {e}")
        finally:
            self.sync_in_progress = False

    def refresh_with_new_parameters(self, bundle: dict[str, Any]) -> None:
        """
        Comprehensive map refresh with full parameter bundle.

        Args:
            bundle: Full parameter bundle with keys:
                - analysis: Analysis parameters
                - weather: Weather parameters
                - date: Date parameters
                - timestamp: Bundle timestamp
        """
        if self.sync_in_progress:
            return

        try:
            self.sync_in_progress = True
            self._set_sync_status("full", "in_progress")

            analysis = bundle.get("analysis", {})
            weather = bundle.get("weather", {})
            date = bundle.get("date", {})

            self._full_map_refresh(analysis, weather, date)

            self.last_analysis_parameters = analysis.copy()
            self.last_weather_parameters = weather.copy()
            self.last_date_parameters = date.copy()

            self._set_sync_status("full", "success")
            self.analytics_sync_completed.emit("parameter_bundle")

        except Exception as e:
            self._set_sync_status("full", "error")
            self._on_error_occurred(f"Bundle sync error: {e}")
        finally:
            self.sync_in_progress = False

    def _set_sync_status(self, sync_type: str, status: str) -> None:
        """Update sync status label."""
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

        if hasattr(self, "analytics_sync_label"):
            self.analytics_sync_label.setText(f"{label} {text}")
            self.analytics_sync_label.setStyleSheet(f"color: {color};")


__all__ = ["AnalyticsSyncCore"]
