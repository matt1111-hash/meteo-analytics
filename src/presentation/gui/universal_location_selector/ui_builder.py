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


def create_universal_location_selector_ui(parent_widget: QWidget) -> dict:
    """
    UI elemek létrehozása universal location selectorhoz.

    Args:
        parent_widget: Szülő widget

    Returns:
        Dict with all UI elements
    """
    # Main layout
    layout = QVBoxLayout(parent_widget)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(16)

    # === HEADER ===
    header_label = QLabel("🇭🇺 Magyar + Globális Lokáció Keresés")
    header_font = QFont()
    header_font.setBold(True)
    header_font.setPointSize(16)
    header_label.setFont(header_font)
    header_label.setStyleSheet("color: #1E293B; margin-bottom: 8px;")
    layout.addWidget(header_label)

    # === SEARCH GROUP ===
    search_group, search_input, status_label = _create_search_group()
    layout.addWidget(search_group)

    # === RESULTS GROUP ===
    results_group, results_list = _create_results_group()
    layout.addWidget(results_group)

    # === SELECTION GROUP ===
    selection_group, location_card, confirm_button = _create_selection_group()
    layout.addWidget(selection_group)

    # Stretch
    layout.addStretch()

    # KOMPAKT SIZING
    parent_widget.setMinimumSize(300, 450)
    parent_widget.setMaximumHeight(550)
    parent_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    return {
        "search_input": search_input,
        "status_label": status_label,
        "results_list": results_list,
        "location_card": location_card,
        "confirm_button": confirm_button,
    }


def _create_search_group() -> tuple:
    """Search group létrehozása."""
    search_group = QGroupBox("🔍 Kombinált Keresés")
    search_group.setStyleSheet(_get_group_box_style())
    search_layout = QVBoxLayout(search_group)
    search_layout.setContentsMargins(12, 16, 12, 12)
    search_layout.setSpacing(12)

    # Modern search input
    search_input = QLineEdit()
    search_input.setPlaceholderText(
        "🇭🇺 Magyar települések + 🌍 44k globális város... (pl. Kiskunhalas, Abaliget, London)"
    )
    search_input.setMinimumHeight(40)
    search_input.setMaximumHeight(44)
    search_input.setStyleSheet(_get_search_input_style())
    search_layout.addWidget(search_input)

    # Status label
    status_label = QLabel("💡 Kezdj el gépelni a kereséshez...")
    status_label.setStyleSheet(_get_status_label_style())
    search_layout.addWidget(status_label)

    return search_group, search_input, status_label


def _create_results_group() -> tuple:
    """Results group létrehozása."""
    results_group = QGroupBox("📋 Keresési Eredmények")
    results_group.setStyleSheet(_get_group_box_style())
    results_layout = QVBoxLayout(results_group)
    results_layout.setContentsMargins(12, 16, 12, 12)

    # Results list
    results_list = QListWidget()
    results_list.setMinimumHeight(200)
    results_list.setMaximumHeight(250)
    results_list.setStyleSheet(_get_results_list_style())
    results_layout.addWidget(results_list)

    return results_group, results_list


def _create_selection_group() -> tuple:
    """Selection group létrehozása."""
    selection_group = QGroupBox("🎯 Kiválasztott Lokáció")
    selection_group.setStyleSheet(_get_group_box_style())
    selection_layout = QVBoxLayout(selection_group)
    selection_layout.setContentsMargins(12, 16, 12, 12)

    # Location card
    location_card = LocationCard()
    selection_layout.addWidget(location_card)

    # Confirm button
    confirm_button = QPushButton("✅ Lokáció Megerősítése")
    confirm_button.setMinimumHeight(40)
    confirm_button.setMaximumHeight(44)
    confirm_button.setEnabled(False)
    confirm_button.setStyleSheet(_get_confirm_button_style())
    selection_layout.addWidget(confirm_button)

    return selection_group, location_card, confirm_button


# === STYLES ===


def _get_group_box_style() -> str:
    """Group box stílus."""
    return """
        QGroupBox {
            font-weight: bold;
            font-size: 14px;
            color: #1E293B;
            border: 2px solid #E2E8F0;
            border-radius: 8px;
            margin-top: 8px;
            padding-top: 8px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px 0 8px;
            background: #FFFFFF;
        }
    """


def _get_search_input_style() -> str:
    """Search input stílus."""
    return """
        QLineEdit {
            background: #FFFFFF;
            border: 2px solid #E2E8F0;
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
            color: #1E293B;
        }
        QLineEdit:hover {
            border: 2px solid #CBD5E1;
        }
        QLineEdit:focus {
            border: 2px solid #3B82F6;
            background: #FFFFFF;
        }
        QLineEdit::placeholder {
            color: #94A3B8;
        }
    """


def _get_status_label_style() -> str:
    """Status label stílus."""
    return """
        color: #64748B;
        font-style: italic;
        background: #F8FAFC;
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid #E2E8F0;
        font-size: 12px;
    """


def _get_results_list_style() -> str:
    """Results list stílus."""
    return """
        QListWidget {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 8px;
        }
        QListWidget::item {
            background: #FFFFFF;
            color: #1E293B;
            border: 1px solid #F1F5F9;
            border-radius: 6px;
            padding: 12px;
            margin: 4px 0px;
            font-size: 13px;
        }
        QListWidget::item:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #F8FAFC, stop:1 #F1F5F9);
            border: 1px solid #CBD5E1;
            color: #1E293B;
        }
        QListWidget::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3B82F6, stop:1 #2563EB);
            color: white;
            border: 1px solid #1D4ED8;
        }
    """


def _get_confirm_button_style() -> str:
    """Confirm button stílus."""
    return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3B82F6, stop:1 #2563EB);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 14px;
            padding: 12px 16px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #2563EB, stop:1 #1D4ED8);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1D4ED8, stop:1 #1E40AF);
        }
        QPushButton:disabled {
            background: #E2E8F0;
            color: #94A3B8;
        }
    """
