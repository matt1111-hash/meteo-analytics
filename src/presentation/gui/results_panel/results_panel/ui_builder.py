#!/usr/bin/env python3
# mypy: ignore-errors

"""
Results Panel - UI Builder

🎨 UI elemek létrehozása results panelhez

Képességek:
- Main layout setup
- Title és progress indicator
- Export és extreme weather gombok
- Tab widget inicializáció

Fájl: src/presentation/gui/results_panel/results_panel/ui_builder.py
"""

import logging
from typing import TYPE_CHECKING

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def init_ui(self) -> None:
    """
    UI elemek inicializálása.

    Args:
        self: ResultsPanel instance
    """
    logger.debug("ResultsPanel._init_ui() START")

    from PySide6.QtWidgets import QVBoxLayout  # noqa: PLC0415

    layout = QVBoxLayout(self)
    layout.setContentsMargins(5, 5, 5, 5)
    layout.setSpacing(5)

    # === FŐCÍM + PROGRESS INDICATOR ===
    title_layout = create_title_layout(self)
    layout.addLayout(title_layout)

    # === TAB WIDGET LÉTREHOZÁSA ===
    self.tab_widget = self.tab_manager.initialize()
    layout.addWidget(self.tab_widget)

    # Progress manager inicializálása
    self.progress_manager.initialize(self.progress_indicator)

    logger.debug("ResultsPanel._init_ui() BEFEJEZVE")


def create_title_layout(self) -> QHBoxLayout:
    """
    Title layout létrehozása.

    Args:
        self: ResultsPanel instance

    Returns:
        QHBoxLayout: Title layout
    """
    from .signal_handlers import _on_extreme_weather_clicked  # noqa: PLC0415

    title_layout = QHBoxLayout()

    # Title label
    self.title_label = QLabel("📊 Időjárási Adatok Elemzése")
    title_font = QFont()
    title_font.setBold(True)
    title_font.setPointSize(14)
    self.title_label.setFont(title_font)
    title_layout.addWidget(self.title_label)

    # Progress indicator
    self.progress_indicator = QLabel("")
    self.progress_indicator.setStyleSheet("""
        QLabel {
            color: #2563eb;
            font-size: 12px;
            font-style: italic;
            padding: 5px 10px;
        }
    """)
    self.progress_indicator.setVisible(False)
    title_layout.addWidget(self.progress_indicator)

    title_layout.addStretch()

    # Export gomb
    self.global_export_btn = QPushButton("💾 Export")
    self.global_export_btn.clicked.connect(lambda: self.export_requested.emit("csv"))
    title_layout.addWidget(self.global_export_btn)

    # Extreme weather gomb
    self.extreme_weather_btn = QPushButton("⚡ Extrém Időjárás")
    self.extreme_weather_btn.clicked.connect(_on_extreme_weather_clicked)
    title_layout.addWidget(self.extreme_weather_btn)

    return title_layout
