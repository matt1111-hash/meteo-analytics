# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Layer Builder - Térkép layer építők.

FÁJL: src/presentation/gui/map/layer_builder.py
"""

import json
from typing import TYPE_CHECKING

try:
    import folium
    from folium import plugins

    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

from .map_constants import (
    COUNTY_STYLE_HIGHLIGHTED,
    COUNTY_STYLE_HOVER,
    COUNTY_STYLE_SELECTED,
)
from .map_state import FoliumMapConfig

if TYPE_CHECKING:
    import geopandas as gpd
