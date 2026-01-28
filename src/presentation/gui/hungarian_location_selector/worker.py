#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Hungarian Location Selector - Background Worker
Magyar Klímaanalitika MVP - GeoJSON adatok betöltése háttérben
"""

import logging
from pathlib import Path

from PySide6.QtCore import QThread, Signal

try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False


logger = logging.getLogger(__name__)


class HungarianLocationWorker(QThread):
    """
    📄 Háttér munkavégző a GeoJSON adatok betöltéséhez.
    """

    # Signalok
    progress_updated = Signal(int)           # progress (0-100)
    counties_loaded = Signal(object)        # GeoDataFrame
    postal_codes_loaded = Signal(object)    # GeoDataFrame
    error_occurred = Signal(str)            # error message
    completed = Signal()                    # összes adat betöltve

    def __init__(self, data_dir: Path):
        super().__init__()
        self.data_dir = data_dir
        self.counties_gdf = None
        self.postal_codes_gdf = None

    def run(self):
        """
        GeoJSON adatok betöltése háttérben.
        """
        try:
            if not GEOPANDAS_AVAILABLE:
                self.error_occurred.emit("GeoPandas nincs telepítve!")
                return

            self.progress_updated.emit(10)

            # Counties betöltése
            counties_file = self.data_dir / "counties.geojson"
            if counties_file.exists():
                self.counties_gdf = gpd.read_file(counties_file)
                self.counties_loaded.emit(self.counties_gdf)
                self.progress_updated.emit(50)
            else:
                self.error_occurred.emit(f"Counties fájl nem található: {counties_file}")
                return

            # Postal codes betöltése (opcionális, nagy fájl)
            postal_codes_file = self.data_dir / "postal_codes.geojson"
            if postal_codes_file.exists():
                # Nagy fájl, részleges betöltés vagy kihagyás
                file_size = postal_codes_file.stat().st_size
                if file_size < 50 * 1024 * 1024:  # 50MB alatt
                    self.postal_codes_gdf = gpd.read_file(postal_codes_file)
                    self.postal_codes_loaded.emit(self.postal_codes_gdf)
                    self.progress_updated.emit(90)
                else:
                    # Nagy fájl esetén kihagyás vagy részleges betöltés
                    self.progress_updated.emit(90)

            self.progress_updated.emit(100)
            self.completed.emit()

        except Exception as e:
            self.error_occurred.emit(f"GeoJSON betöltési hiba: {e}")
