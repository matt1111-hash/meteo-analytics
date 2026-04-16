# mypy: ignore-errors
"""Geocoding Handler - Település keresés és kiválasztás kezelése."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from PySide6.QtCore import QObject, Signal, Slot


class GeocodingHandler(QObject):
    """
    Geocoding kezelése.

    Felelőségek:
    - Keresési kérések kezelése
    - Geocoding eredmények feldolgozása
    - Település kiválasztás kezelése
    - Display név generálás
    """

    # Signalok (ki kell kötni a fő controllerben)
    geocoding_results_ready = Signal(list)
    city_saved_to_db = Signal(dict)
    error_occurred = Signal(str)
    status_updated = Signal(str)

    # Nem kritikus hiba, nem szakítjuk meg a folyamatot

    def __init__(self, worker_manager, database_manager, parent=None):
        """
        GeocodingHandler inicializálása.

        Args:
            worker_manager: WorkerManager példány
            database_manager: DatabaseManager példány
            parent: Szülő QObject
        """
        super().__init__(parent)
        self.worker_manager = worker_manager
        self.database_manager = database_manager
        self._logger = logging.getLogger(__name__)
        self.active_search_query: str | None = None

    @Slot(str)
    def handle_search_request(self, search_query: str) -> None:
        """
        Település keresési kérés kezelése a ControlPanel-től.

        Args:
            search_query: Keresési kifejezés
        """
        self._logger.info(f"🔍 handle_search_request called with: '{search_query}'")

        # Alapszintű validáció
        if not search_query or len(search_query.strip()) < 2:  # noqa: PLR2004
            error_msg = "Legalább 2 karakter szükséges a kereséshez"
            self._logger.error(f"Validation error: {error_msg}")
            self.error_occurred.emit(error_msg)
            return

        # Jelenlegi keresés tárolása
        self.active_search_query = search_query.strip()
        self._logger.info(f"🔍 Active search query set: '{self.active_search_query}'")

        # Státusz frissítése
        search_info = f"Keresés: {self.active_search_query}"
        self.status_updated.emit(search_info + "...")
        self._logger.info(f"🔍 Status updated: {search_info}")

        # Geocoding worker indítása
        try:
            from ..workers.data_fetch_worker import GeocodingWorker  # noqa: PLC0415

            self._logger.info("🚀 Creating GeocodingWorker...")
            worker = GeocodingWorker(self.active_search_query)
            self._logger.info(f"✅ GeocodingWorker created for query: '{self.active_search_query}'")

            # WorkerManager központi használata
            self._logger.info("🚀 Starting worker via WorkerManager...")
            worker_id = self.worker_manager.start_geocoding(worker)
            self._logger.info(f"✅ GeocodingWorker started via WorkerManager with ID: {worker_id}")

        except Exception as e:
            error_msg = f"Geocoding worker indítási hiba: {e}"
            self._logger.error(error_msg)
            import traceback  # noqa: PLC0415

            traceback.print_exc()
            self.error_occurred.emit(error_msg)
            return

        self._logger.info(f"✅ handle_search_request completed successfully for '{search_query}'")

    @Slot(list)
    def on_geocoding_completed(self, results: list[dict[str, Any]]) -> None:
        """
        Geocoding befejezésének kezelése.

        Args:
            results: Település találatok listája
        """
        self._logger.info(f"🔍 on_geocoding_completed called with {len(results)} results")

        try:
            if not results:
                msg = "Nem található település ezzel a névvel"
                self._logger.info("🔍 No results found")
                self.status_updated.emit(msg)
                self.geocoding_results_ready.emit([])
                return

            self._logger.info(f"🔍 Processing {len(results)} geocoding results...")

            # Eredmények feldolgozása és gazdagítása
            processed_results = self._process_geocoding_results(results)
            self._logger.info(f"🔍 Processed {len(processed_results)} results")

            # Státusz frissítése
            status_msg = f"{len(processed_results)} település találat"
            self.status_updated.emit(status_msg)
            self._logger.info(f"🔍 Status updated: {status_msg}")

            # Eredmények továbbítása a GUI-nak
            self._logger.info("📡 Emitting geocoding_results_ready signal...")
            self.geocoding_results_ready.emit(processed_results)

            self._logger.info(f"✅ Geocoding befejezve: {len(processed_results)} találat")

        except Exception as e:
            self._logger.error(f"Geocoding feldolgozási hiba: {e}")
            import traceback  # noqa: PLC0415

            traceback.print_exc()
            self.error_occurred.emit(f"Keresési eredmények feldolgozási hiba: {e}")

    def _process_geocoding_results(self, raw_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Geocoding eredmények feldolgozása és gazdagítása.

        Args:
            raw_results: Nyers API eredmények

        Returns:
            Feldolgozott és gazdagított eredmények
        """
        processed = []

        self._logger.info(f"🔍 Processing {len(raw_results)} raw results")

        for i, result in enumerate(raw_results):
            try:
                # Alapadatok kinyerése
                processed_result = {
                    "name": result.get("name", ""),
                    "latitude": result.get("latitude", 0.0),
                    "longitude": result.get("longitude", 0.0),
                    "country": result.get("country", ""),
                    "admin1": result.get("admin1", ""),  # megye/régió
                    "admin2": result.get("admin2", ""),  # járás
                    "population": result.get("population"),
                    "timezone": result.get("timezone", "UTC"),
                    "elevation": result.get("elevation"),
                    # Megjelenítés a GUI számára
                    "display_name": self._create_display_name(result),
                    "search_rank": result.get("rank", 999),
                    "original_query": self.active_search_query,
                }

                processed.append(processed_result)

                # Debug információ minden 5. eredményhez
                if i < 5 or i % 5 == 0:  # noqa: PLR2004
                    name = processed_result["name"]
                    country = processed_result["country"]
                    self._logger.debug(f"🔍 Result {i}: {name}, {country}")

            except Exception as e:
                self._logger.warning(f"⚠️ Eredmény {i} feldolgozási hiba: {e}")
                continue

        # Rendezés relevancia szerint
        processed.sort(key=lambda x: x["search_rank"])
        self._logger.info("🔍 Results sorted by relevance")

        return processed

    def _create_display_name(self, result: dict[str, Any]) -> str:
        """
        Felhasználóbarát megjelenítési név létrehozása.

        Args:
            result: Geocoding eredmény

        Returns:
            Formázott megjelenítési név
        """
        name = result.get("name", "Ismeretlen")
        admin1 = result.get("admin1", "")
        country = result.get("country", "")

        display_parts = [name]

        if admin1:
            display_parts.append(admin1)

        if country:
            display_parts.append(country)

        return ", ".join(display_parts)

    @Slot(str, float, float, dict)
    def handle_city_selection(
        self,
        city_name: str,
        latitude: float,
        longitude: float,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Település kiválasztás kezelése a ControlPanel-től.

        Args:
            city_name: Település neve
            latitude: Földrajzi szélesség
            longitude: Földrajzi hosszúság
            metadata: További metaadatok

        Returns:
            A létrehozott city_data dictionary
        """
        self._logger.info(
            f"🔍 handle_city_selection called: {city_name} ({latitude:.4f}, {longitude:.4f})"
        )

        try:
            # Kiválasztott település adatainak mentése
            city_data = {
                "name": city_name,
                "latitude": latitude,
                "longitude": longitude,
                "metadata": metadata,
                "selected_at": datetime.now().isoformat(),
            }

            # Státusz frissítése
            status_msg = f"Kiválasztva: {city_name}"
            self.status_updated.emit(status_msg)
            self._logger.info(f"🔍 City selection status: {status_msg}")

            # Adatbázisba mentés (aszinkron)
            self._save_city_to_database(city_data)

            self._logger.info(
                f"✅ Település kiválasztva: {city_name} ({latitude:.4f}, {longitude:.4f})"
            )
            return city_data

        except Exception as e:
            self._logger.error(f"Település kiválasztási hiba: {e}")
            self.error_occurred.emit(f"Település kiválasztási hiba: {e}")
            return {}

    def _save_city_to_database(self, city_data: dict[str, Any]) -> None:
        """
        Település adatok mentése adatbázisba.

        Args:
            city_data: Település adatok
        """
        try:
            self.database_manager.save_city_to_database(city_data)

            # Sikeres mentés jelzése
            self.city_saved_to_db.emit(city_data)

        except Exception as e:
            self._logger.error(f"Adatbázis mentési hiba: {e}")
