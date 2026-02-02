#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Location Widget - UI initialization.
"""

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from src.presentation.gui.theme_manager import register_widget_for_theming
from ...universal_location_selector import UniversalLocationSelector

if TYPE_CHECKING:
    from .core import LocationWidget


class UIInitializer:
    """UI inicializáló a LocationWidget számára."""

    def __init__(self, widget: 'LocationWidget'):
        """
        UIInitializer inicializálása.

        Args:
            widget: LocationWidget instance
        """
        self.widget = widget
        self.group: QGroupBox = None
        self.info_label: QLabel = None
        self.clear_btn: QPushButton = None
        self.location_selector: UniversalLocationSelector = None

    def build(self) -> None:
        """UI elemek létrehozása."""
        # Main layout
        layout = QVBoxLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Group box
        self.group = QGroupBox("🌍 Lokáció Választó")
        group_layout = QVBoxLayout(self.group)
        group_layout.setContentsMargins(12, 16, 12, 12)
        group_layout.setSpacing(12)

        # UniversalLocationSelector
        self.location_selector = UniversalLocationSelector(self.widget.city_manager, self.widget)
        self.location_selector.setMinimumHeight(420)
        self.location_selector.setMaximumHeight(500)
        group_layout.addWidget(self.location_selector)

        # Location info és clear gomb
        info_layout = QHBoxLayout()
        info_layout.setSpacing(8)

        # Info label
        self.info_label = QLabel("Válasszon lokációt...")
        self.info_label.setWordWrap(True)
        self.info_label.setMinimumHeight(40)
        info_layout.addWidget(self.info_label)

        # Clear button
        self.clear_btn = QPushButton("🗑️")
        self.clear_btn.clicked.connect(self.widget.signals._clear_location)
        self.clear_btn.setEnabled(False)
        self.clear_btn.setFixedSize(32, 32)
        self.clear_btn.setToolTip("Lokáció törlése")
        info_layout.addWidget(self.clear_btn)

        group_layout.addLayout(info_layout)

        # Size constraints
        self.group.setMinimumHeight(500)
        self.group.setMaximumHeight(580)

        layout.addWidget(self.group)
