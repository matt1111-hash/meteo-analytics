# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Merged part1+part2 for AnalysisRunners."""

from __future__ import annotations

from .analysis_runners_support import *


class AnalysisRunnersPart1Mixin:  # noqa: D101
    def __init__(self, worker: AnalysisWorker):
        """
        Initialize analysis runners.

        Args:
            worker: AnalysisWorker instance
        """
        self._worker = worker
        self._logger = logging.getLogger(__name__)

    def run_analysis(self, analysis_type: str) -> None:
        """
        Dispatch analysis based on type.

        Args:
            analysis_type: Type of analysis to run
        """
        if analysis_type == "multi_city":
            self._run_multi_city_analysis()
        elif analysis_type == "single_location":
            self._run_single_location_analysis()
        elif analysis_type == "county_analysis":
            self._run_county_analysis()
        else:
            self._worker._emit_error(f"Ismeretlen elemzés típus: {analysis_type}")

    def _run_multi_city_analysis(self):
        """MULTI-CITY ELEMZÉS FUTTATÁSA"""
        if self._worker._interrupt_handler.check("Multi-city elemzés"):
            return

        try:
            self._worker._emit_progress("Multi-city elemzés indítása...", 40)

            # Extract parameters
            region_name = self._worker._request_data.get("region_name")
            county_name = self._worker._request_data.get("county_name")
            date_range = self._worker._request_data.get("date_range", {})
            start_date = date_range.get("start_date")
            date_range.get("end_date")

            # Interrupt check before heavy work
            if self._worker._interrupt_handler.check("Multi-city engine indítás előtt"):
                return

            self._worker._emit_progress("Városok elemzése folyamatban...", 60)

            # Run analysis
            region_or_county = region_name or county_name
            if not region_or_county:
                self._worker._emit_error("Hiányzó régió vagy megye név")
                return

            result = self._worker._multi_city_engine.analyze_multi_city(
                query_type="hottest_today",
                region=region_or_county,
                date=start_date,
                limit=None,
            )

            # Final interrupt check
            if self._worker._interrupt_handler.check("Eredmény feldolgozás előtt"):
                return

            self._worker._emit_progress("Eredmények feldolgozása...", 90)

            # Structure result
            structured_result = {
                "analysis_type": "multi_city",
                "request_params": self._worker._request_data,
                "result_data": result,
                "timestamp": datetime.now().isoformat(),
                "success": True,
            }

            self._worker._emit_progress("Multi-city elemzés befejezve", 100)
            self._worker.analysis_completed.emit(structured_result)

        except Exception as e:
            self._logger.error(f"Multi-city elemzés hiba: {e!s}")
            self._worker._emit_error(f"Multi-city elemzés sikertelen: {e!s}")

    def _run_single_location_analysis(self):
        """
        Single location analysis.
        """
        location_data = self._worker._request_data.get("location_data", {})

        if self._worker._interrupt_handler.check("Single location elemzés"):
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
                return

            # Call WeatherClient with correct parameter names
            weather_data = self._worker._weather_client.get_weather_data(
                latitude=latitude,
                longitude=longitude,
                start_date=date_range.get("start_date"),
                end_date=date_range.get("end_date"),
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

            self._worker._emit_progress("Egyedi elemzés befejezve", 100)
            self._worker.analysis_completed.emit(result)

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
        Progress callback from MultiCityEngine.

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
