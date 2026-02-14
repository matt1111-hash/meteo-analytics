#!/usr/bin/env python3
"""
Multi-City Analytics Engine - Globális időjárás elemzés
Global Weather Analyzer projekt

Fájl: src/analytics/multi_city_engine.py
Cél: Többváros időjárási elemzés koordinálása
- DUAL-API TÁMOGATÁS (Open-Meteo + Meteostat)
- Országválasztás (Magyarország, Európa, Globális)
- BATCH PROCESSING - robusztus párhuzamos feldolgozás
- PROGRESS TRACKING - real-time feedback
- FALLBACK STRATEGY - hibás városok kihagyása

This module re-exports all components from focused sub-modules.
For backward compatibility, all original symbols remain available.
"""

# ============================================================================
# TYPES AND CONSTANTS
# ============================================================================
# ============================================================================
# DEMO
# ============================================================================
from .multi_city_demo import demo_multi_city_engine

# ============================================================================
# CORE ENGINE
# ============================================================================
from .multi_city_engine_core import MultiCityEngine

# ============================================================================
# LEGACY WRAPPERS
# ============================================================================
from .multi_city_legacy import (
    safe_mean,
    safe_median,
    safe_min_max,
    safe_statistics_mean,
    safe_statistics_median,
    safe_statistics_stdev,
    safe_stdev,
)
from .multi_city_types import HUNGARIAN_REGIONAL_MAPPING, REGIONS, Number, NumberOrNone

__all__ = [
    # Types
    "Number",
    "NumberOrNone",
    "HUNGARIAN_REGIONAL_MAPPING",
    "REGIONS",
    # Legacy
    "safe_mean",
    "safe_statistics_mean",
    "safe_median",
    "safe_statistics_median",
    "safe_stdev",
    "safe_statistics_stdev",
    "safe_min_max",
    # Core
    "MultiCityEngine",
    # Demo
    "demo_multi_city_engine",
]


# 🔧 BACKWARD-COMPATIBILITY: Export QUERY_TYPES from engine class
MultiCityEngine.QUERY_TYPES
