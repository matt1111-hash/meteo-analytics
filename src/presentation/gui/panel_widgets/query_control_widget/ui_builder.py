# mypy: ignore-errors
"""
UI builder for QueryControlWidget.

Ez a modul felelős a QueryControlWidget UI elemek felépítéséért.
Csak vezérlőgombokat és progressz kijelzést tartalmaz.
"""

import logging
from typing import Optional

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class QueryControlUIBuilder:
    """
    QueryControlWidget UI builder.

    Felépíti a widget elrendezését és létrehozza az összes UI elemet.
    """

    def __init__(self, parent_widget: QWidget):
        """
        UI builder inicializálása.

        Args:
            parent_widget: Szülő widget
        """
        self._parent = parent_widget
        self._layout: Optional[QVBoxLayout] = None

        # Widget references
        self.query_button: Optional[QPushButton] = None
        self.cancel_button: Optional[QPushButton] = None
        self.progress_bar: Optional[QProgressBar] = None
        self.status_label: Optional[QLabel] = None
        self.progress_text_label: Optional[QLabel] = None

    def build_ui(self) -> QVBoxLayout:
        """
        UI felépítése.

        Returns:
            QVBoxLayout: A fő layout
        """
        logger.debug("QueryControlUIBuilder.build_ui() START")

        # Main layout
        layout = QVBoxLayout(self._parent)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Title
        layout.addWidget(self._create_title_label())

        # Progress section
        layout.addWidget(self._create_progress_frame())

        # Control buttons
        layout.addLayout(self._create_buttons_layout())

        # Stretch
        layout.addStretch()

        self._layout = layout
        logger.debug("QueryControlUIBuilder.build_ui() BEFEJEZVE")
        return layout

    def _create_title_label(self) -> QLabel:
        """Címke létrehozása."""
        title_label = QLabel("📍 Lekérdezés Beállítások")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        return title_label

    def _create_progress_frame(self) -> QFrame:
        """Progress keret létrehozása."""
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.StyledPanel)
        progress_layout = QVBoxLayout(progress_frame)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        progress_layout.addWidget(self.progress_bar)

        # Status and progress text
        status_layout = QHBoxLayout()

        self.status_label = QLabel("✅ Kész a lekérdezésre")
        self.status_label.setStyleSheet("color: #16a34a; font-weight: bold;")
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        self.progress_text_label = QLabel("")
        self.progress_text_label.setVisible(False)
        self.progress_text_label.setStyleSheet("color: #2563eb; font-style: italic;")
        status_layout.addWidget(self.progress_text_label)

        progress_layout.addLayout(status_layout)
        return progress_frame

    def _create_buttons_layout(self) -> QHBoxLayout:
        """Gombok elrendezés létrehozása."""
        buttons_layout = QHBoxLayout()

        # Cancel button
        self.cancel_button = QPushButton("🚫 Megszakítás")
        self.cancel_button.setVisible(False)
        self.cancel_button.setStyleSheet(self._get_cancel_button_style())
        buttons_layout.addWidget(self.cancel_button)

        buttons_layout.addStretch()

        # Query button
        self.query_button = QPushButton("🚀 Lekérdezés Indítása")
        self.query_button.setStyleSheet(self._get_query_button_style())
        buttons_layout.addWidget(self.query_button)

        return buttons_layout

    def _get_cancel_button_style(self) -> str:
        """Cancel button stílus."""
        return """
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
            QPushButton:pressed {
                background-color: #991b1b;
            }
        """

    def _get_query_button_style(self) -> str:
        """Query button stílus."""
        return """
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #6b7280;
            }
        """
