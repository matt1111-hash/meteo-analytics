#!/usr/bin/env python3
# mypy: ignore-errors

"""
Multi-City Widget - UI Builder

🎨 UI elemek létrehozása és témázás

Képességek:
- Group box és layout setup
- Combo box és button létrehozás
- Theme manager regisztráció

Fájl: src/presentation/gui/panel_widgets/multi_city_widget/ui_builder.py
"""

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.presentation.gui.theme_manager import ThemeManager


def create_multi_city_ui(parent_widget: QWidget, theme_manager: "ThemeManager") -> dict:  # noqa: ARG001
    """
    UI elemek létrehozása multi-city widget-hez.

    Args:
        parent_widget: Szülő widget
        theme_manager: ThemeManager instance

    Returns:
        Dict with UI elements (group, combo_box, info_label, clear_btn)
    """
    # Main layout
    layout = QVBoxLayout(parent_widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    # Group box
    group = QGroupBox("🏙️ Multi-City Választó")
    group_layout = QVBoxLayout(group)
    group_layout.setContentsMargins(12, 16, 12, 12)
    group_layout.setSpacing(12)

    # Dropdown combo box
    combo_box = QComboBox()
    combo_box.setMinimumHeight(35)
    combo_box.setEditable(False)
    combo_box.setEnabled(True)
    group_layout.addWidget(combo_box)

    # Selection info label
    info_label = QLabel("Válasszon régiót vagy megyét...")
    info_label.setWordWrap(True)
    info_label.setMinimumHeight(40)
    group_layout.addWidget(info_label)

    # Control buttons
    control_layout = QHBoxLayout()
    control_layout.setSpacing(8)

    clear_btn = QPushButton("❌ Választás törlése")
    control_layout.addWidget(clear_btn)

    # Spacer
    control_layout.addStretch()

    group_layout.addLayout(control_layout)

    # Size constraints
    group.setMinimumHeight(150)
    group.setMaximumHeight(180)

    layout.addWidget(group)

    return {
        "group": group,
        "combo_box": combo_box,
        "info_label": info_label,
        "clear_btn": clear_btn,
    }


def register_widget_for_theming(
    theme_manager: "ThemeManager",  # noqa: ARG001
    widget: QWidget,
    group: QGroupBox,
    combo_box: QComboBox,
    clear_btn: QPushButton,
    info_label: QLabel,
) -> None:
    """
    Widgetek regisztrálása theme manager-hez.

    Args:
        theme_manager: ThemeManager instance
        widget: Fő widget
        group: Group box
        combo_box: Combo box
        clear_btn: Clear button
        info_label: Info label
    """
    from src.presentation.gui.theme_manager import register_widget_for_theming  # noqa: PLC0415

    register_widget_for_theming(widget, "container")
    register_widget_for_theming(group, "container")
    register_widget_for_theming(combo_box, "input")
    register_widget_for_theming(clear_btn, "button")
    register_widget_for_theming(info_label, "text")


def apply_label_styling(label: QLabel, theme_manager: "ThemeManager", style_type: str) -> None:
    """
    Label styling alkalmazása.

    Args:
        label: QLabel widget
        theme_manager: ThemeManager instance
        style_type: "secondary" vagy "primary"
    """
    color_palette = theme_manager.get_color_scheme()
    if not color_palette:
        return

    if style_type == "secondary":
        color = color_palette.get_color("info", "light") or "#9ca3af"
        font_size = "11px"
    elif style_type == "primary":
        color = color_palette.get_color("primary", "base") or "#2563eb"
        font_size = "12px"
    else:
        return

    css = f"QLabel {{ color: {color}; font-size: {font_size}; }}"
    label.setStyleSheet(css)

    from src.presentation.gui.theme_manager import register_widget_for_theming  # noqa: PLC0415

    register_widget_for_theming(label, "text")
