#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Hungarian Location Selector - Signal Handlers
Magyar Klímaanalitika MVP - Signal kezelő metódusok
"""

import logging

logger = logging.getLogger(__name__)


class SignalHandlersMixin:
    """
    🔗 Signal handler mixin a HungarianLocationSelector számára.
    """

    def _on_counties_loaded(self, counties_gdf):
        """
        🗺️ Megyeadatok betöltése befejezve.
        """
        self.counties_gdf = counties_gdf
        self.progress_label.setText("✅ Megyeadatok betöltve...")
        self._update_county_combo()

    def _on_postal_codes_loaded(self, postal_codes_gdf):
        """
        📫 Irányítószám adatok betöltése befejezve.
        """
        self.postal_codes_gdf = postal_codes_gdf
        self.progress_label.setText("✅ Irányítószám adatok betöltve...")

    def _on_data_error(self, error_message: str):
        """
        ❌ Adatok betöltési hiba kezelése.
        """
        self.progress_label.setText(f"❌ {error_message}")
        self.progress_bar.setValue(0)

    def _on_data_loading_completed(self):
        """
        ✅ Összes adat betöltése befejezve.
        """
        self.progress_label.setText("✅ Térképi adatok betöltve!")
        self.progress_bar.setValue(100)

        # Funkcionalitások engedélyezése
        self.county_combo.setEnabled(True)
        self.center_map_btn.setEnabled(True)

        # Timer a progress eltüntetéséhez
        from PySide6.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.progress_label.setText("Kész használatra"))

    def _on_region_changed(self):
        """
        🏛️ Statisztikai régió választás változás kezelése - JAVÍTOTT!
        """
        current_data = self.region_combo.currentData()

        if current_data is None:
            self.current_region = None
            self.region_info.clear()
            self._update_county_combo()
            self._update_debug_display()
            return

        # Régió adatok megjelenítése
        region_data = self.region_data[current_data]
        self.current_region = region_data

        # 🔧 JAVÍTOTT: Információs panel frissítése több info-val
        info_text = f"""
<b>{region_data.display_name}</b> ({region_data.nuts_code})<br>
<b>Közigazgatási központ:</b> {region_data.administrative_center}<br>
<b>Megyék:</b> {', '.join(region_data.counties)}<br>
<b>Átlagos évi hőmérséklet:</b> {region_data.avg_temp_annual}°C<br>
<b>Átlagos évi csapadék:</b> {region_data.avg_precipitation_annual} mm<br>
<br>
<b>Jellemzők:</b><br>
• {' <br>• '.join(region_data.characteristics)}<br>
<br>
<b>Leírás:</b> {region_data.description}
        """.strip()

        self.region_info.setHtml(info_text)

        # Megyék frissítése
        self._update_county_combo()

        # 🔧 JAVÍTOTT: Debug display frissítése
        self._update_debug_display()

        # Signal kibocsátása
        self.region_selected.emit(region_data)
        self.selection_changed.emit()

        # 🔧 JAVÍTOTT: Debug logging
        if self._debug_enabled:
            logger.info(f"🏛️ Régió kiválasztva: {region_data.display_name} - current_region state frissítve")

    def _update_county_combo(self):
        """
        🗺️ Megye combo frissítése a kiválasztott régió alapján - JAVÍTOTT!
        """
        self.county_combo.clear()

        if self.current_region is None:
            self.county_combo.addItem("Először válassz régiót...", None)
            self.county_combo.setEnabled(False)
            return

        if self.counties_gdf is None:
            self.county_combo.addItem("Térképi adatok betöltése...", None)
            self.county_combo.setEnabled(False)
            return

        # 🔧 KRITIKUS: Régió megyéinek hozzáadása (statisztikai régió alapján)
        self.county_combo.addItem("Válassz megyét...", None)

        available_counties = set(self.counties_gdf['megye'].tolist())
        region_counties = set(self.current_region.counties)

        # Közös megyék (régió és GeoJSON alapján)
        valid_counties = region_counties.intersection(available_counties)

        for county in sorted(valid_counties):
            self.county_combo.addItem(county, county)

        # Egyéb megyék is (ha vannak)
        other_counties = available_counties - region_counties
        if other_counties:
            self.county_combo.addItem("--- Egyéb megyék ---", None)
            for county in sorted(other_counties):
                self.county_combo.addItem(f"{county} (egyéb)", county)

        self.county_combo.setEnabled(True)

    def _on_county_changed(self):
        """
        🔧 KRITIKUS JAVÍTÁS: Megye választás változás kezelése - STATE MANAGEMENT FIX!
        """
        current_county = self.county_combo.currentData()

        # 🔧 JAVÍTOTT: Debug logging hozzáadva
        if self._debug_enabled:
            logger.info(f"🗺️ _on_county_changed() hívva - current_county combo data: {current_county}")

        if current_county is None:
            if self._debug_enabled:
                logger.info("🔧 current_county None - state reset")
            self.current_county = None
            self._update_location_info()
            self._update_debug_display()
            return

        if self.counties_gdf is None:
            if self._debug_enabled:
                logger.warning("🔧 counties_gdf None - GeoJSON adatok nem betöltve")
            self.current_county = None
            self._update_location_info()
            self._update_debug_display()
            return

        # 🔧 JAVÍTOTT: Megye geometria lekérdezése robust error handling-gal
        try:
            county_row = self.counties_gdf[self.counties_gdf['megye'] == current_county]

            if county_row.empty:
                if self._debug_enabled:
                    logger.warning(f"🔧 Megye nem található GeoJSON-ben: {current_county}")
                self.current_county = None
                self._update_location_info()
                self._update_debug_display()
                return

            # 🔧 KRITIKUS: Megye adatok tárolása - STATE FRISSÍTÉS!
            geometry = county_row.geometry.iloc[0]
            self.current_county = {
                'name': current_county,
                'geometry': geometry,
                'bounds': geometry.bounds,  # (minx, miny, maxx, maxy)
                'centroid': geometry.centroid
            }

            # 🔧 JAVÍTOTT: Debug logging a state frissítés után
            if self._debug_enabled:
                logger.info(f"✅ current_county state frissítve: {self.current_county['name']}")
                logger.info(f"🎯 Centroid koordináták: {self.current_county['centroid'].y:.4f}, {self.current_county['centroid'].x:.4f}")

            # Lokáció info frissítése
            self._update_location_info()

            # 🔧 JAVÍTOTT: Debug display frissítése
            self._update_debug_display()

            # Signalok kibocsátása
            self.county_selected.emit(current_county, geometry)
            self.selection_changed.emit()

            # Térkép frissítés kérése
            self.map_update_requested.emit(self.current_county['bounds'])

            if self._debug_enabled:
                logger.info("✅ Signalok kibocsátva - county_selected, selection_changed, map_update_requested")

        except Exception as e:
            # 🔧 JAVÍTOTT: Robust error handling
            if self._debug_enabled:
                logger.error(f"❌ Hiba _on_county_changed()-ben: {e}")
            self.current_county = None
            self._update_location_info()
            self._update_debug_display()

    def _update_location_info(self):
        """
        📍 Lokáció információk frissítése.
        """
        from src.data.models import Location

        if self.current_county is None:
            self.lat_label.setText("Szélesség: -")
            self.lon_label.setText("Hosszúság: -")
            self.area_label.setText("Terület: -")
            self.current_location = None
            return

        # Központi koordináták
        centroid = self.current_county['centroid']
        lat = centroid.y
        lon = centroid.x

        self.lat_label.setText(f"Szélesség: {lat:.4f}°")
        self.lon_label.setText(f"Hosszúság: {lon:.4f}°")

        # Terület számítás (közelítő, fok alapú)
        bounds = self.current_county['bounds']
        width = bounds[2] - bounds[0]  # maxx - minx
        height = bounds[3] - bounds[1]  # maxy - miny

        self.area_label.setText(f"Határoló téglalap: {width:.3f}° × {height:.3f}°")

        # Location objektum létrehozása
        self.current_location = Location(
            identifier=self.current_county['name'],
            display_name=self.current_county['name'],
            latitude=lat,
            longitude=lon,
            country_code="HU",
            timezone="Europe/Budapest",
            metadata={
                'region': self.current_region.name if self.current_region else None,
                'region_display_name': self.current_region.display_name if self.current_region else None,
                'nuts_code': self.current_region.nuts_code if self.current_region else None,
                'county': self.current_county['name'],
                'source': 'hungarian_location_selector',
                'bounds': bounds,
                'administrative_center': self.current_region.administrative_center if self.current_region else None
            }
        )

        # Location signal kibocsátása
        self.location_selected.emit(self.current_location)

    def _update_debug_display(self):
        """
        🔧 JAVÍTOTT: Debug információk frissítése.
        """
        if not self._debug_enabled or not hasattr(self, 'debug_label'):
            return

        state_info = {
            'region': self.current_region.display_name if self.current_region else None,
            'county': self.current_county['name'] if self.current_county else None,
            'location': self.current_location.display_name if self.current_location else None
        }

        self.debug_label.setText(f"🔧 DEBUG: State = {state_info}")

    def _center_map_on_selection(self):
        """
        🎯 Térkép központosítása a kiválasztott területre.
        """
        if self.current_county is None:
            return

        bounds = self.current_county['bounds']
        self.map_update_requested.emit(bounds)
