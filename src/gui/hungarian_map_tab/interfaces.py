from typing import Any, Dict

from PySide6.QtWidgets import QWidget


class IMapWidget:
    """Interface for the Map Rendering Engine."""

    def render_map(self, configuration: Dict[str, Any]) -> None:
        """Render the map with the given configuration."""
        raise NotImplementedError

    def add_weather_overlay(self, data: Any) -> None:
        """Add a weather overlay to the map."""
        raise NotImplementedError

    def is_ready(self) -> bool:
        """Check if the map is fully initialized and ready."""
        raise NotImplementedError

    def export_map(self) -> str:
        """Export the current map view to an HTML string or file path."""
        raise NotImplementedError

class IMapEvents:
    """Interface for the Event Bridge."""

    def setup_signal_bridges(self, target_widget: QWidget) -> None:
        """Connect signals from the target widget to event handlers."""
        raise NotImplementedError

    def handle_map_interaction(self, event_type: str, data: Any) -> None:
        """Handle a generic map interaction event."""
        raise NotImplementedError

class IMapAnalyticsBridge:
    """Interface for the Analytics Synchronization."""

    def sync_analysis_parameters(self, params: Dict[str, Any]) -> None:
        """Sync the map state with new analysis parameters."""
        raise NotImplementedError

    def sync_weather_parameters(self, params: Dict[str, Any]) -> None:
        """Sync the map state with new weather parameters."""
        raise NotImplementedError

    def refresh_with_new_parameters(self, bundle: Dict[str, Any]) -> None:
        """Refresh the map with a complete bundle of new parameters."""
        raise NotImplementedError
