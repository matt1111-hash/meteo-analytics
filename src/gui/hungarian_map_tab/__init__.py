#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hungarian Map Tab Package.

Provides the HungarianMapTab widget for displaying Hungarian weather maps.
Refactored from single file to package structure for better maintainability.

Usage:
    from src.gui.hungarian_map_tab import HungarianMapTab
"""

from ._map_tab import HungarianMapTab
from .map_analytics_sync import MapAnalyticsSyncMixin

__all__ = ["HungarianMapTab", "MapAnalyticsSyncMixin"]
