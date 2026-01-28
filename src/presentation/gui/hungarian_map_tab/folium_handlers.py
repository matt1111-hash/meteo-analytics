"""
Folium event handlers for HungarianMapTab.

Ez a modul tartalmazza a Folium térképhez kapcsolódó event handler-eket.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def on_county_selected(self, county_name: str, geometry) -> None:
    """🗺️ Megye kiválasztva a location selector-ben → Folium térkép frissítés."""
    print(f"🗺️ DEBUG: County selected in LocationSelector: {county_name}")

    if not self.auto_sync_enabled:
        print("🔗 DEBUG: Auto-sync disabled, skipping Folium update")
        return

    if not self.map_visualizer or not self.is_folium_ready:
        print("⚠️ DEBUG: Folium MapVisualizer not ready for county selection")
        return

    try:
        bounds = geometry.bounds
        print(f"🎯 DEBUG: County bounds: {bounds}")

        self.map_visualizer.update_map_bounds(bounds)
        self.map_visualizer.set_selected_county(county_name)

        self.loading_status.setText(f"🎯 Folium térkép központosítva: {county_name}")

        self.map_interaction.emit("county_focused", {
            'county_name': county_name,
            'bounds': bounds,
            'source': 'location_selector'
        })

    except Exception as e:
        error_msg = f"Megye Folium térképes megjelenítési hiba: {e}"
        print(f"❌ DEBUG: {error_msg}")
        self._on_error_occurred(error_msg)


def on_map_update_requested(self, bounds) -> None:
    """🎯 Térkép frissítés kérés a location selector-től → Folium frissítés."""
    print(f"🎯 DEBUG: Map update requested with bounds: {bounds}")

    if self.map_visualizer and self.is_folium_ready and self.auto_sync_enabled:
        self.map_visualizer.update_map_bounds(bounds)
        self.loading_status.setText("🎯 Folium térkép frissítve")
    else:
        print("⚠️ DEBUG: Folium MapVisualizer not ready for bounds update")


def on_location_selected(self, location) -> None:
    """🔍 Lokáció kiválasztva a location selector-ben → forward signal."""
    print(f"🔍 DEBUG: Location selected: {location.display_name if location else 'None'}")

    self.current_location_data = location
    self.location_selected.emit(location)

    if location:
        self.loading_status.setText(f"🔍 Kiválasztva: {location.display_name}")


def on_selection_changed(self) -> None:
    """🔄 Selection változás a location selector-ben."""
    print("🔄 DEBUG: Location selector selection changed")

    if self.location_selector:
        selection_info = self.location_selector.get_current_selection()

        region = selection_info.get('region')
        county = selection_info.get('county')

        if county:
            status = f"🗺️ {region.display_name if region else 'Régió'} → {county['name']}"
        elif region:
            status = f"🌡️ {region.display_name}"
        else:
            status = "🗺️ Válassz éghajlati régiót és megyét"

        self.loading_status.setText(status)


def on_folium_map_ready(self) -> None:
    """✅ Folium térkép kész és betöltve → funkciók engedélyezése."""
    print("✅ DEBUG: Folium map ready - enabling functionality")

    self.is_folium_ready = True

    self.export_map_btn.setEnabled(True)
    self.refresh_folium_btn.setEnabled(True)

    if self.weather_bridge and self.multi_city_engine:
        self.refresh_weather_btn.setEnabled(True)

    self.folium_status_label.setText("✅ Folium kész")
    self.folium_status_label.setStyleSheet("color: #27AE60;")

    self.loading_status.setText("✅ Folium interaktív térkép kész!")

    self.folium_ready.emit()


def on_folium_county_clicked(self, county_name: str) -> None:
    """🖱️ Megye kattintás a Folium térképen → location selector frissítés."""
    print(f"🖱️ DEBUG: County clicked on Folium map: {county_name}")

    if self.location_selector and self.auto_sync_enabled:
        success = self.location_selector.set_county(county_name)
        if success:
            print(f"✅ DEBUG: Location selector synced to county: {county_name}")
        else:
            print(f"⚠️ DEBUG: Failed to sync location selector to county: {county_name}")

    self.county_clicked_on_map.emit(county_name)
    self.map_interaction.emit("county_clicked", {
        'county_name': county_name,
        'source': 'folium_map'
    })

    self.loading_status.setText(f"🖱️ Megye kattintva Folium térképen: {county_name}")


def on_folium_coordinates_clicked(self, lat: float, lon: float) -> None:
    """🔍 Koordináta kattintás a Folium térképen."""
    print(f"🔍 DEBUG: Coordinates clicked on Folium map: {lat:.4f}, {lon:.4f}")

    self.map_interaction.emit("coordinates_clicked", {
        'lat': lat,
        'lon': lon,
        'source': 'folium_map'
    })

    self.loading_status.setText(f"🔍 Koordináta: {lat:.4f}°, {lon:.4f}°")


def on_folium_map_moved(self, lat: float, lon: float, zoom: int) -> None:
    """🗺️ Folium térkép mozgott (zoom/pan)."""
    print(f"🗺️ DEBUG: Folium map moved: center=({lat:.4f}, {lon:.4f}), zoom={zoom}")

    self.map_interaction.emit("map_moved", {
        'lat': lat,
        'lon': lon,
        'zoom': zoom,
        'source': 'folium_map'
    })


def on_folium_county_hovered(self, county_name: str) -> None:
    """👆 Megye hover a Folium térképen."""
    print(f"👆 DEBUG: County hovered on Folium map: {county_name}")

    self.loading_status.setText(f"👆 Hover: {county_name}")

    self.map_interaction.emit("county_hovered", {
        'county_name': county_name,
        'source': 'folium_map'
    })


def on_export_completed(self, file_path: str) -> None:
    """💾 Export befejezve → forward signal és status frissítés."""
    print(f"💾 DEBUG: Folium export completed: {file_path}")

    self.loading_status.setText(f"💾 Folium térkép exportálva: {Path(file_path).name}")
    self.export_completed.emit(file_path)


def on_error_occurred(self, error_message: str) -> None:
    """❌ Hiba történt → forward signal és status frissítés."""
    print(f"❌ DEBUG: Folium error occurred: {error_message}")

    self.loading_status.setText(f"❌ Folium hiba: {error_message}")
    self.error_occurred.emit(error_message)


__all__ = [
    "on_county_selected",
    "on_map_update_requested",
    "on_location_selected",
    "on_selection_changed",
    "on_folium_map_ready",
    "on_folium_county_clicked",
    "on_folium_coordinates_clicked",
    "on_folium_map_moved",
    "on_folium_county_hovered",
    "on_export_completed",
    "on_error_occurred",
]
