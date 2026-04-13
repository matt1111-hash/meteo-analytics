# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Analytics Tabs Module.
Heatmap tab widgetek az analytics view számára.

🌡️ KONSTANS HEATMAP TAB WIDGET-EK:
✅ TemperatureTabWidget - hőmérséklet heatmap
✅ PrecipitationTabWidget - csapadék heatmap (meteorológiai színek)
✅ WindTabWidget - szél heatmap (BEAUFORT 13 fokozat)
✅ WindGustTabWidget - max széllökés heatmap (BEAUFORT 13 fokozat)
✅ ClimateTabWidget - fő tab widget összesítése
"""

import logging
from typing import Any

from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

# Chart imports
from ..charts.heatmap_chart import HeatmapCalendarChart
from ..charts.wind_chart import WindChart
from ..charts.wind_rose_chart import WindRoseChart
from .analytics_helpers import MeteorologicalColorMaps

logger = logging.getLogger(__name__)
