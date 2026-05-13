#!/usr/bin/env python3

"""
City Manager - Multi-Source Database Integration (Legacy Export)
Global Weather Analyzer project

BACKWARD COMPATIBILITY SHIM — Re-exports from src.infrastructure.city_manager.*

NEW STRUCTURE (moved to infrastructure):
- city_types.py - RegionType, CitySort, City, CityQuery, CityDatabaseError
- city_manager_db.py - Database connection and initialization
- city_manager_hungarian.py - Hungarian-specific search methods
- city_manager_search.py - Global and unified search methods
- city_manager_stats.py - Statistics, legacy methods, context manager
- city_manager_demo.py - Demo/test code

HASZNÁLAT (Legacy - működik tovább):
from src.data.city_manager import CityManager, City, CityDatabaseError

Javasolt új használat:
from src.infrastructure.city_manager.city_manager_stats import CityManagerStats
from src.infrastructure.city_manager.city_types import City, CityDatabaseError
"""

# Re-export types from infrastructure
from src.infrastructure.city_manager.city_manager_db import CityManagerDB
from src.infrastructure.city_manager.city_manager_demo import demo_dual_database_city_manager
from src.infrastructure.city_manager.city_manager_hungarian import CityManagerHungarian
from src.infrastructure.city_manager.city_manager_search import CityManagerSearch
from src.infrastructure.city_manager.city_manager_stats import CityManagerStats

# Re-export main class (with all functionality)
from src.infrastructure.city_manager.city_manager_stats import CityManagerStats as CityManager
from src.infrastructure.city_manager.city_types import (
    City,
    CityDatabaseError,
    CityQuery,
    CitySort,
    RegionType,
)

__all__ = [
    "City",
    "CityDatabaseError",
    # Main client (with all functionality)
    "CityManager",
    # Individual classes for partial usage
    "CityManagerDB",
    "CityManagerHungarian",
    "CityManagerSearch",
    "CityManagerStats",
    "CityQuery",
    "CitySort",
    # Types
    "RegionType",
    # Demo function
    "demo_dual_database_city_manager",
]
