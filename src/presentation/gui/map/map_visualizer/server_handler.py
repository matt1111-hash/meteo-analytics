#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Map Visualizer - Server Handler

🌐 HTTP szerver kezelése

Képességek:
- Local HTTP server indítása
- Server event handlers
- Server status frissítés

Fájl: src/presentation/gui/map/map_visualizer/server_handler.py
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def start_local_server(self) -> None:
    """
    🌐 Local HTTP server indítása.

    Args:
        self: HungarianMapVisualizer instance
    """
    if self.local_server and self.local_server.running:
        return

    from .map_interactions import LocalHttpServerThread
    self.local_server = LocalHttpServerThread(self)
    self.local_server.server_ready.connect(self._on_server_ready)
    self.local_server.server_error.connect(self._on_server_error)
    self.local_server.start()


def _on_server_ready(self, host: str, port: int) -> None:
    """
    Server ready event handler.

    Args:
        self: HungarianMapVisualizer instance
        host: Server hostname
        port: Server port
    """
    self.http_host = host
    self.http_port = port
    self.server_status_label.setText(f"🌐 Szerver: http://{host}:{port}")
    self.server_status_label.setStyleSheet("color: #27AE60; font-weight: bold;")

    try:
        import folium  # noqa: F401
        self._generate_default_map()
    except ImportError:
        pass


def _on_server_error(self, error_message: str) -> None:
    """
    Server error event handler.

    Args:
        self: HungarianMapVisualizer instance
        error_message: Error message
    """
    self.server_status_label.setText("🌐 Szerver: HIBA")
    self.server_status_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
    self.error_occurred.emit(f"HTTP szerver hiba: {error_message}")


def _show_folium_error(self) -> None:
    """
    ⚠️ Folium hiányzó error megjelenítése.

    Args:
        self: HungarianMapVisualizer instance
    """
    self.status_label.setText("⚠️ Folium library hiányzik! pip install folium")
    self.progress_bar.setVisible(False)
    self.refresh_btn.setEnabled(False)
    self.export_btn.setEnabled(False)
    self.error_occurred.emit("Folium library not installed. Please run: pip install folium branca")
