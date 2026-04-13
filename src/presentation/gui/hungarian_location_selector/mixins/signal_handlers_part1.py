# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for SignalHandlersMixin."""

from __future__ import annotations

from .signal_handlers_support import *


class SignalHandlersMixinPart1Mixin:  # noqa: D101
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
        from PySide6.QtCore import QTimer  # noqa: PLC0415

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
<b>Megyék:</b> {", ".join(region_data.counties)}<br>
<b>Átlagos évi hőmérséklet:</b> {region_data.avg_temp_annual}°C<br>
<b>Átlagos évi csapadék:</b> {region_data.avg_precipitation_annual} mm<br>
<br>
<b>Jellemzők:</b><br>
• {" <br>• ".join(region_data.characteristics)}<br>
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
            logger.info(
                f"🏛️ Régió kiválasztva: {region_data.display_name} - current_region state frissítve"
            )

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

        available_counties = set(self.counties_gdf["megye"].tolist())
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
