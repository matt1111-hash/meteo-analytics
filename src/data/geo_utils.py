#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Geographic Utilities Module (Legacy Export)
🌍 Multi-City Analytics: Földrajzi számítások és koordináta műveletek

This file now re-exports from the refactored modules for backward compatibility.

NEW STRUCTURE:
- geo_types.py - Enums and dataclasses (GeoPoint, BoundingBox, etc.)
- distance_calculator.py - DistanceCalculator class (Haversine, Vincenty)
- geo_utils_core.py - GeoUtils core class (basic operations)
- geo_utils_region.py - GeoUtilsRegion class (region operations)
- geo_utils_analytics.py - GeoUtilsAnalytics class (analytics operations)
- geo_demo.py - Demo functions

HASZNÁLAT (Legacy - működik tovább):
from src.data.geo_utils import GeoUtils, DistanceCalculator, GeoPoint

Javasolt új használat:
from src.data.geo_utils_core import GeoUtils
from src.data.geo_utils_region import GeoUtilsRegion
from src.data.geo_utils_analytics import GeoUtilsAnalytics
from src.data.distance_calculator import DistanceCalculator
from src.data.geo_types import GeoPoint
"""

# Re-export all types
# Re-export calculator
from .distance_calculator import DistanceCalculator

# Re-export demo function
from .geo_demo import demo_geo_utils
from .geo_types import (
    BoundingBox,
    CoordinateSystem,
    DistanceUnit,
    GeographicRegion,
    GeoPoint,
)
from .geo_utils_analytics import GeoUtilsAnalytics

# Re-export GeoUtils classes
from .geo_utils_core import GeoUtils
from .geo_utils_region import GeoUtilsRegion

__all__ = [
    # Types
    "DistanceUnit",
    "CoordinateSystem",
    "GeoPoint",
    "BoundingBox",
    "GeographicRegion",
    # Calculator
    "DistanceCalculator",
    # GeoUtils classes
    "GeoUtils",
    "GeoUtilsRegion",
    "GeoUtilsAnalytics",
    # Demo
    "demo_geo_utils",
]
