#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Map Tab UI Setup Mixin.

Provides UI initialization methods for HungarianMapTab.
Extracted to reduce file size and improve maintainability.

Usage:
    class HungarianMapTab(MapTabUIMixin, MapAnalyticsSyncMixin, QWidget):
        ...
"""

from ..actions import (
    _export_map,
    _on_auto_sync_toggled,
    _on_auto_weather_refresh_toggled,
    _refresh_folium_map,
    _reset_map_view,
)
from ..folium_handlers import (
    on_county_selected,
    on_error_occurred,
    on_export_completed,
    on_folium_coordinates_clicked,
    on_folium_county_clicked,
    on_folium_county_hovered,
    on_folium_map_moved,
    on_folium_map_ready,
    on_location_selected,
    on_map_update_requested,
    on_selection_changed,
)
from ..weather_integration import _refresh_weather_overlay
from .ui_components import MapTabUIComponents
from .ui_handlers import MapTabUIHandlers


class MapTabActions:
    """
    Action handler methods for HungarianMapTab.

    These methods are imported from actions.py and other modules and made available as class methods.
    """
    # Import action functions as methods
    _on_auto_sync_toggled = _on_auto_sync_toggled
    _on_auto_weather_refresh_toggled = _on_auto_weather_refresh_toggled
    _reset_map_view = _reset_map_view
    _export_map = _export_map
    _refresh_folium_map = _refresh_folium_map
    _refresh_weather_overlay = _refresh_weather_overlay

    # Folium handlers (with _ prefix for consistency)
    _on_error_occurred = on_error_occurred
    _on_county_selected = on_county_selected
    _on_map_update_requested = on_map_update_requested
    _on_location_selected = on_location_selected
    _on_folium_map_ready = on_folium_map_ready
    _on_folium_county_clicked = on_folium_county_clicked
    _on_folium_map_moved = on_folium_map_moved
    _on_folium_county_hovered = on_folium_county_hovered
    _on_folium_coordinates_clicked = on_folium_coordinates_clicked
    _on_export_completed = on_export_completed
    _on_selection_changed = on_selection_changed


class MapTabUIMixin(MapTabUIComponents, MapTabUIHandlers, MapTabActions):
    """
    Mixin providing UI setup methods for HungarianMapTab.

    Combines UI component creation, signal handling, and actions.
    """
    pass


__all__ = ["MapTabUIMixin"]
