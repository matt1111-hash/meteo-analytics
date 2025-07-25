#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Control Panel Module (MULTI-YEAR BATCH SUPPORT!)
MVC kompatibilis vezérlő panel modul - LAYOUT & RESPONSIVENESS JAVÍTOTT + MULTI-YEAR BATCH TÁMOGATÁS.

🚀 MULTI-YEAR BATCH TÁMOGATÁS HOZZÁADVA:
✅ Időtartam dropdown (5/10/25/55 év) - ugyanaz mint TrendAnalyticsTab
✅ 1 éves limit ELTÁVOLÍTVA
✅ weather_client.py v4.0 multi-year batch használata
✅ Automatikus dátum számítás dropdown alapján
✅ 55 éves trend elemzések támogatása
✅ Kompatibilitás a meglévő manual dátum picker-ekkel

🔧 LAYOUT & RESPONSIVENESS JAVÍTÁSOK:
✅ Panel width constraints optimalizálva (320-450px)
✅ Widget spacing és margins javítva
✅ Button sizing és responsiveness javítva  
✅ GroupBox sizing optimalizálva
✅ UniversalLocationSelector layout constraints javítva
✅ Fetch button signal chain debug és javítás
✅ Layout overflow problémák megoldva
✅ Modern spacing és padding használata

🌍 ✅ UNIVERSAL LOCATION SELECTOR INTEGRÁCIÓ MEGMARAD:
- UniversalLocationSelector komponens integrálva
- 3-fülecskés lokáció választó (Keresés/Lista/Térkép)
- Kompatibilis signal interfész fenntartva
- Régi city_input + city_results lecserélve
- CityManager automatikusan létrehozva

🎨 ✅ PROFESSZIONÁLIS COLORPALETTE INTEGRÁCIÓ MEGMARAD:
- MockColorScheme eltávolítva
- ColorPalette API használata
- Dinamikus HSL színkezelés
- Semantic color mapping
- Material Design support
- Professional theming

✅ PROVIDER SELECTOR SUPPORT MEGMARAD:
- User-controlled API választás
- Real-time usage tracking display
- Cost monitoring & warnings
- Provider preference persistence
- Smart routing display
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QHBoxLayout, QGroupBox,
    QLineEdit, QComboBox, QPushButton, QDateEdit, QLabel,
    QCheckBox, QSpinBox, QProgressBar, QRadioButton, QButtonGroup,
    QSizePolicy, QFrame, QScrollArea  # 🔧 LAYOUT JAVÍTÁS
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
    🚀 MULTI-YEAR BATCH TÁMOGATÁS + 🔧 LAYOUT & RESPONSIVENESS JAVÍTOTT MVC kompatibilis vezérlő panel.
    
    🚀 MULTI-YEAR BATCH TÁMOGATÁS EBBEN A VERZIÓBAN:
    - Időtartam dropdown (5/10/25/55 év) - TrendAnalyticsTab kompatibilis
    - 1 éves limit ELTÁVOLÍTVA
    - weather_client.py v4.0 multi-year batch használata  
    - Automatikus dátum számítás dropdown alapján
    - Manual dátum választás továbbra is elérhető
    - 55 éves klimatológiai elemzések támogatása
    - Rate limit optimalizált batch-elés
    
    🔧 LAYOUT & RESPONSIVENESS JAVÍTÁSOK MEGMARADNAK:
    - Panel width constraints optimalizálva (320-450px)
    - Widget spacing és margins professzionálisan beállítva
    - Button sizing és responsiveness problémák javítva
    - GroupBox sizing és overflow problémák megoldva
    - UniversalLocationSelector layout constraints optimalizálva
    - Fetch button signal chain debug és javítás
    - Layout overflow és scrolling problémák megoldva
    - Modern spacing használata (12px, 16px, 20px)
    
    🌍 UNIVERSAL LOCATION SELECTOR FEATURES MEGMARADNAK:
    - 3-fülecskés lokáció választó (Keresés/Lista/Térkép)
    - UniversalLocation objektum támogatás
    - Kompatibilis signal interfész
    - CityManager automatikus inicializálás
    
    🎨 PROFESSIONAL COLORPALETTE FEATURES MEGMARADNAK:
    - Dinamikus HSL színkezelés
    - Semantic color mapping
    - Material Design color variants
    - Weather-specific color schemes
    - WCAG accessibility compliance
    - Real-time theme switching
    
    ✅ PROVIDER SELECTOR FEATURES MEGMARADNAK:
    - User-controlled API selection
    - Real-time usage tracking
    - Cost monitoring & alerts
    - Smart routing visualization
    - Automatic fallback handling
    """
    
    # === KIMENŐ SIGNALOK A CONTROLLER FELÉ ===
    
    # Település keresés (kompatibilitás)
    search_requested = Signal(str)  # search_query
    
    # Település kiválasztás (kompatibilitás)
    city_selected = Signal(str, float, float, dict)  # name, lat, lon, metadata
    
    # 🌍 ÚJ - UniversalLocation kiválasztás
    location_changed = Signal(object)  # UniversalLocation objektum
    
    # 🚀 FRISSÍTETT - Időjárási adatok lekérdezése MULTI-YEAR BATCH támogatással
    weather_data_requested = Signal(float, float, str, str, dict)  # lat, lon, start_date, end_date, params
    
    # ✅ PROVIDER SELECTOR SIGNALOK
    provider_changed = Signal(str)  # provider_name ("auto", "open-meteo", "meteostat")
    provider_preferences_updated = Signal(dict)  # updated_preferences
    
    # === EGYÉB SIGNALOK ===
    
    # Helyi hibák (validációs hibák stb.)
    local_error_occurred = Signal(str)  # error_message
    
    def __init__(self, worker_manager: WorkerManager, parent: Optional[QWidget] = None):
        """
        🚀 MULTI-YEAR BATCH TÁMOGATÁS + 🔧 LAYOUT & RESPONSIVENESS JAVÍTOTT vezérlő panel inicializálása.
        
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
        
        # UI állapot
        self.is_fetching = False
        
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
        
        print("🚀 DEBUG: ControlPanel MULTI-YEAR BATCH TÁMOGATÁS + LAYOUT & RESPONSIVENESS JAVÍTOTT verzió kész")
    
    def _init_ui(self) -> None:
        """🚀 MULTI-YEAR BATCH + 🔧 LAYOUT & RESPONSIVENESS JAVÍTOTT UI elemek inicializálása."""
        
        # 🔧 KRITIKUS: PANEL SIZE POLICY ÉS CONSTRAINTS
        self.setMinimumWidth(320)  # Minimum width növelve
        self.setMaximumWidth(450)  # Maximum width növelve 
        self.setMinimumHeight(600)  # Minimum height biztosítása
        
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
        main_layout.setContentsMargins(0, 0, 0, 0)  # Nincs margin az fő layout-on
        main_layout.addWidget(scroll_area)
        
        # Content layout
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(12, 12, 12, 12)  # 🔧 OPTIMÁLIS MARGINS
        layout.setSpacing(16)  # 🔧 OPTIMÁLIS SPACING
        
        # 🌍 UNIVERSAL LOCATION SELECTOR panel
        location_group = self._create_universal_location_group()
        layout.addWidget(location_group)
        
        # 🚀 MULTI-YEAR BATCH: Időtartam kiválasztás panel (ÚJ!)
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
        
        print(f"🚀 DEBUG: ControlPanel MULTI-YEAR BATCH + LAYOUT JAVÍTVA - size: {self.minimumWidth()}-{self.maximumWidth()}px, scroll enabled")
    
    def _create_universal_location_group(self) -> QGroupBox:
        """
        🌍 UNIVERSAL LOCATION SELECTOR widget csoport létrehozása - LAYOUT JAVÍTÁSSAL.
        """
        group = QGroupBox("🌍 Lokáció Választó")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 16, 12, 12)  # 🔧 OPTIMÁLIS MARGINS
        layout.setSpacing(12)  # 🔧 OPTIMÁLIS SPACING
        
        # 🌍 UNIVERSAL LOCATION SELECTOR komponens
        self.universal_location_selector = UniversalLocationSelector(self.city_manager, self)
        
        # 🔧 KRITIKUS: SIZE CONSTRAINTS A UNIVERSAL LOCATION SELECTOR-RA
        self.universal_location_selector.setMinimumHeight(420)  # Minimum magasság növelve
        self.universal_location_selector.setMaximumHeight(500)  # Maximum magasság beállítva
        self.universal_location_selector.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout.addWidget(self.universal_location_selector)
        
        # Kiválasztott lokáció információ megjelenítése
        info_layout = QHBoxLayout()
        info_layout.setSpacing(8)  # 🔧 SPACING JAVÍTÁS
        
        self.location_info_label = QLabel("Válasszon lokációt...")
        self.location_info_label.setWordWrap(True)
        self.location_info_label.setMinimumHeight(40)  # 🔧 MINIMUM HEIGHT
        info_layout.addWidget(self.location_info_label)
        
        # Clear gomb
        self.clear_location_btn = QPushButton("🗑️")
        self.clear_location_btn.clicked.connect(self._clear_location)
        self.clear_location_btn.setEnabled(False)
        self.clear_location_btn.setFixedSize(32, 32)  # 🔧 FIXED SIZE
        self.clear_location_btn.setToolTip("Lokáció törlése")
        info_layout.addWidget(self.clear_location_btn)
        
        layout.addLayout(info_layout)
        
        # 🔧 GROUPBOX SIZE CONSTRAINTS
        group.setMinimumHeight(500)
        group.setMaximumHeight(580)
        
        return group
    
    def _create_time_range_group(self) -> QGroupBox:
        """
        🚀 MULTI-YEAR BATCH: Időtartam kiválasztás widget csoport létrehozása - ÚJ!
        
        TrendAnalyticsTab kompatibilis időtartam opciók.
        """
        group = QGroupBox("⏰ Időtartam (Multi-Year)")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 16, 12, 12)  # 🔧 OPTIMÁLIS MARGINS
        layout.setSpacing(12)  # 🔧 OPTIMÁLIS SPACING
        
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
        
        # 🚀 Időtartam dropdown (TrendAnalyticsTab kompatibilis)
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(8)
        
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems([
            "5 év",
            "10 év", 
            "25 év",
            "55 év (teljes)"
        ])
        self.time_range_combo.setCurrentText("5 év")  # Alapértelmezett
        self.time_range_combo.setMinimumHeight(32)
        self.time_range_combo.setToolTip("Automatikus dátum számítás a mai naptól visszafelé")
        self.time_range_combo.currentTextChanged.connect(self._on_time_range_changed)
        
        form_layout.addRow("Időtartam:", self.time_range_combo)
        layout.addLayout(form_layout)
        
        # Info label a computed dátumokhoz
        self.computed_dates_info = QLabel("Számított időszak: 2020-07-25 → 2025-07-25")
        self.computed_dates_info.setWordWrap(True)
        self.computed_dates_info.setMinimumHeight(40)
        layout.addWidget(self.computed_dates_info)
        
        # 🔧 GROUPBOX SIZE CONSTRAINTS
        group.setMinimumHeight(140)
        group.setMaximumHeight(180)
        
        # Kezdeti számítás
        self._update_computed_dates()
        
        print("🚀 DEBUG: Time range group created with multi-year batch support")
        
        return group
    
    def _create_date_group(self) -> QGroupBox:
        """🚀 MULTI-YEAR BATCH + 🔧 LAYOUT JAVÍTOTT dátum kiválasztás widget csoport - FRISSÍTETT."""
        group = QGroupBox("📅 Manuális Dátumok (Opcionális)")
        layout = QFormLayout(group)
        layout.setContentsMargins(12, 16, 12, 12)  # 🔧 OPTIMÁLIS MARGINS
        layout.setVerticalSpacing(12)  # 🔧 VERTICAL SPACING
        layout.setHorizontalSpacing(8)  # 🔧 HORIZONTAL SPACING
        
        # Kezdő dátum
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setDate(QDate.currentDate().addYears(-5))  # 🚀 5 év alapértelmezett (1 helyett)
        self.start_date.setMinimumHeight(32)  # 🔧 MIN HEIGHT
        layout.addRow("Kezdő dátum:", self.start_date)
        
        # Befejező dátum
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setMinimumHeight(32)  # 🔧 MIN HEIGHT
        layout.addRow("Befejező dátum:", self.end_date)
        
        # Gyors dátum beállítások - MULTI-YEAR BATCH FRISSÍTÉS
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(8)  # 🔧 SPACING
        
        self.last_month_btn = QPushButton("Előző hónap")
        self.last_month_btn.clicked.connect(self._set_last_month)
        self.last_month_btn.setMinimumHeight(28)  # 🔧 MIN HEIGHT
        quick_layout.addWidget(self.last_month_btn)
        
        self.last_year_btn = QPushButton("Előző év")
        self.last_year_btn.clicked.connect(self._set_last_year)
        self.last_year_btn.setMinimumHeight(28)  # 🔧 MIN HEIGHT
        quick_layout.addWidget(self.last_year_btn)
        
        # 🚀 ÚJ: Multi-year gyors gombok
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
        layout.setContentsMargins(12, 16, 12, 12)  # 🔧 OPTIMÁLIS MARGINS
        layout.setSpacing(12)  # 🔧 OPTIMÁLIS SPACING
        
        # Provider radio buttons
        providers_layout = QVBoxLayout()
        providers_layout.setSpacing(8)  # 🔧 RADIO SPACING
        
        # Button group for mutual exclusion
        self.provider_button_group = QButtonGroup()
        
        # Auto provider radio
        self.auto_radio = QRadioButton("🤖 Automatikus (Smart Routing)")
        self.auto_radio.setToolTip("Use-case alapú automatikus provider választás + multi-year batch")
        self.auto_radio.setMinimumHeight(24)  # 🔧 MIN HEIGHT
        self.provider_button_group.addButton(self.auto_radio, 0)
        providers_layout.addWidget(self.auto_radio)
        
        # Open-Meteo radio
        self.openmeteo_radio = QRadioButton("🌍 Open-Meteo (Ingyenes + Multi-Year)")
        self.openmeteo_radio.setToolTip("Ingyenes globális időjárási API 55 éves batch támogatással")
        self.openmeteo_radio.setMinimumHeight(24)  # 🔧 MIN HEIGHT
        self.provider_button_group.addButton(self.openmeteo_radio, 1)
        providers_layout.addWidget(self.openmeteo_radio)
        
        # Meteostat radio
        self.meteostat_radio = QRadioButton("💎 Meteostat (Prémium + 55+ év)")
        self.meteostat_radio.setToolTip("Prémium API 55+ éves történeti adatokkal ($10/hónap)")
        self.meteostat_radio.setMinimumHeight(24)  # 🔧 MIN HEIGHT
        self.provider_button_group.addButton(self.meteostat_radio, 2)
        providers_layout.addWidget(self.meteostat_radio)
        
        # Provider change signal
        self.provider_button_group.buttonClicked.connect(self._on_provider_changed)
        
        layout.addLayout(providers_layout)
        
        # Usage tracking display
        usage_group = QGroupBox("📊 API Használat")
        usage_layout = QVBoxLayout(usage_group)
        usage_layout.setContentsMargins(8, 12, 8, 8)  # 🔧 INNER MARGINS
        usage_layout.setSpacing(8)  # 🔧 INNER SPACING
        
        # Meteostat usage display
        meteostat_layout = QHBoxLayout()
        meteostat_layout.setSpacing(8)  # 🔧 SPACING
        
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
        self.meteostat_usage_bar.setMinimumHeight(20)  # 🔧 MIN HEIGHT
        self.meteostat_usage_bar.setMaximumHeight(24)  # 🔧 MAX HEIGHT
        usage_layout.addWidget(self.meteostat_usage_bar)
        
        # Cost display
        cost_layout = QHBoxLayout()
        cost_layout.setSpacing(8)  # 🔧 SPACING
        
        self.cost_label = QLabel("💰 Havi költség:")
        cost_layout.addWidget(self.cost_label)
        
        self.cost_value = QLabel("$0.00")
        cost_layout.addWidget(self.cost_value)
        
        cost_layout.addStretch()
        usage_layout.addLayout(cost_layout)
        
        # Open-Meteo usage (informational) - FRISSÍTVE MULTI-YEAR INFÓVAL
        openmeteo_layout = QHBoxLayout()
        openmeteo_layout.setSpacing(8)  # 🔧 SPACING
        
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
        self.usage_warning_label.setMinimumHeight(20)  # 🔧 MIN HEIGHT
        layout.addWidget(self.usage_warning_label)
        
        # 🔧 GROUPBOX SIZE CONSTRAINTS
        group.setMinimumHeight(220)
        group.setMaximumHeight(280)
        
        return group
    
    def _create_api_settings_group(self) -> QGroupBox:
        """🔧 LAYOUT JAVÍTOTT API beállítások widget csoport létrehozása."""
        group = QGroupBox("⚙️ API Beállítások")
        layout = QFormLayout(group)
        layout.setContentsMargins(12, 16, 12, 12)  # 🔧 OPTIMÁLIS MARGINS
        layout.setVerticalSpacing(10)  # 🔧 VERTICAL SPACING
        layout.setHorizontalSpacing(8)  # 🔧 HORIZONTAL SPACING
        
        # Időzóna automatikus detektálás
        self.auto_timezone = QCheckBox()
        self.auto_timezone.setChecked(True)
        self.auto_timezone.setMinimumHeight(20)  # 🔧 MIN HEIGHT
        layout.addRow("Automatikus időzóna:", self.auto_timezone)
        
        # Adatok gyorsítótárazása
        self.cache_data = QCheckBox()
        self.cache_data.setChecked(True)
        self.cache_data.setMinimumHeight(20)  # 🔧 MIN HEIGHT
        layout.addRow("Adatok cache-elése:", self.cache_data)
        
        # API timeout beállítás - MULTI-YEAR BATCH-hez optimalizált
        self.api_timeout = QSpinBox()
        self.api_timeout.setRange(30, 300)  # 🚀 NAGYOBB RANGE multi-year batch-hez
        self.api_timeout.setValue(60)  # 🚀 NAGYOBB DEFAULT (30→60s) multi-year batch-hez
        self.api_timeout.setSuffix(" másodperc")
        self.api_timeout.setMinimumHeight(28)  # 🔧 MIN HEIGHT
        self.api_timeout.setToolTip("Multi-year batch lekérdezésekhez nagyobb timeout ajánlott")
        layout.addRow("API timeout:", self.api_timeout)
        
        # 🔧 GROUPBOX SIZE CONSTRAINTS
        group.setMinimumHeight(120)
        group.setMaximumHeight(140)
        
        return group
    
    def _create_query_control_group(self) -> QGroupBox:
        """🔧 LAYOUT & RESPONSIVENESS JAVÍTOTT lekérdezés vezérlés widget csoport."""
        group = QGroupBox("🚀 Lekérdezés (Multi-Year)")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 16, 12, 12)  # 🔧 OPTIMÁLIS MARGINS
        layout.setSpacing(10)  # 🔧 OPTIMÁLIS SPACING
        
        # 🔧 KRITIKUS JAVÍTÁS: Lekérdezés gomb - RESPONSIVE SIZING
        self.fetch_button = QPushButton("📊 Adatok lekérdezése (Multi-Year)")
        self.fetch_button.clicked.connect(self._trigger_weather_fetch)
        self.fetch_button.setEnabled(False)  # 🔧 JAVÍTÁS: Kezdetben letiltva
        
        # 🔧 KRITIKUS: RESPONSIVE BUTTON SIZING
        self.fetch_button.setMinimumHeight(44)  # Nagyobb kattintható terület
        self.fetch_button.setMaximumHeight(48)  # Maximum height constraint
        self.fetch_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Gomb stílus kiemelése
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)  # 🔧 NAGYOBB FONT
        self.fetch_button.setFont(font)
        
        layout.addWidget(self.fetch_button)
        
        # Lekérdezés megszakítás gomb
        self.cancel_button = QPushButton("❌ Megszakítás")
        self.cancel_button.clicked.connect(self._cancel_operations)
        self.cancel_button.setVisible(False)
        self.cancel_button.setMinimumHeight(36)  # 🔧 MIN HEIGHT
        self.cancel_button.setMaximumHeight(40)  # 🔧 MAX HEIGHT
        self.cancel_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.cancel_button)
        
        # 🔧 GROUPBOX SIZE CONSTRAINTS
        group.setMinimumHeight(100)
        group.setMaximumHeight(120)
        
        print("🚀 DEBUG: Query control group MULTI-YEAR BATCH + LAYOUT JAVÍTVA - responsive button sizing")
        
        return group
    
    def _create_status_group(self) -> QGroupBox:
        """🔧 LAYOUT JAVÍTOTT állapot widget csoport létrehozása."""
        group = QGroupBox("📊 Állapot")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 16, 12, 12)  # 🔧 OPTIMÁLIS MARGINS
        layout.setSpacing(10)  # 🔧 OPTIMÁLIS SPACING
        
        # Állapot szöveg
        self.status_label = QLabel("Válasszon lokációt a kezdéshez")
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(40)  # 🔧 MIN HEIGHT 
        self.status_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # 🔧 ALIGNMENT
        layout.addWidget(self.status_label)
        
        # Progressz bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(20)  # 🔧 MIN HEIGHT
        self.progress_bar.setMaximumHeight(24)  # 🔧 MAX HEIGHT
        layout.addWidget(self.progress_bar)
        
        # 🔧 GROUPBOX SIZE CONSTRAINTS
        group.setMinimumHeight(90)
        group.setMaximumHeight(110)
        
        return group
    
    # === 🚀 MULTI-YEAR BATCH LOGIC - ÚJ METÓDUSOK ===
    
    def _on_date_mode_changed(self):
        """
        🚀 Dátum mód változás kezelése (time_range vs manual_dates).
        """
        if self.time_range_radio.isChecked():
            self.date_mode = "time_range"
            self._set_manual_dates_enabled(False)
            self._update_computed_dates()
            print("🚀 DEBUG: Date mode switched to: time_range")
        else:
            self.date_mode = "manual_dates"
            self._set_manual_dates_enabled(True)
            print("🚀 DEBUG: Date mode switched to: manual_dates")
        
        # Fetch button state frissítése
        self._update_fetch_button_state()
    
    def _set_manual_dates_enabled(self, enabled: bool):
        """Manual dátum chooser-ek engedélyezése/letiltása."""
        self.start_date.setEnabled(enabled)
        self.end_date.setEnabled(enabled)
        self.last_month_btn.setEnabled(enabled)
        self.last_year_btn.setEnabled(enabled)
        self.last_5years_btn.setEnabled(enabled)
        self.last_10years_btn.setEnabled(enabled)
        self.last_25years_btn.setEnabled(enabled)
        self.last_55years_btn.setEnabled(enabled)
        
        # Időtartam dropdown ellenkezője
        self.time_range_combo.setEnabled(not enabled)
    
    def _on_time_range_changed(self, time_range_text: str):
        """
        🚀 Időtartam dropdown változás kezelése - automatikus dátum számítás.
        
        Args:
            time_range_text: Kiválasztott időtartam szöveg (pl. "5 év")
        """
        print(f"🚀 DEBUG: _on_time_range_changed: {time_range_text}")
        
        if self.date_mode == "time_range":
            self._update_computed_dates()
        
        # Fetch button state frissítése
        self._update_fetch_button_state()
    
    def _update_computed_dates(self):
        """
        🚀 Automatikus dátum számítás az időtartam dropdown alapján.
        
        TrendAnalyticsTab kompatibilis logika.
        """
        try:
            time_range_text = self.time_range_combo.currentText()
            
            # Évek számának kinyerése
            if "55 év" in time_range_text:
                years = 55
            elif "25 év" in time_range_text:
                years = 25
            elif "10 év" in time_range_text:
                years = 10
            elif "5 év" in time_range_text:
                years = 5
            else:
                years = 5  # Default fallback
            
            # Dátumok számítása
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=years * 365)
            
            # Info label frissítése
            self.computed_dates_info.setText(
                f"Számított időszak: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')} ({years} év)"
            )
            
            print(f"🚀 DEBUG: Computed dates updated: {start_date} → {end_date} ({years} years)")
            
        except Exception as e:
            print(f"❌ DEBUG: Computed dates update error: {e}")
            self.computed_dates_info.setText("Dátum számítási hiba")
    
    def _get_effective_date_range(self) -> tuple[str, str]:
        """
        🚀 Effektív dátum tartomány lekérdezése aktuális mód alapján.
        
        Returns:
            (start_date, end_date) ISO formátumban
        """
        if self.date_mode == "time_range":
            # Automatikus számítás
            time_range_text = self.time_range_combo.currentText()
            
            if "55 év" in time_range_text:
                years = 55
            elif "25 év" in time_range_text:
                years = 25
            elif "10 év" in time_range_text:
                years = 10
            elif "5 év" in time_range_text:
                years = 5
            else:
                years = 5  # Default
            
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
        🚀 ÚJ: N évet visszamenő dátum beállítása.
        
        Args:
            years: Évek száma
        """
        today = QDate.currentDate()
        start = today.addYears(-years)
        end = today
        
        self.start_date.setDate(start)
        self.end_date.setDate(end)
        
        print(f"🚀 DEBUG: Set {years} years back: {start.toString()} → {end.toString()}")
    
    # === WIDGET REGISZTRÁCIÓ ÉS THEMING ===
    
    def _register_widgets_for_theming(self) -> None:
        """
        Widget-ek regisztrálása ThemeManager-hez automatikus téma kezeléshez.
        🎨 PROFESSZIONÁLIS COLORPALETTE INTEGRÁCIÓ - minden widget automatikusan témázódik.
        """
        # === CONTAINER WIDGETS ===
        register_widget_for_theming(self, "container")
        
        # === 🌍 UNIVERSAL LOCATION SELECTOR ===
        register_widget_for_theming(self.universal_location_selector, "container")
        register_widget_for_theming(self.clear_location_btn, "button")
        
        # === 🚀 MULTI-YEAR BATCH UI ELEMEK ===
        register_widget_for_theming(self.time_range_radio, "input")
        register_widget_for_theming(self.manual_dates_radio, "input")
        register_widget_for_theming(self.time_range_combo, "input")
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
        
        print("🚀 DEBUG: ControlPanel MULTI-YEAR BATCH + LAYOUT JAVÍTVA - Professional ColorPalette integrálva")
    
    def _apply_professional_label_styling(self, label: QLabel, style_type: str) -> None:
        """
        🎨 PROFESSZIONÁLIS label styling alkalmazása ColorPalette API-val.
        
        Args:
            label: Címke widget
            style_type: Stílus típus ("primary", "secondary", "error", "success")
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
        # Dátumok validálása
        self.start_date.dateChanged.connect(self._validate_dates)
        self.end_date.dateChanged.connect(self._validate_dates)
        
        # 🔧 JAVÍTÁS: Kezdeti állapot
        self._update_fetch_button_state()
        
        # ✅ PROVIDER SELECTOR default values
        self._load_provider_preferences()
        
        print("🚀 DEBUG: Default values MULTI-YEAR BATCH + JAVÍTVA - fetch button state tracking")
    
    def _connect_internal_signals(self) -> None:
        """🔧 JAVÍTOTT belső signal-slot kapcsolatok - SIGNAL CHAIN JAVÍTÁS."""
        # Lokális hibák kezelése
        self.local_error_occurred.connect(self._show_local_error)
        
        # 🔧 KRITIKUS JAVÍTÁS: UNIVERSAL LOCATION SELECTOR signal kapcsolatok
        print("🔧 DEBUG: Connecting JAVÍTOTT UniversalLocationSelector signals...")
        
        # Search signal
        self.universal_location_selector.search_requested.connect(self.search_requested.emit)
        print("✅ DEBUG: UniversalLocationSelector.search_requested → ControlPanel.search_requested CONNECTED")
        
        # 🔧 KRITIKUS: City selection signal - JAVÍTOTT VERZIÓ
        self.universal_location_selector.city_selected.connect(self._on_location_selected_fixed)
        print("✅ DEBUG: UniversalLocationSelector.city_selected → ControlPanel._on_location_selected_fixed CONNECTED")
        
        # 🔧 KRITIKUS: Location change signal - JAVÍTOTT VERZIÓ  
        self.universal_location_selector.location_changed.connect(self._on_location_changed_fixed)
        print("✅ DEBUG: UniversalLocationSelector.location_changed → ControlPanel._on_location_changed_fixed CONNECTED")
        
        # === PROFESSZIONÁLIS THEMEMANAGER SIGNAL KAPCSOLATOK ===
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        
        if hasattr(self.theme_manager, 'color_scheme_updated'):
            self.theme_manager.color_scheme_updated.connect(self._on_color_scheme_updated)
        
        print("🚀 DEBUG: MULTI-YEAR BATCH + JAVÍTOTT signal connections kész")
    
    def _on_theme_changed(self, theme_name: str) -> None:
        """🎨 PROFESSZIONÁLIS téma változás kezelése."""
        print(f"🎨 DEBUG: ControlPanel JAVÍTOTT theme change: {theme_name}")
        
        # Label-ek újra-stílusozása
        self._apply_professional_label_styling(self.location_info_label, "secondary")
        self._apply_professional_label_styling(self.status_label, "primary")
        self._apply_professional_label_styling(self.computed_dates_info, "secondary")
        
        # ✅ PROVIDER SELECTOR labels újra-stílusozása
        self._refresh_provider_selector_styling()
    
    def _on_color_scheme_updated(self, color_palette) -> None:
        """🎨 PROFESSZIONÁLIS ColorPalette változás kezelése."""
        print("🎨 DEBUG: ControlPanel JAVÍTOTT ColorPalette updated")
        
        # Összes styling újra-alkalmazása
        self._apply_professional_label_styling(self.location_info_label, "secondary")
        self._apply_professional_label_styling(self.status_label, "primary")
        self._apply_professional_label_styling(self.computed_dates_info, "secondary")
        self._refresh_provider_selector_styling()
    
    # === 🔧 JAVÍTOTT UNIVERSAL LOCATION SELECTOR LOGIC ===
    
    def _on_location_selected_fixed(self, name: str, lat: float, lon: float, data: Dict[str, Any]):
        """
        🔧 JAVÍTOTT lokáció kiválasztás kezelése - SIGNAL CHAIN + FETCH BUTTON FIX.
        
        Args:
            name: Város neve
            lat: Szélesség
            lon: Hosszúság  
            data: Lokáció metadata
        """
        try:
            print(f"🔧 DEBUG: _on_location_selected_fixed called: {name} [{lat:.4f}, {lon:.4f}]")
            
            # 🔧 KRITIKUS JAVÍTÁS: current_city_data frissítése
            self.current_city_data = {
                "name": name,
                "latitude": lat,
                "longitude": lon,
                "display_name": name,
                **data
            }
            print(f"🔧 DEBUG: current_city_data FRISSÍTVE: {self.current_city_data['name']}")
            
            # Lokáció info frissítése
            self._update_location_info(name, lat, lon)
            
            # Clear gomb engedélyezése
            self.clear_location_btn.setEnabled(True)
            
            # 🔧 KRITIKUS JAVÍTÁS: Fetch button állapot frissítése
            self._update_fetch_button_state()
            print(f"🔧 DEBUG: Fetch button state frissítve: {self.fetch_button.isEnabled()}")
            
            # Signal továbbítása (kompatibilitás)
            self.city_selected.emit(name, lat, lon, data)
            
            # UI állapot frissítése
            self._update_status(f"Kiválasztva: {name}")
            
            print(f"✅ DEBUG: Location selection JAVÍTVA: {name} - fetch button enabled: {self.fetch_button.isEnabled()}")
            
        except Exception as e:
            print(f"❌ DEBUG: Lokáció kiválasztási hiba: {e}")
            self.local_error_occurred.emit("Lokáció kiválasztási hiba")
    
    def _on_location_changed_fixed(self, location: UniversalLocation):
        """
        🔧 JAVÍTOTT UniversalLocation objektum változás kezelése.
        
        Args:
            location: UniversalLocation objektum
        """
        try:
            print(f"🔧 DEBUG: _on_location_changed_fixed called: {location}")
            
            # UniversalLocation tárolása
            self.current_location = location
            
            # 🔧 KRITIKUS JAVÍTÁS: current_city_data frissítése UniversalLocation-ből
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
                print(f"🔧 DEBUG: current_city_data frissítve UniversalLocation-ből: {self.current_city_data['name']}")
                
                # Fetch button állapot frissítése
                self._update_fetch_button_state()
                print(f"🔧 DEBUG: Fetch button state: {self.fetch_button.isEnabled()}")
            
            # Signal továbbítása
            self.location_changed.emit(location)
            
            print(f"✅ DEBUG: UniversalLocation change JAVÍTVA: {location}")
            
        except Exception as e:
            print(f"❌ DEBUG: UniversalLocation változás hiba: {e}")
    
    def _update_location_info(self, name: str, lat: float, lon: float):
        """Lokáció információ megjelenítés frissítése."""
        info_text = f"📍 {name}\n🗺️ Koordináták: [{lat:.4f}, {lon:.4f}]"
        self.location_info_label.setText(info_text)
        self._apply_professional_label_styling(self.location_info_label, "primary")
    
    def _clear_location(self):
        """🔧 JAVÍTOTT lokáció kiválasztás törlése - FETCH BUTTON FIX."""
        try:
            print("🔧 DEBUG: _clear_location called")
            
            # UniversalLocationSelector törlése
            self.universal_location_selector.clear_selection()
            
            # 🔧 KRITIKUS JAVÍTÁS: Lokális állapot törlése
            self.current_location = None
            self.current_city_data = None
            print("🔧 DEBUG: current_city_data TÖRÖLVE")
            
            # UI elemek visszaállítása
            self.location_info_label.setText("Válasszon lokációt...")
            self._apply_professional_label_styling(self.location_info_label, "secondary")
            self.clear_location_btn.setEnabled(False)
            
            # 🔧 KRITIKUS: Fetch button állapot frissítése
            self._update_fetch_button_state()
            print(f"🔧 DEBUG: Fetch button disabled: {not self.fetch_button.isEnabled()}")
            
            self._update_status("Válasszon lokációt a kezdéshez")
            
            print("✅ DEBUG: Lokáció törlése JAVÍTVA")
            
        except Exception as e:
            print(f"❌ DEBUG: Lokáció törlési hiba: {e}")
    
    # === ✅ PROVIDER SELECTOR LOGIC (UNCHANGED) ===
    
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
    
    def _on_provider_changed(self, button) -> None:
        """Provider radio button változás kezelése."""
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
                
                print(f"🎛️ Provider changed to: {new_provider}")
                
        except Exception as e:
            print(f"❌ Error handling provider change: {e}")
    
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
            
            # Open-Meteo update (informational) - FRISSÍTVE MULTI-YEAR INFÓVAL
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
    
    # === 🚀 FRISSÍTETT WEATHER DATA REQUEST LOGIC - MULTI-YEAR BATCH TÁMOGATÁSSAL ===
    
    def _trigger_weather_fetch(self) -> None:
        """🚀 MULTI-YEAR BATCH TÁMOGATÁS: időjárási adatok lekérdezésének indítása - 1 ÉVES LIMIT ELTÁVOLÍTVA."""
        print("🚀 DEBUG: _trigger_weather_fetch called - MULTI-YEAR BATCH VALIDÁCIÓ")
        
        # 🔧 KRITIKUS VALIDÁCIÓ: Lokáció ellenőrzése
        if not self.current_city_data:
            error_msg = "Nincs kiválasztva lokáció"
            print(f"❌ DEBUG: {error_msg}")
            self.local_error_occurred.emit(error_msg)
            return
        
        if self.is_fetching:
            print("⚠️ DEBUG: Already fetching, ignoring request")
            return
        
        # 🔧 KRITIKUS: Dátumok és paraméterek összegyűjtése
        try:
            latitude = self.current_city_data.get("latitude", 0.0)
            longitude = self.current_city_data.get("longitude", 0.0)
            
            # 🚀 MULTI-YEAR BATCH: Effektív dátum tartomány lekérdezése
            start_date, end_date = self._get_effective_date_range()
            
            print(f"🚀 DEBUG: MULTI-YEAR BATCH params - lat: {latitude}, lon: {longitude}, {start_date} → {end_date}")
            
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
            print(f"🚀 DEBUG: Emitting MULTI-YEAR weather_data_requested signal...")
            self.weather_data_requested.emit(latitude, longitude, start_date, end_date, params)
            
            city_name = self.current_city_data.get("display_name", "Ismeretlen")
            provider_info = f"({self.current_provider})" if self.current_provider != "auto" else "(auto)"
            print(f"✅ DEBUG: MULTI-YEAR Weather data signal ELKÜLDVE: {city_name} {provider_info}")
            
        except Exception as e:
            print(f"❌ DEBUG: MULTI-YEAR Weather fetch hiba: {e}")
            self.local_error_occurred.emit(f"Lekérdezési hiba: {str(e)}")
    
    def _validate_date_range_multiyear(self, start_date: str, end_date: str) -> bool:
        """
        🚀 MULTI-YEAR BATCH: Dátum tartomány lokális validálása - 1 ÉVES LIMIT ELTÁVOLÍTVA!
        
        Args:
            start_date: Kezdő dátum ISO formátumban
            end_date: Befejező dátum ISO formátumban
            
        Returns:
            Validálási eredmény
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
        """🔧 JAVÍTOTT lekérdezés állapot beállítása."""
        print(f"🔧 DEBUG: _set_fetch_state: {fetching}")
        
        self.is_fetching = fetching
        
        # Vezérlők megjelenítése
        self.fetch_button.setVisible(not fetching)
        self.cancel_button.setVisible(fetching)
        
        # Progress bar
        self.progress_bar.setVisible(fetching)
        if fetching:
            self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Lokáció selector letiltása fetch közben
        self.universal_location_selector.setEnabled(not fetching)
        self.clear_location_btn.setEnabled(not fetching and self.current_city_data is not None)
        
        # 🚀 MULTI-YEAR BATCH vezérlők letiltása lekérdezés közben
        self.time_range_radio.setEnabled(not fetching)
        self.manual_dates_radio.setEnabled(not fetching)
        self.time_range_combo.setEnabled(not fetching and self.date_mode == "time_range")
        
        # Dátum vezérlők letiltása lekérdezés közben
        self.start_date.setEnabled(not fetching and self.date_mode == "manual_dates")
        self.end_date.setEnabled(not fetching and self.date_mode == "manual_dates")
        
        # ✅ PROVIDER SELECTOR vezérlők letiltása fetch közben
        self.auto_radio.setEnabled(not fetching)
        self.openmeteo_radio.setEnabled(not fetching)
        self.meteostat_radio.setEnabled(not fetching)
        
        print(f"✅ DEBUG: MULTI-YEAR Fetch state BEÁLLÍTVA: {fetching}")
    
    def _cancel_operations(self) -> None:
        """Műveletek megszakítása."""
        if self.is_fetching:
            # Worker manager megszakítás
            self.worker_manager.cancel_all()
            
            # UI állapot visszaállítása
            self._set_fetch_state(False)
            
            self._update_status("Műveletek megszakítva")
            print("🛑 Műveletek megszakítva")
    
    # === DÁTUM HELPER METÓDUSOK ===
    
    def _set_last_month(self) -> None:
        """Előző hónap beállítása."""
        today = QDate.currentDate()
        start = today.addMonths(-1).addDays(1 - today.day())  # Hónap első napja
        end = today.addDays(-today.day())  # Előző hónap utolsó napja
        
        self.start_date.setDate(start)
        self.end_date.setDate(end)
    
    def _set_last_year(self) -> None:
        """Előző év beállítása."""
        today = QDate.currentDate()
        start = QDate(today.year() - 1, 1, 1)
        end = QDate(today.year() - 1, 12, 31)
        
        self.start_date.setDate(start)
        self.end_date.setDate(end)
    
    def _validate_dates(self) -> None:
        """🔧 JAVÍTOTT dátumok validálása - FETCH BUTTON FRISSÍTÉSSEL."""
        start = self.start_date.date()
        end = self.end_date.date()
        
        if start > end:
            # Ha kezdő dátum nagyobb, automatikusan javítjuk
            if self.sender() == self.start_date:
                self.end_date.setDate(start)
            else:
                self.start_date.setDate(end)
        
        # 🔧 KRITIKUS: Fetch button állapot frissítése
        self._update_fetch_button_state()
    
    # === 🔧 JAVÍTOTT UI ÁLLAPOT KEZELÉS ===
    
    def _update_fetch_button_state(self) -> None:
        """🔧 JAVÍTOTT lekérdezés gomb állapotának frissítése - RÉSZLETES LOGGING."""
        has_location = self.current_city_data is not None
        
        # Dátum validáció a kiválasztott mód alapján
        if self.date_mode == "time_range":
            has_valid_dates = True  # Dropdown mindig valid
        else:
            has_valid_dates = self.start_date.date() <= self.end_date.date()
        
        should_enable = has_location and has_valid_dates and not self.is_fetching
        
        print(f"🚀 DEBUG: _update_fetch_button_state (MULTI-YEAR):")
        print(f"  has_location: {has_location} (current_city_data: {self.current_city_data is not None})")
        print(f"  date_mode: {self.date_mode}")
        print(f"  has_valid_dates: {has_valid_dates}")
        print(f"  is_fetching: {self.is_fetching}")
        print(f"  should_enable: {should_enable}")
        
        self.fetch_button.setEnabled(should_enable)
        
        # Debug location info
        if self.current_city_data:
            print(f"  location: {self.current_city_data.get('name', 'N/A')}")
        else:
            print(f"  location: None")
        
        # Debug date range info
        if self.date_mode == "time_range":
            print(f"  time_range: {self.time_range_combo.currentText()}")
        else:
            print(f"  manual_dates: {self.start_date.date().toString()} → {self.end_date.date().toString()}")
    
    def _update_status(self, message: str) -> None:
        """🎨 PROFESSZIONÁLIS állapot üzenet frissítése."""
        self.status_label.setText(message)
        self._apply_professional_label_styling(self.status_label, "primary")
    
    def _show_local_error(self, message: str) -> None:
        """🎨 PROFESSZIONÁLIS lokális hiba megjelenítése."""
        self.status_label.setText(f"❌ {message}")
        self._apply_professional_label_styling(self.status_label, "error")
        
        # 3 másodperc után visszaállítás
        QTimer.singleShot(3000, lambda: self._apply_professional_label_styling(self.status_label, "primary"))
    
    def _show_success_message(self, message: str) -> None:
        """🎨 PROFESSZIONÁLIS siker üzenet megjelenítése."""
        self.status_label.setText(f"✅ {message}")
        self._apply_professional_label_styling(self.status_label, "success")
        
        # 3 másodperc után visszaállítás
        QTimer.singleShot(3000, lambda: self._apply_professional_label_styling(self.status_label, "primary"))
    
    # === PUBLIKUS SLOT METÓDUSOK A CONTROLLER FELŐLI KOMMUNIKÁCIÓHOZ ===
    
    def _on_geocoding_completed(self, results: List[Dict[str, Any]]) -> None:
        """
        🌍 KOMPATIBILITÁS - Geocoding befejezés kezelése a Controller-től.
        UniversalLocationSelector már kezeli a keresést, de kompatibilitás miatt megtartva.
        """
        print(f"📍 DEBUG: _on_geocoding_completed called (COMPATIBILITY): {len(results)} results")
        
        if not results:
            self._update_status("Nem található település ezzel a névvel")
        else:
            self._update_status(f"{len(results)} település találat")
    
    def update_progress(self, worker_type: str, progress: int) -> None:
        """Progress frissítése a Controller-től."""
        if self.progress_bar.isVisible():
            if progress == 100:
                self.progress_bar.setVisible(False)
                self._set_fetch_state(False)
                self._update_usage_display()
            else:
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(progress)
        
        # Státusz frissítése - MULTI-YEAR BATCH info
        if progress < 100:
            provider_info = f"({self.current_provider})" if self.current_provider != "auto" else ""
            batch_info = ""
            if self.date_mode == "time_range":
                batch_info = f" [{self.time_range_combo.currentText()}]"
            self._update_status(f"⏳ {worker_type}: {progress}% {provider_info}{batch_info}")
    
    def update_status_from_controller(self, message: str) -> None:
        """Státusz frissítése a Controller-től."""
        self._update_status(message)
    
    def on_weather_data_completed(self) -> None:
        """Időjárási adatok lekérdezésének befejezése a Controller-től."""
        self._set_fetch_state(False)
        
        # MULTI-YEAR BATCH specifikus success message
        if self.date_mode == "time_range":
            time_range = self.time_range_combo.currentText()
            self._show_success_message(f"Multi-year adatok sikeresen lekérdezve ({time_range})")
        else:
            self._show_success_message("Adatok sikeresen lekérdezve")
            
        self._update_usage_display()
    
    def on_controller_error(self, error_message: str) -> None:
        """Hiba kezelése a Controller-től."""
        self._set_fetch_state(False)
        self._show_local_error(error_message)
    
    # === ✅ PROVIDER SELECTOR PUBLIKUS API (UNCHANGED) ===
    
    def update_usage_from_controller(self, usage_data: Dict[str, Any]) -> None:
        """Usage adatok frissítése a Controller-től."""
        self.usage_data = usage_data
        self._update_usage_display()
    
    def get_selected_provider(self) -> str:
        """Jelenleg kiválasztott provider lekérdezése."""
        return self.current_provider
    
    def set_provider(self, provider: str) -> None:
        """Provider beállítása programmatikusan."""
        if provider not in ProviderConfig.PROVIDERS:
            return
        
        self.current_provider = provider
        
        # Radio button frissítése
        if provider == "auto":
            self.auto_radio.setChecked(True)
        elif provider == "open-meteo":
            self.openmeteo_radio.setChecked(True)
        elif provider == "meteostat":
            self.meteostat_radio.setChecked(True)
        
        self._save_provider_preferences()
        self._update_status_for_provider_change(provider)
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Jelenlegi provider információk lekérdezése."""
        return {
            "selected_provider": self.current_provider,
            "provider_config": ProviderConfig.PROVIDERS.get(self.current_provider, {}),
            "usage_data": self.usage_data,
            "preferences": self.provider_preferences
        }
    
    # === 🌍 UNIVERSAL LOCATION SELECTOR PUBLIKUS API ===
    
    def get_current_location(self) -> Optional[UniversalLocation]:
        """🌍 ÚJ - Jelenlegi UniversalLocation objektum lekérdezése."""
        return self.current_location
    
    def set_location(self, location: UniversalLocation) -> None:
        """🌍 ÚJ - UniversalLocation beállítása programmatikusan."""
        try:
            self.universal_location_selector.set_current_location(location)
            # Az _on_location_changed_fixed automatikusan meghívódik
            
        except Exception as e:
            print(f"❌ Location beállítási hiba: {e}")
    
    def focus_location_search(self) -> None:
        """🌍 ÚJ - Fókusz a lokáció keresés fülre."""
        self.universal_location_selector.focus_search()
    
    # === 🚀 MULTI-YEAR BATCH PUBLIKUS API - ÚJ FUNKCIÓK ===
    
    def get_date_mode(self) -> str:
        """🚀 ÚJ - Jelenlegi dátum mód lekérdezése."""
        return self.date_mode
    
    def set_date_mode(self, mode: str) -> None:
        """
        🚀 ÚJ - Dátum mód beállítása programmatikusan.
        
        Args:
            mode: "time_range" vagy "manual_dates"
        """
        if mode == "time_range":
            self.time_range_radio.setChecked(True)
        elif mode == "manual_dates":
            self.manual_dates_radio.setChecked(True)
        
        self._on_date_mode_changed()
    
    def get_selected_time_range(self) -> str:
        """🚀 ÚJ - Kiválasztott időtartam lekérdezése."""
        return self.time_range_combo.currentText()
    
    def set_time_range(self, time_range: str) -> None:
        """
        🚀 ÚJ - Időtartam beállítása programmatikusan.
        
        Args:
            time_range: "5 év", "10 év", "25 év", vagy "55 év (teljes)"
        """
        self.time_range_combo.setCurrentText(time_range)
        self._on_time_range_changed(time_range)
    
    def get_computed_date_range(self) -> tuple[str, str]:
        """🚀 ÚJ - Számított dátum tartomány lekérdezése."""
        return self._get_effective_date_range()
    
    def is_multi_year_capable(self) -> bool:
        """🚀 ÚJ - Multi-year batch képesség ellenőrzése."""
        return True  # Ez a verzió támogatja
    
    def get_max_supported_years(self) -> int:
        """🚀 ÚJ - Maximum támogatott évek száma."""
        return 60  # Praktikus limit
    
    # === PUBLIKUS API (KOMPATIBILITÁS) ===
    
    def clear_selection(self) -> None:
        """Kiválasztás törlése."""
        self._clear_location()
    
    def set_enabled(self, enabled: bool) -> None:
        """Panel engedélyezése/letiltása."""
        self.setEnabled(enabled)
    
    def get_current_city_data(self) -> Optional[Dict[str, Any]]:
        """🔧 JAVÍTOTT jelenlegi kiválasztott város adatainak lekérdezése."""
        return self.current_city_data.copy() if self.current_city_data else None
    
    # === PROFESSZIONÁLIS THEMEMANAGER PUBLIKUS API ===
    
    def apply_theme(self, theme_name: str) -> None:
        """🎨 PROFESSZIONÁLIS téma alkalmazása a panel-re."""
        success = self.theme_manager.set_theme(theme_name)
        if success:
            print(f"🎨 DEBUG: ControlPanel Professional theme applied: {theme_name}")
        else:
            print(f"❌ DEBUG: ControlPanel Professional theme failed: {theme_name}")
    
    def get_current_theme(self) -> str:
        """Jelenlegi téma nevének lekérdezése."""
        return self.theme_manager.get_current_theme()
    
    def get_color_palette(self):
        """🎨 PROFESSZIONÁLIS API - ColorPalette objektum lekérdezése."""
        return self.theme_manager.get_color_scheme()
    
    def get_current_colors(self) -> Dict[str, str]:
        """🎨 PROFESSZIONÁLIS API - Jelenlegi színek lekérdezése."""
        return self.theme_manager.get_current_colors()
    
    def get_weather_colors(self) -> Dict[str, str]:
        """🌦️ PROFESSZIONÁLIS API - Időjárás-specifikus színek lekérdezése."""
        return self.theme_manager.get_weather_colors()


# Export
__all__ = ['ControlPanel']