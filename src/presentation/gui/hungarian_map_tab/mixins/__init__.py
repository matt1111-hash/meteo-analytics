"""
Mixins for HungarianMapTab.

Ez a modul tartalmazza a HungarianMapTab mixin osztályait.
"""

from .map_tab_ui import MapTabUIMixin
from .map_analytics_sync import MapAnalyticsSyncMixin

__all__ = ["MapTabUIMixin", "MapAnalyticsSyncMixin"]
