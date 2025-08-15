#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Control Panel Module (ANALYTICS MAP SYNC FIX!)
MVC kompatibilis vezérlő panel modul - ANALYTICS → MAP SYNC SIGNALOK HOZZÁADVA!

🚨 ANALYTICS → MAP SYNC FIX IMPLEMENTÁLVA:
✅ weather_parameters_changed = Signal(dict) - API settings, provider változások
✅ analysis_parameters_changed = Signal(dict) - Analysis típus, régió, megye változások  
✅ date_range_changed = Signal(str, str) - Dátum tartomány változások
✅ parameters_bundle_changed = Signal(dict) - Komplex paraméter csomag
✅ Helper metódusok: _get_current_*_parameters() implementálva
✅ Signal emit hozzáadva minden kritikus változáshoz

🔧 KRITIKUS KISZÜRÜLÉSI BUG JAVÍTÁSOK:
✅ Signal loop megszakítás - blockSignals() használata
✅ State management repair - explicit reaktiválási logika 
✅ Event handler conflict resolution - disconnect/reconnect pattern
✅ Dropdown state tracking - _updating_state flag használata
✅ UI refresh cycle - force update after state changes
✅ Signal chain debugging - részletes logging minden kritikus ponton

🚀 MULTI-YEAR BATCH TÁMOGATÁS + 1 ÉV OPCIÓ MEGMARAD:
✅ Időtartam dropdown (1/5/10/25/55 év) - 1 év opció HOZZÁADVA
✅ 1 éves limit ELTÁVOLÍTVA
✅ weather_client.py v4.0 multi-year batch használata
✅ Automatikus dátum számítás dropdown alapján
✅ 55 éves trend elemzések támogatása
✅ Kompatibilitás a meglévő manual dátum picker-ekkel

🏞️ RÉGIÓ/MEGYE TÁMOGATÁS ÚJ FUNKCIÓK MEGMARADNAK:
✅ Új választó: Egyedi lokáció / Régió elemzés / Megye elemzés
✅ Magyar régiók dropdown (7 statisztikai régió)
✅ Magyar megyék dropdown (19 megye + Budapest)
✅ Multi-city batch lekérdezés régióhoz/megyéhez
✅ Analytics bypass - közvetlen térkép frissítés
✅ city_results formátum generálása térképhez
✅ Régiónkénti/megyénkénti aggregált adatok

🔧 LAYOUT & RESPONSIVENESS JAVÍTÁSOK MEGMARADNAK:
✅ Panel width constraints optimalizálva (320-450px)
✅ Widget spacing és margins javítva
✅ Button sizing és responsiveness javítva  
✅ GroupBox sizing optimalizálva
✅ UniversalLocationSelector layout constraints javítva
✅ Fetch button signal chain debug és javítás
✅ Layout overflow problémák megoldva
✅ Modern spacing és padding használata

🛠️ RÉGIÓ SIGNAL JAVÍTÁS:
✅ region_selection_changed = Signal(str) hozzáadva
✅ region_selection_changed.emit(region) hozzáadva _on_region_changed_safe()-hez
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QHBoxLayout, QGroupBox,
    QLineEdit, QComboBox, QPushButton, QDateEdit, QLabel,
    QCheckBox, QSpinBox, QProgressBar, QRadioButton, QButtonGroup,
    QSizePolicy, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QDate, Signal, QTimer, QSize
from PySide6.QtGui import QFont

from ..config import APIConfig, GUIConfig, ProviderConfig, UserPreferences, UsageTracker
from .utils import GUIConstants
from .workers.data_fetch_worker import WorkerManager
from .theme_manager import get_theme_manager, register_widget_for_theming
from .universal_location_selector import UniversalLocationSelector
from ..data.city_manager import CityManager
from ..data.models import UniversalLocation


class ControlPanel(QWidget):
    """
    🚨 ANALYTICS → MAP SYNC FIX + 🔧 KISZÜRÜLÉSI BUG FIX + 🚀 MULTI-YEAR BATCH TÁMOGATÁS + 🏞️ RÉGIÓ/MEGYE TÁMOGATÁS + LAYOUT & RESPONSIVENESS JAVÍTOTT MVC kompatibilis vezérlő panel.
    
    🚨 ANALYTICS → MAP SYNC FIX EBBEN A VERZIÓBAN:
    - weather_parameters_changed signal - API settings, provider változások
    - analysis_parameters_changed signal - Analysis típus, régió, megye változások  
    - date_range_changed signal - Dátum tartomány változások
    - parameters_bundle_changed signal - Komplex paraméter csomag
    - Helper metódusok minden paraméter típushoz
    - Signal emit minden kritikus változásnál
    
    🔧 KRITIKUS KISZÜRÜLÉSI BUG JAVÍTÁSOK EBBEN A VERZIÓBAN:
    - Signal loop megszakítás blockSignals() használatával
    - State management repair explicit reaktiválási logikával  
    - Event handler conflict resolution disconnect/reconnect pattern-nel
    - Dropdown state tracking _updating_state flag használatával
    - UI refresh cycle force update after state changes
    - Signal chain debugging részletes logging minden kritikus ponton
    
    🚀 MULTI-YEAR BATCH TÁMOGATÁS + 1 ÉV OPCIÓ MEGMARAD:
    - Időtartam dropdown (1/5/10/25/55 év) - 1 év opció HOZZÁADVA
    - 1 éves limit ELTÁVOLÍTVA
    - weather_client.py v4.0 multi-year batch használata  
    - Automatikus dátum számítás dropdown alapján
    - Manual dátum választás továbbra is elérhető
    - 55 éves klimatológiai elemzések támogatása
    - Rate limit optimalizált batch-elés
    
    🏞️ RÉGIÓ/MEGYE TÁMOGATÁS ÚJ FUNKCIÓK MEGMARADNAK:
    - Elemzési típus választó: Egyedi lokáció / Régió elemzés / Megye elemzés
    - Magyar statisztikai régiók: 7 régió (Közép-Magyarország, stb.)
    - Magyar közigazgatási megyék: 19 megye + Budapest
    - Multi-city batch lekérdezés automatikus koordináta gyűjtéssel
    - Analytics View bypass - közvetlen Hungarian Map Tab frissítés
    - city_results formátum: [{'name': 'Város', 'lat': lat, 'lon': lon, 'value': érték}]
    - Régiónkénti/megyénkénti aggregált weather statisztikák
    
    🔧 LAYOUT & RESPONSIVENESS JAVÍTÁSOK MEGMARADNAK:
    - Panel width constraints optimalizálva (320-450px)
    - Widget spacing és margins professzionálisan beállítva
    - Button sizing és responsiveness problémák javítva
    - GroupBox sizing és overflow problémák megoldva
    - UniversalLocationSelector layout constraints optimalizálva
    - Fetch button signal chain debug és javítás
    - Layout overflow és scrolling problémák megoldva
    - Modern spacing használata (12px, 16px, 20px)
    
    🛠️ RÉGIÓ SIGNAL JAVÍTÁS:
    - region_selection_changed = Signal(str) hozzáadva a kimenő signalokhoz
    - region_selection_changed.emit(region) hozzáadva _on_region_changed_safe()-hez
    - Hungarian Map Tab frissítés támogatása régiókiválasztás esetén
    """
    
    # === KIMENŐ SIGNALOK A CONTROLLER FELÉ ===
    
    # Settlement keresés (kompatibilitás)
    search_requested = Signal(str)  # search_query
    
    # Settlement kiválasztás (kompatibilitás)
    city_selected = Signal(str, float, float, dict)  # name, lat, lon, metadata
    
    # 🌍 ÚJ - UniversalLocation kiválasztás
    location_changed = Signal(object)  # UniversalLocation objektum
    
    # 🚀 FRISSÍTETT - Időjárási adatok lekérdezése MULTI-YEAR BATCH támogatással
    weather_data_requested = Signal(float, float, str, str, dict)  # lat, lon, start_date, end_date, params
    
    # 🏞️ ÚJ - Régió/megye multi-city lekérdezés
    multi_city_weather_requested = Signal(str, str, str, str, dict)  # analysis_type, region_id, start_date, end_date, params
    
    # 🛠️ JAVÍTÁS - Régió kiválasztás signal Hungarian Map Tab frissítéshez
    region_selection_changed = Signal(str)  # selected_region
    
    # === 🚨 ANALYTICS → MAP SYNC SIGNALOK ===
    
    # Weather paraméterek változás (API settings, provider)
    weather_parameters_changed = Signal(dict)  # API settings, provider változások
    
    # Analysis paraméterek változás (típus, régió, megye, lokáció)
    analysis_parameters_changed = Signal(dict)  # Analysis típus, régió, megye változások
    
    # Dátum tartomány változás
    date_range_changed = Signal(str, str)  # start_date, end_date
    
    # Komplex paraméter csomag változás (minden paraméter egyben)
    parameters_bundle_changed = Signal(dict)  # Comprehensive bundle minden paraméterrel
    
    # ✅ PROVIDER SELECTOR SIGNALOK
    provider_changed = Signal(str)  # provider_name ("auto", "open-meteo", "meteostat")
    provider_preferences_updated = Signal(dict)  # updated_preferences
    
    # === EGYÉB SIGNALOK ===
    
    # Helyi hibák (validációs hibák stb.)
    local_error_occurred = Signal(str)  # error_message
    
    def __init__(self, worker_manager: WorkerManager, parent: Optional[QWidget] = None):
        """
        🚨 ANALYTICS → MAP SYNC FIX + 🔧 KISZÜRÜLÉSI BUG FIX + 🚀 MULTI-YEAR BATCH TÁMOGATÁS + 🏞️ RÉGIÓ/MEGYE TÁMOGATÁS + LAYOUT & RESPONSIVENESS JAVÍTOTT vezérlő panel inicializálása.
        
        Args:
            worker_manager: Háttérszálak kezelője (kompatibilitás miatt)
            parent: Szülő widget
        """
        super().__init__(parent)
        
        # Worker manager referencia
        self.worker_manager = worker_manager
        
        # === 🌍 CITYMANGER AUTOMATIKUS INICIALIZÁLÁS ===
        self.city_manager = CityManager()
        
        # === PROFESSZIONÁLIS THEMEMANAGER INICIALIZÁLÁSA ===
        self.theme_manager = get_theme_manager()
        
        # === ÁLLAPOT VÁLTOZÓK ===
        
        # 🌍 UniversalLocation objektum tárolás
        self.current_location: Optional[UniversalLocation] = None
        self.current_city_data: Optional[Dict[str, Any]] = None  # 🔧 JAVÍTÁS: Kompatibilitás
        
        # 🏞️ RÉGIÓ/MEGYE elemzés állapot
        self.analysis_type: str = "single_location"  # "single_location", "region", "county"
        self.selected_region: Optional[str] = None
        self.selected_county: Optional[str] = None
        
        # UI állapot
        self.is_fetching = False
        
        # 🔧 KRITIKUS KISZÜRÜLÉSI BUG FIX: State management flags
        self._updating_state = False  # Flag to prevent signal loops
        self._ui_initialized = False  # Flag to ensure proper initialization order
        
        # ✅ PROVIDER SELECTOR állapot
        self.current_provider: str = "auto"
        self.usage_data: Dict[str, Any] = {}
        self.provider_preferences: Dict[str, Any] = {}
        
        # 🚀 MULTI-YEAR BATCH állapot
        self.date_mode: str = "time_range"  # "time_range" vagy "manual_dates"
        
        # === UI ELEMEK ===
        
        # ✅ PROVIDER SELECTOR Timer
        self.usage_update_timer = QTimer()
        self.usage_update_timer.timeout.connect(self._update_usage_display)
        self.usage_update_timer.start(30000)  # 30 seconds interval
        
        # UI inicializálása
        self._init_ui()
        self._setup_default_values()
        self._connect_internal_signals()
        
        # ✅ PROVIDER SELECTOR inicializálás
        self._load_provider_preferences()
        self._update_usage_display()
        
        # === PROFESSZIONÁLIS THEMEMANAGER REGISZTRÁCIÓ ===
        self._register_widgets_for_theming()
        
        # 🔧 KRITIKUS: UI inicializálás befejezve flag
        self._ui_initialized = True
        
        print("🚨 DEBUG: ControlPanel ANALYTICS → MAP SYNC FIX + KISZÜRÜLÉSI BUG FIX + MULTI-YEAR BATCH + RÉGIÓ/MEGYE TÁMOGATÁS + LAYOUT & RESPONSIVENESS JAVÍTOTT verzió kész")
    
    def _init_ui(self) -> None:
        """🚨 ANALYTICS → MAP SYNC FIX + 🔧 KISZÜRÜLÉSI BUG FIX + 🚀 MULTI-YEAR BATCH + 🏞️ RÉGIÓ/MEGYE + LAYOUT & RESPONSIVENESS JAVÍTOTT UI elemek inicializálása."""
        
        # 🔧 KRITIKUS: PANEL SIZE POLICY ÉS CONSTRAINTS
        self.setMinimumWidth(320)
        self.setMaximumWidth(450)
        self.setMinimumHeight(700)
        
        # 🔧 EXPLICIT SIZE POLICY
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        # === 🔧 SCROLL AREA WRAPPER LAYOUT OVERFLOW KEZELÉSHEZ ===
        
        # Scroll area létrehozása
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Scroll content widget
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        
        # Main layout a scroll area-hoz
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
        # Content layout
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)
        
        # 🏞️ Elemzési típus választó panel
        analysis_type_group = self._create_analysis_type_group()
        layout.addWidget(analysis_type_group)
        
        # 🌍 UNIVERSAL LOCATION SELECTOR panel (csak single_location módban)
        self.location_group = self._create_universal_location_group()
        layout.addWidget(self.location_group)
        
        # 🏞️ Régió/megye választó panel (csak region/county módban)
        self.region_county_group = self._create_region_county_group()
        layout.addWidget(self.region_county_group)
        
        # 🚀 MULTI-YEAR BATCH: Időtartam kiválasztás panel (FRISSÍTETT 1 ÉV OPCIÓVAL!)
        time_range_group = self._create_time_range_group()
        layout.addWidget(time_range_group)
        
        # Dátum kiválasztás panel (FRISSÍTETT - opcionális manual mode)
        date_group = self._create_date_group()
        layout.addWidget(date_group)
        
        # ✅ PROVIDER SELECTOR panel
        provider_group = self._create_provider_selector_group()
        layout.addWidget(provider_group)
        
        # API beállítások panel (csökkentett funkciókkal)
        api_group = self._create_api_settings_group()
        layout.addWidget(api_group)
        
        # Lekérdezés vezérlés panel
        query_group = self._create_query_control_group()
        layout.addWidget(query_group)
        
        # Állapot panel
        status_group = self._create_status_group()
        layout.addWidget(status_group)
        
        # Rugalmas hely a panel alján
        layout.addStretch()
        
        print(f"🚨 DEBUG: ControlPanel ANALYTICS → MAP SYNC FIX + KISZÜRÜLÉSI BUG FIX + MULTI-YEAR BATCH + RÉGIÓ/MEGYE + LAYOUT JAVÍTVA - size: {self.minimumWidth()}-{self.maximumWidth()}px, scroll enabled")
    
    def _create_analysis_type_group(self) -> QGroupBox:
        """
        🏞️ Elemzési típus választó widget csoport létrehozása.
        """
        group = QGroupBox("🎯 Elemzési Típus")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(12)
        
        # Radio button group
        self.analysis_type_button_group = QButtonGroup()
        
        # Egyedi lokáció radio
        self.single_location_radio = QRadioButton("📍 Egyedi lokáció elemzés")
        self.single_location_radio.setChecked(True)
        self.single_location_radio.setToolTip("Egy konkrét település részletes időjárási elemzése")
        self.single_location_radio.setMinimumHeight(24)
        self.analysis_type_button_group.addButton(self.single_location_radio, 0)
        layout.addWidget(self.single_location_radio)
        
        # Régió elemzés radio
        self.region_radio = QRadioButton("🏞️ Régió elemzés (Multi-City)")
        self.region_radio.setToolTip("Magyar statisztikai régiók összehasonlító elemzése")
        self.region_radio.setMinimumHeight(24)
        self.analysis_type_button_group.addButton(self.region_radio, 1)
        layout.addWidget(self.region_radio)
        
        # Megye elemzés radio
        self.county_radio = QRadioButton("🏛️ Megye elemzés (Multi-City)")
        self.county_radio.setToolTip("Magyar megyék összehasonlító elemzése")
        self.county_radio.setMinimumHeight(24)
        self.analysis_type_button_group.addButton(self.county_radio, 2)
        layout.addWidget(self.county_radio)
        
        # 🔧 KISZÜRÜLÉSI BUG FIX: Analysis type change signal - VÉDETT VERZIÓ
        self.analysis_type_button_group.buttonClicked.connect(self._on_analysis_type_changed_safe)
        
        # 🔧 GROUPBOX SIZE CONSTRAINTS
        group.setMinimumHeight(110)
        group.setMaximumHeight(130)
        
        return group
    
    def _create_universal_location_group(self) -> QGroupBox:
        """
        🌍 UNIVERSAL LOCATION SELECTOR widget csoport létrehozása - LAYOUT JAVÍTÁSSAL.
        """
        group = QGroupBox("🌍 Lokáció Választó")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(12)
        
        # 🌍 UNIVERSAL LOCATION SELECTOR komponens
        self.universal_location_selector = UniversalLocationSelector(self.city_manager, self)
        
        # 🔧 KRITIKUS: SIZE CONSTRAINTS A UNIVERSAL LOCATION SELECTOR-RA
        self.universal_location_selector.setMinimumHeight(420)
        self.universal_location_selector.setMaximumHeight(500)
        self.universal_location_selector.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout.addWidget(self.universal_location_selector)
        
        # Kiválasztott lokáció információ megjelenítése
        info_layout = QHBoxLayout()
        info_layout.setSpacing(8)
        
        self.location_info_label = QLabel("Válasszon lokációt...")
        self.location_info_label.setWordWrap(True)
        self.location_info_label.setMinimumHeight(40)
        info_layout.addWidget(self.location_info_label)
        
        # Clear gomb
        self.clear_location_btn = QPushButton("🗑️")
        self.clear_location_btn.clicked.connect(self._clear_location)
        self.clear_location_btn.setEnabled(False)
        self.clear_location_btn.setFixedSize(32, 32)
        self.clear_location_btn.setToolTip("Lokáció törlése")
        info_layout.addWidget(self.clear_location_btn)
        
        layout.addLayout(info_layout)
        
        # 🔧 GROUPBOX SIZE CONSTRAINTS
        group.setMinimumHeight(500)
        group.setMaximumHeight(580)
        
        return group
    
    def _create_region_county_group(self) -> QGroupBox:
        """
        🏞️ Régió/megye választó widget csoport létrehozása - KISZÜRÜLÉSI BUG FIX VERZIÓVAL.
        """
        group = QGroupBox("🏞️ Régió/Megye Választó")
        layout = QFormLayout(group)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setVerticalSpacing(12)
        layout.setHorizontalSpacing(8)
        
        # Magyar statisztikai régiók dropdown
        self.region_combo = QComboBox()
        self.region_combo.addItems([
            "Közép-Magyarország",
            "Közép-Dunántúl", 
            "Nyugat-Dunántúl",
            "Dél-Dunántúl",
            "Észak-Magyarország",
            "Észak-Alföld",
            "Dél-Alföld"
        ])
        self.region_combo.setMinimumHeight(32)
        self.region_combo.setToolTip("Magyar statisztikai régiók választása multi-city elemzéshez")
        
        # 🔧 KISZÜRÜLÉSI BUG FIX: VÉDETT SIGNAL KAPCSOLAT
        self.region_combo.currentTextChanged.connect(self._on_region_changed_safe)
        
        layout.addRow("Régió:", self.region_combo)
        
        # Magyar megyék dropdown
        self.county_combo = QComboBox()
        self.county_combo.addItems([
            "Budapest",
            "Bács-Kiskun",
            "Baranya",
            "Békés",
            "Borsod-Abaúj-Zemplén",
            "Csongrád-Csanád",
            "Fejér",
            "Győr-Moson-Sopron",
            "Hajdú-Bihar",
            "Heves",
            "Jász-Nagykun-Szolnok",
            "Komárom-Esztergom",
            "Nógrád",
            "Pest",
            "Somogy",
            "Szabolcs-Szatmár-Bereg",
            "Tolna",
            "Vas",
            "Veszprém",
            "Zala"
        ])
        self.county_combo.setMinimumHeight(32)
        self.county_combo.setToolTip("Magyar megyék választása multi-city elemzéshez")
        
        # 🔧 KISZÜRÜLÉSI BUG FIX: VÉDETT SIGNAL KAPCSOLAT
        self.county_combo.currentTextChanged.connect(self._on_county_changed_safe)
        
        layout.addRow("Megye:", self.county_combo)
        
        # Info label
        self.region_county_info = QLabel("Régió/megye módban több város automatikus lekérdezése")
        self.region_county_info.setWordWrap(True)
        self.region_county_info.setMinimumHeight(40)
        layout.addRow("Info:", self.region_county_info)
        
        # 🔧 GROUPBOX SIZE CONSTRAINTS
        group.setMinimumHeight(140)
        group.setMaximumHeight(180)
        
        # Kezdetben elrejtve (single_location mode aktív)
        group.setVisible(False)
        
        return group
    
    def _create_time_range_group(self) -> QGroupBox:
        """
        🚀 MULTI-YEAR BATCH: Időtartam kiválasztás widget csoport létrehozása - 1 ÉV OPCIÓ HOZZÁADVA!
        """
        group = QGroupBox("⏰ Időtartam (Multi-Year)")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(12)
        
        # Mode selector radio buttons
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(16)
        
        self.time_range_radio = QRadioButton("Időtartam választó")
        self.time_range_radio.setChecked(True)
        self.time_range_radio.setToolTip("Automatikus dátum számítás időtartam alapján")
        self.time_range_radio.setMinimumHeight(24)
        mode_layout.addWidget(self.time_range_radio)
        
        self.manual_dates_radio = QRadioButton("Manuális dátumok")
        self.manual_dates_radio.setToolTip("Pontos dátumok kézi megadása")
        self.manual_dates_radio.setMinimumHeight(24)
        mode_layout.addWidget(self.manual_dates_radio)
        
        layout.addLayout(mode_layout)
        
        # Mode változás kezelése
        self.time_range_radio.toggled.connect(self._on_date_mode_changed)
        self.manual_dates_radio.toggled.connect(self._on_date_mode_changed)
        
        # 🚀 Időtartam dropdown (TrendAnalyticsTab kompatibilis + 1 ÉV HOZZÁADVA!)
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(8)
        
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems([
            "1 év",      # 🚀 ÚJ OPCIÓ HOZZÁADVA!
            "5 év",
            "10 év", 
            "25 év",
            "55 év (teljes)"
        ])
        self.time_range_combo.setCurrentText("1 év")  # 🚀 1 év alapértelmezett
        self.time_range_combo.setMinimumHeight(32)
        self.time_range_combo.setToolTip("Automatikus dátum számítás a mai naptól visszafelé")
        self.time_range_combo.currentTextChanged.connect(self._on_time_range_changed)
        
        form_layout.addRow("Időtartam:", self.time_range_combo)
        layout.addLayout(form_layout)
        
        # Info label a computed dátumokhoz
        self.computed_dates_info = QLabel("Számított időszak: 2024-07-25 → 2025-07-25")
        self.computed_dates_info.setWordWrap(True)
        self.computed_dates_info.setMinimumHeight(40)
        layout.addWidget(self.computed_dates_info)
        
        # 🔧 GROUPBOX SIZE CONSTRAINTS
        group.setMinimumHeight(140)
        group.setMaximumHeight(180)
        
        # Kezdeti számítás
        self._update_computed_dates()
        
        return group
    
    def _create_date_group(self) -> QGroupBox:
        """🚀 MULTI-YEAR BATCH + 🔧 LAYOUT JAVÍTOTT dátum kiválasztás widget csoport - FRISSÍTETT."""
        group = QGroupBox("📅 Manuális Dátumok (Opcionális)")
        layout = QFormLayout(group)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setVerticalSpacing(12)
        layout.setHorizontalSpacing(8)
        
        # Kezdő dátum
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setDate(QDate.currentDate().addYears(-1))  # 🚀 1 év alapértelmezett
        self.start_date.setMinimumHeight(32)
        layout.addRow("Kezdő dátum:", self.start_date)
        
        # Befejező dátum
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setMinimumHeight(32)
        layout.addRow("Befejező dátum:", self.end_date)
        
        # Gyors dátum beállítások - MULTI-YEAR BATCH FRISSÍTÉS
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(8)
        
        self.last_month_btn = QPushButton("Előző hónap")
        self.last_month_btn.clicked.connect(self._set_last_month)
        self.last_month_btn.setMinimumHeight(28)
        quick_layout.addWidget(self.last_month_btn)
        
        self.last_year_btn = QPushButton("Előző év")
        self.last_year_btn.clicked.connect(self._set_last_year)
        self.last_year_btn.setMinimumHeight(28)
        quick_layout.addWidget(self.last_year_btn)
        
        # 🚀 ÚJ: 1 év gyors gomb HOZZÁADVA
        self.last_1year_btn = QPushButton("1 év")
        self.last_1year_btn.clicked.connect(lambda: self._set_years_back(1))
        self.last_1year_btn.setMinimumHeight(28)
        quick_layout.addWidget(self.last_1year_btn)
        
        # 🚀 5 év gyors gomb
        self.last_5years_btn = QPushButton("5 év")
        self.last_5years_btn.clicked.connect(lambda: self._set_years_back(5))
        self.last_5years_btn.setMinimumHeight(28)
        quick_layout.addWidget(self.last_5years_btn)
        
        layout.addRow("Gyors:", quick_layout)
        
        # További multi-year gyors gombok
        quick_layout2 = QHBoxLayout()
        quick_layout2.setSpacing(8)
        
        self.last_10years_btn = QPushButton("10 év")
        self.last_10years_btn.clicked.connect(lambda: self._set_years_back(10))
        self.last_10years_btn.setMinimumHeight(28)
        quick_layout2.addWidget(self.last_10years_btn)
        
        self.last_25years_btn = QPushButton("25 év")
        self.last_25years_btn.clicked.connect(lambda: self._set_years_back(25))
        self.last_25years_btn.setMinimumHeight(28)
        quick_layout2.addWidget(self.last_25years_btn)
        
        self.last_55years_btn = QPushButton("55 év")
        self.last_55years_btn.clicked.connect(lambda: self._set_years_back(55))
        self.last_55years_btn.setMinimumHeight(28)
        quick_layout2.addWidget(self.last_55years_btn)
        
        layout.addRow("Multi-year:", quick_layout2)
        
        # 🔧 GROUPBOX SIZE CONSTRAINTS - KIBŐVÍTVE MULTI-YEAR GOMBOKNAK
        group.setMinimumHeight(160)
        group.setMaximumHeight(200)
        
        # Kezdetben disabled (time_range mode aktív)
        self._set_manual_dates_enabled(False)
        
        return group
    
    def _create_provider_selector_group(self) -> QGroupBox:
        """
        ✅ PROVIDER SELECTOR widget csoport létrehozása - LAYOUT JAVÍTÁSSAL.
        """
        group = QGroupBox("🎛️ Adatforrás Választó")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(12)
        
        # Provider radio buttons
        providers_layout = QVBoxLayout()
        providers_layout.setSpacing(8)
        
        # Button group for mutual exclusion
        self.provider_button_group = QButtonGroup()
        
        # Auto provider radio
        self.auto_radio = QRadioButton("🤖 Automatikus (Smart Routing)")
        self.auto_radio.setToolTip("Use-case alapú automatikus provider választás + multi-year batch")
        self.auto_radio.setMinimumHeight(24)
        self.provider_button_group.addButton(self.auto_radio, 0)
        providers_layout.addWidget(self.auto_radio)
        
        # Open-Meteo radio
        self.openmeteo_radio = QRadioButton("🌍 Open-Meteo (Ingyenes + Multi-Year)")
        self.openmeteo_radio.setToolTip("Ingyenes globális időjárási API 55 éves batch támogatással")
        self.openmeteo_radio.setMinimumHeight(24)
        self.provider_button_group.addButton(self.openmeteo_radio, 1)
        providers_layout.addWidget(self.openmeteo_radio)
        
        # Meteostat radio
        self.meteostat_radio = QRadioButton("💎 Meteostat (Prémium + 55+ év)")
        self.meteostat_radio.setToolTip("Prémium API 55+ éves történeti adatokkal ($10/hónap)")
        self.meteostat_radio.setMinimumHeight(24)
        self.provider_button_group.addButton(self.meteostat_radio, 2)
        providers_layout.addWidget(self.meteostat_radio)
        
        # Provider change signal
        self.provider_button_group.buttonClicked.connect(self._on_provider_changed)
        
        layout.addLayout(providers_layout)
        
        # Usage tracking display
        usage_group = QGroupBox("📊 API Használat")
        usage_layout = QVBoxLayout(usage_group)
        usage_layout.setContentsMargins(8, 12, 8, 8)
        usage_layout.setSpacing(8)
        
        # Meteostat usage display
        meteostat_layout = QHBoxLayout()
        meteostat_layout.setSpacing(8)
        
        self.meteostat_usage_label = QLabel("💎 Meteostat:")
        meteostat_layout.addWidget(self.meteostat_usage_label)
        
        self.meteostat_usage_value = QLabel("0/10000")
        meteostat_layout.addWidget(self.meteostat_usage_value)
        
        meteostat_layout.addStretch()
        usage_layout.addLayout(meteostat_layout)
        
        # Meteostat usage progress bar
        self.meteostat_usage_bar = QProgressBar()
        self.meteostat_usage_bar.setRange(0, 100)
        self.meteostat_usage_bar.setValue(0)
        self.meteostat_usage_bar.setTextVisible(True)
        self.meteostat_usage_bar.setFormat("%p%")
        self.meteostat_usage_bar.setMinimumHeight(20)
        self.meteostat_usage_bar.setMaximumHeight(24)
        usage_layout.addWidget(self.meteostat_usage_bar)
        
        # Cost display
        cost_layout = QHBoxLayout()
        cost_layout.setSpacing(8)
        
        self.cost_label = QLabel("💰 Havi költség:")
        cost_layout.addWidget(self.cost_label)
        
        self.cost_value = QLabel("$0.00")
        cost_layout.addWidget(self.cost_value)
        
        cost_layout.addStretch()
        usage_layout.addLayout(cost_layout)
        
        # Open-Meteo usage (informational) - FRISSÍTVE MULTI-YEAR INFÓVAL
        openmeteo_layout = QHBoxLayout()
        openmeteo_layout.setSpacing(8)
        
        self.openmeteo_usage_label = QLabel("🌍 Open-Meteo:")
        openmeteo_layout.addWidget(self.openmeteo_usage_label)
        
        self.openmeteo_usage_value = QLabel("Unlimited (Multi-Year)")
        openmeteo_layout.addWidget(self.openmeteo_usage_value)
        
        openmeteo_layout.addStretch()
        usage_layout.addLayout(openmeteo_layout)
        
        layout.addWidget(usage_group)
        
        # Usage warning label
        self.usage_warning_label = QLabel("")
        self.usage_warning_label.setWordWrap(True)
        self.usage_warning_label.setMinimumHeight(20)
        layout.addWidget(self.usage_warning_label)
        
        # 🔧 GROUPBOX SIZE CONSTRAINTS
        group.setMinimumHeight(220)
        group.setMaximumHeight(280)
        
        return group
    
    def _create_api_settings_group(self) -> QGroupBox:
        """🔧 LAYOUT JAVÍTOTT API beállítások widget csoport létrehozása."""
        group = QGroupBox("⚙️ API Beállítások")
        layout = QFormLayout(group)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setVerticalSpacing(10)
        layout.setHorizontalSpacing(8)
        
        # Időzóna automatikus detektálás
        self.auto_timezone = QCheckBox()
        self.auto_timezone.setChecked(True)
        self.auto_timezone.setMinimumHeight(20)
        layout.addRow("Automatikus időzóna:", self.auto_timezone)
        
        # Adatok gyorsítótárazása
        self.cache_data = QCheckBox()
        self.cache_data.setChecked(True)
        self.cache_data.setMinimumHeight(20)
        layout.addRow("Adatok cache-elése:", self.cache_data)
        
        # API timeout beállítás - MULTI-YEAR BATCH-hez optimalizált
        self.api_timeout = QSpinBox()
        self.api_timeout.setRange(30, 300)  # 🚀 NAGYOBB RANGE multi-year batch-hez
        self.api_timeout.setValue(60)  # 🚀 NAGYOBB DEFAULT (30→60s) multi-year batch-hez
        self.api_timeout.setSuffix(" másodperc")
        self.api_timeout.setMinimumHeight(28)
        self.api_timeout.setToolTip("Multi-year batch lekérdezésekhez nagyobb timeout ajánlott")
        layout.addRow("API timeout:", self.api_timeout)
        
        # 🔧 GROUPBOX SIZE CONSTRAINTS
        group.setMinimumHeight(120)
        group.setMaximumHeight(140)
        
        return group
    
    def _create_query_control_group(self) -> QGroupBox:
        """🔧 LAYOUT & RESPONSIVENESS JAVÍTOTT lekérdezés vezérlés widget csoport."""
        group = QGroupBox("🚀 Lekérdezés (Multi-Year + Régió/Megye)")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(10)
        
        # 🔧 KRITIKUS JAVÍTÁS: Lekérdezés gomb - RESPONSIVE SIZING
        self.fetch_button = QPushButton("📊 Adatok lekérdezése (Multi-Year)")
        self.fetch_button.clicked.connect(self._trigger_weather_fetch)
        self.fetch_button.setEnabled(False)  # 🔧 JAVÍTÁS: Kezdetben letiltva
        
        # 🔧 KRITIKUS: RESPONSIVE BUTTON SIZING
        self.fetch_button.setMinimumHeight(44)
        self.fetch_button.setMaximumHeight(48)
        self.fetch_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Gomb stílus kiemelése
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        self.fetch_button.setFont(font)
        
        layout.addWidget(self.fetch_button)
        
        # Lekérdezés megszakítás gomb
        self.cancel_button = QPushButton("❌ Megszakítás")
        self.cancel_button.clicked.connect(self._cancel_operations)
        self.cancel_button.setVisible(False)
        self.cancel_button.setMinimumHeight(36)
        self.cancel_button.setMaximumHeight(40)
        self.cancel_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.cancel_button)
        
        # 🔧 GROUPBOX SIZE CONSTRAINTS
        group.setMinimumHeight(100)
        group.setMaximumHeight(120)
        
        return group
    
    def _create_status_group(self) -> QGroupBox:
        """🔧 LAYOUT JAVÍTOTT állapot widget csoport létrehozása."""
        group = QGroupBox("📊 Állapot")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(10)
        
        # Állapot szöveg
        self.status_label = QLabel("Válasszon elemzési típust és lokációt a kezdéshez")
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(40)
        self.status_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.status_label)
        
        # Progressz bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(20)
        self.progress_bar.setMaximumHeight(24)
        layout.addWidget(self.progress_bar)
        
        # 🔧 GROUPBOX SIZE CONSTRAINTS
        group.setMinimumHeight(90)
        group.setMaximumHeight(110)
        
        return group
    
    # === 🚨 ANALYTICS → MAP SYNC HELPER METÓDUSOK ===
    
    def _get_current_analysis_parameters(self) -> Dict[str, Any]:
        """
        🚨 ANALYTICS → MAP SYNC: Jelenlegi analysis paraméterek lekérdezése.
        """
        params = {
            "analysis_type": self.analysis_type,
            "location": None,
            "region": None,
            "county": None
        }
        
        if self.analysis_type == "single_location" and self.current_city_data:
            params["location"] = {
                "name": self.current_city_data.get("name", ""),
                "latitude": self.current_city_data.get("latitude", 0.0),
                "longitude": self.current_city_data.get("longitude", 0.0),
                "display_name": self.current_city_data.get("display_name", "")
            }
        elif self.analysis_type == "region":
            params["region"] = self.selected_region or self.region_combo.currentText()
        elif self.analysis_type == "county":
            params["county"] = self.selected_county or self.county_combo.currentText()
        
        return params
    
    def _get_current_weather_parameters(self) -> Dict[str, Any]:
        """
        🚨 ANALYTICS → MAP SYNC: Jelenlegi weather paraméterek lekérdezése.
        """
        return {
            "provider": self.current_provider,
            "timeout": self.api_timeout.value(),
            "cache": self.cache_data.isChecked(),
            "timezone": "auto" if self.auto_timezone.isChecked() else "UTC"
        }
    
    def _get_current_date_parameters(self) -> Dict[str, Any]:
        """
        🚨 ANALYTICS → MAP SYNC: Jelenlegi date paraméterek lekérdezése.
        """
        start_date, end_date = self._get_effective_date_range()
        
        return {
            "mode": self.date_mode,
            "time_range": self.time_range_combo.currentText() if self.date_mode == "time_range" else None,
            "start_date": start_date,
            "end_date": end_date
        }
    
    def _get_all_parameters(self) -> Dict[str, Any]:
        """
        🚨 ANALYTICS → MAP SYNC: Comprehensive bundle minden paraméterrel.
        """
        return {
            "analysis": self._get_current_analysis_parameters(),
            "weather": self._get_current_weather_parameters(),
            "date": self._get_current_date_parameters(),
            "timestamp": datetime.now().isoformat()
        }
    
    # === 🔧 KISZÜRÜLÉSI BUG FIX - VÉDETT SIGNAL HANDLERS + 🚨 ANALYTICS → MAP SYNC EMIT ===
    
    def _on_analysis_type_changed_safe(self, button):
        """
        🚨 ANALYTICS → MAP SYNC + 🔧 KISZÜRÜLÉSI BUG FIX - Elemzési típus változás kezelése VÉDETT VERZIÓVAL + SIGNAL EMIT.
        """
        if self._updating_state or not self._ui_initialized:
            print("🔧 DEBUG: Analysis type change BLOCKED - updating state or not initialized")
            return
        
        try:
            print("🚨 DEBUG: _on_analysis_type_changed_safe triggered - ENTERING CRITICAL SECTION")
            
            # 🔧 KRITIKUS: State update flag beállítása
            self._updating_state = True
            
            # Új analysis type meghatározása
            if button == self.single_location_radio:
                new_type = "single_location"
            elif button == self.region_radio:
                new_type = "region"
            elif button == self.county_radio:
                new_type = "county"
            else:
                return
                
            if new_type != self.analysis_type:
                old_type = self.analysis_type
                self.analysis_type = new_type
                
                print(f"🚨 DEBUG: Analysis type changed from {old_type} to {new_type} - ANALYTICS → MAP SYNC VERSION")
                
                # UI elemek megjelenítése/elrejtése - SIGNAL BLOCKER VERZIÓVAL
                self._update_ui_for_analysis_type_with_signal_blocking()
                
                # Fetch button állapot frissítése
                self._update_fetch_button_state_safe()
                
                # Status frissítése
                self._update_status_for_analysis_type(new_type)
                
                # 🚨 ANALYTICS → MAP SYNC: Analysis parameters changed signal emit
                analysis_params = self._get_current_analysis_parameters()
                self.analysis_parameters_changed.emit(analysis_params)
                print(f"🚨 DEBUG: analysis_parameters_changed signal EMITTED: {analysis_params}")
                
                # 🚨 ANALYTICS → MAP SYNC: Bundle changed signal emit
                bundle = self._get_all_parameters()
                self.parameters_bundle_changed.emit(bundle)
                print(f"🚨 DEBUG: parameters_bundle_changed signal EMITTED after analysis type change")
                
        except Exception as e:
            print(f"❌ ERROR: Analysis type change SAFE handling error: {e}")
        finally:
            # 🔧 KRITIKUS: State update flag törlése
            self._updating_state = False
            print("🚨 DEBUG: _on_analysis_type_changed_safe - EXITING CRITICAL SECTION")
    
    def _on_region_changed_safe(self, region: str):
        """
        🚨 ANALYTICS → MAP SYNC + 🔧 KISZÜRÜLÉSI BUG FIX - Régió választás változás kezelése VÉDETT VERZIÓVAL + SIGNAL EMIT.
        🛠️ JAVÍTÁS: region_selection_changed signal emit hozzáadva.
        """
        if self._updating_state or not self._ui_initialized:
            print("🔧 DEBUG: Region change BLOCKED - updating state or not initialized")
            return
        
        if self.analysis_type != "region":
            print("🔧 DEBUG: Region change IGNORED - not in region mode")
            return
        
        try:
            print(f"🚨 DEBUG: _on_region_changed_safe triggered: {region} - ENTERING CRITICAL SECTION")
            
            # 🔧 KRITIKUS: State update flag beállítása
            self._updating_state = True
            
            self.selected_region = region
            print(f"🚨 DEBUG: Region selected SAFELY: {region}")
            
            # Fetch button állapot frissítése
            self._update_fetch_button_state_safe()
            
            # Status frissítése
            self._update_status(f"🏞️ Kiválasztott régió: {region}")
            
            # 🛠️ JAVÍTÁS: Region selection changed signal emit - Hungarian Map Tab frissítéshez
            self.region_selection_changed.emit(region)
            print(f"🛠️ DEBUG: region_selection_changed signal EMITTED: {region}")
            
            # 🚨 ANALYTICS → MAP SYNC: Analysis parameters changed signal emit
            analysis_params = self._get_current_analysis_parameters()
            self.analysis_parameters_changed.emit(analysis_params)
            print(f"🚨 DEBUG: analysis_parameters_changed signal EMITTED for region: {analysis_params}")
            
            # 🚨 ANALYTICS → MAP SYNC: Bundle changed signal emit
            bundle = self._get_all_parameters()
            self.parameters_bundle_changed.emit(bundle)
            print(f"🚨 DEBUG: parameters_bundle_changed signal EMITTED after region change")
            
        except Exception as e:
            print(f"❌ ERROR: Region change SAFE handling error: {e}")
        finally:
            # 🔧 KRITIKUS: State update flag törlése
            self._updating_state = False
            print("🚨 DEBUG: _on_region_changed_safe - EXITING CRITICAL SECTION")
    
    def _on_county_changed_safe(self, county: str):
        """
        🚨 ANALYTICS → MAP SYNC + 🔧 KISZÜRÜLÉSI BUG FIX - Megye választás változás kezelése VÉDETT VERZIÓVAL + SIGNAL EMIT.
        """
        if self._updating_state or not self._ui_initialized:
            print("🔧 DEBUG: County change BLOCKED - updating state or not initialized")
            return
        
        if self.analysis_type != "county":
            print("🔧 DEBUG: County change IGNORED - not in county mode")
            return
        
        try:
            print(f"🚨 DEBUG: _on_county_changed_safe triggered: {county} - ENTERING CRITICAL SECTION")
            
            # 🔧 KRITIKUS: State update flag beállítása
            self._updating_state = True
            
            self.selected_county = county
            print(f"🚨 DEBUG: County selected SAFELY: {county}")
            
            # Fetch button állapot frissítése
            self._update_fetch_button_state_safe()
            
            # Status frissítése
            self._update_status(f"🏛️ Kiválasztott megye: {county}")
            
            # 🚨 ANALYTICS → MAP SYNC: Analysis parameters changed signal emit
            analysis_params = self._get_current_analysis_parameters()
            self.analysis_parameters_changed.emit(analysis_params)
            print(f"🚨 DEBUG: analysis_parameters_changed signal EMITTED for county: {analysis_params}")
            
            # 🚨 ANALYTICS → MAP SYNC: Bundle changed signal emit
            bundle = self._get_all_parameters()
            self.parameters_bundle_changed.emit(bundle)
            print(f"🚨 DEBUG: parameters_bundle_changed signal EMITTED after county change")
            
        except Exception as e:
            print(f"❌ ERROR: County change SAFE handling error: {e}")
        finally:
            # 🔧 KRITIKUS: State update flag törlése
            self._updating_state = False
            print("🚨 DEBUG: _on_county_changed_safe - EXITING CRITICAL SECTION")
    
    def _on_location_selected_safe(self, name: str, lat: float, lon: float, data: Dict[str, Any]):
        """
        🚨 ANALYTICS → MAP SYNC + 🔧 KISZÜRÜLÉSI BUG FIX - lokáció kiválasztás kezelése SAFE VERZIÓVAL + SIGNAL EMIT.
        """
        if self._updating_state:
            print("🔧 DEBUG: Location selection BLOCKED - updating state")
            return
        
        try:
            print(f"🚨 DEBUG: _on_location_selected_safe called: {name} [{lat:.4f}, {lon:.4f}] - ENTERING CRITICAL SECTION")
            
            # 🔧 KRITIKUS: State update flag beállítása
            self._updating_state = True
            
            # current_city_data frissítése
            self.current_city_data = {
                "name": name,
                "latitude": lat,
                "longitude": lon,
                "display_name": name,
                **data
            }
            print(f"🚨 DEBUG: current_city_data FRISSÍTVE SAFELY: {self.current_city_data['name']}")
            
            # Lokáció info frissítése
            self._update_location_info(name, lat, lon)
            
            # Clear gomb engedélyezése
            self.clear_location_btn.setEnabled(True)
            
            # Signal továbbítása (kompatibilitás)
            self.city_selected.emit(name, lat, lon, data)
            
            # UI állapot frissítése
            self._update_status(f"Kiválasztva: {name}")
            
            # 🚨 ANALYTICS → MAP SYNC: Analysis parameters changed signal emit
            analysis_params = self._get_current_analysis_parameters()
            self.analysis_parameters_changed.emit(analysis_params)
            print(f"🚨 DEBUG: analysis_parameters_changed signal EMITTED for location: {analysis_params}")
            
            # 🚨 ANALYTICS → MAP SYNC: Bundle changed signal emit
            bundle = self._get_all_parameters()
            self.parameters_bundle_changed.emit(bundle)
            print(f"🚨 DEBUG: parameters_bundle_changed signal EMITTED after location selection")
            
            print(f"✅ DEBUG: Location selection ANALYTICS → MAP SYNC VERSION: {name}")
            
        except Exception as e:
            print(f"❌ DEBUG: Safe lokáció kiválasztási hiba: {e}")
            self.local_error_occurred.emit("Lokáció kiválasztási hiba")
        finally:
            # 🔧 KRITIKUS: State update flag törlése
            self._updating_state = False
            
            # Fetch button állapot frissítése
            self._update_fetch_button_state_safe()
            print("🚨 DEBUG: _on_location_selected_safe - EXITING CRITICAL SECTION")
    
    def _on_provider_changed(self, button) -> None:
        """
        🚨 ANALYTICS → MAP SYNC + ✅ PROVIDER SELECTOR - Provider radio button változás kezelése + SIGNAL EMIT.
        """
        try:
            # Új provider meghatározása
            if button == self.auto_radio:
                new_provider = "auto"
            elif button == self.openmeteo_radio:
                new_provider = "open-meteo"
            elif button == self.meteostat_radio:
                new_provider = "meteostat"
            else:
                return
            
            if new_provider != self.current_provider:
                self.current_provider = new_provider
                
                # Preferences mentése
                self._save_provider_preferences()
                
                # Signal kibocsátása Controller felé
                self.provider_changed.emit(new_provider)
                
                # UI frissítése
                self._update_status_for_provider_change(new_provider)
                
                # 🚨 ANALYTICS → MAP SYNC: Weather parameters changed signal emit
                weather_params = self._get_current_weather_parameters()
                self.weather_parameters_changed.emit(weather_params)
                print(f"🚨 DEBUG: weather_parameters_changed signal EMITTED for provider: {weather_params}")
                
                # 🚨 ANALYTICS → MAP SYNC: Bundle changed signal emit
                bundle = self._get_all_parameters()
                self.parameters_bundle_changed.emit(bundle)
                print(f"🚨 DEBUG: parameters_bundle_changed signal EMITTED after provider change")
                
                print(f"🚨 DEBUG: Provider changed to ANALYTICS → MAP SYNC VERSION: {new_provider}")
                
        except Exception as e:
            print(f"❌ ERROR: Provider change handling error: {e}")
    
    def _on_time_range_changed(self, time_range_text: str):
        """
        🚨 ANALYTICS → MAP SYNC + 🚀 MULTI-YEAR BATCH - Időtartam dropdown változás kezelése + SIGNAL EMIT.
        """
        print(f"🚨 DEBUG: _on_time_range_changed: {time_range_text}")
        
        if self.date_mode == "time_range":
            self._update_computed_dates()
            
            # 🚨 ANALYTICS → MAP SYNC: Date range changed signal emit
            start_date, end_date = self._get_effective_date_range()
            self.date_range_changed.emit(start_date, end_date)
            print(f"🚨 DEBUG: date_range_changed signal EMITTED: {start_date} → {end_date}")
            
            # 🚨 ANALYTICS → MAP SYNC: Bundle changed signal emit
            bundle = self._get_all_parameters()
            self.parameters_bundle_changed.emit(bundle)
            print(f"🚨 DEBUG: parameters_bundle_changed signal EMITTED after time range change")
        
        # Fetch button state frissítése
        self._update_fetch_button_state_safe()
    
    def _on_date_mode_changed(self):
        """
        🚨 ANALYTICS → MAP SYNC + 🚀 MULTI-YEAR BATCH - Dátum mód változás kezelése + SIGNAL EMIT.
        """
        if self.time_range_radio.isChecked():
            self.date_mode = "time_range"
            self._set_manual_dates_enabled(False)
            self._update_computed_dates()
            print("🚨 DEBUG: Date mode switched to: time_range")
        else:
            self.date_mode = "manual_dates"
            self._set_manual_dates_enabled(True)
            print("🚨 DEBUG: Date mode switched to: manual_dates")
        
        # 🚨 ANALYTICS → MAP SYNC: Date range changed signal emit
        start_date, end_date = self._get_effective_date_range()
        self.date_range_changed.emit(start_date, end_date)
        print(f"🚨 DEBUG: date_range_changed signal EMITTED for mode change: {start_date} → {end_date}")
        
        # 🚨 ANALYTICS → MAP SYNC: Bundle changed signal emit
        bundle = self._get_all_parameters()
        self.parameters_bundle_changed.emit(bundle)
        print(f"🚨 DEBUG: parameters_bundle_changed signal EMITTED after date mode change")
        
        # Fetch button state frissítése
        self._update_fetch_button_state_safe()
    
    def _validate_dates_safe(self) -> None:
        """🚨 ANALYTICS → MAP SYNC + 🔧 KISZÜRÜLÉSI BUG FIX - dátumok validálása SAFE VERZIÓVAL + SIGNAL EMIT."""
        if self._updating_state:
            print("🔧 DEBUG: Date validation BLOCKED - updating state")
            return
        
        start = self.start_date.date()
        end = self.end_date.date()
        
        if start > end:
            # Ha kezdő dátum nagyobb, automatikusan javítjuk
            if self.sender() == self.start_date:
                self.end_date.setDate(start)
            else:
                self.start_date.setDate(end)
        
        # 🚨 ANALYTICS → MAP SYNC: Date range changed signal emit (csak manual mode-ban)
        if self.date_mode == "manual_dates":
            start_date, end_date = self._get_effective_date_range()
            self.date_range_changed.emit(start_date, end_date)
            print(f"🚨 DEBUG: date_range_changed signal EMITTED for manual date validation: {start_date} → {end_date}")
            
            # 🚨 ANALYTICS → MAP SYNC: Bundle changed signal emit
            bundle = self._get_all_parameters()
            self.parameters_bundle_changed.emit(bundle)
            print(f"🚨 DEBUG: parameters_bundle_changed signal EMITTED after manual date validation")
        
        # 🔧 KRITIKUS: Fetch button állapot frissítése SAFE VERZIÓVAL
        self._update_fetch_button_state_safe()
    
    def _update_ui_for_analysis_type_with_signal_blocking(self):
        """
        🔧 KISZÜRÜLÉSI BUG FIX - UI elemek frissítése SIGNAL BLOCKING-gal.
        """
        print(f"🔧 DEBUG: _update_ui_for_analysis_type_with_signal_blocking called for: {self.analysis_type}")
        
        try:
            # 🔧 KRITIKUS: Signal blokkolás az összes dropdown-ra
            self.region_combo.blockSignals(True)
            self.county_combo.blockSignals(True)
            
            if self.analysis_type == "single_location":
                print("🔧 DEBUG: Activating single_location mode - WITH SIGNAL BLOCKING")
                
                # Location group megjelenítése és engedélyezése
                self.location_group.setVisible(True)
                self.location_group.setEnabled(True)
                
                # UniversalLocationSelector explicit reaktiválása
                self.universal_location_selector.setEnabled(True)
                self.universal_location_selector.setVisible(True)
                
                # Clear button state preservation
                if self.current_city_data:
                    self.clear_location_btn.setEnabled(True)
                
                # Region/county group elrejtése és letiltása
                self.region_county_group.setVisible(False)
                self.region_county_group.setEnabled(False)
                
                # 🔧 EXPLICIT DISABLE régió/megye combók
                self.region_combo.setEnabled(False)
                self.county_combo.setEnabled(False)
                
                # Fetch button text
                self.fetch_button.setText("📊 Adatok lekérdezése (Single Location)")
                
                print("✅ DEBUG: Single location mode ACTIVATED WITH SIGNAL BLOCKING")
                
            elif self.analysis_type == "region":
                print("🔧 DEBUG: Activating region mode - WITH SIGNAL BLOCKING")
                
                # Location group elrejtése és letiltása
                self.location_group.setVisible(False)
                self.location_group.setEnabled(False)
                
                # Region/county group megjelenítése és engedélyezése
                self.region_county_group.setVisible(True)
                self.region_county_group.setEnabled(True)
                
                # 🔧 EXPLICIT ENABLE/DISABLE combo állapotok
                self.region_combo.setEnabled(True)
                self.county_combo.setEnabled(False)
                
                # Fetch button text
                self.fetch_button.setText("📊 Régió elemzés (Multi-City)")
                
                print("✅ DEBUG: Region mode ACTIVATED WITH SIGNAL BLOCKING")
                
            elif self.analysis_type == "county":
                print("🔧 DEBUG: Activating county mode - WITH SIGNAL BLOCKING")
                
                # Location group elrejtése és letiltása
                self.location_group.setVisible(False)
                self.location_group.setEnabled(False)
                
                # Region/county group megjelenítése és engedélyezése
                self.region_county_group.setVisible(True)
                self.region_county_group.setEnabled(True)
                
                # 🔧 EXPLICIT ENABLE/DISABLE combo állapotok
                self.region_combo.setEnabled(False)
                self.county_combo.setEnabled(True)
                
                # Fetch button text
                self.fetch_button.setText("📊 Megye elemzés (Multi-City)")
                
                print("✅ DEBUG: County mode ACTIVATED WITH SIGNAL BLOCKING")
            
        except Exception as e:
            print(f"❌ ERROR: UI update with signal blocking error: {e}")
        finally:
            # 🔧 KRITIKUS: Signal blokkolás feloldása
            self.region_combo.blockSignals(False)
            self.county_combo.blockSignals(False)
            
            # 🔧 FORCE UI REFRESH
            self.update()
            self.repaint()
            
            print(f"🔧 DEBUG: UI for analysis type {self.analysis_type} UPDATED WITH SIGNAL BLOCKING - signals UNBLOCKED")
    
    def _update_fetch_button_state_safe(self) -> None:
        """🔧 KISZÜRÜLÉSI BUG FIX - Fetch button állapot frissítése VÉDETT VERZIÓVAL."""
        
        if self._updating_state:
            print("🔧 DEBUG: Fetch button state update BLOCKED - updating state")
            return
        
        try:
            # 🏞️ Elemzési típus alapú validáció
            if self.analysis_type == "single_location":
                has_location = self.current_city_data is not None
            elif self.analysis_type == "region":
                has_location = self.region_combo.currentText() != ""
            elif self.analysis_type == "county":
                has_location = self.county_combo.currentText() != ""
            else:
                has_location = False
            
            # Dátum validáció a kiválasztott mód alapján
            if self.date_mode == "time_range":
                has_valid_dates = True  # Dropdown mindig valid
            else:
                has_valid_dates = self.start_date.date() <= self.end_date.date()
            
            should_enable = has_location and has_valid_dates and not self.is_fetching
            
            print(f"🔧 DEBUG: _update_fetch_button_state_safe (KISZÜRÜLÉSI BUG FIX):")
            print(f"  analysis_type: {self.analysis_type}")
            print(f"  has_location: {has_location}")
            print(f"  date_mode: {self.date_mode}")
            print(f"  has_valid_dates: {has_valid_dates}")
            print(f"  is_fetching: {self.is_fetching}")
            print(f"  should_enable: {should_enable}")
            
            self.fetch_button.setEnabled(should_enable)
            
        except Exception as e:
            print(f"❌ ERROR: Safe fetch button state update error: {e}")
    
    # === 🏞️ RÉGIÓ/MEGYE ELEMZÉSI LOGIC ===
    
    def _update_status_for_analysis_type(self, analysis_type: str):
        """Status frissítése elemzési típus változás esetén."""
        if analysis_type == "single_location":
            message = "📍 Egyedi lokáció mód - válasszon egy települést részletes elemzéshez"
        elif analysis_type == "region":
            message = "🏞️ Régió elemzés mód - többváros összehasonlító elemzés"
        elif analysis_type == "county":
            message = "🏛️ Megye elemzés mód - megyénkénti többváros elemzés"
        else:
            message = "Válasszon elemzési típust"
        
        self._update_status(message)
    
    def _get_region_cities(self, region: str) -> List[Dict[str, Any]]:
        """
        🏞️ Régió fővárosainak/nagyvárosainak lekérdezése.
        """
        # Magyar statisztikai régiók főbb városai (reprezentatív minta)
        region_cities = {
            "Közép-Magyarország": [
                {"name": "Budapest", "lat": 47.4979, "lon": 19.0402},
                {"name": "Debrecen", "lat": 47.5316, "lon": 21.6273},
                {"name": "Szentendre", "lat": 47.6667, "lon": 19.0833},
                {"name": "Vác", "lat": 47.7756, "lon": 19.1347}
            ],
            "Közép-Dunántúl": [
                {"name": "Székesfehérvár", "lat": 47.1926, "lon": 18.4104},
                {"name": "Tatabánya", "lat": 47.5692, "lon": 18.3948},
                {"name": "Dunaújváros", "lat": 46.9628, "lon": 18.9395},
                {"name": "Komárom", "lat": 47.7433, "lon": 18.1264}
            ],
            "Nyugat-Dunántúl": [
                {"name": "Győr", "lat": 47.6875, "lon": 17.6504},
                {"name": "Sopron", "lat": 47.6833, "lon": 16.5833},
                {"name": "Szombathely", "lat": 47.2306, "lon": 16.6218},
                {"name": "Zalaegerszeg", "lat": 46.8403, "lon": 16.8468}
            ],
            "Dél-Dunántúl": [
                {"name": "Pécs", "lat": 46.0727, "lon": 18.2330},
                {"name": "Kaposvár", "lat": 46.3667, "lon": 17.8000},
                {"name": "Szekszárd", "lat": 46.3500, "lon": 18.7167},
                {"name": "Dombóvár", "lat": 46.3783, "lon": 18.1392}
            ],
            "Észak-Magyarország": [
                {"name": "Miskolc", "lat": 48.1034, "lon": 20.7784},
                {"name": "Eger", "lat": 47.9030, "lon": 20.3738},
                {"name": "Salgótarján", "lat": 48.1000, "lon": 19.8000},
                {"name": "Kazincbarcika", "lat": 48.2500, "lon": 20.6167}
            ],
            "Észak-Alföld": [
                {"name": "Debrecen", "lat": 47.5316, "lon": 21.6273},
                {"name": "Nyíregyháza", "lat": 47.9560, "lon": 21.7174},
                {"name": "Szolnok", "lat": 47.1833, "lon": 20.2000},
                {"name": "Békéscsaba", "lat": 46.6833, "lon": 21.1000}
            ],
            "Dél-Alföld": [
                {"name": "Szeged", "lat": 46.2530, "lon": 20.1414},
                {"name": "Kecskemét", "lat": 46.9069, "lon": 19.6856},
                {"name": "Békéscsaba", "lat": 46.6833, "lon": 21.1000},
                {"name": "Baja", "lat": 46.1833, "lon": 18.9667}
            ]
        }
        
        return region_cities.get(region, [])
    
    def _get_county_cities(self, county: str) -> List[Dict[str, Any]]:
        """
        🏞️ Megye főbb településeinek lekérdezése.
        """
        # Magyar megyék főbb települései (reprezentatív minta)
        county_cities = {
            "Budapest": [
                {"name": "Budapest", "lat": 47.4979, "lon": 19.0402}
            ],
            "Pest": [
                {"name": "Szentendre", "lat": 47.6667, "lon": 19.0833},
                {"name": "Vác", "lat": 47.7756, "lon": 19.1347},
                {"name": "Cegléd", "lat": 47.1736, "lon": 19.8008},
                {"name": "Gödöllő", "lat": 47.5972, "lon": 19.3669}
            ],
            "Bács-Kiskun": [
                {"name": "Kecskemét", "lat": 46.9069, "lon": 19.6856},
                {"name": "Baja", "lat": 46.1833, "lon": 18.9667},
                {"name": "Kiskunfélegyháza", "lat": 46.7167, "lon": 19.8500},
                {"name": "Kalocsa", "lat": 46.5333, "lon": 18.9833}
            ],
            "Csongrád-Csanád": [
                {"name": "Szeged", "lat": 46.2530, "lon": 20.1414},
                {"name": "Hódmezővásárhely", "lat": 46.4167, "lon": 20.3333}
            ]
        }
        
        return county_cities.get(county, [])
    
    # === 🚀 MULTI-YEAR BATCH LOGIC - 1 ÉV OPCIÓ ===
    
    def _set_manual_dates_enabled(self, enabled: bool):
        """Manual dátum chooser-ek engedélyezése/letiltása."""
        self.start_date.setEnabled(enabled)
        self.end_date.setEnabled(enabled)
        self.last_month_btn.setEnabled(enabled)
        self.last_year_btn.setEnabled(enabled)
        self.last_1year_btn.setEnabled(enabled)
        self.last_5years_btn.setEnabled(enabled)
        self.last_10years_btn.setEnabled(enabled)
        self.last_25years_btn.setEnabled(enabled)
        self.last_55years_btn.setEnabled(enabled)
        
        # Időtartam dropdown ellenkezője
        self.time_range_combo.setEnabled(not enabled)
    
    def _update_computed_dates(self):
        """
        🚀 Automatikus dátum számítás az időtartam dropdown alapján - 1 ÉV OPCIÓ HOZZÁADVA.
        """
        try:
            time_range_text = self.time_range_combo.currentText()
            
            # Évek számának kinyerése - 1 ÉV OPCIÓ HOZZÁADVA
            if "1 év" in time_range_text:
                years = 1  # 🚀 ÚJ OPCIÓ
            elif "55 év" in time_range_text:
                years = 55
            elif "25 év" in time_range_text:
                years = 25
            elif "10 év" in time_range_text:
                years = 10
            elif "5 év" in time_range_text:
                years = 5
            else:
                years = 1  # 🚀 Default fallback 1 évre változtatva
            
            # Dátumok számítása
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=years * 365)
            
            # Info label frissítése
            self.computed_dates_info.setText(
                f"Számított időszak: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')} ({years} év)"
            )
            
            print(f"🚀 DEBUG: Computed dates updated with 1 év support: {start_date} → {end_date} ({years} years)")
            
        except Exception as e:
            print(f"❌ DEBUG: Computed dates update error: {e}")
            self.computed_dates_info.setText("Dátum számítási hiba")
    
    def _get_effective_date_range(self) -> tuple[str, str]:
        """
        🚀 Effektív dátum tartomány lekérdezése aktuális mód alapján - 1 ÉV OPCIÓ TÁMOGATVA.
        """
        if self.date_mode == "time_range":
            # Automatikus számítás - 1 ÉV OPCIÓ HOZZÁADVA
            time_range_text = self.time_range_combo.currentText()
            
            if "1 év" in time_range_text:
                years = 1  # 🚀 ÚJ OPCIÓ
            elif "55 év" in time_range_text:
                years = 55
            elif "25 év" in time_range_text:
                years = 25
            elif "10 év" in time_range_text:
                years = 10
            elif "5 év" in time_range_text:
                years = 5
            else:
                years = 1  # 🚀 Default 1 évre változtatva
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=years * 365)
            
            return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        
        else:
            # Manual dátumok
            start_date = self.start_date.date().toString(Qt.ISODate)
            end_date = self.end_date.date().toString(Qt.ISODate)
            
            return start_date, end_date
    
    def _set_years_back(self, years: int):
        """
        🚀 N évet visszamenő dátum beállítása - 1 ÉV TÁMOGATÁSSAL.
        """
        today = QDate.currentDate()
        start = today.addYears(-years)
        end = today
        
        self.start_date.setDate(start)
        self.end_date.setDate(end)
        
        print(f"🚀 DEBUG: Set {years} years back (1 év támogatással): {start.toString()} → {end.toString()}")
    
    def _set_last_month(self):
        """Előző hónap beállítása."""
        today = QDate.currentDate()
        last_month = today.addMonths(-1)
        self.start_date.setDate(last_month)
        self.end_date.setDate(today)
    
    def _set_last_year(self):
        """Előző év beállítása."""
        today = QDate.currentDate()
        last_year = today.addYears(-1)
        self.start_date.setDate(last_year)
        self.end_date.setDate(today)
    
    # === WIDGET REGISZTRÁCIÓ ÉS THEMING ===
    
    def _register_widgets_for_theming(self) -> None:
        """
        Widget-ek regisztrálása ThemeManager-hez automatikus téma kezeléshez.
        """
        # === CONTAINER WIDGETS ===
        register_widget_for_theming(self, "container")
        
        # === 🏞️ RÉGIÓ/MEGYE ELEMZÉSI UI ELEMEK ===
        register_widget_for_theming(self.single_location_radio, "input")
        register_widget_for_theming(self.region_radio, "input")
        register_widget_for_theming(self.county_radio, "input")
        register_widget_for_theming(self.region_combo, "input")
        register_widget_for_theming(self.county_combo, "input")
        
        # === 🌍 UNIVERSAL LOCATION SELECTOR ===
        register_widget_for_theming(self.universal_location_selector, "container")
        register_widget_for_theming(self.clear_location_btn, "button")
        
        # === 🚀 MULTI-YEAR BATCH UI ELEMEK + 1 ÉV OPCIÓ ===
        register_widget_for_theming(self.time_range_radio, "input")
        register_widget_for_theming(self.manual_dates_radio, "input")
        register_widget_for_theming(self.time_range_combo, "input")
        register_widget_for_theming(self.last_1year_btn, "button")
        register_widget_for_theming(self.last_5years_btn, "button")
        register_widget_for_theming(self.last_10years_btn, "button")
        register_widget_for_theming(self.last_25years_btn, "button")
        register_widget_for_theming(self.last_55years_btn, "button")
        
        # === INPUT WIDGETS ===
        register_widget_for_theming(self.start_date, "input")
        register_widget_for_theming(self.end_date, "input")
        register_widget_for_theming(self.auto_timezone, "input")
        register_widget_for_theming(self.cache_data, "input")
        register_widget_for_theming(self.api_timeout, "input")
        
        # ✅ PROVIDER SELECTOR widgets
        register_widget_for_theming(self.auto_radio, "input")
        register_widget_for_theming(self.openmeteo_radio, "input")
        register_widget_for_theming(self.meteostat_radio, "input")
        register_widget_for_theming(self.meteostat_usage_bar, "container")
        
        # === BUTTON WIDGETS ===
        register_widget_for_theming(self.last_month_btn, "button")
        register_widget_for_theming(self.last_year_btn, "button")
        register_widget_for_theming(self.fetch_button, "button")
        register_widget_for_theming(self.cancel_button, "button")
        
        # === TEXT LABELS ===
        self._apply_professional_label_styling(self.location_info_label, "secondary")
        self._apply_professional_label_styling(self.status_label, "primary")
        self._apply_professional_label_styling(self.computed_dates_info, "secondary")
        self._apply_professional_label_styling(self.region_county_info, "secondary")
        
        # ✅ PROVIDER SELECTOR labels
        self._apply_professional_label_styling(self.meteostat_usage_label, "primary")
        self._apply_professional_label_styling(self.meteostat_usage_value, "primary")
        self._apply_professional_label_styling(self.cost_label, "primary")
        self._apply_professional_label_styling(self.cost_value, "primary")
        self._apply_professional_label_styling(self.openmeteo_usage_label, "primary")
        self._apply_professional_label_styling(self.openmeteo_usage_value, "success")
        self._apply_professional_label_styling(self.usage_warning_label, "secondary")
        
        # === PROGRESS BAR ===
        register_widget_for_theming(self.progress_bar, "container")
        
        print("🚨 DEBUG: ControlPanel ANALYTICS → MAP SYNC FIX + KISZÜRÜLÉSI BUG FIX + MULTI-YEAR BATCH + RÉGIÓ/MEGYE + LAYOUT JAVÍTVA - Professional ColorPalette integrálva")
    
    def _apply_professional_label_styling(self, label: QLabel, style_type: str) -> None:
        """
        🎨 PROFESSZIONÁLIS label styling alkalmazása ColorPalette API-val.
        """
        color_palette = self.theme_manager.get_color_scheme()
        if not color_palette:
            return
        
        # Professzionális color mapping
        if style_type == "secondary":
            color = color_palette.get_color("info", "light") or "#9ca3af"
            font_size = "11px"
        elif style_type == "error":
            color = color_palette.get_color("error", "base") or "#dc2626"
            font_size = "12px"
            font_weight = "bold"
        elif style_type == "success":
            color = color_palette.get_color("success", "base") or "#10b981"
            font_size = "12px"
            font_weight = "bold"
        elif style_type == "warning":
            color = color_palette.get_color("warning", "base") or "#f59e0b"
            font_size = "12px"
            font_weight = "bold"
        else:  # primary
            color = color_palette.get_color("primary", "base") or "#2563eb"
            font_size = "12px"
        
        # CSS generálás
        css_parts = [f"color: {color};", f"font-size: {font_size};"]
        
        if style_type in ["error", "success", "warning"]:
            css_parts.append("font-weight: bold;")
        
        css = f"QLabel {{ {' '.join(css_parts)} }}"
        label.setStyleSheet(css)
        
        register_widget_for_theming(label, "text")
    
    def _setup_default_values(self) -> None:
        """Alapértelmezett értékek beállítása."""
        # Dátumok validálása - SAFE VERZIÓVAL
        self.start_date.dateChanged.connect(self._validate_dates_safe)
        self.end_date.dateChanged.connect(self._validate_dates_safe)
        
        # 🔧 JAVÍTÁS: Kezdeti állapot
        self._update_fetch_button_state_safe()
        
        # ✅ PROVIDER SELECTOR default values
        self._load_provider_preferences()
        
        # 🏞️ Elemzési típus kezdeti állapot - BUG FIX VERZIÓVAL
        self._update_ui_for_analysis_type_with_signal_blocking()
        
        print("🚨 DEBUG: Default values ANALYTICS → MAP SYNC FIX + KISZÜRÜLÉSI BUG FIX + MULTI-YEAR BATCH + RÉGIÓ/MEGYE - fetch button state tracking")
    
    def _connect_internal_signals(self) -> None:
        """🚨 ANALYTICS → MAP SYNC FIX + 🔧 KISZÜRÜLÉSI BUG FIX - belső signal-slot kapcsolatok VÉDETT VERZIÓVAL."""
        # Lokális hibák kezelése
        self.local_error_occurred.connect(self._show_local_error)
        
        # 🔧 KRITIKUS JAVÍTÁS: UNIVERSAL LOCATION SELECTOR signal kapcsolatok
        print("🚨 DEBUG: Connecting ANALYTICS → MAP SYNC FIX UniversalLocationSelector signals...")
        
        # Search signal
        self.universal_location_selector.search_requested.connect(self.search_requested.emit)
        print("✅ DEBUG: UniversalLocationSelector.search_requested → ControlPanel.search_requested CONNECTED")
        
        # 🔧 KRITIKUS: City selection signal - SAFE VERZIÓ
        self.universal_location_selector.city_selected.connect(self._on_location_selected_safe)
        print("✅ DEBUG: UniversalLocationSelector.city_selected → ControlPanel._on_location_selected_safe CONNECTED")
        
        # 🔧 KRITIKUS: Location change signal - SAFE VERZIÓ  
        self.universal_location_selector.location_changed.connect(self._on_location_changed_safe)
        print("✅ DEBUG: UniversalLocationSelector.location_changed → ControlPanel._on_location_changed_safe CONNECTED")
        
        # === PROFESSZIONÁLIS THEMEMANAGER SIGNAL KAPCSOLATOK ===
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        
        if hasattr(self.theme_manager, 'color_scheme_updated'):
            self.theme_manager.color_scheme_updated.connect(self._on_color_scheme_updated)
        
        print("🚨 DEBUG: ANALYTICS → MAP SYNC FIX + KISZÜRÜLÉSI BUG FIX + MULTI-YEAR BATCH + RÉGIÓ/MEGYE signal connections kész")
    
    def _on_theme_changed(self, theme_name: str) -> None:
        """🎨 PROFESSZIONÁLIS téma változás kezelése."""
        print(f"🎨 DEBUG: ControlPanel ANALYTICS → MAP SYNC FIX theme change: {theme_name}")
        
        # Label-ek újra-stílusozása
        self._apply_professional_label_styling(self.location_info_label, "secondary")
        self._apply_professional_label_styling(self.status_label, "primary")
        self._apply_professional_label_styling(self.computed_dates_info, "secondary")
        self._apply_professional_label_styling(self.region_county_info, "secondary")
        
        # ✅ PROVIDER SELECTOR labels újra-stílusozása
        self._refresh_provider_selector_styling()
    
    def _on_color_scheme_updated(self, color_palette) -> None:
        """🎨 PROFESSZIONÁLIS ColorPalette változás kezelése."""
        print("🎨 DEBUG: ControlPanel ANALYTICS → MAP SYNC FIX ColorPalette updated")
        
        # Összes styling újra-alkalmazása
        self._apply_professional_label_styling(self.location_info_label, "secondary")
        self._apply_professional_label_styling(self.status_label, "primary")
        self._apply_professional_label_styling(self.computed_dates_info, "secondary")
        self._apply_professional_label_styling(self.region_county_info, "secondary")
        self._refresh_provider_selector_styling()
    
    # === 🔧 KISZÜRÜLÉSI BUG FIX - SAFE UNIVERSAL LOCATION SELECTOR LOGIC ===
    
    def _on_location_changed_safe(self, location: UniversalLocation):
        """
        🚨 ANALYTICS → MAP SYNC + 🔧 KISZÜRÜLÉSI BUG FIX - UniversalLocation objektum változás kezelése SAFE VERZIÓVAL + SIGNAL EMIT.
        """
        if self._updating_state:
            print("🔧 DEBUG: Location change BLOCKED - updating state")
            return
        
        try:
            print(f"🚨 DEBUG: _on_location_changed_safe called: {location} - ENTERING CRITICAL SECTION")
            
            # 🔧 KRITIKUS: State update flag beállítása
            self._updating_state = True
            
            # UniversalLocation tárolása
            self.current_location = location
            
            # current_city_data frissítése UniversalLocation-ből
            if hasattr(location, 'identifier') and hasattr(location, 'coordinates'):
                self.current_city_data = {
                    "name": location.identifier,
                    "latitude": location.coordinates[0],
                    "longitude": location.coordinates[1],
                    "display_name": getattr(location, 'display_name', location.identifier),
                    "location_type": getattr(location, 'type', 'city'),
                    "country": getattr(location, 'country', ''),
                    "region": getattr(location, 'region', '')
                }
                print(f"🚨 DEBUG: current_city_data frissítve UniversalLocation-ből SAFELY: {self.current_city_data['name']}")
            
            # Signal továbbítása
            self.location_changed.emit(location)
            
            # 🚨 ANALYTICS → MAP SYNC: Analysis parameters changed signal emit
            analysis_params = self._get_current_analysis_parameters()
            self.analysis_parameters_changed.emit(analysis_params)
            print(f"🚨 DEBUG: analysis_parameters_changed signal EMITTED for UniversalLocation: {analysis_params}")
            
            # 🚨 ANALYTICS → MAP SYNC: Bundle changed signal emit
            bundle = self._get_all_parameters()
            self.parameters_bundle_changed.emit(bundle)
            print(f"🚨 DEBUG: parameters_bundle_changed signal EMITTED after UniversalLocation change")
            
            print(f"✅ DEBUG: UniversalLocation change ANALYTICS → MAP SYNC VERSION: {location}")
            
        except Exception as e:
            print(f"❌ DEBUG: Safe UniversalLocation változás hiba: {e}")
        finally:
            # 🔧 KRITIKUS: State update flag törlése
            self._updating_state = False
            
            # Fetch button állapot frissítése
            self._update_fetch_button_state_safe()
            print("🚨 DEBUG: _on_location_changed_safe - EXITING CRITICAL SECTION")
    
    def _update_location_info(self, name: str, lat: float, lon: float):
        """Lokáció információ megjelenítés frissítése."""
        info_text = f"📍 {name}\n🗺️ Koordináták: [{lat:.4f}, {lon:.4f}]"
        self.location_info_label.setText(info_text)
        self._apply_professional_label_styling(self.location_info_label, "primary")
    
    def _clear_location(self):
        """🚨 ANALYTICS → MAP SYNC + 🔧 KISZÜRÜLÉSI BUG FIX - lokáció kiválasztás törlése SAFE VERZIÓVAL + SIGNAL EMIT."""
        if self._updating_state:
            print("🔧 DEBUG: Location clear BLOCKED - updating state")
            return
        
        try:
            print("🚨 DEBUG: _clear_location called - ENTERING CRITICAL SECTION")
            
            # 🔧 KRITIKUS: State update flag beállítása
            self._updating_state = True
            
            # UniversalLocationSelector törlése
            self.universal_location_selector.clear_selection()
            
            # Lokális állapot törlése
            self.current_location = None
            self.current_city_data = None
            print("🚨 DEBUG: current_city_data TÖRÖLVE SAFELY")
            
            # UI elemek visszaállítása
            self.location_info_label.setText("Válasszon lokációt...")
            self._apply_professional_label_styling(self.location_info_label, "secondary")
            self.clear_location_btn.setEnabled(False)
            
            self._update_status("Válasszon lokációt a kezdéshez")
            
            # 🚨 ANALYTICS → MAP SYNC: Analysis parameters changed signal emit
            analysis_params = self._get_current_analysis_parameters()
            self.analysis_parameters_changed.emit(analysis_params)
            print(f"🚨 DEBUG: analysis_parameters_changed signal EMITTED for location clear: {analysis_params}")
            
            # 🚨 ANALYTICS → MAP SYNC: Bundle changed signal emit
            bundle = self._get_all_parameters()
            self.parameters_bundle_changed.emit(bundle)
            print(f"🚨 DEBUG: parameters_bundle_changed signal EMITTED after location clear")
            
            print("✅ DEBUG: Lokáció törlése ANALYTICS → MAP SYNC VERSION")
            
        except Exception as e:
            print(f"❌ DEBUG: Safe lokáció törlési hiba: {e}")
        finally:
            # 🔧 KRITIKUS: State update flag törlése
            self._updating_state = False
            
            # Fetch button állapot frissítése
            self._update_fetch_button_state_safe()
            print("🚨 DEBUG: _clear_location - EXITING CRITICAL SECTION")
    
    # === ✅ PROVIDER SELECTOR LOGIC ===
    
    def _load_provider_preferences(self) -> None:
        """Provider preferences betöltése és UI frissítése."""
        try:
            self.provider_preferences = UserPreferences.load_provider_preferences()
            self.current_provider = self.provider_preferences.get("selected_provider", "auto")
            
            # Radio button állapot beállítása
            if self.current_provider == "auto":
                self.auto_radio.setChecked(True)
            elif self.current_provider == "open-meteo":
                self.openmeteo_radio.setChecked(True)
            elif self.current_provider == "meteostat":
                self.meteostat_radio.setChecked(True)
            
            print(f"🎛️ Provider preferences loaded: {self.current_provider}")
            
        except Exception as e:
            print(f"❌ Error loading provider preferences: {e}")
            self.current_provider = "auto"
            self.auto_radio.setChecked(True)
    
    def _save_provider_preferences(self) -> None:
        """Provider preferences mentése."""
        try:
            self.provider_preferences["selected_provider"] = self.current_provider
            success = UserPreferences.save_provider_preferences(self.provider_preferences)
            
            if success:
                print(f"✅ Provider preferences saved: {self.current_provider}")
            else:
                print("❌ Failed to save provider preferences")
                
        except Exception as e:
            print(f"❌ Error saving provider preferences: {e}")
    
    def _update_status_for_provider_change(self, provider: str) -> None:
        """Státusz frissítése provider változás esetén."""
        provider_info = ProviderConfig.PROVIDERS.get(provider, {})
        provider_name = provider_info.get("name", provider)
        
        if provider == "auto":
            message = f"✅ Automatikus routing aktív - smart provider választás + multi-year batch"
        elif provider == "open-meteo":
            message = f"🌍 Open-Meteo aktív - ingyenes globális API + 55 éves batch"
        elif provider == "meteostat":
            message = f"💎 Meteostat aktív - prémium API + 55+ éves batch ($10/hónap)"
        else:
            message = f"📡 Provider: {provider_name}"
        
        self._update_status(message)
    
    def _update_usage_display(self) -> None:
        """Usage tracking display frissítése."""
        try:
            # Usage adatok betöltése
            self.usage_data = UsageTracker.get_usage_summary()
            
            # Meteostat usage update
            meteostat_requests = self.usage_data.get("meteostat_requests", 0)
            meteostat_limit = self.usage_data.get("meteostat_limit", 10000)
            meteostat_percentage = self.usage_data.get("meteostat_percentage", 0.0)
            meteostat_cost = self.usage_data.get("meteostat_cost", 0.0)
            
            # Usage value update
            self.meteostat_usage_value.setText(f"{meteostat_requests}/{meteostat_limit}")
            
            # Progress bar update
            self.meteostat_usage_bar.setValue(int(meteostat_percentage))
            
            # Cost display update
            self.cost_value.setText(f"${meteostat_cost:.2f}")
            
            # Open-Meteo update (informational)
            openmeteo_requests = self.usage_data.get("openmeteo_requests", 0)
            if openmeteo_requests > 0:
                self.openmeteo_usage_value.setText(f"{openmeteo_requests} (Free + Multi-Year)")
            else:
                self.openmeteo_usage_value.setText("Unlimited (Multi-Year)")
            
            # Warning level check
            warning_level = self.usage_data.get("warning_level", "normal")
            self._update_usage_warning(warning_level, meteostat_percentage)
            
            # Progress bar color based on usage
            self._update_usage_bar_styling(warning_level)
            
        except Exception as e:
            print(f"❌ Error updating usage display: {e}")
    
    def _update_usage_warning(self, warning_level: str, percentage: float) -> None:
        """Usage warning frissítése."""
        if warning_level == "critical":
            warning_text = f"🚨 KRITIKUS: {percentage:.1f}% Meteostat használat! Közel a havi limithez."
            self._apply_professional_label_styling(self.usage_warning_label, "error")
        elif warning_level == "warning":
            warning_text = f"⚠️ FIGYELEM: {percentage:.1f}% Meteostat használat. Havi limit közeledik."
            self._apply_professional_label_styling(self.usage_warning_label, "warning")
        else:
            days_remaining = self.usage_data.get("days_remaining", 30)
            warning_text = f"ℹ️ {days_remaining} nap maradt a hónapból (Multi-Year batch elérhető)"
            self._apply_professional_label_styling(self.usage_warning_label, "secondary")
        
        self.usage_warning_label.setText(warning_text)
    
    def _update_usage_bar_styling(self, warning_level: str) -> None:
        """Usage progress bar színezésének frissítése."""
        color_palette = self.theme_manager.get_color_scheme()
        if not color_palette:
            return
        
        if warning_level == "critical":
            bar_color = color_palette.get_color("error", "base") or "#dc2626"
        elif warning_level == "warning":
            bar_color = color_palette.get_color("warning", "base") or "#f59e0b"
        else:
            bar_color = color_palette.get_color("success", "base") or "#10b981"
        
        css = f"""
        QProgressBar {{
            border: 1px solid #ccc;
            border-radius: 4px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {bar_color};
            border-radius: 3px;
        }}
        """
        self.meteostat_usage_bar.setStyleSheet(css)
    
    def _refresh_provider_selector_styling(self) -> None:
        """Provider Selector összes styling frissítése."""
        # Label styling refresh
        self._apply_professional_label_styling(self.meteostat_usage_label, "primary")
        self._apply_professional_label_styling(self.meteostat_usage_value, "primary")
        self._apply_professional_label_styling(self.cost_label, "primary")
        self._apply_professional_label_styling(self.cost_value, "primary")
        self._apply_professional_label_styling(self.openmeteo_usage_label, "primary")
        self._apply_professional_label_styling(self.openmeteo_usage_value, "success")
        self._update_usage_warning_styling()
    
    def _update_usage_warning_styling(self) -> None:
        """Usage warning styling frissítése téma változás esetén."""
        warning_level = self.usage_data.get("warning_level", "normal")
        percentage = self.usage_data.get("meteostat_percentage", 0.0)
        self._update_usage_warning(warning_level, percentage)
        self._update_usage_bar_styling(warning_level)
    
    # === 🚀 FRISSÍTETT WEATHER DATA REQUEST LOGIC - MULTI-YEAR BATCH + RÉGIÓ/MEGYE TÁMOGATÁSSAL ===
    
    def _trigger_weather_fetch(self) -> None:
        """🚀 MULTI-YEAR BATCH + 🏞️ RÉGIÓ/MEGYE TÁMOGATÁS: időjárási adatok lekérdezésének indítása."""
        print("🚨 DEBUG: _trigger_weather_fetch called - ANALYTICS → MAP SYNC FIX + KISZÜRÜLÉSI BUG FIX + MULTI-YEAR BATCH + RÉGIÓ/MEGYE VALIDÁCIÓ")
        
        if self.is_fetching:
            print("⚠️ DEBUG: Already fetching, ignoring request")
            return
        
        # 🏞️ Elemzési típus alapú lekérdezés
        if self.analysis_type == "single_location":
            self._trigger_single_location_fetch()
        elif self.analysis_type == "region":
            self._trigger_region_fetch()
        elif self.analysis_type == "county":
            self._trigger_county_fetch()
        else:
            error_msg = "Ismeretlen elemzési típus"
            print(f"❌ DEBUG: {error_msg}")
            self.local_error_occurred.emit(error_msg)
    
    def _trigger_single_location_fetch(self) -> None:
        """
        🚀 Egyedi lokáció lekérdezés indítása - MULTI-YEAR BATCH TÁMOGATÁSSAL.
        """
        print("📍 DEBUG: _trigger_single_location_fetch called")
        
        # 🔧 KRITIKUS VALIDÁCIÓ: Lokáció ellenőrzése
        if not self.current_city_data:
            error_msg = "Nincs kiválasztva lokáció"
            print(f"❌ DEBUG: {error_msg}")
            self.local_error_occurred.emit(error_msg)
            return
        
        # 🔧 KRITIKUS: Dátumok és paraméterek összegyűjtése
        try:
            latitude = self.current_city_data.get("latitude", 0.0)
            longitude = self.current_city_data.get("longitude", 0.0)
            
            # 🚀 MULTI-YEAR BATCH: Effektív dátum tartomány lekérdezése
            start_date, end_date = self._get_effective_date_range()
            
            print(f"🚀 DEBUG: SINGLE LOCATION MULTI-YEAR BATCH params - lat: {latitude}, lon: {longitude}, {start_date} → {end_date}")
            
            # API paraméterek + ✅ PROVIDER SELECTOR info + 🚀 MULTI-YEAR BATCH info
            params = {
                "timezone": "auto" if self.auto_timezone.isChecked() else "UTC",
                "cache": self.cache_data.isChecked(),
                "timeout": self.api_timeout.value(),
                "preferred_provider": self.current_provider,
                "user_override": True if self.current_provider != "auto" else False,
                # 🚀 MULTI-YEAR BATCH paraméterek
                "use_case": "single_city_multiyear",
                "batch_mode": True,
                "date_mode": self.date_mode,
                "time_range": self.time_range_combo.currentText() if self.date_mode == "time_range" else None
            }
            
            # 🚀 MULTI-YEAR BATCH: Lokális dátum validáció (1 ÉVES LIMIT ELTÁVOLÍTVA!)
            if not self._validate_date_range_multiyear(start_date, end_date):
                return
            
            # UI állapot frissítése
            self._set_fetch_state(True)
            
            # 🔧 KRITIKUS JAVÍTÁS: Signal kibocsátása a Controller felé
            print(f"🚀 DEBUG: Emitting SINGLE LOCATION MULTI-YEAR weather_data_requested signal...")
            self.weather_data_requested.emit(latitude, longitude, start_date, end_date, params)
            
            city_name = self.current_city_data.get("display_name", "Ismeretlen")
            provider_info = f"({self.current_provider})" if self.current_provider != "auto" else "(auto)"
            print(f"✅ DEBUG: SINGLE LOCATION MULTI-YEAR Weather data signal ELKÜLDVE: {city_name} {provider_info}")
            
        except Exception as e:
            print(f"❌ DEBUG: SINGLE LOCATION MULTI-YEAR Weather fetch hiba: {e}")
            self.local_error_occurred.emit(f"Lekérdezési hiba: {str(e)}")
    
    def _trigger_region_fetch(self) -> None:
        """
        🏞️ Régió multi-city lekérdezés indítása.
        """
        print("🏞️ DEBUG: _trigger_region_fetch called")
        
        # Régió validáció
        if not self.selected_region:
            self.selected_region = self.region_combo.currentText()
        
        if not self.selected_region:
            error_msg = "Nincs kiválasztva régió"
            print(f"❌ DEBUG: {error_msg}")
            self.local_error_occurred.emit(error_msg)
            return
        
        try:
            # 🚀 MULTI-YEAR BATCH: Effektív dátum tartomány lekérdezése
            start_date, end_date = self._get_effective_date_range()
            
            print(f"🏞️ DEBUG: REGION MULTI-CITY BATCH params - region: {self.selected_region}, {start_date} → {end_date}")
            
            # API paraméterek
            params = {
                "timezone": "auto" if self.auto_timezone.isChecked() else "UTC",
                "cache": self.cache_data.isChecked(),
                "timeout": self.api_timeout.value(),
                "preferred_provider": self.current_provider,
                "user_override": True if self.current_provider != "auto" else False,
                # 🏞️ RÉGIÓ/MEGYE paraméterek
                "use_case": "multi_city_region",
                "batch_mode": True,
                "date_mode": self.date_mode,
                "time_range": self.time_range_combo.currentText() if self.date_mode == "time_range" else None,
                "analysis_type": "region",
                "region_name": self.selected_region,
                "cities": self._get_region_cities(self.selected_region),
                "query_type": self.analysis_parameter_combo.currentData() if hasattr(self, "analysis_parameter_combo") else "hottest_today",
            }
            
            # 🚀 MULTI-YEAR BATCH: Lokális dátum validáció
            if not self._validate_date_range_multiyear(start_date, end_date):
                return
            
            # UI állapot frissítése
            self._set_fetch_state(True)
            
            # 🏞️ Signal: Multi-city lekérdezés
            print(f"🏞️ DEBUG: Emitting REGION MULTI-CITY multi_city_weather_requested signal...")
            self.multi_city_weather_requested.emit("region", self.selected_region, start_date, end_date, params)
            
            provider_info = f"({self.current_provider})" if self.current_provider != "auto" else "(auto)"
            print(f"✅ DEBUG: REGION MULTI-CITY Weather data signal ELKÜLDVE: {self.selected_region} {provider_info}")
            
        except Exception as e:
            print(f"❌ DEBUG: REGION MULTI-CITY Weather fetch hiba: {e}")
            self.local_error_occurred.emit(f"Régió lekérdezési hiba: {str(e)}")
    
    def _trigger_county_fetch(self) -> None:
        """
        🏞️ Megye multi-city lekérdezés indítása.
        """
        print("🏛️ DEBUG: _trigger_county_fetch called")
        
        # Megye validáció
        if not self.selected_county:
            self.selected_county = self.county_combo.currentText()
        
        if not self.selected_county:
            error_msg = "Nincs kiválasztva megye"
            print(f"❌ DEBUG: {error_msg}")
            self.local_error_occurred.emit(error_msg)
            return
        
        try:
            # 🚀 MULTI-YEAR BATCH: Effektív dátum tartomány lekérdezése
            start_date, end_date = self._get_effective_date_range()
            
            print(f"🏛️ DEBUG: COUNTY MULTI-CITY BATCH params - county: {self.selected_county}, {start_date} → {end_date}")
            
            # API paraméterek
            params = {
                "timezone": "auto" if self.auto_timezone.isChecked() else "UTC",
                "cache": self.cache_data.isChecked(),
                "timeout": self.api_timeout.value(),
                "preferred_provider": self.current_provider,
                "user_override": True if self.current_provider != "auto" else False,
                # 🏞️ RÉGIÓ/MEGYE paraméterek
                "use_case": "multi_city_county",
                "batch_mode": True,
                "date_mode": self.date_mode,
                "time_range": self.time_range_combo.currentText() if self.date_mode == "time_range" else None,
                "analysis_type": "county",
                "county_name": self.selected_county,
                "cities": self._get_county_cities(self.selected_county),
                "query_type": self.analysis_parameter_combo.currentData() if hasattr(self, "analysis_parameter_combo") else "hottest_today",
            }
            
            # 🚀 MULTI-YEAR BATCH: Lokális dátum validáció
            if not self._validate_date_range_multiyear(start_date, end_date):
                return
            
            # UI állapot frissítése
            self._set_fetch_state(True)
            
            # 🏞️ Signal: Multi-city lekérdezés
            print(f"🏛️ DEBUG: Emitting COUNTY MULTI-CITY multi_city_weather_requested signal...")
            self.multi_city_weather_requested.emit("county", self.selected_county, start_date, end_date, params)
            
            provider_info = f"({self.current_provider})" if self.current_provider != "auto" else "(auto)"
            print(f"✅ DEBUG: COUNTY MULTI-CITY Weather data signal ELKÜLDVE: {self.selected_county} {provider_info}")
            
        except Exception as e:
            print(f"❌ DEBUG: COUNTY MULTI-CITY Weather fetch hiba: {e}")
            self.local_error_occurred.emit(f"Megye lekérdezési hiba: {str(e)}")
    
    def _validate_date_range_multiyear(self, start_date: str, end_date: str) -> bool:
        """
        🚀 MULTI-YEAR BATCH: Dátum tartomány lokális validálása - 1 ÉVES LIMIT ELTÁVOLÍTVA!
        """
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            if start > end:
                self.local_error_occurred.emit("A kezdő dátum nem lehet nagyobb a befejező dátumnál")
                return False
            
            # 🚀 KRITIKUS VÁLTOZÁS: 1 éves limit ELTÁVOLÍTVA!
            # Maximum ~60 éves tartomány (praktikus limit)
            if (end - start).days > 60 * 365:
                self.local_error_occurred.emit("Maximum 60 éves időszak kérdezhető le (praktikus limit)")
                return False
            
            # Minimum 1 nap
            if (end - start).days < 1:
                self.local_error_occurred.emit("Minimum 1 napos időszak szükséges")
                return False
            
            print(f"🚀 DEBUG: MULTI-YEAR validation PASSED: {(end - start).days} napok")
            return True
            
        except ValueError:
            self.local_error_occurred.emit("Érvénytelen dátum formátum")
            return False
    
    def _set_fetch_state(self, fetching: bool) -> None:
        """🔧 KISZÜRÜLÉSI BUG FIX - lekérdezés állapot beállítása SIGNAL BLOCKING-gal."""
        print(f"🔧 DEBUG: _set_fetch_state: {fetching} - WITH SIGNAL BLOCKING")
        
        try:
            # 🔧 KRITIKUS: State update flag beállítása - DE NEM FETCH MÓD ESETÉN!
            if fetching:
                self._updating_state = True
            
            self.is_fetching = fetching
            
            # Vezérlők megjelenítése
            self.fetch_button.setVisible(not fetching)
            self.cancel_button.setVisible(fetching)
            
            # Progress bar
            self.progress_bar.setVisible(fetching)
            if fetching:
                self.progress_bar.setRange(0, 0)  # Indeterminate
            else:
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(0)
            
            # 🔧 KRITIKUS JAVÍTÁS: SIGNAL BLOCKING CSAK FETCH KÖZBEN!
            if fetching:
                # Signal blokkolás CSAK fetch közben
                self.single_location_radio.blockSignals(True)
                self.region_radio.blockSignals(True)
                self.county_radio.blockSignals(True)
                self.region_combo.blockSignals(True)
                self.county_combo.blockSignals(True)
            else:
                # Signal blokkolás feloldása fetch befejezése után
                self.single_location_radio.blockSignals(False)
                self.region_radio.blockSignals(False)
                self.county_radio.blockSignals(False)
                self.region_combo.blockSignals(False)
                self.county_combo.blockSignals(False)
                print("🔧 DEBUG: Signals UNBLOCKED after fetch completion")
            
            # Elemzési típus vezérlők engedélyezése/letiltása
            self.single_location_radio.setEnabled(not fetching)
            self.region_radio.setEnabled(not fetching)
            self.county_radio.setEnabled(not fetching)
            
            # Lokáció selector állapot (csak single_location módban)
            if self.analysis_type == "single_location":
                self.universal_location_selector.setEnabled(not fetching)
                self.clear_location_btn.setEnabled(not fetching and self.current_city_data is not None)
            
            # Régió/megye selector állapot megfelelő analysis type szerint
            self.region_combo.setEnabled(not fetching and self.analysis_type == "region")
            self.county_combo.setEnabled(not fetching and self.analysis_type == "county")
            
            # 🚀 MULTI-YEAR BATCH vezérlők
            self.time_range_radio.setEnabled(not fetching)
            self.manual_dates_radio.setEnabled(not fetching)
            self.time_range_combo.setEnabled(not fetching and self.date_mode == "time_range")
            
            # Dátum vezérlők
            self.start_date.setEnabled(not fetching and self.date_mode == "manual_dates")
            self.end_date.setEnabled(not fetching and self.date_mode == "manual_dates")
            
            # ✅ PROVIDER SELECTOR vezérlők
            self.auto_radio.setEnabled(not fetching)
            self.openmeteo_radio.setEnabled(not fetching)
            self.meteostat_radio.setEnabled(not fetching)
            
            print(f"✅ DEBUG: FETCH STATE JAVÍTVA: {fetching} - Analysis type controls enabled: {not fetching}")
            
        except Exception as e:
            print(f"❌ ERROR: Set fetch state error: {e}")
        finally:
            # 🔧 KRITIKUS JAVÍTÁS: State update flag törlése MINDEN esetben
            if self._updating_state:
                self._updating_state = False
                print("🔧 DEBUG: _updating_state flag RESET in _set_fetch_state finally block")
    
    def _cancel_operations(self) -> None:
        """Lekérdezés megszakítása."""
        print("🚨 DEBUG: _cancel_operations called")
        
        # Worker manager stop parancs
        if self.worker_manager:
            self.worker_manager.stop_all_workers()
        
        # UI állapot visszaállítása
        self._set_fetch_state(False)
        
        self._update_status("Lekérdezés megszakítva")
        print("✅ DEBUG: Operations cancelled")
    
    def _show_local_error(self, error_message: str) -> None:
        """Helyi hiba megjelenítése."""
        print(f"❌ LOCAL ERROR: {error_message}")
        
        # Status frissítése
        self._update_status(f"❌ Hiba: {error_message}")
        
        # Error styling
        self._apply_professional_label_styling(self.status_label, "error")
        
        # Fetch state reset ha szükséges
        if self.is_fetching:
            self._set_fetch_state(False)
    
    def _update_status(self, message: str) -> None:
        """Status üzenet frissítése."""
        self.status_label.setText(message)
        print(f"📊 STATUS: {message}")
        
        # Reset styling to primary if not error
        if not message.startswith("❌"):
            self._apply_professional_label_styling(self.status_label, "primary")
    
    # === 🚨 ANALYTICS → MAP SYNC FIX - PUBLIKUS API METÓDUSOK ===
    
    def get_current_analysis_parameters(self) -> Dict[str, Any]:
        """
        🚨 ANALYTICS → MAP SYNC - Publikus API: Jelenlegi analysis paraméterek lekérdezése.
        """
        return self._get_current_analysis_parameters()
    
    def get_current_weather_parameters(self) -> Dict[str, Any]:
        """
        🚨 ANALYTICS → MAP SYNC - Publikus API: Jelenlegi weather paraméterek lekérdezése.
        """
        return self._get_current_weather_parameters()
    
    def get_current_date_parameters(self) -> Dict[str, Any]:
        """
        🚨 ANALYTICS → MAP SYNC - Publikus API: Jelenlegi date paraméterek lekérdezése.
        """
        return self._get_current_date_parameters()
    
    def get_all_parameters(self) -> Dict[str, Any]:
        """
        🚨 ANALYTICS → MAP SYNC - Publikus API: Comprehensive bundle minden paraméterrel.
        """
        return self._get_all_parameters()
    
    def trigger_analysis_parameters_sync(self) -> None:
        """
        🚨 ANALYTICS → MAP SYNC - Publikus API: Analysis paraméterek szinkronizálás manuális trigger.
        """
        analysis_params = self._get_current_analysis_parameters()
        self.analysis_parameters_changed.emit(analysis_params)
        print(f"🚨 DEBUG: Manual analysis_parameters_changed trigger: {analysis_params}")
    
    def trigger_weather_parameters_sync(self) -> None:
        """
        🚨 ANALYTICS → MAP SYNC - Publikus API: Weather paraméterek szinkronizálás manuális trigger.
        """
        weather_params = self._get_current_weather_parameters()
        self.weather_parameters_changed.emit(weather_params)
        print(f"🚨 DEBUG: Manual weather_parameters_changed trigger: {weather_params}")
    
    def trigger_full_parameters_sync(self) -> None:
        """
        🚨 ANALYTICS → MAP SYNC - Publikus API: Összes paraméter szinkronizálás manuális trigger.
        """
        bundle = self._get_all_parameters()
        self.parameters_bundle_changed.emit(bundle)
        print(f"🚨 DEBUG: Manual parameters_bundle_changed trigger")
    
    # === KOMPATIBILITÁSI METÓDUSOK ===
    
    def get_selected_city_data(self) -> Optional[Dict[str, Any]]:
        """
        Kompatibilitási metódus: Kiválasztott város adatok lekérdezése.
        """
        return self.current_city_data
    
    def get_selected_location(self) -> Optional[UniversalLocation]:
        """
        Kompatibilitási metódus: Kiválasztott UniversalLocation objektum lekérdezése.
        """
        return self.current_location
    
    def get_date_range(self) -> tuple[str, str]:
        """
        Kompatibilitási metódus: Aktuális dátum tartomány lekérdezése.
        """
        return self._get_effective_date_range()
    
    def get_analysis_type(self) -> str:
        """
        Kompatibilitási metódus: Aktuális elemzési típus lekérdezése.
        """
        return self.analysis_type
    
    def get_provider(self) -> str:
        """
        Kompatibilitási metódus: Aktuális provider lekérdezése.
        """
        return self.current_provider
    
    def is_fetch_in_progress(self) -> bool:
        """
        Kompatibilitási metódus: Lekérdezés folyamatban állapot ellenőrzése.
        """
        return self.is_fetching
    
    # === UI FRISSÍTÉSI METÓDUSOK ===
    
    def refresh_ui_state(self) -> None:
        """
        UI állapot teljes frissítése - használható külső hívásokból.
        """
        print("🔄 DEBUG: refresh_ui_state called")
        
        # Elemzési típus UI frissítése
        self._update_ui_for_analysis_type_with_signal_blocking()
        
        # Fetch button állapot frissítése
        self._update_fetch_button_state_safe()
        
        # Provider selector frissítése
        self._update_usage_display()
        
        # Dátum számítás frissítése
        if self.date_mode == "time_range":
            self._update_computed_dates()
        
        print("✅ DEBUG: UI state refreshed")
    
    def set_analysis_type_programmatically(self, analysis_type: str) -> bool:
        """
        Elemzési típus programozott beállítása - használható külső hívásokból.
        """
        if analysis_type not in ["single_location", "region", "county"]:
            print(f"❌ ERROR: Invalid analysis type: {analysis_type}")
            return False
        
        try:
            # Signal blokkolása a programozott változás alatt
            self._updating_state = True
            
            # Radio button beállítása
            if analysis_type == "single_location":
                self.single_location_radio.setChecked(True)
            elif analysis_type == "region":
                self.region_radio.setChecked(True)
            elif analysis_type == "county":
                self.county_radio.setChecked(True)
            
            # Állapot frissítése
            self.analysis_type = analysis_type
            
            # UI frissítése
            self._update_ui_for_analysis_type_with_signal_blocking()
            self._update_fetch_button_state_safe()
            
            print(f"✅ DEBUG: Analysis type set programmatically: {analysis_type}")
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Failed to set analysis type programmatically: {e}")
            return False
        finally:
            self._updating_state = False
    
    def set_provider_programmatically(self, provider: str) -> bool:
        """
        Provider programozott beállítása - használható külső hívásokból.
        """
        if provider not in ["auto", "open-meteo", "meteostat"]:
            print(f"❌ ERROR: Invalid provider: {provider}")
            return False
        
        try:
            # Radio button beállítása
            if provider == "auto":
                self.auto_radio.setChecked(True)
            elif provider == "open-meteo":
                self.openmeteo_radio.setChecked(True)
            elif provider == "meteostat":
                self.meteostat_radio.setChecked(True)
            
            # Állapot frissítése
            self.current_provider = provider
            
            # Preferences mentése
            self._save_provider_preferences()
            
            # Status frissítése
            self._update_status_for_provider_change(provider)
            
            print(f"✅ DEBUG: Provider set programmatically: {provider}")
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Failed to set provider programmatically: {e}")
            return False
    
    def force_fetch_button_update(self) -> None:
        """
        Fetch button állapot kényszerített frissítése - használható külső hívásokból.
        """
        self._update_fetch_button_state_safe()
        print("🔄 DEBUG: Fetch button state force updated")
    
    # === HIÁNYZÓ KOMPATIBILITÁSI METÓDUSOK ===
    
    def _on_geocoding_completed(self, results: List[Dict[str, Any]]) -> None:
        """
        Geocoding eredmények fogadása - kompatibilitási metódus.
        """
        print(f"📍 DEBUG: _on_geocoding_completed called with {len(results)} results")
        
        try:
            # UniversalLocationSelector frissítése az eredményekkel
            if hasattr(self, 'universal_location_selector'):
                self.universal_location_selector.update_search_results(results)
                print(f"✅ DEBUG: Search results updated in UniversalLocationSelector")
            
            # Status frissítése
            if results:
                self._update_status(f"📍 {len(results)} találat")
            else:
                self._update_status("❌ Nincs találat")
                
        except Exception as e:
            print(f"❌ ERROR: Geocoding completion handling error: {e}")
            self.local_error_occurred.emit(f"Geocoding eredmény feldolgozási hiba: {str(e)}")
    
    def _on_geocoding_error(self, error_message: str) -> None:
        """
        Geocoding hiba fogadása - kompatibilitási metódus.
        """
        print(f"❌ DEBUG: _on_geocoding_error called: {error_message}")
        
        # Error status beállítása
        self._update_status(f"❌ Keresési hiba: {error_message}")
        self._apply_professional_label_styling(self.status_label, "error")
        
        # Local error signal emit
        self.local_error_occurred.emit(f"Keresési hiba: {error_message}")
    
    def _on_weather_data_received(self, data: Dict[str, Any]) -> None:
        """
        Weather data fogadása - kompatibilitási metódus.
        """
        print(f"🌤️ DEBUG: _on_weather_data_received called")
        
        try:
            # Fetch state reset
            self._set_fetch_state(False)
            
            # Success status
            location_name = "Unknown"
            if self.current_city_data:
                location_name = self.current_city_data.get("display_name", "Unknown")
            elif self.analysis_type == "region" and self.selected_region:
                location_name = self.selected_region
            elif self.analysis_type == "county" and self.selected_county:
                location_name = self.selected_county
            
            self._update_status(f"✅ Adatok fogadva: {location_name}")
            self._apply_professional_label_styling(self.status_label, "success")
            
            print(f"✅ DEBUG: Weather data received for: {location_name}")
            
        except Exception as e:
            print(f"❌ ERROR: Weather data reception handling error: {e}")
    
    def _on_weather_data_error(self, error_message: str) -> None:
        """
        Weather data hiba fogadása - kompatibilitási metódus.
        """
        print(f"❌ DEBUG: _on_weather_data_error called: {error_message}")
        
        try:
            # Fetch state reset
            self._set_fetch_state(False)
            
            # Error status beállítása
            self._update_status(f"❌ Lekérdezési hiba: {error_message}")
            self._apply_professional_label_styling(self.status_label, "error")
            
            # Local error signal emit
            self.local_error_occurred.emit(f"Lekérdezési hiba: {error_message}")
            
        except Exception as e:
            print(f"❌ ERROR: Weather data error handling error: {e}")
    
    def _on_multi_city_data_received(self, data: Dict[str, Any]) -> None:
        """
        Multi-city data fogadása - kompatibilitási metódus.
        """
        print(f"🏞️ DEBUG: _on_multi_city_data_received called")
        
        try:
            # Fetch state reset
            self._set_fetch_state(False)
            
            # Success status
            region_name = "Unknown"
            if self.analysis_type == "region" and self.selected_region:
                region_name = f"Régió: {self.selected_region}"
            elif self.analysis_type == "county" and self.selected_county:
                region_name = f"Megye: {self.selected_county}"
            
            city_count = len(data.get("city_results", []))
            self._update_status(f"✅ Multi-city adatok fogadva: {region_name} ({city_count} város)")
            self._apply_professional_label_styling(self.status_label, "success")
            
            print(f"✅ DEBUG: Multi-city data received for: {region_name} ({city_count} cities)")
            
        except Exception as e:
            print(f"❌ ERROR: Multi-city data reception handling error: {e}")
    
    def _on_multi_city_data_error(self, error_message: str) -> None:
        """
        Multi-city data hiba fogadása - kompatibilitási metódus.
        """
        print(f"❌ DEBUG: _on_multi_city_data_error called: {error_message}")
        
        try:
            # Fetch state reset
            self._set_fetch_state(False)
            
            # Error status beállítása
            self._update_status(f"❌ Multi-city lekérdezési hiba: {error_message}")
            self._apply_professional_label_styling(self.status_label, "error")
            
            # Local error signal emit
            self.local_error_occurred.emit(f"Multi-city lekérdezési hiba: {error_message}")
            
        except Exception as e:
            print(f"❌ ERROR: Multi-city data error handling error: {e}")
    
    # === PUBLIKUS SLOT METÓDUSOK A CONTROLLER FELŐLI KOMMUNIKÁCIÓHOZ ===
    
    def on_weather_data_completed(self) -> None:
        """
        🚨 ANALYTICS → MAP SYNC + 🚀 MULTI-YEAR BATCH + 🏞️ RÉGIÓ/MEGYE - Időjárási adatok lekérdezésének befejezése a Controller-től.
        """
        print("✅ DEBUG: on_weather_data_completed called from Controller")
        
        self._set_fetch_state(False)
        
        # MULTI-YEAR BATCH + RÉGIÓ/MEGYE specifikus success message
        success_msg = "Adatok sikeresen lekérdezve"
        
        if self.date_mode == "time_range":
            time_range = self.time_range_combo.currentText()
            success_msg += f" ({time_range})"
        
        if self.analysis_type == "region":
            success_msg += f" [Régió: {self.region_combo.currentText()}]"
        elif self.analysis_type == "county":
            success_msg += f" [Megye: {self.county_combo.currentText()}]"
        
        # Status frissítése success styling-gal
        self._update_status(f"✅ {success_msg}")
        self._apply_professional_label_styling(self.status_label, "success")
        
        # Usage display frissítése
        self._update_usage_display()
    
    def on_controller_error(self, error_message: str) -> None:
        """
        🚨 ANALYTICS → MAP SYNC + 🚀 MULTI-YEAR BATCH + 🏞️ RÉGIÓ/MEGYE - Hiba kezelése a Controller-től.
        """
        print(f"❌ DEBUG: on_controller_error called from Controller: {error_message}")
        
        self._set_fetch_state(False)
        self._show_local_error(error_message)
    
    def update_progress(self, worker_type: str, progress: int) -> None:
        """
        🚨 ANALYTICS → MAP SYNC + 🚀 MULTI-YEAR BATCH + 🏞️ RÉGIÓ/MEGYE - Progress frissítése a Controller-től.
        """
        if self.progress_bar.isVisible():
            if progress == 100:
                self.progress_bar.setVisible(False)
                # Az _set_fetch_state(False) már az on_weather_data_completed-ben megtörténik
            else:
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(progress)
        
        if progress < 100:
            provider_info = f"({self.current_provider})" if self.current_provider != "auto" else ""
            batch_info = f" [{self.time_range_combo.currentText()}]" if self.date_mode == "time_range" else ""
            
            analysis_info = ""
            if self.analysis_type == "region":
                analysis_info = f" [Régió: {self.region_combo.currentText()}]"
            elif self.analysis_type == "county":
                analysis_info = f" [Megye: {self.county_combo.currentText()}]"
            
            self._update_status(f"⏳ {worker_type}: {progress}%{provider_info}{batch_info}{analysis_info}")
    
    def update_status_from_controller(self, message: str) -> None:
        """
        🚨 ANALYTICS → MAP SYNC + 🚀 MULTI-YEAR BATCH + 🏞️ RÉGIÓ/MEGYE - Státusz frissítése a Controller-től.
        """
        print(f"📊 DEBUG: update_status_from_controller called: {message}")
        self._update_status(message)
    
    # === DESTRUKTOR ÉS CLEANUP ===
    
    def cleanup(self) -> None:
        """
        ControlPanel cleanup - timer leállítása és erőforrások felszabadítása.
        """
        print("🧹 DEBUG: ControlPanel cleanup started")
        
        try:
            # Timer leállítása
            if hasattr(self, 'usage_update_timer') and self.usage_update_timer:
                self.usage_update_timer.stop()
                print("✅ DEBUG: Usage update timer stopped")
            
            # Worker manager cleanup
            if hasattr(self, 'worker_manager') and self.worker_manager:
                self.worker_manager.stop_all_workers()
                print("✅ DEBUG: Worker manager stopped")
            
            # State reset
            self._updating_state = False
            self.is_fetching = False
            
            print("✅ DEBUG: ControlPanel cleanup completed")
            
        except Exception as e:
            print(f"❌ ERROR: ControlPanel cleanup error: {e}")
    
    def __del__(self):
        """Destruktor."""
        try:
            self.cleanup()
        except:
            pass