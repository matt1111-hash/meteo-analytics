# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for core.py."""

from __future__ import annotations

from .core_part1 import MapViewPart1Mixin
from .core_part2 import MapViewPart2Mixin
from .core_support import *


class MapView(
    MapViewPart1Mixin,
    MapViewPart2Mixin,
    QWidget,
    MapViewIntegrationMixin,
    MapViewDebugMixin,
):
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
