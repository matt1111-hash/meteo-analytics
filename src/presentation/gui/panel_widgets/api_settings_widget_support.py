# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - API Settings Widget
API beállítások widget (Timeout, Cache, Timezone)

🎯 CLEAN ARCHITECTURE REFAKTOR - 5. LÉPÉS
Felelősség: CSAK az API beállítások kezelése
- Single Responsibility: API configuration settings
- Clean Interface: get_state(), set_state(), api_settings_changed signal
- Multi-Year optimalizált beállítások
"""

from typing import Any, Dict, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.presentation.gui.theme_manager import (
    get_theme_manager,
    register_widget_for_theming,
)
