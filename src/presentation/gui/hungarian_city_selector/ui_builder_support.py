# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hungarian City Selector - UI Builder Module
UI komponensek létrehozása a HungarianCitySelector widgethez.
"""

import logging
from collections.abc import Callable
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from src.presentation.gui.hungarian_city_selector.types import (
    HungarianCity,
    HungarianRegions,
)

logger = logging.getLogger(__name__)
