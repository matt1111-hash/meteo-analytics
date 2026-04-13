# mypy: ignore-errors
from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget

from .interfaces import IMapEvents


class MapEvents(QObject, IMapEvents):
    """
    Handles signal bridges and event forwarding for the Map Tab.
    Decouples event logic from the main UI container.
    """

    # Public signals forwarded from components
    location_selected = Signal(object)  # Location data
    county_clicked_on_map = Signal(str)  # Folium county click
    map_interaction = Signal(str, object)  # interaction_type, data
    export_completed = Signal(str)  # file_path
    error_occurred = Signal(str)  # error_message

    # Internal coordination signals
    analytics_sync_requested = Signal(dict)

    def __init__(self, parent=None):  # noqa: D107
        super().__init__(parent)
        self.auto_sync_enabled = True

    def setup_signal_bridges(self, _target_widget: QWidget) -> None:
        """
        Connect signals from the target widget (main tab) to local handlers.
        In a full refactor, this would connect directly to sub-components.
        """
        # This implementation assumes the target_widget (HungarianMapTab)
        # exposes certain signals or components.
        # For now, we act as a signal sink/source.
        pass

    def handle_map_interaction(self, event_type: str, data: Any) -> None:
        """Handle generic map interactions."""
        self.map_interaction.emit(event_type, data)

        if event_type == "county_click":
            self.county_clicked_on_map.emit(str(data))
        elif event_type == "location_select":
            self.location_selected.emit(data)

    def on_export_completed(self, file_path: str) -> None:
        """Handle successful export."""
        self.export_completed.emit(file_path)

    def on_error(self, message: str) -> None:
        """Handle errors."""
        self.error_occurred.emit(message)

    def set_auto_sync(self, enabled: bool) -> None:
        """Toggle auto-synchronization."""
        self.auto_sync_enabled = enabled
