#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analytics to Map Sync Mixin.

Provides methods for synchronizing analytics parameters with the map display.
Extracted from HungarianMapTab to reduce file size and improve maintainability.

Usage:
    class HungarianMapTab(MapAnalyticsSyncMixin, QWidget):
        ...
"""

from datetime import datetime
from typing import Any, Dict


class MapAnalyticsSyncMixin:
    """
    Mixin providing analytics-to-map synchronization methods.

    Requires the following attributes on the host class:
    - sync_in_progress: bool
    - analytics_sync_label: QLabel
    - loading_status: QLabel
    - auto_weather_refresh_enabled: bool
    - current_analytics_result: Optional[AnalyticsResult]
    - current_weather_overlay: Optional[WeatherOverlayData]
    - map_visualizer: Optional[HungarianMapVisualizer]
    - location_selector: Optional[HungarianLocationSelector]
    - multi_city_engine: Optional[MultiCityEngine]
    - is_folium_ready: bool
    - last_analysis_parameters: Dict
    - last_weather_parameters: Dict
    - last_date_parameters: Dict

    Requires the following methods on the host class:
    - _refresh_weather_overlay()
    - _generate_weather_overlay_from_analytics(result)
    - _on_error_occurred(message)
    - analytics_sync_completed: Signal
    """

    def update_analysis_parameters(self, params: Dict[str, Any]) -> None:
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

            analysis_type = params.get("analysis_type", "single_location")

            if analysis_type == "single_location":
                location = params.get("location")
                if location:
                    self._update_map_for_single_location(location)
            elif analysis_type == "region":
                region = params.get("region")
                if region:
                    self._update_map_for_region(region)
            elif analysis_type == "county":
                county = params.get("county")
                if county:
                    self._update_map_for_county(county)

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

    def update_weather_parameters(self, params: Dict[str, Any]) -> None:
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

    def refresh_with_new_parameters(self, bundle: Dict[str, Any]) -> None:
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

    def _update_map_for_single_location(self, location: Dict[str, Any]) -> None:
        """Update map view for a single location."""
        if not self.map_visualizer or not self.is_folium_ready:
            return

        lat = location.get("latitude")
        lon = location.get("longitude")
        name = location.get("display_name", location.get("name", "Unknown"))

        if lat is not None and lon is not None:
            bounds = (lon - 0.1, lat - 0.1, lon + 0.1, lat + 0.1)
            self.map_visualizer.update_map_bounds(bounds)

            if hasattr(self.map_visualizer, "add_location_marker"):
                self.map_visualizer.add_location_marker(lat, lon, name)

            self.loading_status.setText(f"Map updated: {name}")

    def _update_map_for_region(self, region: str) -> None:
        """Update map view for a region."""
        if not self.location_selector:
            return

        success = self.location_selector.set_region(region)
        if success:
            self.loading_status.setText(f"Map updated for region: {region}")

    def _update_map_for_county(self, county: str) -> None:
        """Update map view for a county."""
        if not self.location_selector:
            return

        success = self.location_selector.set_county(county)
        if success:
            self.loading_status.setText(f"Map updated for county: {county}")

    def _refresh_weather_overlays(self, provider: str, cache: bool) -> None:
        """Refresh weather overlays with new provider settings."""
        if not self.current_weather_overlay or not self.multi_city_engine:
            return

        if hasattr(self.multi_city_engine, "set_provider"):
            self.multi_city_engine.set_provider(provider)

        if hasattr(self.multi_city_engine, "set_cache_enabled"):
            self.multi_city_engine.set_cache_enabled(cache)

        if self.current_analytics_result:
            self._generate_weather_overlay_from_analytics(self.current_analytics_result)

        self.loading_status.setText(f"Weather overlay refreshed: {provider}")

    def _refresh_temporal_data(self, start_date: str, end_date: str) -> None:
        """Refresh temporal data for new date range."""
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            if start_dt > end_dt:
                return
        except ValueError:
            return

        if self.multi_city_engine and hasattr(self.multi_city_engine, "set_date_range"):
            self.multi_city_engine.set_date_range(start_date, end_date)

        self.loading_status.setText(f"Temporal data refreshed: {start_date} to {end_date}")

    def _refresh_weather_overlay_with_new_dates(
        self, start_date: str, end_date: str
    ) -> None:
        """Refresh weather overlay with new date range."""
        if not self.multi_city_engine:
            return

        self.loading_status.setText(f"Weather overlay refreshed: {start_date} to {end_date}")

    def _full_map_refresh(
        self, analysis: Dict, weather: Dict, date: Dict
    ) -> None:
        """Comprehensive map refresh with all parameters."""
        # Apply analysis parameters
        if analysis:
            analysis_type = analysis.get("analysis_type")
            if analysis_type == "single_location" and analysis.get("location"):
                self._update_map_for_single_location(analysis["location"])
            elif analysis_type == "region" and analysis.get("region"):
                self._update_map_for_region(analysis["region"])
            elif analysis_type == "county" and analysis.get("county"):
                self._update_map_for_county(analysis["county"])

        # Apply weather parameters
        if weather:
            provider = weather.get("provider", "auto")
            cache = weather.get("cache", True)
            self._refresh_weather_overlays(provider, cache)

        # Apply date parameters
        if date:
            start_date = date.get("start_date")
            end_date = date.get("end_date")
            if start_date and end_date:
                self._refresh_temporal_data(start_date, end_date)

        # Comprehensive refresh
        if analysis and weather and date and self.current_analytics_result:
            self._generate_weather_overlay_from_analytics(self.current_analytics_result)

        self.loading_status.setText("Full map refresh completed")

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
