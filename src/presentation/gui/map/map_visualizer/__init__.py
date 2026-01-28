#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Map Visualizer Module

🗺️ Magyar Folium Térkép Vizualizáló - HELYI HTTP SZERVER VERZIÓ v3.0

Modul szerkezet:
- core.py: HungarianMapVisualizer main class (128 sor)
- ui_builder.py: UI setup (128 sor)
- signal_handlers.py: Signal kezelés (134 sor)
- server_handler.py: HTTP szerver kezelése (64 sor)
- map_generation.py: Map generálás (115 sor)
- public_api.py: Publikus API (205 sor)
- debug.py: Debug metódusok (73 sor)

Fájl: src/presentation/gui/map/map_visualizer/__init__.py
"""

from .core import HungarianMapVisualizer

__all__ = ['HungarianMapVisualizer']
