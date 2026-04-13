#!/usr/bin/env python3
# mypy: ignore-errors

"""
🗺️ Map Interactions - JavaScript híd és HTTP szerver.

FÁJL: src/presentation/gui/map/map_interactions.py
"""

import http.server
import os
import socketserver
import tempfile
import uuid

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QWidget

try:
    import folium  # noqa: F401

    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False


class LocalHttpServerThread(QThread):
    """
    🌐 Helyi HTTP szerver QThread-ben a Folium térképek kiszolgálásához.
    """

    server_ready = Signal(str, int)
    server_error = Signal(str)

    def __init__(self, parent=None):  # noqa: D107
        super().__init__(parent)
        self.server = None
        self.httpd = None
        self.temp_dir = tempfile.gettempdir()
        self.host = "127.0.0.1"
        self.port = 0
        self.running = False

    def run(self) -> None:
        """
        🚀 HTTP szerver indítása háttérben.
        """
        try:
            os.chdir(self.temp_dir)

            class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
                def log_message(self, format, *args):
                    pass

            with socketserver.TCPServer((self.host, self.port), QuietHTTPRequestHandler) as httpd:
                self.httpd = httpd
                self.port = httpd.server_address[1]
                self.running = True

                print(f"🌐 Local HTTP Server started: http://{self.host}:{self.port}")
                self.server_ready.emit(self.host, self.port)
                httpd.serve_forever()

        except Exception as e:
            error_msg = f"HTTP Server error: {e}"
            print(f"❌ {error_msg}")
            self.server_error.emit(error_msg)

    def stop(self) -> None:
        """
        🛑 HTTP szerver leállítása.
        """
        if self.httpd:
            self.httpd.shutdown()
            self.running = False
            print("🛑 Local HTTP Server stopped")


class JavaScriptBridge(QWidget):
    """
    🌉 JavaScript ↔ PySide6 kommunikációs híd.
    """

    county_clicked = Signal(str)
    coordinates_clicked = Signal(float, float)
    map_moved = Signal(float, float, int)
    county_hovered = Signal(str)
    county_unhovered = Signal()

    def __init__(self) -> None:  # noqa: D107
        super().__init__()
        self.bridge_id = str(uuid.uuid4())
        print(f"🌉 JavaScriptBridge created with ID: {self.bridge_id}")

    def handle_county_click(self, county_name: str) -> None:
        """Megye kattintás kezelése JavaScript-ből."""
        print(f"🖱️ JS Bridge: County clicked: {county_name}")
        self.county_clicked.emit(county_name)

    def handle_coordinates_click(self, lat: float, lon: float) -> None:
        """Koordináta kattintás kezelése."""
        print(f"📍 JS Bridge: Coordinates clicked: {lat}, {lon}")
        self.coordinates_clicked.emit(lat, lon)

    def handle_map_move(self, lat: float, lon: float, zoom: int) -> None:
        """Térkép mozgás kezelése."""
        print(f"🗺️ JS Bridge: Map moved: {lat}, {lon}, zoom={zoom}")
        self.map_moved.emit(lat, lon, zoom)

    def handle_county_hover(self, county_name: str) -> None:
        """Megye hover kezelése."""
        print(f"👆 JS Bridge: County hovered: {county_name}")
        self.county_hovered.emit(county_name)

    def handle_county_unhover(self) -> None:
        """Megye hover vége kezelése."""
        self.county_unhovered.emit()


# Export
__all__ = [
    "JavaScriptBridge",
    "LocalHttpServerThread",
]
