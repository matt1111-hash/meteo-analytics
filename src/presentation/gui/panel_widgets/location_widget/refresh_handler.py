#!/usr/bin/env python3
# mypy: ignore-errors

"""
Location Widget - Refresh and reactivation handlers.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import LocationWidget


class RefreshHandler:
    """Refresh handler a LocationWidget számára."""

    def __init__(self, widget: "LocationWidget"):
        """
        RefreshHandler inicializálása.

        Args:
            widget: LocationWidget instance
        """
        self.widget = widget

    def refresh_ui(self) -> None:
        """UI teljes frissítése - REAKTIVÁLÁS TÁMOGATÁS."""
        print("🔄 DEBUG: LocationWidget refresh_ui() called")

        try:
            # Widget enabled state check
            self.widget.ui.group.setEnabled(True)
            self.widget.ui.location_selector.setEnabled(True)

            # UniversalLocationSelector refresh
            if hasattr(self.widget.ui.location_selector, "refresh_ui"):
                self.widget.ui.location_selector.refresh_ui()

            # State validation
            if self.widget.current_city_data:
                name = self.widget.current_city_data.get("name", "Unknown")
                lat = self.widget.current_city_data.get("latitude", 0.0)
                lon = self.widget.current_city_data.get("longitude", 0.0)
                self.widget.signals._update_location_info(name, lat, lon)
                self.widget.ui.clear_btn.setEnabled(True)
            else:
                self.widget.ui.info_label.setText("Válasszon lokációt...")
                self.widget.theme._apply_label_styling(self.widget.ui.info_label, "secondary")
                self.widget.ui.clear_btn.setEnabled(False)

            print("✅ DEBUG: LocationWidget refresh_ui() completed")

        except Exception as e:
            print(f"❌ ERROR: LocationWidget refresh_ui() error: {e}")

    def force_refresh(self) -> None:
        """Kényszerített refresh - WIDGET REAKTIVÁLÁS."""
        print("⚡ DEBUG: LocationWidget force_refresh() called")

        try:
            # Explicit enable cascade
            self.widget.setEnabled(True)
            self.widget.ui.group.setEnabled(True)

            # UniversalLocationSelector force refresh
            if hasattr(self.widget.ui.location_selector, "force_refresh"):
                self.widget.ui.location_selector.force_refresh()
            elif hasattr(self.widget.ui.location_selector, "refresh_ui"):
                self.widget.ui.location_selector.refresh_ui()

            # Layout frissítés
            self.widget.updateGeometry()
            self.widget.update()

            print("✅ DEBUG: LocationWidget force_refresh() completed")

        except Exception as e:
            print(f"❌ ERROR: LocationWidget force_refresh() error: {e}")
