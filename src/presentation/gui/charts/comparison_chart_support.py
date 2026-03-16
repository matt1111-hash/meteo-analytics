# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Multi-Year Comparison Chart
Több év összehasonlító chart widget trend elemzéssel.

📊 MULTI-YEAR COMPARISON CHART: Azonos időszakok összehasonlítása különböző évekből
🎨 TÉMA INTEGRÁCIÓ: ColorPalette trend elemzési színek használata
🔧 KRITIKUS JAVÍTÁS: Duplikáció-mentes frissítés + SIMPLIFIED THEMEMANAGER
✅ Piros (#C43939) téma támogatás
✅ Trend vonalak minden évhez
✅ Szezonális vonalak (tavasz, nyár, ősz, tél)
✅ Statisztikai információk
✅ Optimális legend pozícionálás
"""

from typing import Any, Dict, Optional

import pandas as pd
from PySide6.QtWidgets import QWidget

from src.presentation.gui.theme_manager import get_current_colors

from .base_chart import WeatherChart
