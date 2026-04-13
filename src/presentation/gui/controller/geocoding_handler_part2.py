# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for GeocodingHandler."""

from __future__ import annotations

from .geocoding_handler_support import *


class GeocodingHandlerPart2Mixin:  # noqa: D101
    def _create_display_name(self, result: Dict[str, Any]) -> str:
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
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
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

    def _save_city_to_database(self, city_data: Dict[str, Any]) -> None:
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
