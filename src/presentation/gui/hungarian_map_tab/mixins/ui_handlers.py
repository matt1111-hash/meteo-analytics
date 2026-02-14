#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Map Tab UI Handlers - Signal connection methods.

Provides signal-slot connection methods for HungarianMapTab.
"""

from src.presentation.gui.theme_manager import register_widget_for_theming


class MapTabUIHandlers:
    """
    Signal connection methods for HungarianMapTab.

    Connects UI widgets to their respective event handlers.
    """

    def _setup_theme(self) -> None:
        """Apply theme settings."""
        register_widget_for_theming(self, "container")

    def _connect_signals(self) -> None:
        """Connect signal-slot relationships."""
        # Header button connections
        self.reset_view_btn.clicked.connect(self._reset_map_view)
        self.export_map_btn.clicked.connect(self._export_map)
        self.refresh_folium_btn.clicked.connect(self._refresh_folium_map)
        self.refresh_weather_btn.clicked.connect(self._refresh_weather_overlay)

        # Checkbox connections
        self.auto_sync_check.toggled.connect(self._on_auto_sync_toggled)
        self.auto_weather_refresh_check.toggled.connect(
            self._on_auto_weather_refresh_toggled
        )

        # Location selector signals
        if self.location_selector:
            self.location_selector.county_selected.connect(self._on_county_selected)
            self.location_selector.map_update_requested.connect(
                self._on_map_update_requested
            )
            self.location_selector.location_selected.connect(self._on_location_selected)
            self.location_selector.selection_changed.connect(self._on_selection_changed)

        # Map visualizer signals
        if self.map_visualizer:
            self.map_visualizer.map_ready.connect(self._on_folium_map_ready)
            self.map_visualizer.county_clicked.connect(self._on_folium_county_clicked)
            self.map_visualizer.coordinates_clicked.connect(
                self._on_folium_coordinates_clicked
            )
            self.map_visualizer.map_moved.connect(self._on_folium_map_moved)
            self.map_visualizer.county_hovered.connect(self._on_folium_county_hovered)
            self.map_visualizer.export_completed.connect(self._on_export_completed)
            self.map_visualizer.error_occurred.connect(self._on_error_occurred)


__all__ = ["MapTabUIHandlers"]
