# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for SignalHandlersMixin."""

from __future__ import annotations

from .signal_handlers_support import *


def _reset_county_state(widget: Any) -> None:
    """Reset county-related state and refresh dependent UI."""
    widget.current_county = None
    widget._update_location_info()
    widget._update_debug_display()


def _log_county_selection(widget: Any, current_county: Any) -> None:
    """Log county selection details when debug is enabled."""
    if widget._debug_enabled:
        logger.info(f"🗺️ _on_county_changed() hívva - current_county combo data: {current_county}")


def _build_county_state(current_county: Any, geometry: Any) -> dict[str, Any]:
    """Build the stored county state payload."""
    return {
        "name": current_county,
        "geometry": geometry,
        "bounds": geometry.bounds,
        "centroid": geometry.centroid,
    }


def _handle_missing_county_selection(widget: Any, message: str, level: str = "info") -> None:
    """Handle county reset cases with optional debug logging."""
    if widget._debug_enabled:
        getattr(logger, level)(message)
    _reset_county_state(widget)


def _find_county_geometry(widget: Any, current_county: Any) -> Any | None:
    """Find geometry for the selected county."""
    county_row = widget.counties_gdf[widget.counties_gdf["megye"] == current_county]
    if county_row.empty:
        _handle_missing_county_selection(
            widget,
            f"🔧 Megye nem található GeoJSON-ben: {current_county}",
            "warning",
        )
        return None
    return county_row.geometry.iloc[0]


def _emit_county_selection_signals(widget: Any, current_county: Any, geometry: Any) -> None:
    """Emit county selection signals and refresh map state."""
    widget.county_selected.emit(current_county, geometry)
    widget.selection_changed.emit()
    widget.map_update_requested.emit(widget.current_county["bounds"])
    if widget._debug_enabled:
        logger.info(
            "✅ Signalok kibocsátva - county_selected, selection_changed, map_update_requested"
        )


class SignalHandlersMixinPart2Mixin:  # noqa: D101
    def _on_county_changed(self):
        """
        🔧 KRITIKUS JAVÍTÁS: Megye választás változás kezelése - STATE MANAGEMENT FIX!
        """
        current_county = self.county_combo.currentData()
        _log_county_selection(self, current_county)

        if current_county is None:
            _handle_missing_county_selection(self, "🔧 current_county None - state reset")
            return

        if self.counties_gdf is None:
            _handle_missing_county_selection(
                self, "🔧 counties_gdf None - GeoJSON adatok nem betöltve", "warning"
            )
            return

        try:
            geometry = _find_county_geometry(self, current_county)
            if geometry is None:
                return

            self.current_county = _build_county_state(current_county, geometry)

            if self._debug_enabled:
                logger.info(f"✅ current_county state frissítve: {self.current_county['name']}")
                logger.info(
                    f"🎯 Centroid koordináták: {self.current_county['centroid'].y:.4f}, {self.current_county['centroid'].x:.4f}"
                )

            self._update_location_info()
            self._update_debug_display()
            _emit_county_selection_signals(self, current_county, geometry)

        except Exception as e:
            if self._debug_enabled:
                logger.error(f"❌ Hiba _on_county_changed()-ben: {e}")
            _reset_county_state(self)

    def _update_location_info(self):
        """
        📍 Lokáció információk frissítése.
        """
        from src.domain.entities.location import Location

        if self.current_county is None:
            self.lat_label.setText("Szélesség: -")
            self.lon_label.setText("Hosszúság: -")
            self.area_label.setText("Terület: -")
            self.current_location = None
            return

        # Központi koordináták
        centroid = self.current_county["centroid"]
        lat = centroid.y
        lon = centroid.x

        self.lat_label.setText(f"Szélesség: {lat:.4f}°")
        self.lon_label.setText(f"Hosszúság: {lon:.4f}°")

        # Terület számítás (közelítő, fok alapú)
        bounds = self.current_county["bounds"]
        width = bounds[2] - bounds[0]  # maxx - minx
        height = bounds[3] - bounds[1]  # maxy - miny

        self.area_label.setText(f"Határoló téglalap: {width:.3f}° × {height:.3f}°")  # noqa: RUF001

        # Location objektum létrehozása
        self.current_location = Location(
            identifier=self.current_county["name"],
            display_name=self.current_county["name"],
            latitude=lat,
            longitude=lon,
            country_code="HU",
            timezone="Europe/Budapest",
            metadata={
                "region": self.current_region.name if self.current_region else None,
                "region_display_name": self.current_region.display_name
                if self.current_region
                else None,
                "nuts_code": self.current_region.nuts_code if self.current_region else None,
                "county": self.current_county["name"],
                "source": "hungarian_location_selector",
                "bounds": bounds,
                "administrative_center": self.current_region.administrative_center
                if self.current_region
                else None,
            },
        )

        # Location signal kibocsátása
        self.location_selected.emit(self.current_location)

    def _update_debug_display(self):
        """
        🔧 JAVÍTOTT: Debug információk frissítése.
        """
        if not self._debug_enabled or not hasattr(self, "debug_label"):
            return

        state_info = {
            "region": self.current_region.display_name if self.current_region else None,
            "county": self.current_county["name"] if self.current_county else None,
            "location": self.current_location.display_name if self.current_location else None,
        }

        self.debug_label.setText(f"🔧 DEBUG: State = {state_info}")

    def _center_map_on_selection(self):
        """
        🎯 Térkép központosítása a kiválasztott területre.
        """
        if self.current_county is None:
            return

        bounds = self.current_county["bounds"]
        self.map_update_requested.emit(bounds)
