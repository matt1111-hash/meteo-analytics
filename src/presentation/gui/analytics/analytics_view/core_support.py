# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analytics View - Core Module
Fő AnalyticsView widget osztály.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from src.domain.entities.analytics_models import AnalyticsResult

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ...theme_manager import (
    get_current_colors,
    get_theme_manager,
    register_widget_for_theming,
)
from .multi_city_handler import AnalyticsViewMultiCityHandler
from .statistics_cards import AnalyticsViewStatisticsCards
from .ui_builder import AnalyticsViewUIBuilder

logger = logging.getLogger(__name__)
