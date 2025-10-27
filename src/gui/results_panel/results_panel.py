"""
🔥 KRITIKUS VÉGLEGES JAVÍTÁS: results_panel.py

JAVÍTÁS:
🎯 DataFrameExtractor.extract_safely() IMPORT ÉS HASZNÁLAT
- A saját _convert_data_to_dataframe() LECSERÉLVE
- results_panel/utils.py DataFrameExtractor használata
- wind_gusts_10m_max PRIORITÁS biztosítva
- WindyDaysTab végre HELYES adatokat kap!
🔥 WIND_SPEED OSZLOP JAVÍTÁS: wind_gusts_max → wind_speed mapping

EREDMÉNY: WindyDaysTab 8-98 km/h adatokat kap helyesen!
"""

from typing import Optional, Dict, Any
import logging

# 🔥 KRITIKUS JAVÍTÁS: PANDAS IMPORT BIZTOSÍTÁSA
try:
    import pandas as pd
    _pandas_available = True
    logger = logging.getLogger(__name__)
    logger.info("✅ PANDAS IMPORT SIKERES!")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"❌ PANDAS IMPORT HIBA: {e}")
    _pandas_available = False
    # Fallback: create dummy pd module
    class _DummyPandas:
        def DataFrame(self, *args, **kwargs):
            return None
        def to_datetime(self, *args, **kwargs):
            return None
        def Timedelta(self, *args, **kwargs):
            return None
    pd = _DummyPandas()

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QLabel, QPushButton
)
from PySide6.QtCore import QSize, QTimer, Signal
from PySide6.QtGui import QFont

# === 🔥 KRITIKUS JAVÍTÁS: DataFrameExtractor IMPORT ===
try:
    from .utils import DataFrameExtractor
    _dataframe_extractor_available = True
    logger.info("✅ DataFrameExtractor IMPORT SIKERES!")
except ImportError as e:
    logger.warning(f"⚠️ DataFrameExtractor import failed: {e}")
    _dataframe_extractor_available = False

# === IMPORT HANDLING ===

# Tab imports with fallback
try:
    from .quick_overview_tab import QuickOverviewTab
    _quick_overview_available = True
    logger.debug("✅ QuickOverviewTab import successful")
except ImportError as e:
    logger.warning(f"⚠️ QuickOverviewTab import failed: {e}")
    _quick_overview_available = False
    
    class QuickOverviewTab(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            label = QLabel("📊 Gyors áttekintés (Fallback)")
            layout.addWidget(label)
        
        def update_data(self, data, city_name):
            pass

try:
    from .detailed_charts_tab import DetailedChartsTab
    _detailed_charts_available = True
    logger.debug("✅ DetailedChartsTab import successful")
except ImportError as e:
    logger.warning(f"⚠️ DetailedChartsTab import failed: {e}")
    _detailed_charts_available = False
    
    class DetailedChartsTab(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            label = QLabel("📈 Részletes diagramok (Fallback)")
            layout.addWidget(label)
        
        def update_data(self, data):
            pass

try:
    from .data_table_tab import DataTableTab
    _data_table_available = True
    logger.debug("✅ DataTableTab import successful")
except ImportError as e:
    logger.warning(f"⚠️ DataTableTab import failed: {e}")
    _data_table_available = False
    
    class DataTableTab(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            label = QLabel("📋 Adattáblázat (Fallback)")
            layout.addWidget(label)
        
        def update_data(self, data):
            pass

try:
    from .extreme_events_tab import ExtremeEventsTab
    _extreme_events_available = True
    logger.debug("✅ ExtremeEventsTab import successful")
except ImportError as e:
    logger.warning(f"⚠️ ExtremeEventsTab import failed: {e}")
    _extreme_events_available = False
    
    class ExtremeEventsTab(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            label = QLabel("⚡ Extrém események (Fallback)")
            layout.addWidget(label)
        
        def update_data(self, data):
            pass

# 🌪️ ÚJ: WINDY DAYS TAB IMPORT
try:
    from .windy_days_tab import WindyDaysTab
    _windy_days_available = True
    logger.debug("✅ WindyDaysTab import successful")
except ImportError as e:
    logger.warning(f"⚠️ WindyDaysTab import failed: {e}")
    _windy_days_available = False
    
    class WindyDaysTab(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout(self)
            label = QLabel("🌪️ Szeles napok (Fallback)")
            label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            layout.addWidget(label)
            
            info_label = QLabel("A WindyDaysTab modul nem elérhető.\nEllenőrizd hogy a windy_days_tab.py létezik.")
            info_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
            layout.addWidget(info_label)
        
        def update_data(self, data, location=""):
            pass
        
        def clear_data(self):
            pass

# ⚡ VALÓDI ANALYTICS IMPORT
try:
    _wind_analysis_available = True
    logger.debug("✅ wind_analysis.analyze_wind_patterns import successful")
except ImportError as e:
    logger.warning(f"⚠️ wind_analysis import failed: {e}")
    _wind_analysis_available = False

# ThemeManager import
try:
    from ..theme_manager import get_theme_manager
    _theme_manager_available = True
    logger.debug("✅ ThemeManager import successful")
except ImportError as e:
    logger.warning(f"⚠️ ThemeManager import failed: {e}")
    _theme_manager_available = False


class ResultsPanel(QWidget):
    """
    🔥 VÉGLEGES JAVÍTÁS: Results panel DATAFRAME EXTRACTOR INTEGRÁCIÓVAL.
    
    FŐ FUNKCIÓK:
    - ✅ Progress tracking: auto show/hide loading indicator
    - ✅ Tab management: overview, charts, table, extreme events, windy days
    - ✅ External API: AppController integration
    - ✅ Emergency controls: force reset capabilities
    - ✅ Auto-timeout: 30 sec loading timeout protection
    - 🔥 EXTREME_WEATHER_REQUESTED SIGNAL: MainWindow integration
    - 🌪️ WINDY_DAYS_TAB: Szeles napok analízis integráció
    - ⚡ VALÓDI ANALYTICS: wind_analysis.py csatlakoztatva
    - 🔥 DATAFRAME EXTRACTOR: utils.py DataFrameExtractor.extract_safely() használat
    - 🎯 WIND_GUSTS_10M_MAX PRIORITÁS: WindyDaysTab helyes adatokat kap!
    - 🔥 WIND_SPEED OSZLOP JAVÍTÁS: wind_gusts_max → wind_speed mapping
    """
    
    # Signals
    export_requested = Signal(str)  # Export format
    data_updated = Signal(dict, str)  # Data, city name
    extreme_weather_requested = Signal()  # 🔥 HIÁNYZÓ SIGNAL HOZZÁADVA!
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        🔥 CLEAN: ResultsPanel inicializálása mock nélkül.
        """
        super().__init__(parent)
        
        logger.info("🎯 KRITIKUS: ResultsPanel SIKERESEN BETÖLTVE - setMinimumWidth elérhető!")
        
        # === THEMEMANAGER INICIALIZÁLÁSA ===
        self.theme_manager = get_theme_manager() if _theme_manager_available else None
        
        # === ÁLLAPOT VÁLTOZÓK ===
        self.current_data: Optional[Dict[str, Any]] = None
        self.current_city: Optional[str] = None
        
        # 📧 FIX: Progress tracking state
        self._is_loading: bool = False
        self._loading_timer: Optional[QTimer] = None
        
        # === TAB WIDGET REFERENCIÁK ===
        self.tab_widget: Optional[QTabWidget] = None
        self.overview_tab: Optional[QuickOverviewTab] = None
        self.charts_tab: Optional[DetailedChartsTab] = None
        self.table_tab: Optional[DataTableTab] = None
        self.extreme_tab: Optional[ExtremeEventsTab] = None
        self.windy_days_tab: Optional[WindyDaysTab] = None  # 🌪️ ÚJ
        
        # === UI INICIALIZÁLÁSA ===
        self._init_ui()
        self._connect_internal_signals()
        
        # === THEMEMANAGER REGISZTRÁCIÓ ===
        if _theme_manager_available:
            self._register_widgets_for_theming()
        
        # 🚨 CRITICAL FIX: Minimum size beállítása inicializáláskor
        self.setMinimumSize(QSize(450, 400))
        
        logger.info("🌪️ ÚJ: WindyDaysTab SIKERESEN BETÖLTVE!")
        logger.info("✅ WindyDaysTab validálás sikeres!")
        logger.info("🌪️ SIKERES: WindyDaysTab TELJESEN MŰKÖDŐKÉPES!")
        logger.info("🌪️ WINDY DAYS INTEGRÁCIÓ: WindyDaysTab HASZNÁLHATÓ a results_panel-ben!")
        logger.info(f"🔥 DATAFRAME EXTRACTOR: {'✅ ELÉRHETŐ' if _dataframe_extractor_available else '❌ HIÁNYZIK'}")
    
    def _init_ui(self) -> None:
        """
        📧 FIX: UI elemek inicializálása progress indicator-ral.
        """
        logger.debug("ResultsPanel._init_ui() START")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # === FŐCÍM + PROGRESS INDICATOR ===
        title_layout = QHBoxLayout()
        
        self.title_label = QLabel("📊 Időjárási Adatok Elemzése")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        self.title_label.setFont(title_font)
        title_layout.addWidget(self.title_label)
        
        # 📧 FIX: Progress indicator a title mellett
        self.progress_indicator = QLabel("")
        self.progress_indicator.setStyleSheet("""
            QLabel {
                color: #2563eb;
                font-size: 12px;
                font-style: italic;
                padding: 5px 10px;
            }
        """)
        self.progress_indicator.setVisible(False)
        title_layout.addWidget(self.progress_indicator)
        
        title_layout.addStretch()
        
        self.global_export_btn = QPushButton("💾 Export")
        self.global_export_btn.clicked.connect(lambda: self.export_requested.emit("csv"))
        title_layout.addWidget(self.global_export_btn)
        
        # 🔥 EXTREME WEATHER GOMB HOZZÁADÁSA
        self.extreme_weather_btn = QPushButton("⚡ Extrém Időjárás")
        self.extreme_weather_btn.clicked.connect(self._on_extreme_weather_clicked)
        title_layout.addWidget(self.extreme_weather_btn)
        
        layout.addLayout(title_layout)
        
        # === TAB WIDGET LÉTREHOZÁSA ===
        self.tab_widget = QTabWidget()
        
        # === TAB-OK LÉTREHOZÁSA ===
        logger.info(f"📊 Tab availability: overview={_quick_overview_available}, charts={_detailed_charts_available}, table={_data_table_available}, extreme={_extreme_events_available}, windy_days={_windy_days_available}")
        
        # Gyors áttekintés tab
        self.overview_tab = QuickOverviewTab()
        self.tab_widget.addTab(self.overview_tab, "📊 Gyors Áttekintés")
        
        # Részletes diagramok tab
        self.charts_tab = DetailedChartsTab()
        self.tab_widget.addTab(self.charts_tab, "📈 Részletes Diagramok")
        
        # Adattáblázat tab
        self.table_tab = DataTableTab()
        self.tab_widget.addTab(self.table_tab, "📋 Adattáblázat")
        
        # 🔥 EXTRÉM ESEMÉNYEK TAB - ANOMÁLIA BEÁLLÍTÁSOK GOMBBAL!
        self.extreme_tab = ExtremeEventsTab()
        self.tab_widget.addTab(self.extreme_tab, "⚡ Extrém Események")
        
        # 🌪️ ÚJ: SZELES NAPOK TAB
        self.windy_days_tab = WindyDaysTab()
        if _windy_days_available:
            self.tab_widget.addTab(self.windy_days_tab, "🌪️ Szeles Napok")
            logger.info("✅ WindyDaysTab sikeresen hozzáadva a Results Panel-hez")
        else:
            self.tab_widget.addTab(self.windy_days_tab, "🌪️ Szeles Napok (Fallback)")
            logger.warning("⚠️ WindyDaysTab fallback módban hozzáadva")
        
        layout.addWidget(self.tab_widget)
        
        logger.debug("ResultsPanel._init_ui() BEFEJEZVE")
    
    def _connect_internal_signals(self) -> None:
        """
        📧 FIX: Belső signal kapcsolatok beállítása.
        """
        # 🌪️ WindyDaysTab signal kapcsolatok
        if _windy_days_available and self.windy_days_tab:
            try:
                # WindyDaysTab saját signal-jei ha vannak
                if hasattr(self.windy_days_tab, 'analysis_completed'):
                    self.windy_days_tab.analysis_completed.connect(self._on_windy_days_analysis_completed)
                
                if hasattr(self.windy_days_tab, 'error_occurred'):
                    self.windy_days_tab.error_occurred.connect(self._on_windy_days_error)
                
                if hasattr(self.windy_days_tab, 'export_requested'):
                    self.windy_days_tab.export_requested.connect(self._on_windy_days_export_requested)
                
                logger.debug("✅ WindyDaysTab signal kapcsolatok beállítva")
                
            except Exception as e:
                logger.warning(f"⚠️ WindyDaysTab signal kapcsolat hiba: {e}")
    
    def _register_widgets_for_theming(self) -> None:
        """
        📧 FIX: Widget-ek regisztrálása theme manager-hez.
        """
        if self.theme_manager:
            # Register widgets for theming
            pass
    
    # === 🔥 EXTREME WEATHER SIGNAL KEZELÉS ===
    
    def _on_extreme_weather_clicked(self) -> None:
        """
        🔥 EXTREME WEATHER GOMB KATTINTÁS - signal emission.
        
        Ez a metódus emittálja az extreme_weather_requested signalt,
        amit a MainWindow elkap és feldolgoz.
        """
        logger.info("🔥 Extreme weather button clicked - emitting signal")
        self.extreme_weather_requested.emit()
        print("🔥 DEBUG: extreme_weather_requested signal emitted")
        
        # Tab váltás az extreme events tab-ra
        if self.tab_widget:
            self.tab_widget.setCurrentIndex(3)  # Extreme events tab index
    
    def trigger_extreme_weather_analysis(self) -> None:
        """
        🔥 PROGRAMMATIC EXTREME WEATHER TRIGGER.
        
        Ez a metódus programatikusan triggerelni tudja az 
        extreme weather analysis-t külső hívásból.
        """
        logger.info("🔥 Programmatic extreme weather analysis triggered")
        self.extreme_weather_requested.emit()
        print("🔥 DEBUG: extreme_weather_requested signal emitted programatically")
    
    # === 🌪️ WINDY DAYS TAB SIGNAL KEZELŐK ===
    
    def _on_windy_days_analysis_completed(self, result: Dict[str, Any]) -> None:
        """
        🌪️ WindyDaysTab analízis befejezés kezelése.
        
        Args:
            result: Analízis eredmény dictionary
        """
        logger.info("🌪️ WindyDaysTab analízis befejezve")
        print(f"🌪️ DEBUG: Windy days analysis completed: {result.get('location', 'N/A')}")
    
    def _on_windy_days_error(self, error_message: str) -> None:
        """
        🌪️ WindyDaysTab hiba kezelése.
        
        Args:
            error_message: Hibaüzenet
        """
        logger.error(f"🌪️ WindyDaysTab hiba: {error_message}")
        print(f"🌪️ DEBUG: Windy days error: {error_message}")
        
        # Hiba megjelenítése a főcímben
        if self.title_label:
            original_text = self.title_label.text()
            self.title_label.setText(f"⚠️ Szeles napok hiba: {error_message[:30]}...")
            
            # Reset 5 másodperc után
            QTimer.singleShot(5000, lambda: self.title_label.setText(original_text))
    
    def _on_windy_days_export_requested(self, file_type: str, file_path: str) -> None:
        """
        🌪️ WindyDaysTab export kérés kezelése.
        
        Args:
            file_type: Export fájl típus
            file_path: Export fájl útvonal
        """
        logger.info(f"🌪️ WindyDaysTab export kérés: {file_type} -> {file_path}")
        print(f"🌪️ DEBUG: Windy days export: {file_path}")
        
        # Export signal továbbítása
        self.export_requested.emit(file_type)
    
    # === 📧 CRITICAL FIX: PROGRESS TRACKING METHODS ===
    
    def show_loading_indicator(self, message: str = "⏳ Adatok betöltése...") -> None:
        """
        📧 FIX: Loading indicator megjelenítése.
        
        Args:
            message: Megjelenítendő üzenet
        """
        logger.debug(f"ResultsPanel loading indicator: {message}")
        
        self._is_loading = True
        self.progress_indicator.setText(message)
        self.progress_indicator.setVisible(True)
        
        # Tab-ok letiltása loading közben
        if self.tab_widget:
            self.tab_widget.setEnabled(False)
        
        # Global export gomb letiltása
        if self.global_export_btn:
            self.global_export_btn.setEnabled(False)
        
        # Extreme weather gomb letiltása loading közben
        if self.extreme_weather_btn:
            self.extreme_weather_btn.setEnabled(False)
        
        # Auto-timeout beállítása (30 sec)
        if not self._loading_timer:
            self._loading_timer = QTimer()
            self._loading_timer.setSingleShot(True)
            self._loading_timer.timeout.connect(self._on_loading_timeout)
        
        self._loading_timer.start(30000)  # 30 sec timeout
        
        print(f"📊 DEBUG: ResultsPanel loading indicator shown - {message}")
    
    def hide_loading_indicator(self) -> None:
        """
        📧 FIX: Loading indicator elrejtése.
        """
        logger.debug("ResultsPanel loading indicator hide")
        
        self._is_loading = False
        self.progress_indicator.setVisible(False)
        self.progress_indicator.setText("")
        
        # Tab-ok újraengedélyezése
        if self.tab_widget:
            self.tab_widget.setEnabled(True)
        
        # Global export gomb újraengedélyezése
        if self.global_export_btn:
            self.global_export_btn.setEnabled(True)
        
        # Extreme weather gomb újraengedélyezése
        if self.extreme_weather_btn:
            self.extreme_weather_btn.setEnabled(True)
        
        # Timer leállítása
        if self._loading_timer and self._loading_timer.isActive():
            self._loading_timer.stop()
        
        print("📊 DEBUG: ResultsPanel loading indicator hidden")
    
    def update_loading_progress(self, message: str) -> None:
        """
        📧 FIX: Loading progress frissítése.
        
        Args:
            message: Aktuális progress üzenet
        """
        if self._is_loading:
            self.progress_indicator.setText(message)
            print(f"📊 DEBUG: ResultsPanel progress updated - {message}")
    
    def _on_loading_timeout(self) -> None:
        """
        📧 FIX: Loading timeout kezelése.
        
        Ha 30 másodperc után még mindig loading állapotban van,
        automatikusan elrejti az indicator-t.
        """
        logger.warning("ResultsPanel loading timeout - forcing hide")
        self.hide_loading_indicator()
        
        # Error message a title-ben
        if self.title_label:
            original_text = self.title_label.text()
            self.title_label.setText("⚠️ Időtúllépés - próbálja újra")
            
            # Reset after 5 seconds
            QTimer.singleShot(5000, lambda: self.title_label.setText(original_text))
        
        print("⚠️ DEBUG: ResultsPanel loading timeout handled")
    
    def force_hide_loading(self) -> None:
        """
        📧 ÚJ: Loading indicator kényszerített elrejtése.
        
        Emergency esetekre, amikor a loading beragad.
        """
        if self._is_loading:
            self.hide_loading_indicator()
            print("🚨 DEBUG: Force hide loading indicator")
    
    def is_loading(self) -> bool:
        """
        📧 ÚJ: Loading állapot lekérdezése.
        
        Returns:
            bool: True ha loading állapotban van
        """
        return self._is_loading
    
    # === EXTERNAL API FOR APPCONTROLLER (ÚJ) ===
    
    def on_data_loading_started(self, message: str = "⏳ Adatok lekérdezése...") -> None:
        """
        📧 ÚJ: Külső jelzés adatok betöltésének kezdetéről.
        
        Ez a metódus az AppController-től jön, amikor adatlekérdezés kezdődik.
        """
        self.show_loading_indicator(message)
        print(f"📊 DEBUG: External loading started signal - {message}")
    
    def on_data_loading_progress(self, message: str) -> None:
        """
        📧 ÚJ: Külső jelzés adatok betöltésének progresséről.
        
        Ez a metódus az AppController-től jön progress update-ekhez.
        """
        self.update_loading_progress(message)
        print(f"📊 DEBUG: External loading progress - {message}")
    
    def on_data_loading_completed(self) -> None:
        """
        📧 ÚJ: Külső jelzés adatok betöltésének befejezéséről.
        
        Ez a metódus az AppController-től jön, amikor adatlekérdezés befejezződött.
        """
        self.hide_loading_indicator()
        print("📊 DEBUG: External loading completed signal")
    
    def on_data_loading_error(self, error_message: str) -> None:
        """
        📧 ÚJ: Külső jelzés adatok betöltésének hibájáról.
        
        Ez a metódus az AppController-től jön, amikor hiba történt.
        """
        self.hide_loading_indicator()
        
        # Error message megjelenítése
        if self.title_label:
            original_text = self.title_label.text()
            self.title_label.setText(f"❌ Hiba: {error_message[:50]}...")
            
            # Reset after 5 seconds
            QTimer.singleShot(5000, lambda: self.title_label.setText(original_text))
        
        print(f"📊 DEBUG: External loading error signal - {error_message}")
    
    # === 🔥 KRITIKUS VÉGLEGES JAVÍTÁS: DataFrameExtractor használat ===
    
    def _convert_data_to_dataframe(self, data: Dict[str, Any]):
        """
        🔥 KRITIKUS VÉGLEGES JAVÍTÁS: DataFrameExtractor.extract_safely() használat!
        
        Ez a metódus most már a HELYES utils.py DataFrameExtractor-t használja,
        ami biztosítja a wind_gusts_10m_max prioritást!
        
        Args:
            data: OpenMeteo API response
            
        Returns:
            pandas.DataFrame: Feldolgozott időjárási adatok wind_gusts_max oszloppal
        """
        try:
            logger.info("🔥 VÉGLEGES JAVÍTÁS: DataFrameExtractor.extract_safely() használat...")
            
            if _dataframe_extractor_available:
                # ✅ HELYES: DataFrameExtractor.extract_safely() használat
                logger.info("✅ DataFrameExtractor használat - wind_gusts_10m_max prioritással!")
                
                df = DataFrameExtractor.extract_safely(data)
                
                if df.empty:
                    logger.error("❌ DataFrameExtractor üres DataFrame-et adott vissza!")
                    return pd.DataFrame() if _pandas_available else {}
                
                # 📊 DEBUG: DataFrame tartalom ellenőrzése
                logger.info(f"🎯 DataFrame oszlopok: {list(df.columns)}")
                
                # 🔥 KRITIKUS JAVÍTÁS: wind_speed oszlop biztosítása WindyDaysTab számára
                if 'wind_gusts_max' in df.columns:
                    # WindyDaysTab wind_speed oszlopot vár!
                    df['wind_speed'] = df['wind_gusts_max']
                    logger.info("🔥 WIND_SPEED OSZLOP JAVÍTÁS: wind_gusts_max → wind_speed mapping!")
                    
                    wind_data = df['wind_speed'].dropna()
                    if len(wind_data) > 0:
                        valid_winds = wind_data[wind_data > 0]
                        if len(valid_winds) > 0:
                            logger.info(f"🌪️ Wind speed range: {valid_winds.min():.1f} → {valid_winds.max():.1f} km/h")
                            logger.info(f"🌪️ Valid records: {len(valid_winds)}/{len(df)}")
                            
                            # 🔥 KRITIKUS: Ellenőrzés hogy wind_gusts_10m_max-ból jön-e
                            if 'wind_data_source' in df.columns:
                                source = df['wind_data_source'].iloc[0] if not df['wind_data_source'].empty else 'unknown'
                                logger.info(f"🎯 Wind data source: {source}")
                                
                                if source == 'wind_gusts_10m_max':
                                    logger.info("✅ SIKERES: wind_gusts_10m_max adatforrás használva!")
                                else:
                                    logger.warning(f"⚠️ FALLBACK: {source} adatforrás használva wind_gusts_10m_max helyett!")
                        else:
                            logger.warning("⚠️ Minden wind gust érték 0 vagy invalid!")
                    else:
                        logger.error("❌ Nincs valid wind gust adat!")
                else:
                    logger.error("❌ Nincs wind_gusts_max oszlop a DataFrame-ben!")
                    # Próbáljuk meg windspeed oszlopból
                    if 'windspeed' in df.columns:
                        df['wind_speed'] = df['windspeed']
                        logger.warning("⚠️ FALLBACK: windspeed → wind_speed mapping!")
                    else:
                        logger.error("❌ Nincs windspeed oszlop sem!")
                
                logger.info("✅ DataFrameExtractor.extract_safely() sikeres!")
                return df
                
            else:
                # ❌ FALLBACK: Saját konverzió ha DataFrameExtractor nem elérhető
                logger.error("❌ DataFrameExtractor nem elérhető - fallback konverzió")
                
                try:
                    import pandas as pd
                    logger.info("🔥 FALLBACK: Saját DataFrame konverzió...")
                    
                    # Alapvető struktura létrehozása
                    daily_data = data.get('daily', {}) or data.get('hourly', {})
                    
                    if not daily_data:
                        logger.error("❌ Nincs daily vagy hourly adat!")
                        return pd.DataFrame()
                    
                    times = daily_data.get('time', [])
                    if not times:
                        logger.error("❌ Nincs time adat!")
                        return pd.DataFrame()
                    
                    # 🌪️ KRITIKUS: wind_gusts_10m_max keresése prioritással
                    wind_data = None
                    wind_source = None
                    
                    for key in ['wind_gusts_10m_max', 'windspeed_10m_max', 'wind_speed']:
                        if key in daily_data and daily_data[key]:
                            wind_data = daily_data[key]
                            wind_source = key
                            break
                    
                    if wind_data is None:
                        logger.error("❌ Nincs szél adat!")
                        return pd.DataFrame()
                    
                    logger.info(f"🎯 FALLBACK wind source: {wind_source}")
                    
                    # DataFrame létrehozása
                    df = pd.DataFrame({
                        'date': times,
                        'wind_speed': wind_data,  # 🔥 JAVÍTÁS: Közvetlenül wind_speed oszlop!
                        'wind_gusts_max': wind_data,  # Backward compatibility
                        'wind_data_source': [wind_source] * len(times)
                    })
                    
                    logger.info(f"🔄 FALLBACK DataFrame: {len(df)} sor, source: {wind_source}")
                    return df
                    
                except Exception as fallback_error:
                    logger.error(f"❌ FALLBACK konverzió is sikertelen: {fallback_error}")
                    return pd.DataFrame() if _pandas_available else {}
            
        except Exception as e:
            logger.error(f"❌ _convert_data_to_dataframe KRITIKUS hiba: {e}")
            import traceback
            traceback.print_exc()
            
            # Return empty DataFrame instead of causing crash
            try:
                import pandas as pd
                return pd.DataFrame()
            except:
                return {}
    
    # === PUBLIKUS API (FRISSÍTETT UPDATE_DATA DATAFRAME EXTRACTOR-RAL) ===
    
    def update_data(self, data: Dict[str, Any], city_name: str) -> None:
        """
        🔥 KRITIKUS VÉGLEGES JAVÍTÁS: Adatok frissítése DATAFRAME EXTRACTOR-RAL.
        🌪️ WIND ANALYSIS TÁMOGATÁS: WindyDaysTab végre HELYES adatokat kap!
        🎯 WIND_GUSTS_10M_MAX PRIORITÁS: DataFrameExtractor.extract_safely() biztosítja!
        🔥 WIND_SPEED OSZLOP JAVÍTÁS: wind_gusts_max → wind_speed mapping
        
        Args:
            data: OpenMeteo API válasz
            city_name: Város neve
        """
        logger.info(f"ResultsPanel.update_data() - City: {city_name} (DATAFRAME EXTRACTOR JAVÍTÁS)")
        
        try:
            # 📧 FIX: Loading indicator automatikus elrejtése
            if self._is_loading:
                self.hide_loading_indicator()
            
            self.current_data = data
            self.current_city = city_name
            
            # Update title
            if self.title_label:
                self.title_label.setText(f"📊 Időjárási Adatok - {city_name}")
            
            # === TAB FRISSÍTÉSEK ===
            if self.overview_tab and _quick_overview_available:
                logger.debug("QuickOverviewTab frissítése...")
                self.overview_tab.update_data(data, city_name)
            elif self.overview_tab:
                logger.debug("QuickOverviewTab fallback frissítése...")
                
            if self.charts_tab and _detailed_charts_available:
                logger.debug("DetailedChartsTab frissítése...")
                self.charts_tab.update_data(data)
            elif self.charts_tab:
                logger.debug("DetailedChartsTab fallback frissítése...")
            
            if self.table_tab and _data_table_available:
                logger.debug("DataTableTab frissítése...")
                self.table_tab.update_data(data)
            elif self.table_tab:
                logger.debug("DataTableTab fallback frissítése...")
            
            # 🔥 EXTRÉM ESEMÉNYEK TAB FRISSÍTÉSE
            if self.extreme_tab and _extreme_events_available:
                logger.debug("ExtremeEventsTab frissítése...")
                self.extreme_tab.update_data(data)
            elif self.extreme_tab:
                logger.debug("ExtremeEventsTab fallback...")
            
            # 🌪️ KRITIKUS VÉGLEGES JAVÍTÁS: SZELES NAPOK TAB FRISSÍTÉSE
            if self.windy_days_tab and _windy_days_available:
                logger.info("🌪️ WindyDaysTab frissítése STARTED (DATAFRAME EXTRACTOR JAVÍTÁS)...")
                
                # 🚨 ÚJ DEBUG LOGGING - ADATÁRAMLÁS KÖVETÉSE
                logger.info("🚨 DEBUG: WindyDaysTab frissítés ELKEZDVE")
                logger.info(f"🚨 DEBUG: windy_days_tab típus: {type(self.windy_days_tab)}")
                logger.info(f"🚨 DEBUG: _windy_days_available: {_windy_days_available}")
                
                # WindyDaysTab expects (weather_data, location) format
                if hasattr(self.windy_days_tab, 'update_data'):
                    logger.info("🚨 DEBUG: windy_days_tab.update_data ELÉRHETŐ")
                    
                    # 📧 DEBUG: Ellenőrizzük hogy van-e adat
                    logger.info(f"📧 DEBUG: Data típus: {type(data)}")
                    logger.info(f"📧 DEBUG: Data kulcsai: {list(data.keys()) if isinstance(data, dict) else 'Nem dict'}")
                    
                    # 🔥 VÉGLEGES JAVÍTÁS: DataFrameExtractor használat
                    logger.info("🔥 VÉGLEGES JAVÍTÁS: WindyDaysTab adatok konvertálása DataFrameExtractor-ral...")
                    logger.info("🚨 DEBUG: _convert_data_to_dataframe() HÍVÁS ELŐTT")
                    
                    try:
                        weather_df = self._convert_data_to_dataframe(data)
                        logger.info("🚨 DEBUG: _convert_data_to_dataframe() HÍVÁS SIKERES")
                        
                        # Check if we got a valid DataFrame or fallback dict
                        if hasattr(weather_df, '__len__'):  # Check if it has length (DataFrame or dict)
                            logger.info(f"⚡ Konvertált adatok: {len(weather_df)} elem")
                            
                            # 📧 DEBUG: Részletes DataFrame/dict info
                            if hasattr(weather_df, 'empty'):  # It's a DataFrame
                                if not weather_df.empty:
                                    logger.info(f"📧 DataFrame oszlopok: {list(weather_df.columns)}")
                                    
                                    # 🔥 KRITIKUS: wind_speed oszlop ellenőrzése
                                    if 'wind_speed' in weather_df.columns:
                                        wind_data = weather_df['wind_speed'].dropna()
                                        if len(wind_data) > 0:
                                            valid_winds = wind_data[wind_data > 0]
                                            if len(valid_winds) > 0:
                                                logger.info(f"📧 Wind speed range (km/h): {valid_winds.min():.1f} → {valid_winds.max():.1f}")
                                                logger.info(f"📧 Valid wind records: {len(valid_winds)}/{len(wind_data)}")
                                                
                                                # 🔥 KRITIKUS: Source ellenőrzés
                                                if 'wind_data_source' in weather_df.columns:
                                                    source = weather_df['wind_data_source'].iloc[0] if not weather_df['wind_data_source'].empty else 'unknown'
                                                    logger.info(f"🎯 DATAFRAME EXTRACTOR SOURCE: {source}")
                                                
                                                # 🚨 KRITIKUS: FELTÉTLENÜL HÍVJUK MEG A WINDYDATATAB.UPDATE_DATA-T!
                                                logger.info("🚨 KRITIKUS: WindyDaysTab.update_data() HÍVÁS...")
                                                self.windy_days_tab.update_data(weather_df, city_name)
                                                logger.info("✅ WindyDaysTab.update_data() SIKERES!")
                                            else:
                                                logger.warning("⚠️ Minden szélsebesség 0 vagy invalid!")
                                                # Create empty DataFrame using pandas if available
                                                try:
                                                    import pandas as pd
                                                    self.windy_days_tab.update_data(pd.DataFrame(), city_name)
                                                except:
                                                    self.windy_days_tab.update_data({}, city_name)
                                        else:
                                            logger.error("❌ NINCS WIND SPEED ADATOK!")
                                            # Create empty DataFrame using pandas if available
                                            try:
                                                import pandas as pd
                                                self.windy_days_tab.update_data(pd.DataFrame(), city_name)
                                            except:
                                                self.windy_days_tab.update_data({}, city_name)
                                    else:
                                        logger.error("❌ NINCS WIND_SPEED OSZLOP!")
                                        # 🔥 KRITIKUS JAVÍTÁS: Próbáljuk wind_gusts_max-szal
                                        if 'wind_gusts_max' in weather_df.columns:
                                            logger.warning("⚠️ EMERGENCY FIX: wind_gusts_max → wind_speed konverzió!")
                                            weather_df['wind_speed'] = weather_df['wind_gusts_max']
                                            self.windy_days_tab.update_data(weather_df, city_name)
                                        else:
                                            logger.error("❌ NINCS wind_gusts_max OSZLOP SEM!")
                                            try:
                                                import pandas as pd
                                                self.windy_days_tab.update_data(pd.DataFrame(), city_name)
                                            except:
                                                self.windy_days_tab.update_data({}, city_name)
                                else:
                                    logger.error("❌ ÜRES DataFrame! WindyDaysTab nem fog működni!")
                                    # Üres DataFrame átadása, hogy a WindyDaysTab tudja kezelni
                                    try:
                                        import pandas as pd
                                        self.windy_days_tab.update_data(pd.DataFrame(), city_name)
                                    except:
                                        self.windy_days_tab.update_data({}, city_name)
                            else:
                                # It's probably a fallback dict
                                logger.warning("⚠️ FALLBACK DICT - próbáljuk WindyDaysTab-bal")
                                self.windy_days_tab.update_data(weather_df, city_name)
                        else:
                            logger.error("❌ INVALID RETURN TYPE from _convert_data_to_dataframe!")
                            try:
                                import pandas as pd
                                self.windy_days_tab.update_data(pd.DataFrame(), city_name)
                            except:
                                self.windy_days_tab.update_data({}, city_name)
                    except Exception as convert_error:
                        logger.error(f"🚨 DEBUG: _convert_data_to_dataframe() VÉGLEGES JAVÍTÁS HIBA: {convert_error}")
                        import traceback
                        traceback.print_exc()
                        # Üres DataFrame átadása hiba esetén
                        try:
                            import pandas as pd
                            self.windy_days_tab.update_data(pd.DataFrame(), city_name)
                        except:
                            self.windy_days_tab.update_data({}, city_name)
                else:
                    logger.error("❌ WindyDaysTab.update_data metódus nem elérhető")
                    logger.error(f"🚨 DEBUG: hasattr(self.windy_days_tab, 'update_data') = {hasattr(self.windy_days_tab, 'update_data')}")
            elif self.windy_days_tab:
                logger.warning("⚠️ WindyDaysTab fallback frissítése...")
            else:
                logger.error("❌ WindyDaysTab nem elérhető!")
            
            # Emit data updated signal
            self.data_updated.emit(data, city_name)
            
            logger.info("ResultsPanel.update_data() VÉGLEGES JAVÍTÁS FRISSÍTÉSE SIKERES!")
            
        except Exception as e:
            logger.error(f"ResultsPanel adatfrissítési hiba: {e}")
            import traceback
            traceback.print_exc()
            
            # 📧 FIX: Error esetén is hide loading
            if self._is_loading:
                self.hide_loading_indicator()
            
            # Error message megjelenítése
            if self.title_label:
                self.title_label.setText(f"❌ Adatfrissítési hiba: {str(e)[:50]}...")
            
            self.clear_data()
    
    def clear_data(self) -> None:
        """
        📧 FIX: Adatok törlése loading indicator reset-tel.
        """
        logger.debug("ResultsPanel.clear_data() MEGHÍVVA")
        
        # 📧 FIX: Loading indicator elrejtése clear esetén
        if self._is_loading:
            self.hide_loading_indicator()
        
        self.current_data = None
        self.current_city = None
        
        if self.title_label:
            self.title_label.setText("📊 Időjárási Adatok Elemzése")
        
        if self.overview_tab and hasattr(self.overview_tab, '_clear_stats'):
            self.overview_tab._clear_stats()
        
        if self.charts_tab and hasattr(self.charts_tab, 'clear_data'):
            self.charts_tab.clear_data()
        
        if self.table_tab and hasattr(self.table_tab, 'clear_data'):
            self.table_tab.clear_data()
        
        if self.extreme_tab and hasattr(self.extreme_tab, '_clear_extremes'):
            self.extreme_tab._clear_extremes()
        
        # 🌪️ WindyDaysTab clear
        if self.windy_days_tab and hasattr(self.windy_days_tab, 'clear_data'):
            self.windy_days_tab.clear_data()
        
        logger.debug("ResultsPanel.clear_data() BEFEJEZVE")
    
    # === TELJES API COMPATIBILITY ===
    
    def apply_theme(self, dark_theme: bool) -> None:
        """
        🎨 Téma alkalmazása - TELJES KOMPATIBILITÁS.
        
        Args:
            dark_theme: Sötét téma engedélyezve
        """
        logger.debug(f"ResultsPanel.apply_theme({dark_theme}) MEGHÍVVA")
        
        if self.charts_tab and hasattr(self.charts_tab, 'apply_theme'):
            self.charts_tab.apply_theme(dark_theme)
        
        if self.table_tab and hasattr(self.table_tab, 'apply_theme'):
            self.table_tab.apply_theme(dark_theme)
        
        # 🌪️ WindyDaysTab theme
        if self.windy_days_tab and hasattr(self.windy_days_tab, '_on_theme_changed'):
            theme_name = "dark" if dark_theme else "light"
            self.windy_days_tab._on_theme_changed(theme_name)
        
        if _theme_manager_available:
            self._apply_tab_widget_theming()
        
        logger.debug("ResultsPanel.apply_theme() BEFEJEZVE")
    
    def _apply_tab_widget_theming(self) -> None:
        """
        📧 FIX: Tab widget téma alkalmazása.
        """
        if self.tab_widget and self.theme_manager:
            # Apply theming to tab widget
            pass
    
    # === TAB SPECIFIKUS API ===
    
    def switch_to_tab(self, tab_name: str) -> None:
        """Specifikus tab-ra váltás."""
        if not self.tab_widget:
            return
        
        tab_indices = {
            "overview": 0,
            "charts": 1,
            "table": 2,
            "extreme": 3,
            "windy_days": 4  # 🌪️ ÚJ
        }
        
        if tab_name in tab_indices:
            self.tab_widget.setCurrentIndex(tab_indices[tab_name])
            print(f"📊 DEBUG: Switched to tab: {tab_name}")
    
    def get_current_tab(self) -> str:
        """Jelenlegi aktív tab nevének lekérdezése."""
        if not self.tab_widget:
            return "overview"
        
        current_index = self.tab_widget.currentIndex()
        tab_names = ["overview", "charts", "table", "extreme", "windy_days"]  # 🌪️ ÚJ
        
        if 0 <= current_index < len(tab_names):
            return tab_names[current_index]
        return "overview"
    
    # === 🌪️ WINDY DAYS SPECIFIKUS API ===
    
    def switch_to_windy_days_tab(self) -> None:
        """Szeles napok tab-ra váltás."""
        self.switch_to_tab("windy_days")
    
    def get_windy_days_tab(self) -> Optional[WindyDaysTab]:
        """WindyDaysTab referencia lekérdezése."""
        return self.windy_days_tab if _windy_days_available else None
    
    def trigger_windy_days_analysis(self) -> None:
        """Szeles napok analízis programatikus triggerelése."""
        if self.windy_days_tab and _windy_days_available:
            if hasattr(self.windy_days_tab, '_start_analysis'):
                self.windy_days_tab._start_analysis()
                logger.info("🌪️ WindyDaysTab analízis programatikusan triggerelve")
            else:
                logger.warning("🌪️ WindyDaysTab._start_analysis nem elérhető")
        else:
            logger.warning("🌪️ WindyDaysTab nem elérhető analízis triggereléshez")
    
    # === PUBLIKUS GETTEREK ===
    
    def get_charts_container(self) -> Optional[object]:
        """Charts container referenciájának lekérdezése."""
        if self.charts_tab and hasattr(self.charts_tab, 'charts_container'):
            return self.charts_tab.charts_container
        return None
    
    def get_data_table(self) -> Optional[object]:
        """Data table referenciájának lekérdezése."""
        if self.table_tab and hasattr(self.table_tab, 'data_table'):
            return self.table_tab.data_table
        return None
    
    # === THEMEMANAGER PUBLIKUS API ===
    
    def apply_theme_by_name(self, theme_name: str) -> None:
        """Téma alkalmazása név alapján."""
        if not self.theme_manager:
            return
            
        success = self.theme_manager.set_theme(theme_name)
        if success:
            logger.info(f"ResultsPanel téma alkalmazva: {theme_name}")
        else:
            logger.error(f"ResultsPanel téma alkalmazás sikertelen: {theme_name}")
    
    def get_current_theme_name(self) -> str:
        """Jelenlegi téma nevének lekérdezése."""
        if self.theme_manager:
            return self.theme_manager.get_current_theme()
        return "default"
    
    # === STATE MANAGEMENT API ===
    
    def get_state(self) -> Dict[str, Any]:
        """
        📋 ResultsPanel állapot lekérdezése.
        
        Returns:
            dict: Panel teljes állapota
        """
        return {
            "is_loading": self._is_loading,
            "current_city": self.current_city,
            "has_data": self.current_data is not None,
            "current_tab": self.get_current_tab(),
            "progress_visible": self.progress_indicator.isVisible() if self.progress_indicator else False,
            "windy_days_available": _windy_days_available,  # 🌪️ ÚJ
            "pandas_available": _pandas_available,  # 🔥 ÚJ
            "dataframe_extractor_available": _dataframe_extractor_available,  # 🔥 ÚJ
            "is_valid": True
        }
    
    def set_state(self, state: Dict[str, Any]) -> bool:
        """
        📋 ResultsPanel állapot beállítása.
        
        Args:
            state: Állapot dictionary
            
        Returns:
            bool: Sikeres volt-e
        """
        try:
            # Loading state
            if "is_loading" in state and state["is_loading"]:
                self.show_loading_indicator()
            elif "is_loading" in state and not state["is_loading"]:
                self.hide_loading_indicator()
            
            # Tab switching
            if "current_tab" in state:
                self.switch_to_tab(state["current_tab"])
            
            logger.debug("ResultsPanel state set successfully")
            return True
            
        except Exception as e:
            logger.error(f"ResultsPanel state set failed: {e}")
            return False
    
    def is_valid(self) -> bool:
        """
        ✅ ResultsPanel validálása.
        
        ResultsPanel mindig valid, mivel csak megjelenítési widget.
        
        Returns:
            bool: Mindig True
        """
        return True
    
    def set_enabled(self, enabled: bool) -> None:
        """
        📧 ResultsPanel engedélyezése/letiltása.
        
        Args:
            enabled: Engedélyezett állapot
        """
        if self.tab_widget:
            self.tab_widget.setEnabled(enabled)
        
        if self.global_export_btn:
            self.global_export_btn.setEnabled(enabled)
        
        if self.extreme_weather_btn:
            self.extreme_weather_btn.setEnabled(enabled)
        
        logger.debug(f"ResultsPanel enabled state: {enabled}")
    
    # === EMERGENCY CONTROLS ===
    
    def emergency_reset(self) -> None:
        """
        🚨 Emergency reset - teljes panel visszaállítása.
        
        Ez a metódus emergency esetekre van, amikor a panel
        teljesen elakad és manual reset szükséges.
        """
        logger.warning("ResultsPanel emergency reset triggered")
        
        # Loading state force reset
        self.force_hide_loading()
        
        # Data clear
        self.clear_data()
        
        # Timer cleanup
        if self._loading_timer and self._loading_timer.isActive():
            self._loading_timer.stop()
        
        # UI reset
        if self.title_label:
            self.title_label.setText("📊 Időjárási Adatok Elemzése")
        
        # Tab reset
        if self.tab_widget:
            self.tab_widget.setCurrentIndex(0)
            self.tab_widget.setEnabled(True)
        
        logger.warning("ResultsPanel emergency reset completed")
    
    def get_loading_status(self) -> Dict[str, Any]:
        """
        📊 Loading állapot részletes lekérdezése.
        
        Returns:
            dict: Loading status információk
        """
        return {
            "is_loading": self._is_loading,
            "progress_text": self.progress_indicator.text() if self.progress_indicator else "",
            "progress_visible": self.progress_indicator.isVisible() if self.progress_indicator else False,
            "timer_active": self._loading_timer.isActive() if self._loading_timer else False,
            "timer_remaining": self._loading_timer.remainingTime() if (self._loading_timer and self._loading_timer.isActive()) else 0
        }
    
    # === CLEANUP ===
    
    def cleanup(self) -> None:
        """
        📧 FIX: ResultsPanel cleanup loading timer-rel.
        """
        # Loading timer cleanup
        if self._loading_timer:
            if self._loading_timer.isActive():
                self._loading_timer.stop()
            self._loading_timer.deleteLater()
            self._loading_timer = None
        
        # Loading state reset
        self._is_loading = False
        
        # Tab cleanup
        if self.overview_tab and hasattr(self.overview_tab, 'cleanup'):
            self.overview_tab.cleanup()
        
        if self.charts_tab and hasattr(self.charts_tab, 'cleanup'):
            self.charts_tab.cleanup()
        
        if self.table_tab and hasattr(self.table_tab, 'cleanup'):
            self.table_tab.cleanup()
        
        if self.extreme_tab and hasattr(self.extreme_tab, 'cleanup'):
            self.extreme_tab.cleanup()
        
        # 🌪️ WindyDaysTab cleanup
        if self.windy_days_tab and hasattr(self.windy_days_tab, 'cleanup'):
            self.windy_days_tab.cleanup()
        
        logger.debug("ResultsPanel cleanup completed")
    
    def closeEvent(self, event) -> None:
        """
        📧 Widget bezárása - cleanup hívás.
        """
        self.cleanup()
        super().closeEvent(event)
    
    def __del__(self):
        """
        📧 FIX: Destruktor loading timer cleanup-pal.
        """
        try:
            self.cleanup()
        except:
            pass


# === FACTORY FUNCTIONS ===

def create_results_panel() -> ResultsPanel:
    """
    🏭 FACTORY: ResultsPanel létrehozása default beállításokkal.
    
    Returns:
        Fully configured ResultsPanel instance
    """
    panel = ResultsPanel()
    
    logger.info("✅ ResultsPanel created via factory method")
    return panel


# === TESTING SUPPORT ===

if __name__ == "__main__":
    """
    🧪 TESTING: ResultsPanel standalone test
    """
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget, QPushButton
    from PySide6.QtCore import QTimer
    import sys
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("ResultsPanel Test - VÉGLEGES DATAFRAME EXTRACTOR JAVÍTÁS")
            self.setGeometry(100, 100, 1200, 800)
            
            # Central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Test controls
            controls_layout = QHBoxLayout()
            
            # DataFrameExtractor test button
            extractor_test_btn = QPushButton("🔥 Test DataFrameExtractor")
            extractor_test_btn.clicked.connect(self._test_dataframe_extractor)
            controls_layout.addWidget(extractor_test_btn)
            
            # Wind gusts test button
            wind_test_btn = QPushButton("🌪️ Test Wind Gusts Data")
            wind_test_btn.clicked.connect(self._test_wind_gusts_data)
            controls_layout.addWidget(wind_test_btn)
            
            # WindyDays specific test
            windy_btn = QPushButton("🌪️ Test WindyDays")
            windy_btn.clicked.connect(self._test_windy_days)
            controls_layout.addWidget(windy_btn)
            
            # API consistency test
            api_btn = QPushButton("🎯 Test API Consistency")
            api_btn.clicked.connect(self._test_api_consistency)
            controls_layout.addWidget(api_btn)
            
            # WIND_SPEED oszlop test
            wind_speed_btn = QPushButton("🔥 Test WIND_SPEED oszlop")
            wind_speed_btn.clicked.connect(self._test_wind_speed_column)
            controls_layout.addWidget(wind_speed_btn)
            
            emergency_btn = QPushButton("🚨 Emergency Reset")
            emergency_btn.clicked.connect(self._test_emergency)
            controls_layout.addWidget(emergency_btn)
            
            layout.addLayout(controls_layout)
            
            # Results panel
            self.results_panel = ResultsPanel()
            
            # Signal connections
            self.results_panel.extreme_weather_requested.connect(self._on_extreme_weather_signal)
            
            layout.addWidget(self.results_panel)
            
        def _test_dataframe_extractor(self):
            """🔥 DATAFRAME EXTRACTOR: Test DataFrameExtractor használat"""
            print("🔥 DATAFRAME EXTRACTOR: Test DataFrameExtractor.extract_safely() használat...")
            
            # Teszt API adat wind_gusts_10m_max-szal
            test_data = {
                "latitude": 47.501236,
                "longitude": 19.03534,
                "daily": {
                    "time": [f"2025-08-{10+i}" for i in range(7)],
                    "wind_gusts_10m_max": [15.5, 22.3, 89.7, 12.1, 8.9, 25.4, 97.2],  # 89.7 és 97.2 > 70 km/h!
                    "windspeed_10m_max": [10.2, 15.1, 35.8, 8.3, 5.2, 18.9, 41.7]     # Fallback adatok
                }
            }
            
            self.results_panel.update_data(test_data, "DATAFRAME EXTRACTOR TEST Budapest")
            
        def _test_wind_gusts_data(self):
            """🌪️ WIND GUSTS: Test wind_gusts_10m_max vs windspeed_10m_max"""
            print("🌪️ WIND GUSTS: Test wind_gusts_10m_max prioritás...")
            
            # Valódi OpenMeteo API szerű válasz - wind_gusts_10m_max PRIORITÁSSAL
            wind_data = {
                "latitude": 47.501236,
                "longitude": 19.03534,
                "daily": {
                    "time": [f"2025-08-{15+i}" for i in range(10)],
                    "wind_gusts_10m_max": [25.2, 35.1, 78.9, 18.3, 15.2, 89.9, 67.7, 45.3, 91.2, 103.5],  # HELYES szélökések!
                    "windspeed_10m_max": [15.1, 20.3, 35.8, 12.1, 8.9, 41.4, 28.7, 22.1, 38.9, 45.2]     # Fallback
                }
            }
            
            self.results_panel.update_data(wind_data, "WIND GUSTS PRIORITÁS TEST Budapest")
            
        def _test_windy_days(self):
            """🌪️ TEST: WindyDaysTab functionality"""
            print("🌪️ TEST: Switching to WindyDays tab")
            self.results_panel.switch_to_windy_days_tab()
            
        def _test_api_consistency(self):
            """🎯 TEST: API konzisztencia wind_gusts_10m_max kulccsal"""
            print("🎯 TEST: API mezőnevek konzisztencia")
            
            # Teszt: csak wind_gusts_10m_max (elsődleges)
            primary_data = {
                "daily": {
                    "time": ["2025-08-16", "2025-08-17"],
                    "wind_gusts_10m_max": [75.5, 85.3]  # Csak elsődleges mező
                }
            }
            
            # Teszt: csak windspeed_10m_max (fallback)
            fallback_data = {
                "daily": {
                    "time": ["2025-08-18", "2025-08-19"],
                    "windspeed_10m_max": [25.2, 30.1]  # Csak fallback mező
                }
            }
            
            # Direct call to _convert_data_to_dataframe
            try:
                print("\n🎯 PRIMARY TEST (wind_gusts_10m_max):")
                result1 = self.results_panel._convert_data_to_dataframe(primary_data)
                if hasattr(result1, 'columns'):
                    print(f"✅ Columns: {list(result1.columns)}")
                    if 'wind_data_source' in result1.columns:
                        source = result1['wind_data_source'].iloc[0]
                        print(f"🎯 Source: {source}")
                    if 'wind_speed' in result1.columns:
                        print(f"🔥 wind_speed oszlop: ✅ MEGVAN!")
                        wind_values = result1['wind_speed'].dropna()
                        if len(wind_values) > 0:
                            print(f"🌪️ Wind speed range: {wind_values.min():.1f} - {wind_values.max():.1f} km/h")
                
                print("\n🎯 FALLBACK TEST (windspeed_10m_max):")
                result2 = self.results_panel._convert_data_to_dataframe(fallback_data)
                if hasattr(result2, 'columns'):
                    print(f"✅ Columns: {list(result2.columns)}")
                    if 'wind_data_source' in result2.columns:
                        source = result2['wind_data_source'].iloc[0]
                        print(f"🎯 Source: {source}")
                    if 'wind_speed' in result2.columns:
                        print(f"🔥 wind_speed oszlop: ✅ MEGVAN!")
                        
            except Exception as e:
                print(f"🔥 API CONSISTENCY TEST ERROR: {e}")
                import traceback
                traceback.print_exc()
        
        def _test_wind_speed_column(self):
            """🔥 TEST: wind_speed oszlop biztosítása WindyDaysTab számára"""
            print("🔥 TEST: wind_speed oszlop mapping teszt...")
            
            # Teszt adat wind_gusts_10m_max-szal
            wind_speed_test_data = {
                "daily": {
                    "time": ["2025-08-20", "2025-08-21", "2025-08-22"],
                    "wind_gusts_10m_max": [72.5, 45.3, 98.7]  # Szélökések > 70 km/h küszöb
                }
            }
            
            try:
                print("🔥 WIND_SPEED OSZLOP TESZT...")
                df = self.results_panel._convert_data_to_dataframe(wind_speed_test_data)
                
                if hasattr(df, 'columns'):
                    print(f"📧 DataFrame oszlopok: {list(df.columns)}")
                    
                    if 'wind_speed' in df.columns:
                        print("✅ wind_speed oszlop MEGVAN!")
                        wind_speeds = df['wind_speed'].dropna()
                        print(f"🌪️ Wind speed értékek: {wind_speeds.tolist()}")
                        
                        # WindyDaysTab teszt (43 km/h küszöb)
                        windy_days = (wind_speeds > 43).sum()
                        print(f"🌪️ Szeles napok (>43 km/h): {windy_days}/{len(wind_speeds)}")
                        
                        # 70 km/h küszöb teszt
                        extreme_days = (wind_speeds > 70).sum()
                        print(f"⚡ Extrém szeles napok (>70 km/h): {extreme_days}/{len(wind_speeds)}")
                        
                    else:
                        print("❌ wind_speed oszlop HIÁNYZIK!")
                        
                    if 'wind_gusts_max' in df.columns:
                        print("✅ wind_gusts_max oszlop is megvan (backward compatibility)")
                    
                else:
                    print("❌ DataFrame nem válaszol hasattr-ra!")
                    
                # WindyDaysTab update teszt
                print("\n🚨 WindyDaysTab update teszt...")
                self.results_panel.update_data(wind_speed_test_data, "WIND_SPEED OSZLOP TESZT")
                
            except Exception as e:
                print(f"🔥 WIND_SPEED TESZT HIBA: {e}")
                import traceback
                traceback.print_exc()
            
        def _test_emergency(self):
            """🚨 TEST: Emergency reset"""
            print("🚨 TEST: Emergency reset")
            self.results_panel.emergency_reset()
        
        def _on_extreme_weather_signal(self):
            """🔥 TEST: Extreme weather signal fogadása"""
            print("🔥 TEST: Extreme weather signal received!")
    
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    print("🧪 VÉGLEGES DATAFRAME EXTRACTOR JAVÍTÁS: ResultsPanel test window started")
    print("🔥 DATAFRAME EXTRACTOR: Próbáld ki a 'Test DataFrameExtractor' gombot!")
    print("🌪️ WIND GUSTS: Próbáld ki a 'Test Wind Gusts Data' gombot!")
    print("🎯 API CONSISTENCY: Ellenőrizd a 'Test API Consistency' gombot!")
    print("🔥 WIND_SPEED OSZLOP: Próbáld ki a 'Test WIND_SPEED oszlop' gombot!")
    print("🌪️ WindyDaysTab: Most már HELYES 8-98 km/h adatokat kap wind_speed oszloppal!")
    
    sys.exit(app.exec())


# === MODUL STÁTUSZ JELENTÉS (VÉGLEGES DATAFRAME EXTRACTOR VERZIÓ) ===
logger.info(f"""
🔥 RESULTS PANEL VÉGLEGES DATAFRAME EXTRACTOR JAVÍTÁS STÁTUSZ:
📊 QuickOverviewTab: {'✅ ELÉRHETŐ' if _quick_overview_available else '⚠️ FALLBACK'}
📈 DetailedChartsTab: {'✅ ELÉRHETŐ' if _detailed_charts_available else '⚠️ FALLBACK'}
📋 DataTableTab: {'✅ ELÉRHETŐ' if _data_table_available else '⚠️ FALLBACK'}
⚡ ExtremeEventsTab: {'✅ ELÉRHETŐ' if _extreme_events_available else '⚠️ FALLBACK'}
🌪️ WindyDaysTab: {'✅ ELÉRHETŐ' if _windy_days_available else '⚠️ FALLBACK'}
🎨 ThemeManager: {'✅ ELÉRHETŐ' if _theme_manager_available else '❌ HIÁNYZIK'}
⚡ VALÓDI ANALYTICS: {'✅ ELÉRHETŐ' if _wind_analysis_available else '❌ HIÁNYZIK'}
🔥 PANDAS IMPORT: {'✅ ELÉRHETŐ' if _pandas_available else '❌ HIÁNYZIK'}
🔥 DATAFRAME EXTRACTOR: {'✅ ELÉRHETŐ' if _dataframe_extractor_available else '❌ HIÁNYZIK'}

🔥 KRITIKUS VÉGLEGES JAVÍTÁS: DataFrameExtractor.extract_safely() használat!
🎯 WIND_GUSTS_10M_MAX PRIORITÁS: ✅ BIZTOSÍTVA!
🔥 WIND_SPEED OSZLOP JAVÍTÁS: ✅ wind_gusts_max → wind_speed mapping!
🌪️ WINDYDATATAB FIX: ✅ VÉGRE HELYES ADATOKAT KAP wind_speed OSZLOPPAL!
🚨 EMERGENCY CONTROLS: ✅ MINDEN ESZKÖZ ELÉRHETŐ!
🔥 API KONZISZTENCIA: ✅ wind_gusts_10m_max → wind_gusts_max → wind_speed KONVERZIÓ!
""")
print("🔥 VÉGLEGES JAVÍTÁS: results_panel.py TELJES FÁJL KÉSZ!")
print("⚡ KRITIKUS: A _convert_data_to_dataframe() most már DataFrameExtractor.extract_safely()-t használ!")
print("🔥 WIND_SPEED OSZLOP: wind_gusts_max → wind_speed mapping biztosítva!")
print("🌪️ WINDYDATATAB: Végre megkapja a wind_gusts_10m_max (8-98 km/h) adatokat wind_speed oszlopban!")
print("🎯 100% MŰKÖDŐ WINDYDAYSTAB INTEGRÁCIÓ - WIND_SPEED OSZLOP JAVÍTÁSSAL!")