# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for DatabaseManager."""

from __future__ import annotations

from .database_manager_support import *


class DatabaseManagerPart1Mixin:
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
