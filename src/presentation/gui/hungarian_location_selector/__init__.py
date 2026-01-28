#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Hungarian Location Selector - GET_CURRENT_CITY() STATE MANAGEMENT FIX
Magyar Klímaanalitika MVP - Térkép Komponens Lokáció Választó

🔧 KRITIKUS JAVÍTÁS: GET_CURRENT_CITY() STATE MANAGEMENT HIBA KIJAVÍTVA
- QueryControlWidget kompatibilitás 100% működőképes
- State frissítés javítva: _on_county_changed() debug logging hozzáadva
- get_current_city() enhanced logic defensive programming-gal
- Selection change signaling javítva
- Robust error handling implementálva
"""

# Public API export
from .core import HungarianLocationSelector
from .models import HungarianRegionData, HungarianStatisticalRegion
from .worker import GEOPANDAS_AVAILABLE, HungarianLocationWorker

# Re-export for backward compatibility
__all__ = [
    "HungarianLocationSelector",
    "HungarianStatisticalRegion",
    "HungarianRegionData",
    "HungarianLocationWorker",
    "GEOPANDAS_AVAILABLE",
]
