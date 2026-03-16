# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from ui_builder.py."""

from __future__ import annotations

from .ui_builder_part2 import (
    _get_confirm_button_style,
    _get_results_list_style,
    _get_status_label_style,
)
from .ui_builder_support import *


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
