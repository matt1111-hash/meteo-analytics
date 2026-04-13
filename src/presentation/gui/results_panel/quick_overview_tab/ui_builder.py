#!/usr/bin/env python3
# mypy: ignore-errors

"""
Quick Overview Tab - UI Builder

UI elemek létrehozása a gyors áttekintés tab-hoz.

Fájl: src/presentation/gui/results_panel/quick_overview_tab/ui_builder.py
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    pass


def create_title_label() -> QLabel:
    """Cím label létrehozása."""
    title_label = QLabel("Gyors Áttekintés")
    title_font = QFont()
    title_font.setBold(True)
    title_font.setPointSize(16)
    title_label.setFont(title_font)
    title_label.setAlignment(Qt.AlignCenter)
    return title_label


def create_stats_container(
    theme_manager,
    apply_text_styling,
    apply_accent_styling,
    stat_labels: dict[str, QLabel],
) -> tuple[QWidget, QGroupBox, QGroupBox, QGroupBox, tuple, QGroupBox]:
    """
    Statisztikai kártyák konténer létrehozása.

    Returns:
        Tuple of (container, temp_card, precip_card, wind_card, info_card_tuple, mini_charts_container)
    """
    container = QWidget()
    layout = QGridLayout(container)
    layout.setSpacing(10)

    # Hőmérséklet kártya
    temp_card = create_stat_card(
        "Hőmérséklet",
        [
            ("Átlag", "avg_temp", "°C"),
            ("Maximum", "max_temp", "°C"),
            ("Minimum", "min_temp", "°C"),
            ("Hőingás", "temp_range", "°C"),
        ],
        "#f59e0b",
        theme_manager,
        apply_text_styling,
        apply_accent_styling,
        stat_labels,
    )
    layout.addWidget(temp_card, 0, 0)

    # Csapadék kártya
    precip_card = create_stat_card(
        "Csapadék",
        [
            ("Összesen", "total_precip", "mm"),
            ("Átlag/nap", "avg_precip", "mm"),
            ("Maximum", "max_precip", "mm"),
            ("Esős napok", "rainy_days", "nap"),
        ],
        "#3b82f6",
        theme_manager,
        apply_text_styling,
        apply_accent_styling,
        stat_labels,
    )
    layout.addWidget(precip_card, 0, 1)

    # Szél kártya
    wind_card = create_stat_card(
        "Széllökések",
        [
            ("Átlag", "avg_wind", "km/h"),
            ("Maximum", "max_wind", "km/h"),
            ("Szeles napok", "windy_days", "nap"),
            ("Uralkodó irány", "wind_direction", ""),
        ],
        "#10b981",
        theme_manager,
        apply_text_styling,
        apply_accent_styling,
        stat_labels,
    )
    layout.addWidget(wind_card, 0, 2)

    # Általános információk kártya
    info_card_tuple = create_info_card(theme_manager)
    info_card = info_card_tuple[0]  # Extract just the QGroupBox
    layout.addWidget(info_card, 1, 0, 1, 3)

    return container, temp_card, precip_card, wind_card, info_card_tuple


def create_stat_card(
    title: str,
    stats: list[tuple[str, str, str]],
    accent_color: str,
    theme_manager,  # noqa: ARG001
    apply_text_styling,
    apply_accent_styling,
    stat_labels: dict[str, QLabel],
) -> QGroupBox:
    """Egyetlen statisztikai kártya létrehozása."""
    card = QGroupBox(title)
    layout = QVBoxLayout(card)
    layout.setSpacing(8)

    for label_text, key, unit in stats:
        stat_layout = QHBoxLayout()

        # Stat label
        label = QLabel(f"{label_text}:")
        label.setMinimumWidth(70)
        apply_text_styling(label)
        stat_layout.addWidget(label)

        # Value label
        value_label = QLabel("-")
        stat_layout.addWidget(value_label)

        # Unit label
        if unit:
            unit_label = QLabel(unit)
            apply_text_styling(unit_label)
            stat_layout.addWidget(unit_label)

        stat_layout.addStretch()
        layout.addLayout(stat_layout)

        # Label referencia mentése
        stat_labels[key] = value_label
        apply_accent_styling(value_label, accent_color)

    return card


def create_info_card(theme_manager) -> tuple[QGroupBox, QLabel, QLabel, QLabel, QLabel]:  # noqa: ARG001
    """Általános információs kártya létrehozása."""
    card = QGroupBox("Információ")

    layout = QVBoxLayout(card)

    city_info_label = QLabel("Város: -")
    date_range_label = QLabel("Időszak: -")
    data_source_label = QLabel("Adatforrás: -")
    record_count_label = QLabel("Rekordok: -")

    layout.addWidget(city_info_label)
    layout.addWidget(date_range_label)
    layout.addWidget(data_source_label)
    layout.addWidget(record_count_label)

    return (
        card,
        city_info_label,
        date_range_label,
        data_source_label,
        record_count_label,
    )


def create_mini_charts_container() -> QGroupBox:
    """Mini előnézeti chartok konténer létrehozása."""
    container = QGroupBox("Grafikai Előnézet")
    container.setMinimumHeight(200)

    layout = QVBoxLayout(container)

    placeholder = QLabel("Mini grafikon előnézetek")
    placeholder.setAlignment(Qt.AlignCenter)

    layout.addWidget(placeholder)

    return container, placeholder


def create_quick_actions() -> tuple[QWidget, QPushButton, QPushButton, QPushButton]:
    """Gyors akció gombok létrehozása."""
    container = QWidget()
    layout = QHBoxLayout(container)

    charts_btn = QPushButton("Részletes Diagramok")
    table_btn = QPushButton("Adattáblázat")
    extreme_btn = QPushButton("Extrém Események")

    layout.addWidget(charts_btn)
    layout.addWidget(table_btn)
    layout.addWidget(extreme_btn)
    layout.addStretch()

    return container, charts_btn, table_btn, extreme_btn
