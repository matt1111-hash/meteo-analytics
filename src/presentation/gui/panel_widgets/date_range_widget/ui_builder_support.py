# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date Range Widget - UI Builder

🎨 UI elemek létrehozása dátum tartomány választóhoz

Képességek:
- Time range group létrehozása
- Manual dates group létrehozása
- Theme manager regisztráció

Fájl: src/presentation/gui/panel_widgets/date_range_widget/ui_builder.py
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.presentation.gui.theme_manager import ThemeManager
