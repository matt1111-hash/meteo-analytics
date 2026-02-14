#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provider Widget - UI Builder

🎨 UI elemek létrehozása provider widgethez

Képességek:
- Provider selection group
- Usage monitoring group
- Details group
- Control buttons

Fájl: src/presentation/gui/panel_widgets/provider_widget/ui_builder.py
"""

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from src.presentation.gui.theme_manager import register_widget_for_theming

if TYPE_CHECKING:
    pass


def setup_provider_ui(self) -> None:
    """
    UI komponensek inicializálása.

    Args:
        self: ProviderWidget instance
    """
    print("🔧 DEBUG: Setting up ProviderWidget UI...")

    # Main layout
    layout = QVBoxLayout(self)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(8)

    # === PROVIDER SELECTION GROUP ===
    selection_group = create_provider_selection_group(self)
    layout.addWidget(selection_group)

    # === USAGE MONITORING GROUP ===
    usage_group = create_usage_monitoring_group(self)
    layout.addWidget(usage_group)

    # === DETAILS GROUP ===
    details_group = create_details_group(self)
    layout.addWidget(details_group)

    # === CONTROL BUTTONS ===
    button_layout = create_control_buttons(self)
    layout.addLayout(button_layout)

    # Stretch at bottom
    layout.addStretch()

    print("✅ DEBUG: ProviderWidget UI setup complete - OPEN-METEO ALAPÉRTELMEZETT")


def create_provider_selection_group(self) -> QGroupBox:
    """
    Provider selection group létrehozása.

    Args:
        self: ProviderWidget instance

    Returns:
        QGroupBox: Provider selection group
    """
    selection_group = QGroupBox("🌍 Adatszolgáltató")
    register_widget_for_theming(selection_group, "container")
    selection_layout = QVBoxLayout(selection_group)

    # Provider dropdown
    provider_layout = QHBoxLayout()

    provider_label = QLabel("Provider:")
    register_widget_for_theming(provider_label, "text")
    provider_layout.addWidget(provider_label)

    self.provider_combo = QComboBox()
    register_widget_for_theming(self.provider_combo, "input")
    populate_provider_combo(self)
    provider_layout.addWidget(self.provider_combo)

    selection_layout.addLayout(provider_layout)

    # Status display - OPEN-METEO ALAPÉRTELMEZETT ÜZENET
    self.status_label = QLabel("🌍 Open-Meteo aktív - Ingyenes, korlátlan használat")
    register_widget_for_theming(self.status_label, "text")
    self.status_label.setWordWrap(True)
    selection_layout.addWidget(self.status_label)

    return selection_group


def create_usage_monitoring_group(self) -> QGroupBox:
    """
    Usage monitoring group létrehozása.

    Args:
        self: ProviderWidget instance

    Returns:
        QGroupBox: Usage monitoring group
    """
    usage_group = QGroupBox("📊 Használat Monitoring")
    register_widget_for_theming(usage_group, "container")
    usage_layout = QVBoxLayout(usage_group)

    # Usage progress bar
    self.usage_progress = QProgressBar()
    register_widget_for_theming(self.usage_progress, "progress")
    self.usage_progress.setMinimum(0)
    self.usage_progress.setMaximum(100)
    self.usage_progress.setValue(0)
    usage_layout.addWidget(self.usage_progress)

    # Usage label - OPEN-METEO ALAPÉRTELMEZETT
    self.usage_label = QLabel("🌍 Ingyenes - Korlátlan használat")
    register_widget_for_theming(self.usage_label, "text")
    usage_layout.addWidget(self.usage_label)

    # Cost label - OPEN-METEO ALAPÉRTELMEZETT
    self.cost_label = QLabel("💰 Költség: $0.00/hó")
    register_widget_for_theming(self.cost_label, "text")
    usage_layout.addWidget(self.cost_label)

    return usage_group


def create_details_group(self) -> QGroupBox:
    """
    Details group létrehozása.

    Args:
        self: ProviderWidget instance

    Returns:
        QGroupBox: Details group
    """
    details_group = QGroupBox("📋 Részletek")
    register_widget_for_theming(details_group, "container")
    details_layout = QVBoxLayout(details_group)

    self.details_text = QTextEdit()
    register_widget_for_theming(self.details_text, "input")
    self.details_text.setMaximumHeight(80)
    self.details_text.setReadOnly(True)
    # OPEN-METEO KIEMELÉS
    self.details_text.setText(
        "🌍 Open-Meteo: Ingyenes, korlátlan, megbízható\n💎 Meteostat: Premium, API key szükséges\n🤖 Auto: Smart routing (opcionális)"
    )
    details_layout.addWidget(self.details_text)

    return details_group


def create_control_buttons(self) -> QHBoxLayout:
    """
    Control buttons létrehozása.

    Args:
        self: ProviderWidget instance

    Returns:
        QHBoxLayout: Button layout
    """
    from .monitoring import _refresh_usage_stats, _reset_usage_stats

    button_layout = QHBoxLayout()

    refresh_button = QPushButton("🔄 Frissítés")
    register_widget_for_theming(refresh_button, "button")
    refresh_button.clicked.connect(_refresh_usage_stats)
    button_layout.addWidget(refresh_button)

    reset_button = QPushButton("🗑️ Reset")
    register_widget_for_theming(reset_button, "button")
    reset_button.clicked.connect(_reset_usage_stats)
    button_layout.addWidget(reset_button)

    button_layout.addStretch()

    return button_layout


def populate_provider_combo(self) -> None:
    """
    Provider dropdown feltöltése - OPEN-METEO ELSŐ HELYEN!

    Args:
        self: ProviderWidget instance
    """
    providers = [
        # 🎯 OPEN-METEO ELSŐ HELYEN (ALAPÉRTELMEZETT)
        ("open-meteo", "🌍 Open-Meteo (Ingyenes) ⭐ AJÁNLOTT"),
        ("meteostat", "💎 Meteostat (Premium)"),
        ("weatherapi", "🌤️ WeatherAPI (Premium)"),
        ("openweather", "☁️ OpenWeatherMap (Premium)"),
        ("auto", "🤖 Automatikus (Smart Routing)"),  # Auto utolsó helyen!
    ]

    for value, display in providers:
        self.provider_combo.addItem(display, value)

    # 🎯 KRITIKUS: Open-Meteo alapértelmezett (index 0)
    self.provider_combo.setCurrentIndex(0)

    print("🌍 DEBUG: Provider combo populated - OPEN-METEO ALAPÉRTELMEZETT")
