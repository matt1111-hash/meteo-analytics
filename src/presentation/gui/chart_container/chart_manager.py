#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
ChartContainer Chart Manager - Manage chart updates and clearing.
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from .core import ChartsContainer


class ChartManager:
    """Handle chart updates and clearing."""

    def __init__(self, container: "ChartsContainer"):
        """
        Initialize chart manager.

        Args:
            container: ChartsContainer instance
        """
        self._container = container

    def update_all(self, data: Dict[str, Any]) -> None:
        """
        Update all charts with new data.

        Args:
            data: Weather data dictionary
        """
        print("📈 DEBUG: ChartsContainer.update_charts() - WIND GUSTS KRITIKUS JAVÍTÁS")

        try:
            self._container.current_data = data

            # Debug wind data
            self._debug_wind_data(data)

            # Sequential update - one chart at a time
            print("🌡️ UPDATING temp_chart...")
            self._container.temp_chart.update_data(data)

            print("🌧️ UPDATING precip_chart...")
            self._container.precip_chart.update_data(data)

            # Wind chart with explicit debug
            print("🌪️ UPDATING wind_chart...")
            try:
                self._container.wind_chart.update_data(data)
                print("✅ DEBUG: wind_chart.update_data() végrehajtva")
            except Exception as wind_error:
                print(f"❌ DEBUG: wind_chart.update_data() HIBA: {wind_error}")

            # New professional charts
            print("📅 UPDATING heatmap_chart...")
            self._container.heatmap_chart.update_data(data)

            # WindRose chart with explicit debug
            print("🌹 UPDATING windrose_chart...")
            try:
                self._container.windrose_chart.update_data(data)
                print("✅ DEBUG: windrose_chart.update_data() végrehajtva")
            except Exception as windrose_error:
                print(f"❌ DEBUG: windrose_chart.update_data() HIBA: {windrose_error}")

            print("📊 UPDATING comparison_chart...")
            self._container.comparison_chart.update_data(data)

            print("✅ DEBUG: All professional charts updated")

            # Final debug check
            self._debug_final_status()

        except Exception as e:
            print(f"❌ DEBUG: ChartsContainer frissítési hiba: {e}")
            import traceback

            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")

    def clear_all(self) -> None:
        """Clear all charts."""
        self._container.current_data = None

        charts = [
            self._container.temp_chart,
            self._container.precip_chart,
            self._container.wind_chart,
            self._container.heatmap_chart,
            self._container.windrose_chart,
            self._container.comparison_chart,
        ]

        for chart in charts:
            chart.clear_chart()

        print("🧹 DEBUG: All professional charts cleared")

    def _debug_wind_data(self, data: Dict[str, Any]) -> None:
        """Debug wind data in input."""
        daily_data = data.get("daily", {})
        wind_gusts_max = daily_data.get("wind_gusts_max", [])
        windspeed_10m_max = daily_data.get("windspeed_10m_max", [])

        print("🌪️ DEBUG: Input data széladatok:")
        print(f"🌪️ DEBUG: - wind_gusts_max: {len(wind_gusts_max)} elem")
        print(f"🌪️ DEBUG: - windspeed_10m_max: {len(windspeed_10m_max)} elem")

        if wind_gusts_max:
            print(f"🌪️ DEBUG: - wind_gusts_max minta: {wind_gusts_max[:3]}")
        if windspeed_10m_max:
            print(f"🌪️ DEBUG: - windspeed_10m_max minta: {windspeed_10m_max[:3]}")

    def _debug_final_status(self) -> None:
        """Debug final chart status."""
        if hasattr(self._container.wind_chart, "current_data"):
            status = (
                "VAN"
                if self._has_chart_data(self._container.wind_chart.current_data)
                else "NINCS"
            )
            print(f"🌪️ FINAL DEBUG: wind_chart.current_data: {status}")

        if hasattr(self._container.windrose_chart, "current_data"):
            status = (
                "VAN"
                if self._has_chart_data(self._container.windrose_chart.current_data)
                else "NINCS"
            )
            print(f"🌹 FINAL DEBUG: windrose_chart.current_data: {status}")

    @staticmethod
    def _has_chart_data(value: Any) -> bool:
        """Return whether a chart current_data payload is non-empty."""
        if value is None:
            return False
        if hasattr(value, "empty"):
            return not value.empty
        try:
            return len(value) > 0
        except Exception:
            return True
