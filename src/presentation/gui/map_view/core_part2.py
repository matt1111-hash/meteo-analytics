# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for MapView."""

from __future__ import annotations

from .core_support import *


class MapViewPart2Mixin:
    def get_map_status(self) -> str:
        """
        📊 Térkép státusz lekérdezése (delegált).

        Returns:
            Státusz szöveg
        """
        if self.map_tab:
            return self.map_tab.get_map_status()
        return "Folium térkép nem elérhető"

    def refresh_all_components(self) -> None:
        """
        🔄 Összes komponens frissítése (delegált).
        """
        if self.map_tab:
            self.map_tab.refresh_all_components()

    def clear_selection(self) -> None:
        """
        🧹 Kiválasztás törlése (delegált).
        """
        if self.map_tab:
            self.map_tab.clear_selection()

    def reset_map_view(self) -> None:
        """
        🔄 Folium térkép visszaállítása alaphelyzetre (delegált).
        """
        if self.map_tab:
            self.map_tab._reset_map_view()

    def export_map(self) -> None:
        """
        💾 Folium térkép exportálása (delegált).
        """
        if self.map_tab:
            self.map_tab._export_map()

    # === FOLIUM SPECIFIKUS API ===

    def set_theme(self, theme: str) -> None:
        """
        🎨 Téma beállítása Folium térképhez (delegált).

        Args:
            theme: Téma neve ("light" vagy "dark")
        """
        if self.map_tab:
            self.map_tab.set_theme(theme)
            print(f"🎨 DEBUG: MapView Folium theme set to: {theme}")

    def set_weather_data(self, weather_data: Dict[str, Any]) -> None:
        """
        🌤️ Időjárási adatok beállítása Folium overlay-hez (delegált).

        Args:
            weather_data: Időjárási adatok dictionary
        """
        if self.map_tab:
            self.map_tab.set_weather_data(weather_data)
            print("🌤️ DEBUG: Weather data set for Folium overlay via MapView")

    def toggle_auto_sync(self, enabled: bool) -> None:
        """
        🔗 Auto-szinkronizáció ki/bekapcsolása (delegált).

        Args:
            enabled: Engedélyezett-e az auto-sync
        """
        if self.map_tab:
            self.map_tab.toggle_auto_sync(enabled)
            print(f"🔗 DEBUG: MapView auto-sync {'enabled' if enabled else 'disabled'}")
