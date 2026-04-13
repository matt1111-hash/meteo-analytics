# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Map Visualizer - Public API

🌐 Publikus interfész

Képességek:
- Overlay parameter kezelése
- Counties geodataframe beállítása
- Weather data beállítása
- Map bounds frissítése
- Map style és view kontrol

Fájl: src/presentation/gui/map/map_visualizer/public_api.py
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..map_state import FoliumMapConfig
