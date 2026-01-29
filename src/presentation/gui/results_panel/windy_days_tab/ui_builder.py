#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windy Days Tab - UI Builder

UI elemek létrehozása a szeles napok analízis tab-hoz.

Fájl: src/presentation/gui/results_panel/windy_days_tab/ui_builder.py
"""

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.analytics.wind_analysis import WINDY_DAY_THRESHOLD_KMH


def create_header_section() -> tuple[QFrame, QLabel, QLabel]:
    """
    Header szekció létrehozása.

    Returns:
        Tuple of (frame, title_label, desc_label)
    """
    header_frame = QFrame()
    header_frame.setFrameStyle(QFrame.StyledPanel)
    header_layout = QVBoxLayout(header_frame)

    # Főcím
    title_label = QLabel("Szeles Napok Analízis")
    title_label.setObjectName("windy_days_title")
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
    title_label.setAlignment(Qt.AlignCenter)

    # Leírás
    desc_label = QLabel(
        "Havi szeles napok eloszlásának vizsgálata beállítható küszöbértékkel"
    )
    desc_label.setObjectName("windy_days_desc")
    desc_label.setStyleSheet("font-size: 12px; color: #7f8c8d; font-style: italic;")
    desc_label.setAlignment(Qt.AlignCenter)
    desc_label.setWordWrap(True)

    header_layout.addWidget(title_label)
    header_layout.addWidget(desc_label)

    return header_frame, title_label, desc_label


def create_controls_section(
    default_threshold: float,
) -> tuple[QGroupBox, QSpinBox, QPushButton, QPushButton]:
    """
    Kontroll szekció létrehozása.

    Args:
        default_threshold: Alapértelmezett küszöbérték

    Returns:
        Tuple of (group, spinbox, analyze_button, export_button)
    """
    controls_group = QGroupBox("Beállítások")
    controls_layout = QGridLayout(controls_group)

    # Küszöbérték beállítás
    threshold_label = QLabel("Küszöbérték (km/h):")
    threshold_spinbox = QSpinBox()
    threshold_spinbox.setRange(10, 100)
    threshold_spinbox.setValue(int(default_threshold))
    threshold_spinbox.setSuffix(" km/h")
    threshold_spinbox.setToolTip("Szeles nap küszöbérték szélsebességben")
    threshold_spinbox.setObjectName("threshold_spinbox")

    # Automatikus frissítés checkbox - létrehozás, de a caller adja vissza
    auto_update_checkbox = QPushButton("Automatikus frissítés")
    auto_update_checkbox.setCheckable(True)
    auto_update_checkbox.setChecked(True)
    auto_update_checkbox.setObjectName("auto_update_checkbox")

    # Gombok
    analyze_button = QPushButton("Analízis Futtatása")
    analyze_button.setObjectName("analyze_button")
    analyze_button.setMinimumHeight(35)
    analyze_button.setStyleSheet("""
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #21618c;
        }
        QPushButton:disabled {
            background-color: #bdc3c7;
        }
    """)

    export_button = QPushButton("Export Chart")
    export_button.setObjectName("export_button")
    export_button.setEnabled(False)
    export_button.setMinimumHeight(35)

    # Layout elrendezés
    controls_layout.addWidget(threshold_label, 0, 0)
    controls_layout.addWidget(threshold_spinbox, 0, 1)
    controls_layout.addWidget(auto_update_checkbox, 0, 2)
    controls_layout.addWidget(analyze_button, 1, 0, 1, 2)
    controls_layout.addWidget(export_button, 1, 2)

    return controls_group, threshold_spinbox, analyze_button, export_button


def create_progress_section() -> QProgressBar:
    """Progress bar szekció létrehozása."""
    progress_bar = QProgressBar()
    progress_bar.setVisible(False)
    progress_bar.setStyleSheet("""
        QProgressBar {
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
        }
        QProgressBar::chunk {
            background-color: #3498db;
            border-radius: 3px;
        }
    """)
    return progress_bar


def create_chart_section(chart) -> tuple[QFrame, QLabel]:
    """
    Chart szekció létrehozása.

    Args:
        chart: WindyDaysChart instance

    Returns:
        Tuple of (frame, title_label)
    """
    chart_frame = QFrame()
    chart_frame.setFrameStyle(QFrame.StyledPanel)
    chart_layout = QVBoxLayout(chart_frame)

    # Chart címke
    chart_title = QLabel("Havi Szeles Napok Oszlopdiagram")
    chart_title.setObjectName("chart_title")
    chart_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #34495e;")
    chart_title.setAlignment(Qt.AlignLeft)

    chart_layout.addWidget(chart_title)
    chart_layout.addWidget(chart, 1)

    return chart_frame, chart_title


def create_summary_section() -> tuple[QFrame, QTextEdit]:
    """
    Összefoglaló szekció létrehozása.

    Returns:
        Tuple of (frame, summary_text)
    """
    summary_frame = QFrame()
    summary_frame.setFrameStyle(QFrame.StyledPanel)
    summary_layout = QVBoxLayout(summary_frame)

    # Summary címke
    summary_title = QLabel("Részletes Összefoglaló")
    summary_title.setObjectName("summary_title")
    summary_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #34495e;")

    # Text area
    summary_text = QTextEdit()
    summary_text.setObjectName("summary_text")
    summary_text.setReadOnly(True)
    summary_text.setMaximumWidth(350)
    summary_text.setStyleSheet("""
        QTextEdit {
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            background-color: #f8f9fa;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 11px;
            padding: 8px;
        }
    """)

    summary_layout.addWidget(summary_title)
    summary_layout.addWidget(summary_text, 1)

    return summary_frame, summary_text


def create_footer_section() -> tuple[QFrame, QLabel]:
    """
    Footer szekció létrehozása.

    Returns:
        Tuple of (frame, info_label)
    """
    footer_frame = QFrame()
    footer_frame.setMaximumHeight(30)
    footer_layout = QHBoxLayout(footer_frame)

    # Info label
    info_label = QLabel("Tipp: Küszöbérték változtatáskor automatikusan újraszámít")
    info_label.setObjectName("footer_info")
    info_label.setStyleSheet("font-size: 10px; color: #7f8c8d; font-style: italic;")

    footer_layout.addWidget(info_label)
    footer_layout.addStretch()

    return footer_frame, info_label


def create_content_splitter() -> QSplitter:
    """Content splitter létrehozása."""
    splitter = QSplitter(Qt.Horizontal)
    splitter.setSizes([600, 300])
    splitter.setChildrenCollapsible(False)
    return splitter
