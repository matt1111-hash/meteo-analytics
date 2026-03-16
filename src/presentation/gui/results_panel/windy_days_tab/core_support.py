# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windy Days Tab - Core

Szeles napok analízis tab komponens.

Fájl: src/presentation/gui/results_panel/windy_days_tab/core.py
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, Optional

import pandas as pd
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QVBoxLayout, QWidget

from src.domain.analytics.wind_models import WINDY_DAY_THRESHOLD_KMH
from src.presentation.gui.charts.windy_days_chart import WindyDaysChart
from src.presentation.gui.theme_manager import (
    ProfessionalThemeManager,
    register_widget_for_theming,
)

from .data_processor import (
    clear_data,
    get_current_threshold,
    set_threshold,
    update_data,
)
from .handlers import (
    handle_analyze_clicked,
    handle_auto_update_toggled,
    handle_export_clicked,
    handle_threshold_changed,
)
from .ui_builder import (
    create_chart_section,
    create_content_splitter,
    create_controls_section,
    create_footer_section,
    create_header_section,
    create_progress_section,
    create_summary_section,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import (
        QFrame,
        QGroupBox,
        QProgressBar,
        QPushButton,
        QSpinBox,
        QTextEdit,
    )

logger = logging.getLogger(__name__)
