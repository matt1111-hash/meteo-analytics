#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Analytics Widgets Module.
Rekord kártya widgetek az analytics view számára.

🏆 REKORD KÁRTYÁK:
✅ RecordCard - kompakt rekord kártya
✅ RecordSummaryCard - 5 rekord kategória summary
"""

import logging
from typing import Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)


class RecordCard(QWidget):
    """🏆 Kompakt rekord kártya widget - TAB LAYOUT-hoz optimalizált"""

    def __init__(self, icon: str, title: str, value: str = "-", date: str = "-"):
        super().__init__()
        self.icon = icon
        self.title = title
        self._setup_ui()
        self.update_record(value, date)

    def _setup_ui(self):
        """Kompakt rekord kártya UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        # Icon + title
        header_layout = QHBoxLayout()

        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet("font-size: 14px;")
        header_layout.addWidget(icon_label)

        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-size: 9px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Value
        self.value_label = QLabel("-")
        self.value_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #C43939;")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)

        # Date
        self.date_label = QLabel("-")
        self.date_label.setStyleSheet("font-size: 7px; color: gray;")
        self.date_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.date_label)

        # Kompakt styling
        self.setStyleSheet("""
            RecordCard {
                background-color: #f9fafb;
                border: 1px solid #d1d5db;
                border-radius: 3px;
                max-height: 65px;
                max-width: 200px;
            }
        """)

    def update_record(self, value: str, date: str):
        """Rekord értékek frissítése"""
        self.value_label.setText(value)
        self.date_label.setText(date)


class RecordSummaryCard(QWidget):
    """🏆 5 rekord kategória - EXTRA KOMPAKT TAB LAYOUT-hoz"""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Extra kompakt summary kártya"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)

        # Cím
        title_label = QLabel("🏆 REKORD SZÉLSŐSÉGEK")
        title_font = QLabel().font()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 5 rekord kártya - EXTRA KOMPAKT
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(3)

        self.hottest_card = RecordCard("🔥", "Legmelegebb")
        self.coldest_card = RecordCard("🧊", "Leghidegebb")
        self.wettest_card = RecordCard("🌧️", "Legcsapadék")
        self.driest_card = RecordCard("🏜️", "Legszáraz")
        self.windiest_card = RecordCard("💨", "Legszelesebb")

        cards_layout.addWidget(self.hottest_card)
        cards_layout.addWidget(self.coldest_card)
        cards_layout.addWidget(self.wettest_card)
        cards_layout.addWidget(self.driest_card)
        cards_layout.addWidget(self.windiest_card)

        layout.addLayout(cards_layout)

        # Extra kompakt styling
        self.setStyleSheet("""
            RecordSummaryCard {
                background-color: white;
                border: 2px solid #C43939;
                border-radius: 4px;
                margin: 2px;
                max-height: 90px;
            }
        """)

    def update_records(self, records: Dict[str, Dict[str, str]]):
        """Rekordok frissítése"""
        if 'hottest' in records:
            rec = records['hottest']
            self.hottest_card.update_record(rec.get('value', '-'), rec.get('date', '-'))

        if 'coldest' in records:
            rec = records['coldest']
            self.coldest_card.update_record(rec.get('value', '-'), rec.get('date', '-'))

        if 'wettest' in records:
            rec = records['wettest']
            self.wettest_card.update_record(rec.get('value', '-'), rec.get('date', '-'))

        if 'driest' in records:
            rec = records['driest']
            self.driest_card.update_record(rec.get('value', '-'), rec.get('date', '-'))

        if 'windiest' in records:
            rec = records['windiest']
            self.windiest_card.update_record(rec.get('value', '-'), rec.get('date', '-'))


__all__ = [
    "RecordCard",
    "RecordSummaryCard",
]
