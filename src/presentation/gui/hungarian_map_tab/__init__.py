#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hungarian Map Tab Package.

Provides the HungarianMapTab widget for displaying Hungarian weather maps.
Refactored from single file to package structure for better maintainability.

Usage:
    from src.presentation.gui.hungarian_map_tab import HungarianMapTab
"""

from ._map_tab import HungarianMapTab
from .map_analytics_sync import MapAnalyticsSyncMixin
from .map_tab_ui import MapTabUIMixin

__all__ = ["HungarianMapTab", "MapAnalyticsSyncMixin", "MapTabUIMixin"]
