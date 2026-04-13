# mypy: ignore-errors
"""
Initialization module for HungarianMapTab.

Ez a modul tartalmazza a komponensek inicializálását.
"""

import logging

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)


def initialize_weather_components(self) -> None:
    """
    🌤️ Weather integráció komponensek inicializálása.
    """
    try:
        from src.analytics.ports import get_multi_city_engine_port  # noqa: PLC0415
        from src.presentation.gui.weather_data_bridge import WeatherDataBridge  # noqa: PLC0415

        self.weather_bridge = WeatherDataBridge()
        print("✅ DEBUG: WeatherDataBridge initialized")

        self.multi_city_engine = get_multi_city_engine_port()
        print("✅ DEBUG: MultiCityEngine initialized")

    except Exception as e:
        print(f"❌ DEBUG: Weather components initialization error: {e}")
        self.weather_bridge = None
        self.multi_city_engine = None


def initialize_components_steps(self) -> None:
    """
    Komponensek inicializálása és adatok betöltése.
    """
    print("🔧 DEBUG: Initializing HungarianMapTab components...")

    # Loading indikáció
    self.loading_progress.setVisible(True)
    self.loading_progress.setValue(10)
    self.loading_status.setText("🔄 GeoJSON adatok betöltése...")
    self.data_loading_started.emit()

    # Weather komponensek státusz
    if self.weather_bridge and self.multi_city_engine:
        self.weather_status_label.setText("🌤️ Weather: Kész")
        self.weather_status_label.setStyleSheet("color: #27AE60;")
    else:
        self.weather_status_label.setText("🌤️ Weather: Hiba")
        self.weather_status_label.setStyleSheet("color: #E74C3C;")

    # Analytics Sync státusz
    self.analytics_sync_label.setText("🔄 Analytics Sync: Kész")
    self.analytics_sync_label.setStyleSheet("color: #27AE60;")

    # Folium elérhetőség
    if self.map_visualizer and not self.map_visualizer.is_folium_available():
        self.folium_status_label.setText("❌ Folium hiányzik")
        self.folium_status_label.setStyleSheet("color: #E74C3C;")
        _show_folium_installation_message(self)
    else:
        self.folium_status_label.setText("✅ Folium elérhető")
        self.folium_status_label.setStyleSheet("color: #27AE60;")

    # Timer a folyamat szimulálásához
    QTimer.singleShot(500, lambda: _initialize_step_1(self))


def _show_folium_installation_message(self) -> None:
    """⚠️ Folium hiány esetén telepítési útmutató."""
    QMessageBox.information(
        self,
        "Folium Library Hiányzik",
        "A teljes interaktív térkép működéséhez szükséges a Folium library.\n\n"
        "Telepítés:\n"
        "pip install folium branca geopandas\n\n"
        "A térkép static módban fog működni Folium nélkül.",
    )


def _initialize_step_1(self) -> None:
    """Inicializálás 1. lépés: Location selector adatok."""
    print("🔧 DEBUG: Initialization step 1 - Location selector data")

    self.loading_progress.setValue(30)
    self.loading_status.setText("🔍 Lokáció választó inicializálása...")

    QTimer.singleShot(1000, lambda: _initialize_step_2(self))


def _initialize_step_2(self) -> None:
    """Inicializálás 2. lépés: GeoDataFrame megosztás."""
    print("🔧 DEBUG: Initialization step 2 - GeoDataFrame sharing")

    self.loading_progress.setValue(60)
    self.loading_status.setText("🗺️ Folium térképes adatok megosztása...")

    if self.location_selector:
        self.counties_gdf = self.location_selector.get_counties_geodataframe()

        if self.counties_gdf is not None:
            print(f"✅ DEBUG: Counties GeoDataFrame received: {len(self.counties_gdf)} counties")

            if self.map_visualizer:
                self.map_visualizer.set_counties_geodataframe(self.counties_gdf)
                print("✅ DEBUG: Counties GeoDataFrame shared with Folium MapVisualizer")
        else:
            print("⚠️ DEBUG: Counties GeoDataFrame not available yet")

    QTimer.singleShot(1000, lambda: _initialize_step_3(self))


def _initialize_step_3(self) -> None:
    """Inicializálás 3. lépés: Folium térkép generálás."""
    print("🔧 DEBUG: Initialization step 3 - Folium map generation")

    self.loading_progress.setValue(80)
    self.loading_status.setText("🗺️ Folium interaktív térkép generálása...")

    if self.map_visualizer and self.map_visualizer.is_folium_available():
        pass  # A map_visualizer automatikusan indítja a Folium generálást

    QTimer.singleShot(1500, lambda: _initialize_step_4(self))


def _initialize_step_4(self) -> None:
    """Inicializálás 4. lépés: Finalizálás."""
    print("🔧 DEBUG: Initialization step 4 - Finalization")

    self.loading_progress.setValue(95)
    self.loading_status.setText("✅ Folium térképes dashboard finalizálása...")

    self.is_data_loaded = True

    QTimer.singleShot(500, lambda: _initialization_complete(self))


def _initialization_complete(self) -> None:
    """Inicializálás befejezése."""
    print("✅ DEBUG: HungarianMapTab initialization complete")

    self.loading_progress.setValue(100)
    self.loading_status.setText("✅ Magyar Folium térképes dashboard kész!")

    QTimer.singleShot(2000, lambda: _hide_loading_indicators(self))
    self.data_loading_completed.emit()


def _hide_loading_indicators(self) -> None:
    """Loading indikátorok elrejtése."""
    self.loading_progress.setVisible(False)
    self.loading_status.setText(
        "🗺️ Kattints a megyékre a Folium térképen vagy használd a bal oldali választót!"
    )


__all__ = [
    "initialize_components_steps",
    "initialize_weather_components",
]
