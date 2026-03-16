# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for MapView."""

from __future__ import annotations

from .core_support import *


class MapViewPart1Mixin:
    def __init__(self, parent=None):
        """
        MapView inicializálása.

        Args:
            parent: Szülő widget
        """
        super().__init__(parent)

        # Komponens referencia
        self.map_tab: Optional[HungarianMapTab] = None

        # UI építés
        self._setup_ui()
        self._setup_theme()
        self._connect_signals()

        print("🗺️ DEBUG: MapView initialized with Folium HungarianMapTab integration")

    def _setup_ui(self) -> None:
        """
        🎨 UI komponensek létrehozása - Folium HungarianMapTab integrációval.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Teljes hely a map tab-nak
        layout.setSpacing(0)

        # Folium HungarianMapTab létrehozása és hozzáadása
        self.map_tab = HungarianMapTab()
        layout.addWidget(self.map_tab)

        print("✅ DEBUG: MapView UI setup complete with Folium HungarianMapTab")

    def _setup_theme(self) -> None:
        """
        🎨 Téma beállítások alkalmazása.
        """
        register_widget_for_theming(self, "container")

    def _connect_signals(self) -> None:
        """
        🔗 Signal forwarding beállítása Folium HungarianMapTab-ból.
        """
        if self.map_tab:
            # Signal forwarding - HungarianMapTab signalok → MapView signalok
            self.map_tab.location_selected.connect(self.location_selected.emit)
            self.map_tab.county_clicked_on_map.connect(self.county_clicked_on_map.emit)
            self.map_tab.map_interaction.connect(self.map_interaction.emit)
            self.map_tab.export_completed.connect(self.export_completed.emit)
            self.map_tab.error_occurred.connect(self.error_occurred.emit)
            self.map_tab.data_loading_completed.connect(
                self.data_loading_completed.emit
            )
            self.map_tab.folium_ready.connect(self.folium_ready.emit)

            print("✅ DEBUG: MapView Folium signal forwarding setup complete")
        else:
            print("❌ DEBUG: MapTab is None - cannot setup signal forwarding")

    # === PUBLIKUS API - FOLIUM HUNGARIANMAPTAB DELEGÁLÁS ===

    def get_map_tab(self) -> Optional[HungarianMapTab]:
        """
        🗺️ Folium HungarianMapTab referencia lekérdezése.

        Returns:
            HungarianMapTab példány vagy None
        """
        return self.map_tab

    def get_location_selector(self):
        """
        📍 Location selector referencia lekérdezése (delegált).

        Returns:
            HungarianLocationSelector példány vagy None
        """
        if self.map_tab:
            return self.map_tab.get_location_selector()
        return None

    def get_map_visualizer(self):
        """
        🗺️ Folium map visualizer referencia lekérdezése (delegált).

        Returns:
            HungarianMapVisualizer példány vagy None
        """
        if self.map_tab:
            return self.map_tab.get_map_visualizer()
        return None

    def get_current_location(self):
        """
        📍 Jelenlegi lokáció lekérdezése (delegált).

        Returns:
            Location objektum vagy None
        """
        if self.map_tab:
            return self.map_tab.get_current_location()
        return None

    def set_region_and_county(self, region_key: str, county_name: str) -> bool:
        """
        📍 Régió és megye beállítása (delegált).

        Args:
            region_key: Éghajlati régió kulcs
            county_name: Megye neve

        Returns:
            Sikeres volt-e a beállítás
        """
        if self.map_tab:
            return self.map_tab.set_region_and_county(region_key, county_name)
        return False

    def focus_on_county(self, county_name: str) -> bool:
        """
        🎯 Folium térkép fókuszálása megyére (delegált).

        Args:
            county_name: Megye neve

        Returns:
            Sikeres volt-e a fókuszálás
        """
        if self.map_tab:
            return self.map_tab.focus_on_county(county_name)
        return False

    def get_available_counties(self) -> list:
        """
        📋 Elérhető megyék listája (delegált).

        Returns:
            Megyenevek listája
        """
        if self.map_tab:
            return self.map_tab.get_available_counties()
        return []

    def is_ready(self) -> bool:
        """
        ✅ Térképes nézet kész használatra (delegált).

        Returns:
            Kész-e a használatra
        """
        if self.map_tab:
            return self.map_tab.is_ready()
        return False

    def is_folium_ready(self) -> bool:
        """
        ✅ Folium térkép kész használatra (delegált).

        Returns:
            Folium térkép kész-e
        """
        if self.map_tab:
            return self.map_tab.is_folium_ready()
        return False
