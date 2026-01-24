#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
City Manager - Multi-Source Database Integration (Legacy Export)
Global Weather Analyzer project

This file now re-exports from the refactored modules for backward compatibility.

NEW STRUCTURE:
- city_types.py - RegionType, CitySort, City, CityQuery, CityDatabaseError
- city_manager_db.py - Database connection and initialization
- city_manager_hungarian.py - Hungarian-specific search methods
- city_manager_search.py - Global and unified search methods
- city_manager_stats.py - Statistics, legacy methods, context manager
- city_manager_demo.py - Demo/test code

HASZNÁLAT (Legacy - működik tovább):
from src.data.city_manager import CityManager, City, CityDatabaseError

Javasolt új használat:
from src.data.city_manager_stats import CityManagerStats as CityManager
from src.data.city_types import City, CityDatabaseError
"""

# Re-export types
from src.data.city_types import (
    RegionType,
    CitySort,
    City,
    CityQuery,
    CityDatabaseError
)

# Re-export main class (with all functionality)
from src.data.city_manager_stats import CityManagerStats as CityManager

# Re-export demo function
from src.data.city_manager_demo import demo_dual_database_city_manager

# Also export individual classes for those who want partial functionality
from src.data.city_manager_db import CityManagerDB
from src.data.city_manager_hungarian import CityManagerHungarian
from src.data.city_manager_search import CityManagerSearch
from src.data.city_manager_stats import CityManagerStats

__all__ = [
    # Types
    'RegionType',
    'CitySort',
    'City',
    'CityQuery',
    'CityDatabaseError',

    # Main client (with all functionality)
    'CityManager',

    # Individual classes for partial usage
    'CityManagerDB',
    'CityManagerHungarian',
    'CityManagerSearch',
    'CityManagerStats',

    # Demo function
    'demo_dual_database_city_manager'
]
