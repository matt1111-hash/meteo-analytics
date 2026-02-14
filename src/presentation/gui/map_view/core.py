#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Map View - Core

🗺️ Map View Widget - Teljes magyar Folium térképes nézet

Képességek:
- Folium HungarianMapTab integráció
- Signal forwarding
- Alapvető delegációs metódusok

Fájl: src/presentation/gui/map_view/core.py
"""

from typing import Any, Dict, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..theme_manager import register_widget_for_theming
from .debug import MapViewDebugMixin
from .hungarian_map_tab import HungarianMapTab
from .integration import MapViewIntegrationMixin


class MapView(QWidget, MapViewIntegrationMixin, MapViewDebugMixin):
    """
    🗺️ Map View Widget - Teljes magyar Folium térképes nézet.

    Ez a widget a MainWindow térképes nézetét biztosítja, és integrálja
    a HungarianMapTab komponenst Folium támogatással:
    - Hierarchikus magyar lokáció választót (bal oldal)
    - Folium interaktív térképet (jobb oldal)
    - JavaScript bridge támogatást
    - Kétirányú szinkronizációt
    - Weather overlay funkcionalitást
    - Export funkcionalitást

    🚀 FOLIUM SIGNALOK (forwarded):
    - location_selected(location_data): Lokáció kiválasztva
    - county_clicked_on_map(county_name): Megye kattintva Folium térképen
    - map_interaction(interaction_type, data): Térkép interakció
    - export_completed(file_path): Export befejezve
    - error_occurred(message): Hiba történt
    - folium_ready(): Folium térkép betöltve
    """

    # Forwarded signalok a HungarianMapTab-ból (Folium verzió)
    location_selected = Signal(object)  # Location data
    county_clicked_on_map = Signal(str)  # Folium county click
    map_interaction = Signal(str, object)  # interaction_type, data
    export_completed = Signal(str)  # file_path
    error_occurred = Signal(str)  # error_message
    data_loading_completed = Signal()  # adatok betöltve
    folium_ready = Signal()  # Folium térkép kész

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
