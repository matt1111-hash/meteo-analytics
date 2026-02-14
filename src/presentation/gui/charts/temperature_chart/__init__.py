#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Temperature Chart Module

Global Weather Analyzer - Enhanced Temperature Chart
Fejlett hőmérséklet grafikon widget professzionális vizualizációval.

🌡️ ENHANCED TEMPERATURE CHART: Színes zónák, trend vonalak, statisztikai elemek
🎨 TÉMA INTEGRÁCIÓ: ColorPalette használata professzionális színekhez
🔧 KRITIKUS JAVÍTÁS: Robusztus update cycle duplikáció nélkül + LEGEND POZÍCIÓ JAVÍTVA
🎯 TOOLTIP INTEGRÁCIÓ: WeatherTooltipMixin - SZUPER KONZERVATÍV MEGKÖZELÍTÉS!
✅ Piros (#C43939) téma támogatás
✅ Professzionális nagy méretű diagramok
✅ Optimális legend elhelyezés
✅ Valódi API adatok használata (mock adatok tiltva)
✅ INTERAKTÍV TOOLTIP FUNKCIÓK: Hover + Click eventi
✅ SMART TOOLTIP POSITIONING: Dynamic placement, nem lóg ki

Modul szerkezet:
- core.py: EnhancedTemperatureChart main class (93 sor)
- data_extractor.py: TemperatureDataExtractor (60 sor)
- plotting.py: TemperaturePlottingMixin (143 sor)
- formatting.py: TemperatureFormattingMixin (72 sor)
- tooltip_handler.py: TemperatureTooltipHandlerMixin (220 sor)

Fájl: src/presentation/gui/charts/temperature_chart/__init__.py
"""

from .core import EnhancedTemperatureChart

__all__ = ["EnhancedTemperatureChart"]
