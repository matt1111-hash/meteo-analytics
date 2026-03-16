"""Tests for GeoUtilsRegion from geo_utils_region.py."""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

from src.data.distance_calculator import DistanceCalculator
from src.data.geo_types import BoundingBox, GeoPoint, GeographicRegion
from src.data.geo_utils_core import GeoUtils
from src.data.geo_utils_region import GeoUtilsRegion


@pytest.fixture
def geo_utils() -> GeoUtilsRegion:
    """Create GeoUtilsRegion instance."""
    return GeoUtilsRegion()


@pytest.fixture
def sample_cities() -> List[Dict[str, Any]]:
    """Sample city data for testing."""
    return [
        {"city": "Budapest", "lat": 47.4979, "lon": 19.0402, "population": 1752286},
        {"city": "Debrecen", "lat": 47.5314, "lon": 21.6269, "population": 201881},
        {"city": "Szeged", "lat": 46.2530, "lon": 20.1414, "population": 161837},
        {"city": "Miskolc", "lat": 48.1035, "lon": 20.7784, "population": 157177},
    ]
