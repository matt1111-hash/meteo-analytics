#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analytics to Map Sync Mixin.

Provides methods for synchronizing analytics parameters with the map display.
Extracted from HungarianMapTab to reduce file size and improve maintainability.

Usage:
    class HungarianMapTab(MapAnalyticsSyncMixin, QWidget):
        ...
"""

from .analytics_sync_core import AnalyticsSyncCore
from .analytics_sync_helpers import AnalyticsSyncHelpers


class MapAnalyticsSyncMixin(AnalyticsSyncCore, AnalyticsSyncHelpers):
    """
    Mixin providing analytics-to-map synchronization methods.

    Combines core sync functionality with helper methods.
    """
    pass


__all__ = ["MapAnalyticsSyncMixin"]
