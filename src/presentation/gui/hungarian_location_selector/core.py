#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Hungarian Location Selector - Core Widget
Magyar Klímaanalitika MVP - Térkép Komponens Lokáció Választó

FUNKCIÓK:
- 7 statisztikai régió választás (Control Panel konzisztens!)
- Megye választás (GeoJSON alapú)
- Járás/település szűrés
- Koordináta megjelenítés
- Térképes előnézet integráció
- 🔧 JAVÍTOTT: QueryControlWidget kompatibilitás (get_current_city, get_current_coordinates)

SIGNALOK:
- region_selected(region_data): Statisztikai régió kiválasztva
- county_selected(county_name, geometry): Megye kiválasztva
- location_selected(location): Pontos lokáció kiválasztva
- selection_changed(): Bármilyen választás változott
- map_update_requested(bounds): Térkép frissítés kérés
"""

import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from .data import init_statistical_regions
from .mixins import (
    PublicApiMixin,
    QueryControlWidgetCompatMixin,
    SetupMixin,
    SignalHandlersMixin,
)

logger = logging.getLogger(__name__)


class HungarianLocationSelector(
    QWidget,
    SetupMixin,
    SignalHandlersMixin,
    QueryControlWidgetCompatMixin,
    PublicApiMixin,
):
    """
    🗺️ Hierarchikus magyar lokáció választó widget - GET_CURRENT_CITY() STATE MANAGEMENT JAVÍTVA!

    🔧 KRITIKUS JAVÍTÁS:
    - State management hiba kijavítva: _on_county_changed() robust logging
    - get_current_city() enhanced defensive programming
    - Selection change signaling javítva
    - QueryControlWidget kompatibilitás 100% működőképes
    - Error handling és debug logging implementálva
    """

    # Signalok
    region_selected = Signal(object)  # HungarianRegionData
    county_selected = Signal(str, object)  # county_name, geometry
    location_selected = Signal(object)  # Location object
    selection_changed = Signal()  # általános változás
    map_update_requested = Signal(object)  # map bounds/center

    def __init__(self, parent=None):
        super().__init__(parent)

        # Adatok
        self.region_data = init_statistical_regions()
        self.counties_gdf = None
        self.postal_codes_gdf = None
        self.current_region = None
        self.current_county = None
        self.current_location = None

        # 🔧 JAVÍTOTT: Debug state tracking
        self._debug_enabled = True  # Debug logging engedélyezve

        # Worker thread
        self.data_worker = None

        # UI építés
        self._setup_ui()
        self._setup_theme()
        self._connect_signals()

        # Adatok betöltésének indítása
        self._start_data_loading()
