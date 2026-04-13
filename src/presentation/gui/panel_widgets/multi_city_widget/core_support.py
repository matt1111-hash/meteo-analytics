# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Multi-City Widget - Core

🏙️ Multi-City választó widget fő osztálya

Képességek:
- Magyar régiók/megyék dropdown választás
- Analysis type alapú mode váltás (region vs county)
- Selection state management
- Signal kibocsátás selection változáskor

Fájl: src/presentation/gui/panel_widgets/multi_city_widget/core.py
"""

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget
from src.domain.ports import CityManagerPort
from src.presentation.gui.theme_manager import get_theme_manager

from .combo_handler import ComboHandler
from .public_api import MultiCityWidgetPublicAPI
from .regional_data import get_hungarian_regions
from .ui_builder import (
    apply_label_styling,
    create_multi_city_ui,
    register_widget_for_theming,
)
