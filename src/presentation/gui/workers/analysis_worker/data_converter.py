"""
AnalysisWorker Data Converter - Convert weather data formats.
🎯 List[Dict] → Dict[List] conversion with wind direction compatibility.
"""

import logging
import traceback
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from .core import AnalysisWorker


class DataConverter:
    """
    Convert weather data between formats.

    🎯 KRITIKUS JAVÍTÁS: ADATKONVERZIÓ List[Dict] → Dict[List]
    🌹 SZÉLIRÁNY KOMPATIBILITÁS: WindChart/WindRose támogatás!
    """

    def __init__(self, worker: "AnalysisWorker"):
        """
        Initialize data converter.

        Args:
            worker: AnalysisWorker instance
        """
        self._worker = worker
        self._logger = logging.getLogger(__name__)

    def convert_to_legacy_format(self, weather_data: List[Dict]) -> Optional[Dict]:
        """
        🎯 Convert WeatherClient format to AppController format.

        WeatherClient format (List[Dict]):
        [{"date": "2024-01-01", "winddirection_10m_dominant": 310, ...}, ...]

        AppController format (Dict[List]):
        {"daily": {"time": ["2024-01-01"], "winddirection_10m_dominant": [310], ...}}

        🌹 CHART COMPATIBILITY KEYS:
        - winddirection_10m_dominant → winddirection (WindRoseChart)
        - windgusts_10m_max → wind_gusts_max (WindChart)

        Args:
            weather_data: WeatherClient returned List[Dict] data

        Returns:
            AppController expected Dict[List] format or None
        """
        try:
            self._logger.info(
                f"🎯 ADATKONVERZIÓ kezdés: {type(weather_data)} → Dict[List]"
            )

            if not weather_data:
                self._logger.warning("🎯 Üres weather_data")
                return None

            if not isinstance(weather_data, list):
                self._logger.warning(
                    f"🎯 Váratlan weather_data típus: {type(weather_data)}"
                )
                return None

            if not weather_data or not isinstance(weather_data[0], dict):
                self._logger.warning("🎯 Weather_data nem List[Dict] formátum")
                return None

            # CONVERSION: List[Dict] → Dict[List]
            result = {"daily": {}}

            sample_keys = list(weather_data[0].keys())
            self._logger.info(f"🎯 Konvertálandó kulcsok: {sample_keys}")

            for key in sample_keys:
                if key == "date":
                    # 'date' → 'time' (AppController expectation)
                    result["daily"]["time"] = [
                        record.get("date") for record in weather_data
                    ]
                    self._logger.info(
                        f"🎯 Konvertálva: date → time ({len(result['daily']['time'])} elem)"
                    )
                else:
                    result["daily"][key] = [record.get(key) for record in weather_data]
                    self._logger.info(
                        f"🎯 Konvertálva: {key} ({len(result['daily'][key])} elem)"
                    )

            # 🌹 CHART COMPATIBILITY KEYS
            self._add_compatibility_keys(result)

            # Metadata
            self._add_metadata(result, weather_data)

            # Validate result
            if not self._validate_result(result):
                return None

            self._log_conversion_stats(result)
            return result

        except Exception as e:
            self._logger.error(f"🎯 ADATKONVERZIÓ HIBA: {e}")
            self._logger.error(traceback.format_exc())
            return None

    def _add_compatibility_keys(self, result: Dict) -> None:
        """Add chart compatibility keys."""
        self._logger.info("🌹 Chart kompatibilitási kulcsok hozzáadása...")

        daily = result["daily"]

        # winddirection_10m_dominant → winddirection (WindRoseChart)
        if "winddirection_10m_dominant" in daily:
            daily["winddirection"] = daily["winddirection_10m_dominant"]
            self._logger.info(
                "🌹 ✅ Kompatibilitási kulcs: winddirection_10m_dominant → winddirection"
            )

        # wind_gusts_10m_max → wind_gusts_max (WindChart)
        # wind_gusts_10m_max → windgusts_10m_max (DetectAnomaliesUseCase)
        # OpenMeteo API returns wind_gusts_10m_max (underscore AFTER "wind")
        if "wind_gusts_10m_max" in daily:
            daily["wind_gusts_max"] = daily["wind_gusts_10m_max"]
            daily["windgusts_10m_max"] = daily["wind_gusts_10m_max"]
            self._logger.info(
                "🌹 ✅ Kompatibilitási kulcs: wind_gusts_10m_max → wind_gusts_max"
            )
            self._logger.info(
                "🌹 ✅ Kompatibilitási kulcs: wind_gusts_10m_max → windgusts_10m_max (Anomaly Detection)"
            )

        # 🌹 windspeed_10m_max → wind_speed_max (WindChart/WindyDaysChart)
        # 🌹 windspeed_10m_max → wind_speed_10m_max (DetectAnomaliesUseCase)
        if "windspeed_10m_max" in daily:
            daily["wind_speed_max"] = daily["windspeed_10m_max"]
            daily["wind_speed_10m_max"] = daily["windspeed_10m_max"]
            self._logger.info(
                "🌹 ✅ Kompatibilitási kulcs: windspeed_10m_max → wind_speed_max"
            )
            self._logger.info(
                "🌹 ✅ Kompatibilitási kulcs: windspeed_10m_max → wind_speed_10m_max (Anomaly Detection)"
            )

        # wind_direction_10m_dominant alias
        if "winddirection_10m_dominant" in daily:
            daily["wind_direction_10m_dominant"] = daily["winddirection_10m_dominant"]
            self._logger.info(
                "🌹 ✅ Kompatibilitási kulcs: winddirection_10m_dominant → wind_direction_10m_dominant"
            )

    def _add_metadata(self, result: Dict, weather_data: List[Dict]) -> None:
        """Add metadata from first record."""
        if not weather_data:
            return

        first_record = weather_data[0]

        for meta_key in ["latitude", "longitude", "timezone", "elevation"]:
            if meta_key in first_record:
                result[meta_key] = first_record[meta_key]
                self._logger.info(
                    f"🎯 Metadata hozzáadva: {meta_key} = {first_record[meta_key]}"
                )

    def _validate_result(self, result: Dict) -> bool:
        """Validate converted result."""
        if not result.get("daily", {}).get("time"):
            self._logger.error("🎯 KONVERZIÓ HIBA: Nincs 'time' mező!")
            return False
        return True

    def _log_conversion_stats(self, result: Dict) -> None:
        """Log conversion statistics."""
        record_count = len(result["daily"]["time"])
        self._logger.info(f"🎯 KONVERZIÓ SIKERES: {record_count} rekord konvertálva")
        self._logger.info(f"🎯 Végső daily kulcsok: {list(result['daily'].keys())}")

        # Wind direction compatibility check
        if "winddirection_10m_dominant" in result["daily"]:
            wind_directions = result["daily"]["winddirection_10m_dominant"]
            valid_directions = [d for d in wind_directions if d is not None]
            if valid_directions:
                self._logger.info(
                    f"🌹 Szélirány adatok: {len(valid_directions)} érvényes érték"
                )
                self._logger.info(
                    f"🌹 Szélirány tartomány: {min(valid_directions):.0f}° → {max(valid_directions):.0f}°"
                )

                if "winddirection" in result["daily"]:
                    compat_count = len(
                        [d for d in result["daily"]["winddirection"] if d is not None]
                    )
                    self._logger.info(
                        f"🌹 ✅ WindRoseChart kompatibilitás: {compat_count} érték"
                    )

        # Wind gusts compatibility check
        if "windgusts_10m_max" in result["daily"]:
            wind_gusts = result["daily"]["windgusts_10m_max"]
            valid_gusts = [g for g in wind_gusts if g is not None and g > 0]
            if valid_gusts:
                max_gust = max(valid_gusts)
                self._logger.info(
                    f"🌪️ Széllökés adatok: {len(valid_gusts)} érvényes érték"
                )
                self._logger.info(f"🌪️ Maximum széllökés: {max_gust:.1f} km/h")

                if "wind_gusts_max" in result["daily"]:
                    compat_count = len(
                        [
                            g
                            for g in result["daily"]["wind_gusts_max"]
                            if g is not None and g > 0
                        ]
                    )
                    self._logger.info(
                        f"🌪️ ✅ WindChart kompatibilitás: {compat_count} érték"
                    )
