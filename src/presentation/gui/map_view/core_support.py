# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Map View - Core

🗺️ Map View Widget - Teljes magyar Folium térképes nézet

Képességek:
- Folium HungarianMapTab integráció
- Signal forwarding
- Alapvető delegációs metódusok

Fájl: src/presentation/gui/map_view/core.py
"""

from typing import Any, Dict, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..theme_manager import register_widget_for_theming
from .debug import MapViewDebugMixin
from .hungarian_map_tab import HungarianMapTab
from .integration import MapViewIntegrationMixin
