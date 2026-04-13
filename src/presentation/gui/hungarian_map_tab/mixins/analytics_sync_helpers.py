#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Analytics Sync Helpers - Helper methods for sync operations.

Provides helper methods for map updates and data refresh.
"""

from datetime import datetime
from typing import Any


def _apply_analysis_refresh(helper: "AnalyticsSyncHelpers", analysis: dict) -> None:
    """Apply analysis parameters during full refresh."""
    analysis_type = analysis.get("analysis_type")
    if analysis_type == "single_location" and analysis.get("location"):
        helper._update_map_for_single_location(analysis["location"])
        return
    if analysis_type == "region" and analysis.get("region"):
        helper._update_map_for_region(analysis["region"])
        return
    if analysis_type == "county" and analysis.get("county"):
        helper._update_map_for_county(analysis["county"])


def _apply_weather_refresh(helper: "AnalyticsSyncHelpers", weather: dict) -> None:
    """Apply weather parameters during full refresh."""
    provider = weather.get("provider", "auto")
    cache = weather.get("cache", True)
    helper._refresh_weather_overlays(provider, cache)


def _apply_date_refresh(helper: "AnalyticsSyncHelpers", date: dict) -> None:
    """Apply date parameters during full refresh."""
    start_date = date.get("start_date")
    end_date = date.get("end_date")
    if start_date and end_date:
        helper._refresh_temporal_data(start_date, end_date)


class AnalyticsSyncHelpers:
    """
    Helper methods for analytics-to-map synchronization.

    Provides map update and data refresh helper functions.
    """

    def _update_map_for_single_location(self, location: dict[str, Any]) -> None:
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

    def _refresh_weather_overlay_with_new_dates(self, start_date: str, end_date: str) -> None:
        """Refresh weather overlay with new date range."""
        if not self.multi_city_engine:
            return

        self.loading_status.setText(f"Weather overlay refreshed: {start_date} to {end_date}")

    def _full_map_refresh(self, analysis: dict, weather: dict, date: dict) -> None:
        """Comprehensive map refresh with all parameters."""
        if analysis:
            _apply_analysis_refresh(self, analysis)
        if weather:
            _apply_weather_refresh(self, weather)
        if date:
            _apply_date_refresh(self, date)
        if analysis and weather and date and self.current_analytics_result:
            self._generate_weather_overlay_from_analytics(self.current_analytics_result)

        self.loading_status.setText("Full map refresh completed")


__all__ = ["AnalyticsSyncHelpers"]
