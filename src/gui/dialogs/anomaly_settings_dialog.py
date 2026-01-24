#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Anomália Beállítások Dialog
🎨 TELJES GUI: Testreszabható küszöbök, profilok, kategóriák
⚙️ FUNKCIONALITÁS: Real-time preview, automatikus mentés, predefined profilok
🔗 INTEGRÁCIÓ: AnomalyDetector dynamic settings, signal-based frissítés

🚀 MODERN GUI FEATURES:
✅ QDoubleSpinBox küszöbök
✅ QComboBox profil választó
✅ QColorDialog szín választó
✅ Real-time preview
✅ JSON profil mentés/betöltés
✅ Signal-based kommunikáció
"""

import logging
from typing import Dict, Any, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QGroupBox, QLabel, QPushButton, QComboBox, QDoubleSpinBox,
    QSpinBox, QLineEdit, QTextEdit, QColorDialog, QMessageBox,
    QTabWidget, QWidget
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor

from ...data.anomaly_profile_manager import AnomalyProfileManager
from ..utils import AnomalyConstants
from ..theme_manager import get_theme_manager, register_widget_for_theming

logger = logging.getLogger(__name__)


class AnomalySettingsDialog(QDialog):
    """
    🎨 Anomália Beállítások Dialog - Teljes GUI Kezelés
    
    🎯 FŐBB FUNKCIÓK:
    ✅ Küszöbértékek testreszabása (hőmérséklet, csapadék, szél)
    ✅ Profil menedzsment (új, szerkesztés, törlés, választás)
    ✅ Kategória szerkesztő (név, szín, ikon, küszöb)
    ✅ Real-time preview és validáció
    ✅ Automatikus mentés JSON fájlba
    ✅ Predefined profilok (default, tropical, arctic)
    
    🔗 SIGNALS:
    settings_changed(dict) - Beállítások változtak
    profile_changed(str) - Aktív profil változott
    """
    
    # Signals
    settings_changed = Signal(dict)
    profile_changed = Signal(str)
    
    def __init__(self, parent=None):
        """Anomália beállítások dialog inicializálása."""
        super().__init__(parent)
        
        self.theme_manager = get_theme_manager()
        self.profile_manager = AnomalyProfileManager()
        
        # Belső állapot
        self.current_profile: str = "default"
        self.unsaved_changes: bool = False
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self._update_preview)
        
        # UI komponensek tárolása
        self.profile_combo: Optional[QComboBox] = None
        self.temp_widgets: Dict[str, QDoubleSpinBox] = {}
        self.precip_widgets: Dict[str, QDoubleSpinBox] = {}
        self.wind_widgets: Dict[str, QSpinBox] = {}
        self.category_widgets: Dict[str, Dict] = {}
        self.preview_text: Optional[QTextEdit] = None
        
        self._setup_dialog()
        self._init_ui()
        self._load_current_profile()
        self._register_for_theming()
        
        logger.info("🎨 AnomalySettingsDialog inicializálva")
    
    def _setup_dialog(self) -> None:
        """Dialog alapbeállítások."""
        self.setWindowTitle("⚙️ Anomália Beállítások")
        self.setModal(True)
        self.resize(800, 600)
        self.setMinimumSize(600, 400)
        
        # Window icon és flags
        self.setWindowFlags(
            Qt.Dialog | 
            Qt.WindowTitleHint | 
            Qt.WindowCloseButtonHint |
            Qt.WindowMaximizeButtonHint
        )
    
    def _init_ui(self) -> None:
        """UI felépítése."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Fejléc (cím + profil választó)
        header_section = self._create_header_section()
        layout.addWidget(header_section)
        
        # Fő tartalom (tab widget)
        main_tabs = self._create_main_tabs()
        layout.addWidget(main_tabs)
        
        # Gombok (mentés, mégse, alkalmazás)
        buttons_section = self._create_buttons_section()
        layout.addWidget(buttons_section)
    
    def _create_header_section(self) -> QWidget:
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
        profile_section = self._create_profile_section()
        layout.addWidget(profile_section)
        
        return container
    
    def _create_profile_section(self) -> QGroupBox:
        """Profil választó és menedzsment gombok."""
        group = QGroupBox("📁 Profilok")
        layout = QHBoxLayout(group)
        
        # Profil dropdown
        layout.addWidget(QLabel("Aktív profil:"))
        
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(150)
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        layout.addWidget(self.profile_combo)
        
        # Profil menedzsment gombok
        new_btn = QPushButton("🆕 Új")
        new_btn.setToolTip("Új profil létrehozása")
        new_btn.clicked.connect(self._create_new_profile)
        layout.addWidget(new_btn)
        
        edit_btn = QPushButton("✏️ Szerk")
        edit_btn.setToolTip("Profil átnevezése")
        edit_btn.clicked.connect(self._edit_profile_name)
        layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Törlés")
        delete_btn.setToolTip("Profil törlése")
        delete_btn.clicked.connect(self._delete_profile)
        layout.addWidget(delete_btn)
        
        return group
    
    def _create_main_tabs(self) -> QTabWidget:
        """Főbb beállítási tab-ok."""
        tabs = QTabWidget()
        
        # 1. Küszöbértékek tab
        thresholds_tab = self._create_thresholds_tab()
        tabs.addTab(thresholds_tab, "🌡️ Küszöbértékek")
        
        # 2. Kategóriák tab
        categories_tab = self._create_categories_tab()
        tabs.addTab(categories_tab, "🏷️ Kategóriák")
        
        # 3. Előnézet tab
        preview_tab = self._create_preview_tab()
        tabs.addTab(preview_tab, "👁️ Előnézet")
        
        return tabs
    
    def _create_thresholds_tab(self) -> QWidget:
        """Küszöbértékek beállítása tab."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        
        # Hőmérséklet szekció
        temp_section = self._create_temperature_section()
        layout.addWidget(temp_section)
        
        # Csapadék szekció
        precip_section = self._create_precipitation_section()
        layout.addWidget(precip_section)
        
        # Szél szekció
        wind_section = self._create_wind_section()
        layout.addWidget(wind_section)
        
        layout.addStretch()
        
        return container
    
    def _create_temperature_section(self) -> QGroupBox:
        """🌡️ Hőmérséklet küszöbök szekció."""
        group = QGroupBox("🌡️ Hőmérséklet Küszöbök")
        layout = QFormLayout(group)
        
        # Meleg küszöb
        hot_spinbox = QDoubleSpinBox()
        hot_spinbox.setRange(-50.0, 60.0)
        hot_spinbox.setSuffix(" °C")
        hot_spinbox.setDecimals(1)
        hot_spinbox.setValue(AnomalyConstants.TEMP_HOT_THRESHOLD)
        hot_spinbox.valueChanged.connect(self._on_setting_changed)
        self.temp_widgets["hot"] = hot_spinbox
        layout.addRow("🔥 Meleg küszöb:", hot_spinbox)
        
        # Hideg küszöb
        cold_spinbox = QDoubleSpinBox()
        cold_spinbox.setRange(-50.0, 40.0)
        cold_spinbox.setSuffix(" °C")
        cold_spinbox.setDecimals(1)
        cold_spinbox.setValue(AnomalyConstants.TEMP_COLD_THRESHOLD)
        cold_spinbox.valueChanged.connect(self._on_setting_changed)
        self.temp_widgets["cold"] = cold_spinbox
        layout.addRow("❄️ Hideg küszöb:", cold_spinbox)
        
        # Infó label
        info_label = QLabel("💡 Meleg küszöb felett 'forró', hideg alatt 'fagyos' kategória.")
        info_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        layout.addRow("", info_label)
        
        return group
    
    def _create_precipitation_section(self) -> QGroupBox:
        """🌧️ Csapadék küszöbök szekció."""
        group = QGroupBox("🌧️ Csapadék Küszöbök")
        layout = QFormLayout(group)
        
        # Magas küszöb
        high_spinbox = QDoubleSpinBox()
        high_spinbox.setRange(0.0, 500.0)
        high_spinbox.setSuffix(" mm")
        high_spinbox.setDecimals(1)
        high_spinbox.setValue(AnomalyConstants.PRECIP_HIGH_THRESHOLD)
        high_spinbox.valueChanged.connect(self._on_setting_changed)
        self.precip_widgets["high"] = high_spinbox
        layout.addRow("🌊 Magas küszöb:", high_spinbox)
        
        # Alacsony küszöb
        low_spinbox = QDoubleSpinBox()
        low_spinbox.setRange(0.0, 50.0)
        low_spinbox.setSuffix(" mm")
        low_spinbox.setDecimals(1)
        low_spinbox.setValue(AnomalyConstants.PRECIP_LOW_THRESHOLD)
        low_spinbox.valueChanged.connect(self._on_setting_changed)
        self.precip_widgets["low"] = low_spinbox
        layout.addRow("🏜️ Alacsony küszöb:", low_spinbox)
        
        # Infó label
        info_label = QLabel("💡 Magas küszöb felett 'esős', alacsony alatt 'száraz' kategória.")
        info_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        layout.addRow("", info_label)
        
        return group
    
    def _create_wind_section(self) -> QGroupBox:
        """🌪️ Szél kategóriák szekció."""
        group = QGroupBox("🌪️ Szél Kategóriák")
        layout = QFormLayout(group)
        
        # Szeles küszöb
        windy_spinbox = QSpinBox()
        windy_spinbox.setRange(10, 200)
        windy_spinbox.setSuffix(" km/h")
        windy_spinbox.setValue(AnomalyConstants.WIND_HIGH_THRESHOLD)
        windy_spinbox.valueChanged.connect(self._on_setting_changed)
        self.wind_widgets["high"] = windy_spinbox
        layout.addRow("💨 Szeles küszöb:", windy_spinbox)
        
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
            spinbox.valueChanged.connect(self._on_setting_changed)
            self.wind_widgets[key] = spinbox
            
            icon = {"normal": "🌿", "strong": "🌬️", "extreme": "🌪️", "hurricane": "🌀"}[key]
            layout.addRow(f"{icon} {name}:", spinbox)
        
        # Infó label
        info_label = QLabel("💡 Szélsebesség kategóriák szélvihar elemzéshez.")
        info_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        layout.addRow("", info_label)
        
        return group
    
    def _create_categories_tab(self) -> QWidget:
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
        categories_grid = self._create_categories_grid()
        layout.addWidget(categories_grid)
        
        layout.addStretch()
        
        return container
    
    def _create_categories_grid(self) -> QWidget:
        """Kategóriák szerkesztése grid layout."""
        container = QWidget()
        layout = QGridLayout(container)
        layout.setSpacing(15)
        
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
            self.category_widgets[key] = {}
            
            # Kategória név (readonly)
            cat_label = QLabel(key.title())
            cat_label.setStyleSheet("padding: 4px; background: #f3f4f6; border-radius: 4px;")
            layout.addWidget(cat_label, row, 0)
            
            # Szerkeszthető név
            name_edit = QLineEdit(name)
            name_edit.textChanged.connect(self._on_setting_changed)
            self.category_widgets[key]["name"] = name_edit
            layout.addWidget(name_edit, row, 1)
            
            # Szín választó
            color_btn = QPushButton()
            color_btn.setFixedSize(40, 30)
            color_btn.setStyleSheet(f"background: {color}; border: 1px solid #ccc; border-radius: 4px;")
            color_btn.clicked.connect(lambda checked, k=key: self._choose_color(k))
            self.category_widgets[key]["color"] = color_btn
            self.category_widgets[key]["color_value"] = color
            layout.addWidget(color_btn, row, 2)
            
            # Ikon választó
            icon_btn = QPushButton(icon)
            icon_btn.setFixedSize(40, 30)
            icon_btn.clicked.connect(lambda checked, k=key: self._choose_icon(k))
            self.category_widgets[key]["icon"] = icon_btn
            layout.addWidget(icon_btn, row, 3)
            
            # Küszöb info (readonly)
            threshold_label = QLabel(threshold)
            threshold_label.setStyleSheet("padding: 4px; color: #6b7280;")
            layout.addWidget(threshold_label, row, 4)
        
        return container
    
    def _create_preview_tab(self) -> QWidget:
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
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(300)
        layout.addWidget(self.preview_text)
        
        # Teszt adatok szekció
        test_section = self._create_test_section()
        layout.addWidget(test_section)
        
        layout.addStretch()
        
        return container
    
    def _create_test_section(self) -> QGroupBox:
        """Teszt adatok szekció az előnézethez."""
        group = QGroupBox("🧪 Teszt Adatok")
        layout = QHBoxLayout(group)
        
        test_btn1 = QPushButton("🔥 Forró Nap Teszt")
        test_btn1.clicked.connect(lambda: self._run_test("hot_day"))
        layout.addWidget(test_btn1)
        
        test_btn2 = QPushButton("❄️ Hideg Nap Teszt")
        test_btn2.clicked.connect(lambda: self._run_test("cold_day"))
        layout.addWidget(test_btn2)
        
        test_btn3 = QPushButton("🌧️ Esős Nap Teszt")
        test_btn3.clicked.connect(lambda: self._run_test("rainy_day"))
        layout.addWidget(test_btn3)
        
        test_btn4 = QPushButton("🌪️ Viharos Nap Teszt")
        test_btn4.clicked.connect(lambda: self._run_test("windy_day"))
        layout.addWidget(test_btn4)
        
        return group
    
    def _create_buttons_section(self) -> QWidget:
        """Alsó gombok szekció."""
        container = QWidget()
        layout = QHBoxLayout(container)
        
        # Bal oldali gombok
        reset_btn = QPushButton("🔄 Alapértelmezett")
        reset_btn.setToolTip("Jelenlegi profil visszaállítása alapértékekre")
        reset_btn.clicked.connect(self._reset_to_defaults)
        layout.addWidget(reset_btn)
        
        layout.addStretch()
        
        # Jobb oldali gombok
        apply_btn = QPushButton("✅ Alkalmaz")
        apply_btn.setToolTip("Beállítások alkalmazása mentés nélkül")
        apply_btn.clicked.connect(self._apply_settings)
        layout.addWidget(apply_btn)
        
        save_btn = QPushButton("💾 Mentés")
        save_btn.setToolTip("Beállítások mentése és alkalmazása")
        save_btn.clicked.connect(self._save_and_apply)
        layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Mégse")
        cancel_btn.setToolTip("Módosítások elvetése")
        cancel_btn.clicked.connect(self._cancel_changes)
        layout.addWidget(cancel_btn)
        
        return container
    
    def _register_for_theming(self) -> None:
        """Widget-ek regisztrálása témakezéléshez."""
        register_widget_for_theming(self, "container")
        
        # További widget regisztrálások itt...
        logger.debug("AnomalySettingsDialog - Widgets regisztrálva témakezéléshez")
    
    # ===== EVENT HANDLERS =====
    
    def _on_profile_changed(self, profile_name: str) -> None:
        """Profil váltás eseménykezelő."""
        if profile_name and profile_name != self.current_profile:
            self.current_profile = profile_name
            self._load_profile_settings(profile_name)
            self.profile_changed.emit(profile_name)
            logger.info(f"Profil váltva: {profile_name}")
    
    def _on_setting_changed(self) -> None:
        """Beállítás változás eseménykezelő."""
        self.unsaved_changes = True
        self.preview_timer.start(500)  # 500ms delay a preview frissítéshez
    
    def _choose_color(self, category_key: str) -> None:
        """Szín választó dialog."""
        current_color = self.category_widgets[category_key]["color_value"]
        color = QColorDialog.getColor(QColor(current_color), self, f"Szín választás - {category_key}")
        
        if color.isValid():
            hex_color = color.name()
            self.category_widgets[category_key]["color_value"] = hex_color
            self.category_widgets[category_key]["color"].setStyleSheet(
                f"background: {hex_color}; border: 1px solid #ccc; border-radius: 4px;"
            )
            self._on_setting_changed()
    
    def _choose_icon(self, category_key: str) -> None:
        """Ikon választó (egyszerű emoji lista)."""
        icons = ["🌱", "⚠️", "🚨", "💀", "🔥", "❄️", "🌧️", "🌪️", "☀️", "⛅", "🌈", "⚡"]
        
        # Egyszerű ikon választó dialog
        from PySide6.QtWidgets import QInputDialog
        icon, ok = QInputDialog.getItem(
            self, 
            f"Ikon választás - {category_key}", 
            "Válassz ikont:", 
            icons, 
            0, 
            False
        )
        
        if ok and icon:
            self.category_widgets[category_key]["icon"].setText(icon)
            self._on_setting_changed()
    
    def _run_test(self, test_type: str) -> None:
        """Teszt futtatása az előnézetben."""
        test_data = {
            "hot_day": {"temp_max": 42.5, "temp_min": 28.0, "precipitation": 0.0, "wind_speed": 15.0},
            "cold_day": {"temp_max": -15.0, "temp_min": -25.0, "precipitation": 5.0, "wind_speed": 35.0},
            "rainy_day": {"temp_max": 22.0, "temp_min": 16.0, "precipitation": 125.0, "wind_speed": 25.0},
            "windy_day": {"temp_max": 18.0, "temp_min": 12.0, "precipitation": 2.0, "wind_speed": 85.0}
        }
        
        data = test_data.get(test_type, {})
        self._simulate_anomaly_detection(data)
    
    def _simulate_anomaly_detection(self, test_data: Dict[str, float]) -> None:
        """Anomália detektálás szimulálása a teszt adatokkal."""
        current_settings = self._get_current_settings()
        
        results = []
        
        # Hőmérséklet teszt
        temp_max = test_data.get("temp_max", 20.0)
        if temp_max > current_settings["temp_hot"]:
            results.append(f"🔥 FORRÓ: {temp_max}°C > {current_settings['temp_hot']}°C")
        elif temp_max < current_settings["temp_cold"]:
            results.append(f"❄️ HIDEG: {temp_max}°C < {current_settings['temp_cold']}°C")
        else:
            results.append(f"🌡️ NORMÁLIS: {temp_max}°C")
        
        # Csapadék teszt
        precip = test_data.get("precipitation", 0.0)
        if precip > current_settings["precip_high"]:
            results.append(f"🌊 ESŐS: {precip}mm > {current_settings['precip_high']}mm")
        elif precip < current_settings["precip_low"]:
            results.append(f"🏜️ SZÁRAZ: {precip}mm < {current_settings['precip_low']}mm")
        else:
            results.append(f"🌧️ NORMÁLIS: {precip}mm")
        
        # Szél teszt
        wind = test_data.get("wind_speed", 0.0)
        if wind > current_settings["wind_hurricane"]:
            results.append(f"🌀 ORKÁN: {wind}km/h")
        elif wind > current_settings["wind_extreme"]:
            results.append(f"🌪️ EXTRÉM: {wind}km/h")
        elif wind > current_settings["wind_strong"]:
            results.append(f"🌬️ ERŐS: {wind}km/h")
        elif wind > current_settings["wind_normal"]:
            results.append(f"💨 MÉRSÉKELT: {wind}km/h")
        else:
            results.append(f"🌿 CSENDES: {wind}km/h")
        
        # Eredmények megjelenítése
        self.preview_text.setText("\n".join(results))
    
    # ===== PROFILE MANAGEMENT =====
    
    def _load_current_profile(self) -> None:
        """Aktuális profil betöltése."""
        profiles = self.profile_manager.get_available_profiles()
        
        self.profile_combo.clear()
        self.profile_combo.addItems(profiles)
        
        current = self.profile_manager.get_active_profile()
        if current in profiles:
            self.profile_combo.setCurrentText(current)
            self.current_profile = current
        
        self._load_profile_settings(self.current_profile)
    
    def _load_profile_settings(self, profile_name: str) -> None:
        """Profil beállítások betöltése a UI-ba."""
        settings = self.profile_manager.load_profile(profile_name)
        
        # Hőmérséklet
        self.temp_widgets["hot"].setValue(settings.get("temp_hot", 35.0))
        self.temp_widgets["cold"].setValue(settings.get("temp_cold", -10.0))
        
        # Csapadék
        self.precip_widgets["high"].setValue(settings.get("precip_high", 100.0))
        self.precip_widgets["low"].setValue(settings.get("precip_low", 5.0))
        
        # Szél
        self.wind_widgets["high"].setValue(settings.get("wind_high", 70))
        self.wind_widgets["normal"].setValue(settings.get("wind_normal", 50))
        self.wind_widgets["strong"].setValue(settings.get("wind_strong", 70))
        self.wind_widgets["extreme"].setValue(settings.get("wind_extreme", 100))
        self.wind_widgets["hurricane"].setValue(settings.get("wind_hurricane", 120))
        
        self.unsaved_changes = False
        self._update_preview()
        
        logger.info(f"Profil beállítások betöltve: {profile_name}")
    
    def _get_current_settings(self) -> Dict[str, Any]:
        """Aktuális UI beállítások összegyűjtése."""
        return {
            "temp_hot": self.temp_widgets["hot"].value(),
            "temp_cold": self.temp_widgets["cold"].value(),
            "precip_high": self.precip_widgets["high"].value(),
            "precip_low": self.precip_widgets["low"].value(),
            "wind_high": self.wind_widgets["high"].value(),
            "wind_normal": self.wind_widgets["normal"].value(),
            "wind_strong": self.wind_widgets["strong"].value(),
            "wind_extreme": self.wind_widgets["extreme"].value(),
            "wind_hurricane": self.wind_widgets["hurricane"].value()
        }
    
    def _create_new_profile(self) -> None:
        """Új profil létrehozása."""
        from PySide6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, "Új Profil", "Profil neve:")
        if ok and name.strip():
            if self.profile_manager.create_profile(name.strip()):
                self._load_current_profile()
                self.profile_combo.setCurrentText(name.strip())
                logger.info(f"Új profil létrehozva: {name}")
            else:
                QMessageBox.warning(self, "Hiba", f"Profil '{name}' már létezik!")
    
    def _edit_profile_name(self) -> None:
        """Profil átnevezése."""
        if self.current_profile == "default":
            QMessageBox.information(self, "Info", "Az alapértelmezett profil nem nevezhető át!")
            return
        
        from PySide6.QtWidgets import QInputDialog
        
        new_name, ok = QInputDialog.getText(self, "Profil Átnevezése", "Új név:", text=self.current_profile)
        if ok and new_name.strip() and new_name.strip() != self.current_profile:
            if self.profile_manager.rename_profile(self.current_profile, new_name.strip()):
                self._load_current_profile()
                self.profile_combo.setCurrentText(new_name.strip())
                logger.info(f"Profil átnevezve: {self.current_profile} → {new_name}")
            else:
                QMessageBox.warning(self, "Hiba", f"Profil '{new_name}' már létezik!")
    
    def _delete_profile(self) -> None:
        """Profil törlése."""
        if self.current_profile == "default":
            QMessageBox.information(self, "Info", "Az alapértelmezett profil nem törölhető!")
            return
        
        reply = QMessageBox.question(
            self, 
            "Profil Törlése", 
            f"Biztosan törölni szeretnéd a '{self.current_profile}' profilt?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.profile_manager.delete_profile(self.current_profile):
                self._load_current_profile()
                logger.info(f"Profil törölve: {self.current_profile}")
            else:
                QMessageBox.warning(self, "Hiba", "Profil törlése sikertelen!")
    
    # ===== SAVE/LOAD/APPLY =====
    
    def _update_preview(self) -> None:
        """Előnézet frissítése."""
        settings = self._get_current_settings()
        
        preview_text = f"""
🎯 AKTUÁLIS BEÁLLÍTÁSOK:

🌡️ HŐMÉRSÉKLET:
• Forró küszöb: > {settings['temp_hot']}°C
• Hideg küszöb: < {settings['temp_cold']}°C

🌧️ CSAPADÉK:
• Magas küszöb: > {settings['precip_high']}mm
• Alacsony küszöb: < {settings['precip_low']}mm

🌪️ SZÉL KATEGÓRIÁK:
• Szeles küszöb: > {settings['wind_high']}km/h
• Normális: < {settings['wind_normal']}km/h
• Erős: {settings['wind_normal']}-{settings['wind_strong']}km/h
• Extrém: {settings['wind_strong']}-{settings['wind_extreme']}km/h
• Orkán: > {settings['wind_hurricane']}km/h

📁 Aktív profil: {self.current_profile}
{"⚠️ Nem mentett változások!" if self.unsaved_changes else "✅ Mentett állapot"}
        """
        
        if self.preview_text:
            self.preview_text.setText(preview_text.strip())
    
    def _reset_to_defaults(self) -> None:
        """Alapértelmezett értékek visszaállítása."""
        reply = QMessageBox.question(
            self,
            "Alapértelmezett Visszaállítás",
            "Biztos visszaállítod az alapértelmezett értékeket?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.profile_manager.reset_profile_to_defaults(self.current_profile)
            self._load_profile_settings(self.current_profile)
            logger.info(f"Profil visszaállítva alapértelmezettre: {self.current_profile}")
    
    def _apply_settings(self) -> None:
        """Beállítások alkalmazása mentés nélkül."""
        settings = self._get_current_settings()
        self.settings_changed.emit(settings)
        logger.info("Beállítások alkalmazva (mentés nélkül)")
    
    def _save_and_apply(self) -> None:
        """Beállítások mentése és alkalmazása."""
        settings = self._get_current_settings()
        
        if self.profile_manager.save_profile(self.current_profile, settings):
            self.profile_manager.set_active_profile(self.current_profile)
            self.settings_changed.emit(settings)
            self.unsaved_changes = False
            self._update_preview()
            
            QMessageBox.information(self, "Siker", f"Beállítások mentve a '{self.current_profile}' profilba!")
            logger.info(f"Beállítások mentve és alkalmazva: {self.current_profile}")
        else:
            QMessageBox.warning(self, "Hiba", "Beállítások mentése sikertelen!")
    
    def _cancel_changes(self) -> None:
        """Módosítások elvetése."""
        if self.unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Módosítások Elvetése",
                "Vannak nem mentett módosítások. Biztos elveted őket?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        self.reject()
    
    def closeEvent(self, event) -> None:
        """Dialog bezárás esemény."""
        self._cancel_changes()
        event.accept()


# 🧪 DEMO FUNKCIÓ
def demo_anomaly_settings_dialog():
    """Demo: Anomália beállítások dialog tesztelése."""
    import sys
    from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
    
    app = QApplication(sys.argv)
    
    main_window = QWidget()
    main_window.setWindowTitle("Anomália Beállítások Demo")
    main_window.resize(400, 200)
    
    layout = QVBoxLayout(main_window)
    
    open_btn = QPushButton("⚙️ Anomália Beállítások Megnyitása")
    
    def open_dialog():
        dialog = AnomalySettingsDialog(main_window)
        dialog.settings_changed.connect(lambda settings: print(f"🔧 Beállítások változtak: {settings}"))
        dialog.profile_changed.connect(lambda profile: print(f"📁 Profil váltva: {profile}"))
        dialog.exec()
    
    open_btn.clicked.connect(open_dialog)
    layout.addWidget(open_btn)
    
    main_window.show()
    
    return app.exec()


if __name__ == "__main__":
    demo_anomaly_settings_dialog()
