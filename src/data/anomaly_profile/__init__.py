#!/usr/bin/env python3
"""
Global Weather Analyzer - Anomaly Profile Package
Anomália profilok menedzsmentje.
"""

from .default_profiles import create_default_profiles, create_profiles_data
from .manager import AnomalyProfileManager

__all__ = ["AnomalyProfileManager", "create_default_profiles", "create_profiles_data"]
