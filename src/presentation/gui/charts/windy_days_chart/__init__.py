#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windy Days Chart

Szeles napok oszlopdiagram chart komponens.

Képességek:
- Havi szeles napok ábrázolása
- Színkódolás és interaktív elemek
- Export és info lekérdezés

Fájl: src/presentation/gui/charts/windy_days_chart/__init__.py
"""

from .core import WindyDaysChart
from .factory import create_windy_days_chart, demo_windy_days_chart

__all__ = [
    'WindyDaysChart',
    'create_windy_days_chart',
    'demo_windy_days_chart',
]
