#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Anomaly Settings Dialog - UI Builder Module
UI komponensek létrehozása az AnomalySettingsDialoghoz.
"""

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...utils import AnomalyConstants

if TYPE_CHECKING:
    from src.presentation.gui.dialogs.anomaly_settings_dialog.core import (
        AnomalySettingsDialog,
    )


logger = logging.getLogger(__name__)


class AnomalySettingsUIBuilder:
    """UI építő osztály az AnomalySettingsDialoghoz."""

    def __init__(self, dialog: 'AnomalySettingsDialog'):
        """Inicializálás."""
        self.dialog = dialog

    def create_header_section(self) -> QWidget:
        """Fejléc szekció: cím + profil választó."""
        container = QWidget()
        layout = QHBoxLayout(container)

        # Cím
        title_label = QLabel("⚙️ Anomália Beállítások")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(18)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        layout.addStretch()

        # Profil választó szekció
        profile_section = self.create_profile_section()
        layout.addWidget(profile_section)

        return container

    def create_profile_section(self) -> QGroupBox:
        """Profil választó és menedzsment gombok."""
        group = QGroupBox("📁 Profilok")
        layout = QHBoxLayout(group)

        # Profil dropdown
        layout.addWidget(QLabel("Aktív profil:"))

        self.dialog.profile_combo = QComboBox()
        self.dialog.profile_combo.setMinimumWidth(150)
        self.dialog.profile_combo.currentTextChanged.connect(self.dialog._on_profile_changed)
        layout.addWidget(self.dialog.profile_combo)

        # Profil menedzsment gombok
        new_btn = QPushButton("🆕 Új")
        new_btn.setToolTip("Új profil létrehozása")
        new_btn.clicked.connect(self.dialog._create_new_profile)
        layout.addWidget(new_btn)

        edit_btn = QPushButton("✏️ Szerk")
        edit_btn.setToolTip("Profil átnevezése")
        edit_btn.clicked.connect(self.dialog._edit_profile_name)
        layout.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ Törlés")
        delete_btn.setToolTip("Profil törlése")
        delete_btn.clicked.connect(self.dialog._delete_profile)
        layout.addWidget(delete_btn)

        return group

    def create_main_tabs(self) -> QTabWidget:
        """Főbb beállítási tab-ok."""
        tabs = QTabWidget()

        # 1. Küszöbértékek tab
        thresholds_tab = self.create_thresholds_tab()
        tabs.addTab(thresholds_tab, "🌡️ Küszöbértékek")

        # 2. Kategóriák tab
        categories_tab = self.create_categories_tab()
        tabs.addTab(categories_tab, "🏷️ Kategóriák")

        # 3. Előnézet tab
        preview_tab = self.create_preview_tab()
        tabs.addTab(preview_tab, "👁️ Előnézet")

        return tabs

    def create_thresholds_tab(self) -> QWidget:
        """Küszöbértékek beállítása tab."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)

        # Hőmérséklet szekció
        temp_section = self.create_temperature_section()
        layout.addWidget(temp_section)

        # Csapadék szekció
        precip_section = self.create_precipitation_section()
        layout.addWidget(precip_section)

        # Szél szekció
        wind_section = self.create_wind_section()
        layout.addWidget(wind_section)

        layout.addStretch()

        return container

    def create_temperature_section(self) -> QGroupBox:
        """🌡️ Hőmérséklet küszöbök szekció."""
        group = QGroupBox("🌡️ Hőmérséklet Küszöbök")
        layout = QVBoxLayout(group)

        self.dialog.temp_widgets = {}

        # Meleg küszöb
        hot_spinbox = QDoubleSpinBox()
        hot_spinbox.setRange(-50.0, 60.0)
        hot_spinbox.setSuffix(" °C")
        hot_spinbox.setDecimals(1)
        hot_spinbox.setValue(AnomalyConstants.TEMP_HOT_THRESHOLD)
        hot_spinbox.valueChanged.connect(self.dialog._on_setting_changed)
        self.dialog.temp_widgets["hot"] = hot_spinbox
        layout.addWidget(QLabel("🔥 Meleg küszöb:"))
        layout.addWidget(hot_spinbox)

        # Hideg küszöb
        cold_spinbox = QDoubleSpinBox()
        cold_spinbox.setRange(-50.0, 40.0)
        cold_spinbox.setSuffix(" °C")
        cold_spinbox.setDecimals(1)
        cold_spinbox.setValue(AnomalyConstants.TEMP_COLD_THRESHOLD)
        cold_spinbox.valueChanged.connect(self.dialog._on_setting_changed)
        self.dialog.temp_widgets["cold"] = cold_spinbox
        layout.addWidget(QLabel("❄️ Hideg küszöb:"))
        layout.addWidget(cold_spinbox)

        # Infó label
        info_label = QLabel("💡 Meleg küszöb felett 'forró', hideg alatt 'fagyos' kategória.")
        info_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        layout.addWidget(info_label)

        return group

    def create_precipitation_section(self) -> QGroupBox:
        """🌧️ Csapadék küszöbök szekció."""
        group = QGroupBox("🌧️ Csapadék Küszöbök")
        layout = QVBoxLayout(group)

        self.dialog.precip_widgets = {}

        # Magas küszöb
        high_spinbox = QDoubleSpinBox()
        high_spinbox.setRange(0.0, 500.0)
        high_spinbox.setSuffix(" mm")
        high_spinbox.setDecimals(1)
        high_spinbox.setValue(AnomalyConstants.PRECIP_HIGH_THRESHOLD)
        high_spinbox.valueChanged.connect(self.dialog._on_setting_changed)
        self.dialog.precip_widgets["high"] = high_spinbox
        layout.addWidget(QLabel("🌊 Magas küszöb:"))
        layout.addWidget(high_spinbox)

        # Alacsony küszöb
        low_spinbox = QDoubleSpinBox()
        low_spinbox.setRange(0.0, 50.0)
        low_spinbox.setSuffix(" mm")
        low_spinbox.setDecimals(1)
        low_spinbox.setValue(AnomalyConstants.PRECIP_LOW_THRESHOLD)
        low_spinbox.valueChanged.connect(self.dialog._on_setting_changed)
        self.dialog.precip_widgets["low"] = low_spinbox
        layout.addWidget(QLabel("🏜️ Alacsony küszöb:"))
        layout.addWidget(low_spinbox)

        # Infó label
        info_label = QLabel("💡 Magas küszöb felett 'esős', alacsony alatt 'száraz' kategória.")
        info_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        layout.addWidget(info_label)

        return group

    def create_wind_section(self) -> QGroupBox:
        """🌪️ Szél kategóriák szekció."""
        group = QGroupBox("🌪️ Szél Kategóriák")
        layout = QVBoxLayout(group)

        self.dialog.wind_widgets = {}

        # Szeles küszöb
        windy_spinbox = QSpinBox()
        windy_spinbox.setRange(10, 200)
        windy_spinbox.setSuffix(" km/h")
        windy_spinbox.setValue(AnomalyConstants.WIND_HIGH_THRESHOLD)
        windy_spinbox.valueChanged.connect(self.dialog._on_setting_changed)
        self.dialog.wind_widgets["high"] = windy_spinbox
        layout.addWidget(QLabel("💨 Szeles küszöb:"))
        layout.addWidget(windy_spinbox)

        # Szélvihar kategóriák
        categories = [
            ("Mérsékelt", 50, "normal"),
            ("Erős", 70, "strong"),
            ("Extrém", 100, "extreme"),
            ("Orkán", 120, "hurricane")
        ]

        for name, default_value, key in categories:
            spinbox = QSpinBox()
            spinbox.setRange(20, 300)
            spinbox.setSuffix(" km/h")
            spinbox.setValue(default_value)
            spinbox.valueChanged.connect(self.dialog._on_setting_changed)
            self.dialog.wind_widgets[key] = spinbox

            icon = {"normal": "🌿", "strong": "🌬️", "extreme": "🌪️", "hurricane": "🌀"}[key]
            layout.addWidget(QLabel(f"{icon} {name}:"))
            layout.addWidget(spinbox)

        # Infó label
        info_label = QLabel("💡 Szélsebesség kategóriák szélvihar elemzéshez.")
        info_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        layout.addWidget(info_label)

        return group

    def create_categories_tab(self) -> QWidget:
        """Kategóriák testreszabása tab."""
        container = QWidget()
        layout = QVBoxLayout(container)

        info_label = QLabel("🏷️ Kategória nevek, színek és ikonok testreszabása")
        info_label.setAlignment(Qt.AlignCenter)
        info_font = QFont()
        info_font.setBold(True)
        info_label.setFont(info_font)
        layout.addWidget(info_label)

        # Kategória szerkesztő grid
        categories_grid = self.create_categories_grid()
        layout.addWidget(categories_grid)

        layout.addStretch()

        return container

    def create_categories_grid(self) -> QWidget:
        """Kategóriák szerkesztése grid layout."""
        container = QWidget()
        layout = QGridLayout(container)
        layout.setSpacing(15)

        self.dialog.category_widgets = {}

        # Fejlécek
        headers = ["Kategória", "Név", "Szín", "Ikon", "Küszöb"]
        for col, header in enumerate(headers):
            label = QLabel(header)
            label.setStyleSheet("font-weight: bold; padding: 8px;")
            layout.addWidget(label, 0, col)

        # Kategóriák
        categories = [
            ("normal", "Normális", "#10b981", "🌱", "< 35°C"),
            ("warning", "Figyelmeztetés", "#f59e0b", "⚠️", "35-40°C"),
            ("danger", "Veszélyes", "#dc2626", "🚨", "> 40°C"),
            ("extreme", "Extrém", "#7c2d12", "💀", "> 45°C")
        ]

        for row, (key, name, color, icon, threshold) in enumerate(categories, 1):
            self.dialog.category_widgets[key] = {}

            # Kategória név (readonly)
            cat_label = QLabel(key.title())
            cat_label.setStyleSheet("padding: 4px; background: #f3f4f6; border-radius: 4px;")
            layout.addWidget(cat_label, row, 0)

            # Szerkeszthető név
            name_edit = QLineEdit(name)
            name_edit.textChanged.connect(self.dialog._on_setting_changed)
            self.dialog.category_widgets[key]["name"] = name_edit
            layout.addWidget(name_edit, row, 1)

            # Szín választó
            color_btn = QPushButton()
            color_btn.setFixedSize(40, 30)
            color_btn.setStyleSheet(f"background: {color}; border: 1px solid #ccc; border-radius: 4px;")
            color_btn.clicked.connect(lambda checked, k=key: self.dialog._choose_color(k))
            self.dialog.category_widgets[key]["color"] = color_btn
            self.dialog.category_widgets[key]["color_value"] = color
            layout.addWidget(color_btn, row, 2)

            # Ikon választó
            icon_btn = QPushButton(icon)
            icon_btn.setFixedSize(40, 30)
            icon_btn.clicked.connect(lambda checked, k=key: self.dialog._choose_icon(k))
            self.dialog.category_widgets[key]["icon"] = icon_btn
            layout.addWidget(icon_btn, row, 3)

            # Küszöb info (readonly)
            threshold_label = QLabel(threshold)
            threshold_label.setStyleSheet("padding: 4px; color: #6b7280;")
            layout.addWidget(threshold_label, row, 4)

        return container

    def create_preview_tab(self) -> QWidget:
        """Előnézet tab."""
        container = QWidget()
        layout = QVBoxLayout(container)

        # Előnézet címke
        preview_label = QLabel("👁️ Aktuális Beállítások Előnézete")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_font = QFont()
        preview_font.setBold(True)
        preview_label.setFont(preview_font)
        layout.addWidget(preview_label)

        # Előnézet szöveg terület
        self.dialog.preview_text = QTextEdit()
        self.dialog.preview_text.setReadOnly(True)
        self.dialog.preview_text.setMaximumHeight(300)
        layout.addWidget(self.dialog.preview_text)

        # Teszt adatok szekció
        test_section = self.create_test_section()
        layout.addWidget(test_section)

        layout.addStretch()

        return container

    def create_test_section(self) -> QGroupBox:
        """Teszt adatok szekció az előnézethez."""
        group = QGroupBox("🧪 Teszt Adatok")
        layout = QHBoxLayout(group)

        test_btn1 = QPushButton("🔥 Forró Nap Teszt")
        test_btn1.clicked.connect(lambda: self.dialog._run_test("hot_day"))
        layout.addWidget(test_btn1)

        test_btn2 = QPushButton("❄️ Hideg Nap Teszt")
        test_btn2.clicked.connect(lambda: self.dialog._run_test("cold_day"))
        layout.addWidget(test_btn2)

        test_btn3 = QPushButton("🌧️ Esős Nap Teszt")
        test_btn3.clicked.connect(lambda: self.dialog._run_test("rainy_day"))
        layout.addWidget(test_btn3)

        test_btn4 = QPushButton("🌪️ Viharos Nap Teszt")
        test_btn4.clicked.connect(lambda: self.dialog._run_test("windy_day"))
        layout.addWidget(test_btn4)

        return group

    def create_buttons_section(self) -> QWidget:
        """Alsó gombok szekció."""
        container = QWidget()
        layout = QHBoxLayout(container)

        # Bal oldali gombok
        reset_btn = QPushButton("🔄 Alapértelmezett")
        reset_btn.setToolTip("Jelenlegi profil visszaállítása alapértékekre")
        reset_btn.clicked.connect(self.dialog._reset_to_defaults)
        layout.addWidget(reset_btn)

        layout.addStretch()

        # Jobb oldali gombok
        apply_btn = QPushButton("✅ Alkalmaz")
        apply_btn.setToolTip("Beállítások alkalmazása mentés nélkül")
        apply_btn.clicked.connect(self.dialog._apply_settings)
        layout.addWidget(apply_btn)

        save_btn = QPushButton("💾 Mentés")
        save_btn.setToolTip("Beállítások mentése és alkalmazása")
        save_btn.clicked.connect(self.dialog._save_and_apply)
        layout.addWidget(save_btn)

        cancel_btn = QPushButton("❌ Mégse")
        cancel_btn.setToolTip("Módosítások elvetése")
        cancel_btn.clicked.connect(self.dialog._cancel_changes)
        layout.addWidget(cancel_btn)

        return container
