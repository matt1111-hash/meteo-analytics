"""
Mixins for HungarianMapTab.

Ez a modul tartalmazza a HungarianMapTab mixin osztályait.
"""

from .map_analytics_sync import MapAnalyticsSyncMixin
from .map_tab_ui import MapTabUIMixin

__all__ = ["MapTabUIMixin", "MapAnalyticsSyncMixin"]
