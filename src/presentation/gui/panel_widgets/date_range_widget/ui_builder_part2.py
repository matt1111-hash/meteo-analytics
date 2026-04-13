# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from ui_builder.py."""

from __future__ import annotations

from .ui_builder_support import *


def register_for_theming(
    theme_manager: ThemeManager,
    parent_widget: QWidget,
    time_range_group: QGroupBox,
    manual_dates_group: QGroupBox,
    time_range_radio: QRadioButton,
    manual_dates_radio: QRadioButton,
    time_range_combo: QComboBox,
    start_date: QDateEdit,
    end_date: QDateEdit,
    buttons: list,
    computed_dates_info: QLabel,
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
    from src.presentation.gui.theme_manager import register_widget_for_theming

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


def apply_label_styling(theme_manager: ThemeManager, label: QLabel, style_type: str) -> None:
    """
    Label styling alkalmazása.

    Args:
        theme_manager: ThemeManager instance
        label: QLabel widget
        style_type: "secondary" vagy "primary"
    """
    from src.presentation.gui.theme_manager import register_widget_for_theming

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
