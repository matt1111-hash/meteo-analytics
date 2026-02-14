"""
Action handlers for HungarianMapTab.

Ez a modul tartalmazza a felhasználói akciók kezelését.
"""

import logging

logger = logging.getLogger(__name__)


def _on_auto_sync_toggled(self, enabled: bool) -> None:
    """🔗 Auto-szinkronizáció ki/bekapcsolása."""
    self.auto_sync_enabled = enabled
    print(f"🔗 DEBUG: Auto-sync {'enabled' if enabled else 'disabled'}")

    if enabled:
        self.loading_status.setText("🔗 Auto-szinkronizáció engedélyezve")
    else:
        self.loading_status.setText("🔗 Auto-szinkronizáció letiltva")


def _on_auto_weather_refresh_toggled(self, enabled: bool) -> None:
    """🌤️ Auto weather refresh ki/bekapcsolása."""
    self.auto_weather_refresh_enabled = enabled
    print(f"🌤️ DEBUG: Auto weather refresh {'enabled' if enabled else 'disabled'}")

    if enabled:
        self.loading_status.setText("🌤️ Auto weather refresh engedélyezve")
    else:
        self.loading_status.setText("🌤️ Auto weather refresh letiltva")


def _reset_map_view(self) -> None:
    """🔄 Folium térkép nézet visszaállítása."""
    print("🔄 DEBUG: Resetting Folium map view to default Hungary view")

    if self.map_visualizer:
        self.map_visualizer.reset_map_view()
        self.loading_status.setText("🔄 Folium térkép visszaállítva alaphelyzetre")

    if self.location_selector:
        self.location_selector.reset_selection()

    self.map_interaction.emit(
        "view_reset", {"action": "reset_to_hungary", "source": "manual_reset"}
    )


def _export_map(self) -> None:
    """💾 Folium térkép exportálás kérése."""
    print("💾 DEBUG: Folium map export requested")

    if self.map_visualizer:
        self.map_visualizer._export_map()
    else:
        error_msg = "Folium térkép nem elérhető az exportáláshoz"
        self._on_error_occurred(error_msg)


def _refresh_folium_map(self) -> None:
    """🗺️ Folium térkép manuális újragenerálása."""
    print("🗺️ DEBUG: Manual Folium map refresh requested")

    if self.map_visualizer:
        self.map_visualizer._refresh_map()
        self.loading_status.setText("🔄 Folium térkép újragenerálása...")
    else:
        print("⚠️ DEBUG: Folium MapVisualizer not available for refresh")


__all__ = [
    "_on_auto_sync_toggled",
    "_on_auto_weather_refresh_toggled",
    "_reset_map_view",
    "_export_map",
    "_refresh_folium_map",
]
