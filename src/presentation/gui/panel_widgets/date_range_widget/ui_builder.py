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
    from ..theme_manager import ThemeManager


def create_time_range_group(parent_widget: QWidget) -> dict:
    """
    Time range csoport létrehozása.

    Args:
        parent_widget: Szülő widget

    Returns:
        Dict with UI elements (group, radio, combo, info_label)
    """
    time_range_group = QGroupBox("⏰ Időtartam (Multi-Year)")
    group_layout = QVBoxLayout(time_range_group)
    group_layout.setContentsMargins(12, 16, 12, 12)
    group_layout.setSpacing(12)

    # Mode selector radio buttons
    mode_layout = QHBoxLayout()
    mode_layout.setSpacing(16)

    time_range_radio = QRadioButton("Időtartam választó")
    time_range_radio.setChecked(True)
    time_range_radio.setToolTip("Automatikus dátum számítás időtartam alapján")
    time_range_radio.setMinimumHeight(24)
    mode_layout.addWidget(time_range_radio)

    manual_dates_radio = QRadioButton("Manuális dátumok")
    manual_dates_radio.setToolTip("Pontos dátumok kézi megadása")
    manual_dates_radio.setMinimumHeight(24)
    mode_layout.addWidget(manual_dates_radio)

    group_layout.addLayout(mode_layout)

    # Időtartam dropdown
    form_layout = QFormLayout()
    form_layout.setVerticalSpacing(10)
    form_layout.setHorizontalSpacing(8)

    time_range_combo = QComboBox()
    time_range_combo.addItems([
        "1 év",
        "5 év",
        "10 év",
        "25 év",
        "55 év (teljes)",
    ])
    time_range_combo.setCurrentText("1év")
    time_range_combo.setMinimumHeight(32)
    time_range_combo.setToolTip("Automatikus dátum számítás a mai naptól visszafelé")

    form_layout.addRow("Időtartam:", time_range_combo)
    group_layout.addLayout(form_layout)

    # Computed dates info
    computed_dates_info = QLabel("Számított időszak: 2024-08-13 → 2025-08-13")
    computed_dates_info.setWordWrap(True)
    computed_dates_info.setMinimumHeight(40)
    group_layout.addWidget(computed_dates_info)

    # Size constraints
    time_range_group.setMinimumHeight(140)
    time_range_group.setMaximumHeight(180)

    parent_widget.layout().addWidget(time_range_group)

    return {
        "time_range_group": time_range_group,
        "time_range_radio": time_range_radio,
        "manual_dates_radio": manual_dates_radio,
        "time_range_combo": time_range_combo,
        "computed_dates_info": computed_dates_info
    }


def create_manual_dates_group(parent_widget: QWidget) -> dict:
    """
    Manual dates csoport létrehozása.

    Args:
        parent_widget: Szülő widget

    Returns:
        Dict with UI elements
    """
    manual_dates_group = QGroupBox("📅 Manuális Dátumok (Opcionális)")
    group_layout = QFormLayout(manual_dates_group)
    group_layout.setContentsMargins(12, 16, 12, 12)
    group_layout.setVerticalSpacing(12)
    group_layout.setHorizontalSpacing(8)

    # Start date
    start_date = QDateEdit()
    start_date.setCalendarPopup(True)
    start_date.setDisplayFormat("yyyy-MM-dd")
    start_date.setDate(QDate.currentDate().addYears(-1))
    start_date.setMinimumHeight(32)
    group_layout.addRow("Kezdő dátum:", start_date)

    # End date
    end_date = QDateEdit()
    end_date.setCalendarPopup(True)
    end_date.setDisplayFormat("yyyy-MM-dd")
    end_date.setDate(QDate.currentDate())
    end_date.setMinimumHeight(32)
    group_layout.addRow("Befejező dátum:", end_date)

    # Quick buttons row 1
    quick_layout1 = QHBoxLayout()
    quick_layout1.setSpacing(8)

    last_month_btn = QPushButton("Előző hónap")
    last_month_btn.setMinimumHeight(28)
    quick_layout1.addWidget(last_month_btn)

    last_year_btn = QPushButton("Előző év")
    last_year_btn.setMinimumHeight(28)
    quick_layout1.addWidget(last_year_btn)

    last_1year_btn = QPushButton("1 év")
    last_1year_btn.setMinimumHeight(28)
    quick_layout1.addWidget(last_1year_btn)

    last_5years_btn = QPushButton("5 év")
    last_5years_btn.setMinimumHeight(28)
    quick_layout1.addWidget(last_5years_btn)

    group_layout.addRow("Gyors:", quick_layout1)

    # Quick buttons row 2
    quick_layout2 = QHBoxLayout()
    quick_layout2.setSpacing(8)

    last_10years_btn = QPushButton("10 év")
    last_10years_btn.setMinimumHeight(28)
    quick_layout2.addWidget(last_10years_btn)

    last_25years_btn = QPushButton("25 év")
    last_25years_btn.setMinimumHeight(28)
    quick_layout2.addWidget(last_25years_btn)

    last_55years_btn = QPushButton("55 év")
    last_55years_btn.setMinimumHeight(28)
    quick_layout2.addWidget(last_55years_btn)

    group_layout.addRow("Multi-year:", quick_layout2)

    # Size constraints
    manual_dates_group.setMinimumHeight(160)
    manual_dates_group.setMaximumHeight(200)

    parent_widget.layout().addWidget(manual_dates_group)

    return {
        "manual_dates_group": manual_dates_group,
        "start_date": start_date,
        "end_date": end_date,
        "last_month_btn": last_month_btn,
        "last_year_btn": last_year_btn,
        "last_1year_btn": last_1year_btn,
        "last_5years_btn": last_5years_btn,
        "last_10years_btn": last_10years_btn,
        "last_25years_btn": last_25years_btn,
        "last_55years_btn": last_55years_btn
    }


def register_for_theming(
    theme_manager: "ThemeManager",
    parent_widget: QWidget,
    time_range_group: QGroupBox,
    manual_dates_group: QGroupBox,
    time_range_radio: QRadioButton,
    manual_dates_radio: QRadioButton,
    time_range_combo: QComboBox,
    start_date: QDateEdit,
    end_date: QDateEdit,
    buttons: list,
    computed_dates_info: QLabel
) -> None:
    """
    Widgetek regisztrálása theme manager-hez.

    Args:
        theme_manager: ThemeManager instance
        parent_widget: Szülő widget
        time_range_group: Time range group box
        manual_dates_group: Manual dates group box
        time_range_radio: Time range radio button
        manual_dates_radio: Manual dates radio button
        time_range_combo: Time range combo box
        start_date: Start date edit
        end_date: End date edit
        buttons: Quick buttons list
        computed_dates_info: Computed dates info label
    """
    from ..theme_manager import register_widget_for_theming

    register_widget_for_theming(parent_widget, "container")
    register_widget_for_theming(time_range_group, "container")
    register_widget_for_theming(manual_dates_group, "container")

    # Radio buttons
    register_widget_for_theming(time_range_radio, "input")
    register_widget_for_theming(manual_dates_radio, "input")

    # Combo és date edits
    register_widget_for_theming(time_range_combo, "input")
    register_widget_for_theming(start_date, "input")
    register_widget_for_theming(end_date, "input")

    # Buttons
    for btn in buttons:
        register_widget_for_theming(btn, "button")

    # Labels
    apply_label_styling(theme_manager, computed_dates_info, "secondary")


def apply_label_styling(
    theme_manager: "ThemeManager",
    label: QLabel,
    style_type: str
) -> None:
    """
    Label styling alkalmazása.

    Args:
        theme_manager: ThemeManager instance
        label: QLabel widget
        style_type: "secondary" vagy "primary"
    """
    from ..theme_manager import register_widget_for_theming

    color_palette = theme_manager.get_color_scheme()
    if not color_palette:
        return

    if style_type == "secondary":
        color = color_palette.get_color("info", "light") or "#9ca3af"
        font_size = "11px"
    else:
        color = color_palette.get_color("primary", "base") or "#2563eb"
        font_size = "12px"

    css = f"QLabel {{ color: {color}; font-size: {font_size}; }}"
    label.setStyleSheet(css)

    register_widget_for_theming(label, "text")
