# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Analysis Type Widget
Elemzési típus választó widget (Egyedi/Régió/Megye)

🎯 CLEAN ARCHITECTURE REFAKTOR - 1. LÉPÉS
Felelősség: CSAK az elemzési típus választás kezelése
- Single Responsibility: Csak analysis type selection
- Clean Interface: get_state(), set_state(), analysis_type_changed signal
- No Business Logic: Csak UI state management
"""

from typing import Any, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QGroupBox,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)
from src.presentation.gui.theme_manager import (
    get_theme_manager,
    register_widget_for_theming,
)
