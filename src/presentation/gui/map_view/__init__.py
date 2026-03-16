#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Map View Module

🗺️ Map View Widget - Teljes magyar Folium térképes nézet

Képességek:
- Folium HungarianMapTab integráció
- Signal forwarding
- JavaScript bridge támogatás
- Kétirányú szinkronizáció

Fájl: src/presentation/gui/map_view/__init__.py
"""

# Re-export for backward compatibility
from .core import MapView
from .demo import demo_map_view_folium

__all__ = ["MapView", "demo_map_view_folium"]
