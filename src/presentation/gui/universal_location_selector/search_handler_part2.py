# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for SearchHandler."""

from __future__ import annotations

from .search_handler_support import *


class SearchHandlerPart2Mixin:
    def _display_results(self, results: List[Dict[str, Any]]) -> None:
        """
        Keresési eredmények megjelenítése MAGYAR PRIORITÁSSAL

        Args:
            results: Talált városok listája
        """
        self.results_list.clear()

        for city in results[:20]:  # Első 20 eredmény
            try:
                # Alap adatok
                name = city.get("city", city.get("name", "Unknown"))
                lat = city.get("lat", 0.0)
                lon = city.get("lon", 0.0)
                is_hungarian = city.get("is_hungarian", False)

                # MAGYAR SPECIFIKUS FORMATTING
                if is_hungarian:
                    display_text = self._format_hungarian_city(city, name, lat, lon)
                else:
                    # GLOBÁLIS FORMATTING (eredeti)
                    display_text = self._format_global_city(city, name, lat, lon)

                # List item létrehozása
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, city)
                self.results_list.addItem(item)

            except Exception as e:
                logger.warning(f"Eredmény feldolgozási hiba: {e}")

    def _format_hungarian_city(
        self, city: Dict[str, Any], name: str, lat: float, lon: float
    ) -> str:
        """
        Magyar város formázása.

        Args:
            city: City objektum
            name: Város neve
            lat: Szélesség
            lon: Hosszúság

        Returns:
            Formázott szöveg
        """
        flag = "🇭🇺"

        # Display név: "Kiskunhalas, Bács-Kiskun megye"
        megye = city.get("megye", "")
        if megye:
            display_name = f"{name}, {megye} megye"
        else:
            display_name = name

        # Settlement type info
        settlement_info = ""
        settlement_type = city.get("settlement_type")
        if settlement_type:
            settlement_info = f" ({settlement_type})"

        # Population info
        pop_info = ""
        population = city.get("population")
        if population:
            pop_info = f"\n👥 {population:,} lakos"

        return f"{flag} {display_name}{settlement_info}{pop_info}\n🗺️ [{lat:.3f}, {lon:.3f}]"

    def _format_global_city(
        self, city: Dict[str, Any], name: str, lat: float, lon: float
    ) -> str:
        """
        Globális város formázása.

        Args:
            city: City objektum
            name: Város neve
            lat: Szélesség
            lon: Hosszúság

        Returns:
            Formázott szöveg
        """
        flag = "🌍"
        country = city.get("country", "") or ""
        region = city.get("admin_name", "") or ""

        display_text = f"{flag} {name}"
        if region and region != name:
            display_text += f"\n📍 {region}"
        if country:
            display_text += f", {country}"
        display_text += f"\n🗺️ [{lat:.3f}, {lon:.3f}]"

        return display_text
