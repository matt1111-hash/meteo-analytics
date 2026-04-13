# mypy: ignore-errors
"""
AnalysisWorker Data Converter - Convert weather data formats.
🎯 List[Dict] → Dict[List] conversion with wind direction compatibility.
"""

import logging
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import AnalysisWorker


def _is_valid_weather_payload(converter: "DataConverter", weather_data: list[dict]) -> bool:
    """Validate incoming weather data structure."""
    if not weather_data:
        converter._logger.warning("🎯 Üres weather_data")
        return False
    if not isinstance(weather_data, list):
        converter._logger.warning(f"🎯 Váratlan weather_data típus: {type(weather_data)}")
        return False
    if not isinstance(weather_data[0], dict):
        converter._logger.warning("🎯 Weather_data nem List[Dict] formátum")
        return False
    return True


def _convert_records_to_daily(converter: "DataConverter", weather_data: list[dict]) -> dict:
    """Convert List[Dict] records into the legacy daily structure."""
    result = {"daily": {}}
    sample_keys = list(weather_data[0].keys())
    converter._logger.info(f"🎯 Konvertálandó kulcsok: {sample_keys}")
    for key in sample_keys:
        target_key = "time" if key == "date" else key
        source_key = "date" if key == "date" else key
        result["daily"][target_key] = [record.get(source_key) for record in weather_data]
        converter._logger.info(f"🎯 Konvertálva: {key} ({len(result['daily'][target_key])} elem)")
    return result


def _log_direction_stats(converter: "DataConverter", result: dict) -> None:
    """Log wind direction compatibility statistics."""
    if "winddirection_10m_dominant" not in result["daily"]:
        return
    wind_directions = result["daily"]["winddirection_10m_dominant"]
    valid_directions = [d for d in wind_directions if d is not None]
    if not valid_directions:
        return
    converter._logger.info(f"🌹 Szélirány adatok: {len(valid_directions)} érvényes érték")
    converter._logger.info(
        f"🌹 Szélirány tartomány: {min(valid_directions):.0f}° → {max(valid_directions):.0f}°"
    )
    if "winddirection" in result["daily"]:
        compat_count = len([d for d in result["daily"]["winddirection"] if d is not None])
        converter._logger.info(f"🌹 ✅ WindRoseChart kompatibilitás: {compat_count} érték")


def _log_gust_stats(converter: "DataConverter", result: dict) -> None:
    """Log wind gust compatibility statistics."""
    if "windgusts_10m_max" not in result["daily"]:
        return
    wind_gusts = result["daily"]["windgusts_10m_max"]
    valid_gusts = [g for g in wind_gusts if g is not None and g > 0]
    if not valid_gusts:
        return
    converter._logger.info(f"🌪️ Széllökés adatok: {len(valid_gusts)} érvényes érték")
    converter._logger.info(f"🌪️ Maximum széllökés: {max(valid_gusts):.1f} km/h")
    if "wind_gusts_max" in result["daily"]:
        compat_count = len(
            [g for g in result["daily"]["wind_gusts_max"] if g is not None and g > 0]
        )
        converter._logger.info(f"🌪️ ✅ WindChart kompatibilitás: {compat_count} érték")


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

    def convert_to_legacy_format(self, weather_data: list[dict]) -> dict | None:
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
            self._logger.info(f"🎯 ADATKONVERZIÓ kezdés: {type(weather_data)} → Dict[List]")
            if not _is_valid_weather_payload(self, weather_data):
                return None
            result = _convert_records_to_daily(self, weather_data)
            self._add_compatibility_keys(result)
            self._add_metadata(result, weather_data)
            if not self._validate_result(result):
                return None
            self._log_conversion_stats(result)
            return result

        except Exception as e:
            self._logger.error(f"🎯 ADATKONVERZIÓ HIBA: {e}")
            self._logger.error(traceback.format_exc())
            return None

    def _add_compatibility_keys(self, result: dict) -> None:
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
            self._logger.info("🌹 ✅ Kompatibilitási kulcs: wind_gusts_10m_max → wind_gusts_max")
            self._logger.info(
                "🌹 ✅ Kompatibilitási kulcs: wind_gusts_10m_max → windgusts_10m_max (Anomaly Detection)"
            )

        # 🌹 windspeed_10m_max → wind_speed_max (WindChart/WindyDaysChart)
        # 🌹 windspeed_10m_max → wind_speed_10m_max (DetectAnomaliesUseCase)
        if "windspeed_10m_max" in daily:
            daily["wind_speed_max"] = daily["windspeed_10m_max"]
            daily["wind_speed_10m_max"] = daily["windspeed_10m_max"]
            self._logger.info("🌹 ✅ Kompatibilitási kulcs: windspeed_10m_max → wind_speed_max")
            self._logger.info(
                "🌹 ✅ Kompatibilitási kulcs: windspeed_10m_max → wind_speed_10m_max (Anomaly Detection)"
            )

        # wind_direction_10m_dominant alias
        if "winddirection_10m_dominant" in daily:
            daily["wind_direction_10m_dominant"] = daily["winddirection_10m_dominant"]
            self._logger.info(
                "🌹 ✅ Kompatibilitási kulcs: winddirection_10m_dominant → wind_direction_10m_dominant"
            )

    def _add_metadata(self, result: dict, weather_data: list[dict]) -> None:
        """Add metadata from first record."""
        if not weather_data:
            return

        first_record = weather_data[0]

        for meta_key in ["latitude", "longitude", "timezone", "elevation"]:
            if meta_key in first_record:
                result[meta_key] = first_record[meta_key]
                self._logger.info(f"🎯 Metadata hozzáadva: {meta_key} = {first_record[meta_key]}")

    def _validate_result(self, result: dict) -> bool:
        """Validate converted result."""
        if not result.get("daily", {}).get("time"):
            self._logger.error("🎯 KONVERZIÓ HIBA: Nincs 'time' mező!")
            return False
        return True

    def _log_conversion_stats(self, result: dict) -> None:
        """Log conversion statistics."""
        record_count = len(result["daily"]["time"])
        self._logger.info(f"🎯 KONVERZIÓ SIKERES: {record_count} rekord konvertálva")
        self._logger.info(f"🎯 Végső daily kulcsok: {list(result['daily'].keys())}")
        _log_direction_stats(self, result)
        _log_gust_stats(self, result)
