#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Heatmap Chart Module

Global Weather Analyzer - Heatmap Calendar Chart
🎯 CLEAN HEATMAP - TOOLTIP NÉLKÜL

📋 FUNKCIÓK:
✅ Calendar heatmap renderelés
✅ Valódi hónap címkék
✅ 365 konstans felbontás
✅ Meteorológiai színskálák

Modul szerkezet:
- core.py: HeatmapCalendarChart main class (223 sor)
- data_extractor.py: Data extraction és aggregáció (87 sor)
- calendar_builder.py: Kalendár mátrix építés (44 sor)
- colormap_handler.py: Colormap kezelése (59 sor)
- axes_formatter.py: Tengelyek formázása (102 sor)
- colorbar_handler.py: Colorbar létrehozása (40 sor)
- categories.py: Kategorizálás (94 sor)

Fájl: src/presentation/gui/charts/heatmap_chart/__init__.py
"""

from .core import HeatmapCalendarChart

__all__ = ["HeatmapCalendarChart"]
