# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Heatmap Chart - Core

🎯 HeatmapCalendarChart main class

Képességek:
- Main class
- Update és plotting
- Placeholder rendering

Fájl: src/presentation/gui/charts/heatmap_chart/core.py
"""

import logging
from typing import Any, Optional

import numpy as np
import pandas as pd
from PySide6.QtWidgets import QWidget
from src.presentation.gui.theme_manager import get_current_colors

from ..base_chart import WeatherChart
from .axes_formatter import format_period_text, setup_axes_and_labels
from .calendar_builder import build_calendar_matrix
from .colorbar_handler import create_colorbar
from .colormap_handler import get_colormap_and_norm
from .data_extractor import aggregate_to_365, extract_daily_data

logger = logging.getLogger(__name__)
