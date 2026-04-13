# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for DatabaseManager."""

from __future__ import annotations

from .database_manager_support import *


def _extract_weather_row(daily_data: Dict[str, Any], index: int) -> tuple[Any, Any]:
    """Extract wind metrics for one daily row."""
    wind_gusts_max = None
    if "wind_gusts_max" in daily_data and index < len(daily_data["wind_gusts_max"]):
        wind_gusts_max = daily_data["wind_gusts_max"][index]
    windspeed_max = None
    if "windspeed_10m_max" in daily_data and index < len(daily_data["windspeed_10m_max"]):
        windspeed_max = daily_data["windspeed_10m_max"][index]
    return windspeed_max, wind_gusts_max


def _build_weather_insert_row(
    city_id: Any, date: Any, daily_data: Dict[str, Any], index: int, data_provider: str
) -> tuple[Any, ...]:
    """Build the insert row for one daily weather record."""
    windspeed_max, wind_gusts_max = _extract_weather_row(daily_data, index)
    return (
        city_id,
        date,
        daily_data["temperature_2m_max"][index]
        if index < len(daily_data["temperature_2m_max"])
        else None,
        daily_data["temperature_2m_min"][index]
        if index < len(daily_data["temperature_2m_min"])
        else None,
        daily_data["precipitation_sum"][index]
        if index < len(daily_data["precipitation_sum"])
        else None,
        windspeed_max,
        wind_gusts_max,
        data_provider,
    )


def _log_saved_wind_metrics(
    database_manager: Any,
    data_provider: str,
    date: Any,
    windspeed_max: Any,
    wind_gusts_max: Any,
) -> None:
    """Log noteworthy saved wind metrics."""
    if windspeed_max is not None and windspeed_max > 40:  # noqa: PLR2004
        database_manager._logger.info(
            f"🌪️ Saved high wind speed ({data_provider}): {date} - {windspeed_max:.1f} km/h"
        )
    if wind_gusts_max is not None and wind_gusts_max > 80:  # noqa: PLR2004
        database_manager._logger.info(
            f"🌪️ Saved extreme wind gust ({data_provider}): {date} - {wind_gusts_max:.1f} km/h"
        )


class DatabaseManagerPart2Mixin:  # noqa: D101
    def save_weather_to_database(
        self, weather_data: Dict[str, Any], current_city_data: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Időjárási adatok mentése adatbázisba wind gusts támogatással.

        Args:
            weather_data: Feldolgozott időjárási adatok
            current_city_data: Jelenlegi város adatai

        Returns:
            bool: Sikeres volt-e a mentés
        """
        try:
            if not current_city_data:
                self._logger.warning("⚠️ Nincs város adat az időjárási adatok mentéséhez")
                return False

            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Város ID lekérdezése
            cursor.execute(
                """
                SELECT id FROM cities
                WHERE name = ? AND latitude = ? AND longitude = ?
            """,
                (
                    current_city_data["name"],
                    current_city_data["latitude"],
                    current_city_data["longitude"],
                ),
            )

            city_result = cursor.fetchone()
            if not city_result:
                self._logger.warning("⚠️ Város nem található az adatbázisban")
                conn.close()
                return False

            city_id = city_result[0]
            daily_data = weather_data["daily"]

            # Provider információ
            data_provider = weather_data.get("provider", "unknown")

            # Időjárási adatok mentése
            saved_count = 0
            for i, date in enumerate(daily_data["time"]):
                try:
                    row = _build_weather_insert_row(city_id, date, daily_data, i, data_provider)
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO weather_data
                        (city_id, date, temp_max, temp_min, precipitation, windspeed_max, wind_gusts_max, data_provider)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        row,
                    )
                    saved_count += 1
                    windspeed_max, wind_gusts_max = row[5], row[6]
                    _log_saved_wind_metrics(
                        self, data_provider, date, windspeed_max, wind_gusts_max
                    )

                except Exception as e:
                    self._logger.warning(f"⚠️ Rekord mentési hiba: {e}")
                    continue

            conn.commit()
            conn.close()

            self._logger.info(
                f"✅ Weather data mentve adatbázisba ({data_provider}): {saved_count} rekord"
            )
            return True

        except Exception as e:
            self._logger.error(f"Weather data adatbázis hiba: {e}")
            return False

    def get_connection(self) -> sqlite3.Connection:
        """
        Adatbázis kapcsolat lekérdezése.

        Returns:
            SQLite kapcsolat
        """
        return sqlite3.connect(str(self.db_path))

    @property
    def path(self) -> Path:
        """Adatbázis útvonal lekérdezése."""
        return self.db_path
