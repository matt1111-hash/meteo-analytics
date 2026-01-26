from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QObject, Signal

from src.presentation.gui.map import HungarianMapVisualizer
from src.presentation.gui.weather_data_bridge import WeatherDataBridge
from src.data.models import AnalyticsResult

from .interfaces import IMapWidget

class MapWidget(QWidget, IMapWidget):
    """
    Wrapper around HungarianMapVisualizer to implement IMapWidget.
    Handles rendering logic and weather overlay generation.
    """
    
    # Signals forwarded from visualizer
    map_ready = Signal()
    county_clicked = Signal(str)
    coordinates_clicked = Signal(float, float)
    map_moved = Signal(float, float, int)
    county_hovered = Signal(str)
    export_completed = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, visualizer: Optional[HungarianMapVisualizer] = None, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        
        if visualizer:
            self.map_visualizer = visualizer
            # Re-parenting logic if needed, but usually visualizer is already in a layout
            # If visualizer is passed, we assume it's already part of the UI, 
            # or we add it here if it has no parent layout.
            if self.map_visualizer.parent() is None:
                 self._layout.addWidget(self.map_visualizer)
        else:
            self.map_visualizer = HungarianMapVisualizer()
            self._layout.addWidget(self.map_visualizer)
        
        self.weather_bridge = WeatherDataBridge()
        
        self._connect_signals()

    def _connect_signals(self):
        """Connect internal signals."""
        self.map_visualizer.map_ready.connect(self.map_ready)
        self.map_visualizer.county_clicked.connect(self.county_clicked)
        self.map_visualizer.coordinates_clicked.connect(self.coordinates_clicked)
        self.map_visualizer.map_moved.connect(self.map_moved)
        self.map_visualizer.county_hovered.connect(self.county_hovered)
        self.map_visualizer.export_completed.connect(self.export_completed)
        self.map_visualizer.error_occurred.connect(self.error_occurred)

    # --- IMapWidget Implementation ---

    def render_map(self, configuration: Dict[str, Any]) -> None:
        """Render the map with the given configuration."""
        # For now, just triggers the visualizer's refresh or setup
        # In a full impl, this would pass config to map_visualizer
        pass

    def add_weather_overlay(self, data: Any) -> None:
        """Add a weather overlay to the map."""
        if hasattr(self.map_visualizer, "add_weather_overlay"):
            self.map_visualizer.add_weather_overlay(data)

    def is_ready(self) -> bool:
        """Check if the map is fully initialized and ready."""
        return self.map_visualizer.is_folium_ready()

    def export_map(self) -> str:
        """Export the current map view to an HTML string or file path."""
        # This functionality is usually triggered via a method on visualizer that emits a signal
        # For direct export, we might need to expose a method in Visualizer
        if hasattr(self.map_visualizer, "export_map"):
             # This usually initiates export and returns immediately, signal follows
             self.map_visualizer.export_map()
        return ""

    # --- Extended Functionality (Logic moved from MapTab) ---

    def generate_weather_overlay_from_analytics(self, analytics_result: AnalyticsResult) -> Optional[Any]:
        """
        Generate weather overlay data from analytics result.
        Uses WeatherDataBridge for conversion.
        """
        if not analytics_result:
            return None
            
        try:
            # WeatherDataBridge handles the complexity of data conversion
            overlay_data = self.weather_bridge.create_overlay_from_analytics(analytics_result)
            return overlay_data
        except Exception as e:
            self.error_occurred.emit(f"Overlay generation error: {e}")
            return None

    def refresh_folium_map(self):
        """Force refresh of the map."""
        if hasattr(self.map_visualizer, "refresh_map"):
            self.map_visualizer.refresh_map()
    
    def update_map_bounds(self, bounds):
        """Update map bounds."""
        self.map_visualizer.update_map_bounds(bounds)
        
    def set_selected_county(self, county_name):
        """Set selected county."""
        self.map_visualizer.set_selected_county(county_name)

    def set_counties_geodataframe(self, gdf):
        """Pass GeoDataFrame to visualizer."""
        self.map_visualizer.set_counties_geodataframe(gdf)

    def is_folium_available(self) -> bool:
        return self.map_visualizer.is_folium_available()