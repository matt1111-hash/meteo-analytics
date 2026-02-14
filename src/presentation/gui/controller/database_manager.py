#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database Manager - Adatbázis műveletek kezelése

Kezeli az SQLite adatbázis kapcsolatot, séma frissítéseket
és az adatok mentését városokhoz és időjárási adatokhoz.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional


class DatabaseManager:
    """
    Adatbázis műveletek kezelése.

    Felelőségek:
    - Adatbázis kapcsolat inicializálása
    - Séma frissítések (wind_gusts_max, data_provider oszlopok)
    - Város adatok mentése
    - Időjárási adatok mentése
    """

    def __init__(self, db_path: Path):
        """
        DatabaseManager inicializálása.

        Args:
            db_path: Adatbázis fájl elérési útja
        """
        self.db_path = db_path
        self._logger = logging.getLogger(__name__)
        self._init_database_connection()

    def _init_database_connection(self) -> None:
        """Adatbázis kapcsolat inicializálása wind gusts séma frissítéssel."""
        try:
            # Adatbázis mappa létrehozása ha nem létezik
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            # Kapcsolat tesztelése és séma frissítés
            conn = sqlite3.connect(str(self.db_path))

            # Adatbázis séma frissítés wind_gusts_max oszloppal
            self._update_database_schema(conn)

            conn.close()

            self._logger.info(
                f"✅ Adatbázis kapcsolat OK (WIND GUSTS support): {self.db_path}"
            )

        except Exception as e:
            self._logger.error(f"Adatbázis kapcsolat hiba: {e}")
            raise

    def _update_database_schema(self, conn: sqlite3.Connection) -> None:
        """
        Adatbázis séma frissítés wind_gusts_max oszloppal.

        Args:
            conn: SQLite kapcsolat
        """
        try:
            cursor = conn.cursor()

            # Ellenőrizzük, hogy létezik-e a wind_gusts_max oszlop
            cursor.execute("PRAGMA table_info(weather_data)")
            columns = [column[1] for column in cursor.fetchall()]

            if "wind_gusts_max" not in columns:
                self._logger.info("🌪️ wind_gusts_max oszlop nem létezik - hozzáadás...")

                # Új oszlop hozzáadása
                cursor.execute("""
                    ALTER TABLE weather_data
                    ADD COLUMN wind_gusts_max REAL
                """)

                self._logger.info("✅ wind_gusts_max oszlop sikeresen hozzáadva")

                # Index létrehozása a gyorsabb lekérdezésekhez
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_weather_data_wind_gusts_max
                    ON weather_data(wind_gusts_max)
                """)

                self._logger.info("✅ wind_gusts_max index sikeresen létrehozva")

            else:
                self._logger.info("✅ wind_gusts_max oszlop már létezik")

            # Provider tracking oszlop hozzáadása
            if "data_provider" not in columns:
                self._logger.info("🌐 data_provider oszlop nem létezik - hozzáadás...")

                cursor.execute("""
                    ALTER TABLE weather_data
                    ADD COLUMN data_provider TEXT DEFAULT 'open-meteo'
                """)

                self._logger.info("✅ data_provider oszlop sikeresen hozzáadva")

            conn.commit()

        except Exception as e:
            self._logger.error(f"Adatbázis séma frissítés hiba: {e}")
            # Nem kritikus hiba, folytatjuk a működést

    def save_city_to_database(self, city_data: Dict[str, Any]) -> None:
        """
        Település adatok mentése adatbázisba.

        Args:
            city_data: Település adatok
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Upsert (INSERT OR REPLACE) művelet
            cursor.execute(
                """
                INSERT OR REPLACE INTO cities (name, latitude, longitude, country, region)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    city_data["name"],
                    city_data["latitude"],
                    city_data["longitude"],
                    city_data["metadata"].get("country", ""),
                    city_data["metadata"].get("admin1", ""),
                ),
            )

            conn.commit()
            conn.close()

            self._logger.info(f"✅ Település mentve adatbázisba: {city_data['name']}")

        except Exception as e:
            self._logger.error(f"Adatbázis mentési hiba: {e}")

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
                self._logger.warning(
                    "⚠️ Nincs város adat az időjárási adatok mentéséhez"
                )
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
                    # Wind gusts_max oszlop hozzáadása
                    wind_gusts_max = None
                    if "wind_gusts_max" in daily_data and i < len(
                        daily_data["wind_gusts_max"]
                    ):
                        wind_gusts_max = daily_data["wind_gusts_max"][i]

                    # Windspeed_10m_max proper handling
                    windspeed_max = None
                    if "windspeed_10m_max" in daily_data and i < len(
                        daily_data["windspeed_10m_max"]
                    ):
                        windspeed_max = daily_data["windspeed_10m_max"][i]

                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO weather_data
                        (city_id, date, temp_max, temp_min, precipitation, windspeed_max, wind_gusts_max, data_provider)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            city_id,
                            date,
                            daily_data["temperature_2m_max"][i]
                            if i < len(daily_data["temperature_2m_max"])
                            else None,
                            daily_data["temperature_2m_min"][i]
                            if i < len(daily_data["temperature_2m_min"])
                            else None,
                            daily_data["precipitation_sum"][i]
                            if i < len(daily_data["precipitation_sum"])
                            else None,
                            windspeed_max,
                            wind_gusts_max,
                            data_provider,
                        ),
                    )
                    saved_count += 1

                    # Debug logolás szélsebesség + széllökésekhez
                    if windspeed_max is not None and windspeed_max > 40:
                        self._logger.info(
                            f"🌪️ Saved high wind speed ({data_provider}): {date} - {windspeed_max:.1f} km/h"
                        )
                    if wind_gusts_max is not None and wind_gusts_max > 80:
                        self._logger.info(
                            f"🌪️ Saved extreme wind gust ({data_provider}): {date} - {wind_gusts_max:.1f} km/h"
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
