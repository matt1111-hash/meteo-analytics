#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analytics View Module - Refaktorált
Multi-city régió elemzések dashboard konstans heatmap-ekkel.

✅ REFAKTORÁLT MŰKÖDÉS:
- A nézet most már nem indít saját lekérdezéseket.
- A gombok egy központi `multi_city_query_requested` signalt bocsátanak ki.
- A MainWindow kezeli a lekérdezést és az eredményt egy publikus slot-on
  (`update_with_multi_city_result`) keresztül küldi vissza.
"""

# Re-export core
from src.presentation.gui.analytics.analytics_view.core import AnalyticsView

# Re-export color maps
from src.presentation.gui.analytics.analytics_helpers import MeteorologicalColorMaps

__all__ = [
    'AnalyticsView',
    'MeteorologicalColorMaps'
]
