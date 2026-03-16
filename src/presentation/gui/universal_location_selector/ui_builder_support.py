# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Location Selector - UI Builder

🎨 UI elemek létrehozása és stílusok

Képességek:
- Search group setup
- Results group setup
- Selection group setup
- CSS stílusok alkalmazása

Fájl: src/presentation/gui/universal_location_selector/ui_builder.py
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .location_card import LocationCard
