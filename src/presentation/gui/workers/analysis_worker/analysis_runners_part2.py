# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for AnalysisRunners."""

from __future__ import annotations

from .analysis_runners_support import *


class AnalysisRunnersPart2Mixin:  # noqa: D101
    def _run_single_location_analysis(self):  # noqa: PLR0915
        """
        🎯 EGYEDI LOKÁCIÓ ELEMZÉSE - ADATKONVERZIÓS FIX!
        """
        print("=" * 80)
        print("🚨 DEBUG: _run_single_location_analysis() ELEJE")
        print(f"🚨 DEBUG: _worker._request_data keys: {list(self._worker._request_data.keys())}")
        location_data = self._worker._request_data.get("location_data", {})
        print(
            f"🚨 DEBUG: _worker._request_data['location_data'] keys: {list(location_data.keys())}"
        )
        print("=" * 80)

        if self._worker._interrupt_handler.check("Single location elemzés"):
            print("❌ DEBUG: Interrupt check returned True - returning early")
            return

        try:
            self._worker._emit_progress("Egyedi lokáció elemzése...", 50)

            # Extract coordinates (re-fetch after debug output)
            location_data = self._worker._request_data.get("location_data", {})
            date_range = self._worker._request_data.get("date_range", {})

            # Flexible coordinate extraction
            latitude, longitude = self._extract_coordinates(location_data)

            if latitude is None or longitude is None:
                error_msg = f"Hiányzó koordináták: latitude={latitude}, longitude={longitude}"
                self._logger.error(f"🔧 {error_msg}")
                self._worker._emit_error(error_msg)
                return

            self._logger.info(f"🔧 WeatherClient hívás: latitude={latitude}, longitude={longitude}")

            # Interrupt check before API call
            if self._worker._interrupt_handler.check("Weather API hívás előtt"):
                print("❌ DEBUG: Interrupt check before API call - returning")
                return

            # Call WeatherClient with correct parameter names
            print(f"🚨 DEBUG: get_weather_data() HÍVÁS ELŐTT - lat={latitude}, lon={longitude}")
            print(
                f"🚨 DEBUG: start_date={date_range.get('start_date')}, end_date={date_range.get('end_date')}"
            )

            weather_data = self._worker._weather_client.get_weather_data(
                latitude=latitude,
                longitude=longitude,
                start_date=date_range.get("start_date"),
                end_date=date_range.get("end_date"),
            )

            print(
                f"🚨 DEBUG: get_weather_data() VISSZATÉRT - típus={type(weather_data)}, elemszám={len(weather_data) if weather_data else 0}"
            )
            self._logger.info("✅ WeatherClient sikeres")

            if self._worker._interrupt_handler.check("Single location feldolgozás"):
                return

            # Convert data format
            self._worker._emit_progress("Adatok konvertálása...", 80)
            converted_data = self._worker._data_converter.convert_to_legacy_format(weather_data)

            if not converted_data:
                self._worker._emit_error("Adatkonverzió sikertelen")
                return

            # Structure result
            result = {
                "analysis_type": "single_location",
                "request_params": self._worker._request_data,
                "result_data": converted_data,
                "timestamp": datetime.now().isoformat(),
                "success": True,
            }

            print(f"🚨 DEBUG: analysis_completed.emit() ELŐTT - result keys: {list(result.keys())}")
            self._worker._emit_progress("Egyedi elemzés befejezve", 100)
            self._worker.analysis_completed.emit(result)
            print("🚨 DEBUG: analysis_completed.emit() UTÁN - signal elküldve")

            print("=" * 80)
            print("🚨 DEBUG: _run_single_location_analysis() VÉGE - SIKERES")
            print("=" * 80)

        except Exception as e:
            self._logger.error(f"Single location elemzés hiba: {e!s}")
            self._logger.error(traceback.format_exc())
            self._worker._emit_error(f"Egyedi elemzés sikertelen: {e!s}")

    def _extract_coordinates(self, location_data: Dict) -> tuple:
        """
        Extract coordinates from various formats.

        Args:
            location_data: Location data dictionary

        Returns:
            Tuple of (latitude, longitude) or (None, None)
        """
        latitude = None
        longitude = None

        # From location_data object - support both key formats
        if location_data:
            latitude = location_data.get("latitude") or location_data.get("lat")
            longitude = location_data.get("longitude") or location_data.get("lon")
            self._logger.info(f"🔧 Koordináták location_data-ból: lat={latitude}, lon={longitude}")

        # Fallback to direct parameters
        if latitude is None or longitude is None:
            latitude = self._worker._request_data.get("latitude")
            longitude = self._worker._request_data.get("longitude")
            self._logger.info(
                f"🔧 Koordináták direkt paraméterekből: lat={latitude}, lon={longitude}"
            )

        return latitude, longitude

    def _run_county_analysis(self):
        """MEGYE ELEMZÉSE"""
        # Similar logic to multi_city
        self._run_multi_city_analysis()

    def _progress_callback(self, message: str, percentage: int) -> bool:
        """
        PROGRESS CALLBACK - From MultiCityEngine

        Args:
            message: Progress message
            percentage: Progress percentage

        Returns:
            True to continue, False to stop
        """
        if self._worker._interrupt_handler.check("Progress callback"):
            return False

        self._worker._emit_progress(message, percentage)
        return True
