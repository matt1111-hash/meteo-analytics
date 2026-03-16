#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Dialogs - UI Builder

🎨 UI elemek létrehozása

Képességek:
- Ablak beállítások
- UI inicializálás
- Widgetek létrehozása

Fájl: src/presentation/gui/dialogs/ui_builder.py
"""

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QButtonGroup,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QRadioButton,
    QTableWidget,
)

if TYPE_CHECKING:
    pass

from ..utils import GUIConstants


def _setup_window(self) -> None:
    """
    Ablak alapbeállításai - THEMEMANAGER KOMPATIBILIS.

    Args:
        self: ExtremeWeatherDialog instance
    """
    self.setWindowTitle(f"Extrém időjárási események - {self.city_name}")
    self.setMinimumSize(GUIConstants.DIALOG_MIN_WIDTH, GUIConstants.DIALOG_MIN_HEIGHT)

    # ThemeManager automatikus styling (szülő CSS öröklés helyett)


def _init_ui(self) -> None:
    """
    UI elemek inicializálása - MINIMAL CSS APPROACH.

    Args:
        self: ExtremeWeatherDialog instance
    """
    from PySide6.QtWidgets import QVBoxLayout

    layout = QVBoxLayout(self)
    layout.setSpacing(GUIConstants.LAYOUT_SPACING)

    # Periódus kiválasztó panel
    period_group = _create_period_selection_group(self)
    layout.addWidget(period_group)

    # Extrém értékek táblázata
    self.extreme_table = _create_extreme_table(self)
    layout.addWidget(self.extreme_table)

    # Bezárás gomb - JAVÍTVA: self.close_button mentése
    self.close_button = _create_close_button(self)
    layout.addWidget(self.close_button)


def _create_period_selection_group(self):
    """
    Periódus kiválasztó widget létrehozása - THEMEMANAGER KOMPATIBILIS.

    Args:
        self: ExtremeWeatherDialog instance

    Returns:
        QGroupBox: Periódus kiválasztó csoport
    """
    from .event_handlers import _on_period_type_changed

    period_group = QGroupBox("Időszak típusa")
    period_layout = QHBoxLayout(period_group)

    # Gomb csoport a kölcsönös kizáráshoz
    self.period_type_group = QButtonGroup()

    # Radio gombok
    self.daily_radio = QRadioButton("Napi adatok")
    self.monthly_radio = QRadioButton("Havi adatok")

    # Alapértelmezett kiválasztás
    self.daily_radio.setChecked(True)

    # Gombok hozzáadása a csoporthoz
    self.period_type_group.addButton(self.daily_radio)
    self.period_type_group.addButton(self.monthly_radio)

    # Layout-hoz adás
    period_layout.addWidget(self.daily_radio)
    period_layout.addWidget(self.monthly_radio)
    period_layout.addStretch()

    # Eseménykezelők
    self.daily_radio.toggled.connect(lambda: _on_period_type_changed(self))
    self.monthly_radio.toggled.connect(lambda: _on_period_type_changed(self))

    return period_group


def _create_extreme_table(self):
    """
    Extrém értékek táblázatának létrehozása - THEMEMANAGER KOMPATIBILIS.

    Args:
        self: ExtremeWeatherDialog instance

    Returns:
        QTableWidget: Extrém értékek táblázata
    """
    table = QTableWidget()
    table.setColumnCount(3)
    table.setHorizontalHeaderLabels(["Kategória", "Érték", "Dátum"])

    # Táblázat beállítások (stílus nélkül - ThemeManager kezeli)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.verticalHeader().setVisible(False)

    return table


def _create_close_button(self):
    """
    Bezárás gomb létrehozása - THEMEMANAGER KOMPATIBILIS.

    🔧 JAVÍTÁS: Most már self.close_button-ként mentjük

    Args:
        self: ExtremeWeatherDialog instance

    Returns:
        QPushButton: Bezárás gomb
    """
    close_button = QPushButton("Bezárás")
    close_button.clicked.connect(self.accept)
    close_button.setMinimumHeight(GUIConstants.BUTTON_HEIGHT)
    return close_button
