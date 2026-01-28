"""
Szeles napok tab komponens a Results Panel-hez.

Ez a modul a szeles napok analízisének UI kezelését valósítja meg,
integrálva a wind_analysis analytics modult és a windy_days_chart komponenst.

🔧 KRITIKUS JAVÍTÁS: DUPLA KONVERZIÓ ELTÁVOLÍTVA!
✅ MEGBÍZIK A RESULTSPANEL KONVERZIÓJÁBAN!
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional

import pandas as pd
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QSpinBox, QGroupBox,
    QTextEdit, QSplitter, QFrame, QProgressBar,
    QComboBox, QCheckBox
)

# Relatív importok
from src.analytics.wind_analysis import (
    analyze_wind_patterns, 
    format_wind_analysis_summary,
    get_chart_data_for_monthly_windy_days,
    WINDY_DAY_THRESHOLD_KMH
)
from ..charts.windy_days_chart import WindyDaysChart
from ..theme_manager import ProfessionalThemeManager

logger = logging.getLogger(__name__)


class WindyDaysTab(QWidget):
    """
    Szeles napok analízis tab komponens.
    
    Megjeleníti a szeles napok havi eloszlását oszlopdiagramon,
    beállítható küszöbértékkel és részletes statisztikákkal.
    
    🔧 JAVÍTÁS: MEGBÍZIK A RESULTSPANEL KONVERZIÓJÁBAN!
    ❌ DUPLA KONVERZIÓ ELTÁVOLÍTVA!
    """
    
    # Signals
    analysis_completed = Signal(dict)
    error_occurred = Signal(str)
    export_requested = Signal(str, str)  # file_type, file_path
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Inicializálás."""
        super().__init__(parent)
        
        # Komponensek
        self.chart: Optional[WindyDaysChart] = None
        self.summary_text: Optional[QTextEdit] = None
        self.threshold_spinbox: Optional[QSpinBox] = None
        self.progress_bar: Optional[QProgressBar] = None
        self.analyze_button: Optional[QPushButton] = None
        self.export_button: Optional[QPushButton] = None
        self.auto_update_checkbox: Optional[QCheckBox] = None
        
        # Adatok
        self.current_weather_data: Optional[pd.DataFrame] = None
        self.current_location: str = "Ismeretlen helyszín"
        self.current_analysis_result: Optional[Dict] = None
        
        # Theme manager
        self.theme_manager = ProfessionalThemeManager()
        
        # UI inicializálás
        self._init_ui()
        self._connect_signals()
        self._apply_theme()
        
        logger.info("WindyDaysTab inicializálva (EGYSÉG KONVERZIÓ JAVÍTÁSSAL)")
    
    def _init_ui(self) -> None:
        """UI elemek inicializálása."""
        try:
            # Fő layout
            main_layout = QVBoxLayout(self)
            main_layout.setSpacing(10)
            main_layout.setContentsMargins(10, 10, 10, 10)
            
            # Header
            self._create_header_section(main_layout)
            
            # Kontroll panel
            self._create_controls_section(main_layout)
            
            # Progress bar
            self._create_progress_section(main_layout)
            
            # Fő content splitter
            content_splitter = QSplitter(Qt.Horizontal)
            
            # Chart és summary
            self._create_chart_section(content_splitter)
            self._create_summary_section(content_splitter)
            
            # Splitter arányok
            content_splitter.setSizes([600, 300])
            content_splitter.setChildrenCollapsible(False)
            
            main_layout.addWidget(content_splitter, 1)
            
            # Footer
            self._create_footer_section(main_layout)
            
            logger.info("WindyDaysTab UI inicializálva")
            
        except Exception as e:
            logger.error(f"Hiba a UI inicializálásában: {e}")
    
    def _create_header_section(self, layout: QVBoxLayout) -> None:
        """Header szekció létrehozása."""
        try:
            header_frame = QFrame()
            header_frame.setFrameStyle(QFrame.StyledPanel)
            header_layout = QVBoxLayout(header_frame)
            
            # Főcím
            title_label = QLabel("🌪️ Szeles Napok Analízis")
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
            title_label.setAlignment(Qt.AlignCenter)
            
            # Leírás
            desc_label = QLabel(
                "Havi szeles napok eloszlásának vizsgálata beállítható küszöbértékkel"
            )
            desc_label.setStyleSheet("font-size: 12px; color: #7f8c8d; font-style: italic;")
            desc_label.setAlignment(Qt.AlignCenter)
            desc_label.setWordWrap(True)
            
            header_layout.addWidget(title_label)
            header_layout.addWidget(desc_label)
            
            layout.addWidget(header_frame)
            
        except Exception as e:
            logger.error(f"Hiba a header létrehozásában: {e}")
    
    def _create_controls_section(self, layout: QVBoxLayout) -> None:
        """Kontroll szekció létrehozása."""
        try:
            controls_group = QGroupBox("Beállítások")
            controls_layout = QGridLayout(controls_group)
            
            # Küszöbérték beállítás
            threshold_label = QLabel("Küszöbérték (km/h):")
            self.threshold_spinbox = QSpinBox()
            self.threshold_spinbox.setRange(10, 100)
            self.threshold_spinbox.setValue(int(WINDY_DAY_THRESHOLD_KMH))
            self.threshold_spinbox.setSuffix(" km/h")
            self.threshold_spinbox.setToolTip("Szeles nap küszöbérték szélsebességben")
            
            # Automatikus frissítés
            self.auto_update_checkbox = QCheckBox("Automatikus frissítés")
            self.auto_update_checkbox.setChecked(True)
            self.auto_update_checkbox.setToolTip("Automatikus újraszámítás küszöbérték változáskor")
            
            # Gombok
            self.analyze_button = QPushButton("🔄 Analízis Futtatása")
            self.analyze_button.setMinimumHeight(35)
            self.analyze_button.setStyleSheet("""
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
            
            self.export_button = QPushButton("📊 Export Chart")
            self.export_button.setEnabled(False)
            self.export_button.setMinimumHeight(35)
            
            # Layout elrendezés
            controls_layout.addWidget(threshold_label, 0, 0)
            controls_layout.addWidget(self.threshold_spinbox, 0, 1)
            controls_layout.addWidget(self.auto_update_checkbox, 0, 2)
            controls_layout.addWidget(self.analyze_button, 1, 0, 1, 2)
            controls_layout.addWidget(self.export_button, 1, 2)
            
            layout.addWidget(controls_group)
            
        except Exception as e:
            logger.error(f"Hiba a kontrollok létrehozásában: {e}")
    
    def _create_progress_section(self, layout: QVBoxLayout) -> None:
        """Progress bar szekció létrehozása."""
        try:
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            self.progress_bar.setStyleSheet("""
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
            
            layout.addWidget(self.progress_bar)
            
        except Exception as e:
            logger.error(f"Hiba a progress bar létrehozásában: {e}")
    
    def _create_chart_section(self, parent_widget) -> None:
        """Chart szekció létrehozása."""
        try:
            chart_frame = QFrame()
            chart_frame.setFrameStyle(QFrame.StyledPanel)
            chart_layout = QVBoxLayout(chart_frame)
            
            # Chart címke
            chart_title = QLabel("📈 Havi Szeles Napok Oszlopdiagram")
            chart_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #34495e;")
            chart_title.setAlignment(Qt.AlignLeft)
            
            # Windy days chart
            self.chart = WindyDaysChart()
            
            chart_layout.addWidget(chart_title)
            chart_layout.addWidget(self.chart, 1)
            
            parent_widget.addWidget(chart_frame)
            
        except Exception as e:
            logger.error(f"Hiba a chart szekció létrehozásában: {e}")
    
    def _create_summary_section(self, parent_widget) -> None:
        """Összefoglaló szekció létrehozása."""
        try:
            summary_frame = QFrame()
            summary_frame.setFrameStyle(QFrame.StyledPanel)
            summary_layout = QVBoxLayout(summary_frame)
            
            # Summary címke
            summary_title = QLabel("📋 Részletes Összefoglaló")
            summary_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #34495e;")
            
            # Text area
            self.summary_text = QTextEdit()
            self.summary_text.setReadOnly(True)
            self.summary_text.setMaximumWidth(350)
            self.summary_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                    background-color: #f8f9fa;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 11px;
                    padding: 8px;
                }
            """)
            
            # Kezdeti üzenet
            self._set_initial_summary_message()
            
            summary_layout.addWidget(summary_title)
            summary_layout.addWidget(self.summary_text, 1)
            
            parent_widget.addWidget(summary_frame)
            
        except Exception as e:
            logger.error(f"Hiba az összefoglaló szekció létrehozásában: {e}")
    
    def _create_footer_section(self, layout: QVBoxLayout) -> None:
        """Footer szekció létrehozása."""
        try:
            footer_frame = QFrame()
            footer_frame.setMaximumHeight(30)
            footer_layout = QHBoxLayout(footer_frame)
            
            # Info label
            info_label = QLabel("💡 Tipp: Küszöbérték változtatáskor automatikusan újraszámít")
            info_label.setStyleSheet("font-size: 10px; color: #7f8c8d; font-style: italic;")
            
            footer_layout.addWidget(info_label)
            footer_layout.addStretch()
            
            layout.addWidget(footer_frame)
            
        except Exception as e:
            logger.error(f"Hiba a footer létrehozásában: {e}")
    
    def _connect_signals(self) -> None:
        """Signal kapcsolatok létrehozása."""
        try:
            if self.analyze_button:
                self.analyze_button.clicked.connect(self._on_analyze_clicked)
            
            if self.export_button:
                self.export_button.clicked.connect(self._on_export_clicked)
            
            if self.threshold_spinbox:
                self.threshold_spinbox.valueChanged.connect(self._on_threshold_changed)
            
            if self.auto_update_checkbox:
                self.auto_update_checkbox.toggled.connect(self._on_auto_update_toggled)
            
            # Theme manager
            self.theme_manager.theme_changed.connect(self._on_theme_changed)
            
            logger.info("WindyDaysTab signal kapcsolatok létrehozva")
            
        except Exception as e:
            logger.error(f"Hiba a signal kapcsolatok létrehozásában: {e}")
    
    def _set_initial_summary_message(self) -> None:
        """Kezdeti üzenet beállítása az összefoglalóban."""
        try:
            initial_message = """
🌪️ Szeles Napok Analízis

Még nem futott analízis.

Kattints az "Analízis Futtatása" gombra 
az időjárási adatok elemzéséhez.

Beállítható paraméterek:
• Küszöbérték: szélsebesség limit
• Automatikus frissítés: ki/bekapcsolás

A rendszer megszámolja azokat a napokat,
amikor a maximális szélsebesség meghaladja
a beállított küszöbértéket.

✅ MEGBÍZIK A RESULTSPANEL KONVERZIÓJÁBAN!
❌ DUPLA KONVERZIÓ ELTÁVOLÍTVA!
            """.strip()
            
            if self.summary_text:
                self.summary_text.setPlainText(initial_message)
                
        except Exception as e:
            logger.error(f"Hiba a kezdeti üzenet beállításában: {e}")
    
    def _on_analyze_clicked(self) -> None:
        """Analízis gomb kattintás kezelése."""
        try:
            logger.info("Szeles napok analízis indítása")
            
            if self.current_weather_data is None or self.current_weather_data.empty:
                self.error_occurred.emit("Nincs elérhető időjárási adat az analízishez")
                return
            
            self._start_analysis()
            
        except Exception as e:
            logger.error(f"Hiba az analízis indításában: {e}")
            self.error_occurred.emit(f"Hiba az analízis indításában: {e}")
    
    def _on_export_clicked(self) -> None:
        """Export gomb kattintás kezelése."""
        try:
            if self.chart and self.current_analysis_result:
                from PySide6.QtWidgets import QFileDialog
                
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Chart Exportálása",
                    f"szeles_napok_{self.current_location.replace(' ', '_')}.png",
                    "PNG Files (*.png);;PDF Files (*.pdf);;All Files (*)"
                )
                
                if file_path:
                    success = self.chart.export_chart(file_path)
                    if success:
                        self.export_requested.emit("chart", file_path)
                    else:
                        self.error_occurred.emit("Hiba a chart exportálásában")
                        
        except Exception as e:
            logger.error(f"Hiba az exportálásban: {e}")
            self.error_occurred.emit(f"Export hiba: {e}")
    
    def _on_threshold_changed(self, value: int) -> None:
        """Küszöbérték változás kezelése."""
        try:
            logger.info(f"Küszöbérték változott: {value} km/h")
            
            # Automatikus frissítés ha be van kapcsolva
            if (self.auto_update_checkbox and 
                self.auto_update_checkbox.isChecked() and 
                self.current_weather_data is not None):
                
                # Kis késleltetés a túl gyakori frissítés elkerülésére
                QTimer.singleShot(500, self._start_analysis)
                
        except Exception as e:
            logger.error(f"Hiba a küszöbérték változás kezelésében: {e}")
    
    def _on_auto_update_toggled(self, checked: bool) -> None:
        """Automatikus frissítés toggle kezelése."""
        try:
            logger.info(f"Automatikus frissítés: {'be' if checked else 'ki'}kapcsolva")
            
        except Exception as e:
            logger.error(f"Hiba az auto update toggle kezelésében: {e}")
    
    def _start_analysis(self) -> None:
        """
        ✅ JAVÍTOTT ANALÍZIS INDÍTÁSA - DUPLA KONVERZIÓ NÉLKÜL!
        
        A ResultsPanel már konvertálta a m/s → km/h adatokat,
        ezért közvetlenül használjuk a current_weather_data-t!
        """
        try:
            # UI állapot
            self._set_analysis_state(True)
            
            # ✅ NINCS DUPLA KONVERZIÓ! Megbízunk a ResultsPanel-ben!
            logger.info("✅ KONVERZIÓ NÉLKÜLI ANALÍZIS: Megbízunk a ResultsPanel km/h konverziójában")
            
            # Paraméterek
            threshold = self.threshold_spinbox.value() if self.threshold_spinbox else WINDY_DAY_THRESHOLD_KMH
            location = self.current_location
            
            logger.info(f"🔧 ANALÍZIS PARAMÉTEREI: threshold={threshold} km/h, location={location}")
            logger.info(f"🔧 WEATHER DATA: {len(self.current_weather_data)} sor, oszlopok: {list(self.current_weather_data.columns)}")
            
            # Wind speed ellenőrzés
            if 'wind_speed' in self.current_weather_data.columns:
                wind_speeds = self.current_weather_data['wind_speed'].dropna()
                if len(wind_speeds) > 0:
                    logger.info(f"🔧 KAPOTT WIND_SPEED (ResultsPanel konvertálta): {wind_speeds.min():.1f} - {wind_speeds.max():.1f} km/h")
                else:
                    logger.error("❌ ÜRES WIND_SPEED OSZLOP!")
                    self.error_occurred.emit("Nincs szélsebesség adat")
                    self._set_analysis_state(False)
                    return
            else:
                logger.error("❌ HIÁNYZIK A WIND_SPEED OSZLOP!")
                self.error_occurred.emit("Hiányzik a wind_speed oszlop")
                self._set_analysis_state(False)
                return
            
            # ✅ ANALÍZIS FUTTATÁSA KÖZVETLENÜL A KAPOTT ADATOKKAL!
            analysis_result = analyze_wind_patterns(
                self.current_weather_data,  # ✅ KÖZVETLENÜL HASZNÁLJUK (már km/h-ban van)!
                location_name=location,
                threshold_kmh=threshold
            )
            
            # Chart adatok előkészítése
            chart_data = get_chart_data_for_monthly_windy_days(analysis_result)
            
            # Eredmények megjelenítése
            self._display_analysis_results(analysis_result, chart_data, threshold)
            
            # UI állapot visszaállítása
            self._set_analysis_state(False)
            
            # Signal kibocsátása
            self.analysis_completed.emit({
                'analysis_result': analysis_result,
                'chart_data': chart_data,
                'threshold': threshold,
                'location': location
            })
            
            logger.info("✅ Szeles napok analízis befejezve (DUPLA KONVERZIÓ NÉLKÜL)")
            
        except Exception as e:
            logger.error(f"❌ Hiba az analízisben: {e}")
            import traceback
            traceback.print_exc()
            self._set_analysis_state(False)
            self.error_occurred.emit(f"Analízis hiba: {e}")
    
    def _display_analysis_results(self, analysis_result, chart_data: Dict, threshold: float) -> None:
        """Analízis eredmények megjelenítése."""
        try:
            # Chart frissítése
            if self.chart:
                chart_update_data = {
                    'chart_data': chart_data,
                    'threshold_kmh': threshold,
                    'location_name': self.current_location
                }
                self.chart.update_data(chart_update_data)
            
            # Summary frissítése
            if self.summary_text:
                summary = format_wind_analysis_summary(analysis_result)
                # ✅ ÚJ INFO: Nincs dupla konverzió
                summary_with_fix_info = f"{summary}\n\n✅ JAVÍTÁS: Megbízik a ResultsPanel km/h konverziójában!\n❌ Dupla konverzió eltávolítva!"
                self.summary_text.setPlainText(summary_with_fix_info)
            
            # Export gomb engedélyezése
            if self.export_button:
                self.export_button.setEnabled(True)
            
            # Eredmény tárolása
            self.current_analysis_result = {
                'analysis_result': analysis_result,
                'chart_data': chart_data,
                'threshold': threshold
            }
            
            logger.info("✅ Analízis eredmények megjelenítve (DUPLA KONVERZIÓ NÉLKÜL)")
            
        except Exception as e:
            logger.error(f"❌ Hiba az eredmények megjelenítésében: {e}")
    
    def _set_analysis_state(self, running: bool) -> None:
        """Analízis állapot UI frissítése."""
        try:
            if self.analyze_button:
                self.analyze_button.setEnabled(not running)
                self.analyze_button.setText("⏳ Elemzés..." if running else "🔄 Analízis Futtatása")
            
            if self.progress_bar:
                self.progress_bar.setVisible(running)
                if running:
                    self.progress_bar.setRange(0, 0)  # Indeterminate
                    
        except Exception as e:
            logger.error(f"Hiba az analízis állapot beállításában: {e}")
    
    def _apply_theme(self) -> None:
        """Theme alkalmazása."""
        try:
            # Theme manager regisztráció
            self.theme_manager.register_widget_for_theming(self)
            
            # Chart theme
            if self.chart:
                self.theme_manager.register_widget_for_theming(self.chart)
                
        except Exception as e:
            logger.error(f"Hiba a theme alkalmazásában: {e}")
    
    def _on_theme_changed(self, theme_name: str) -> None:
        """Theme változás kezelése."""
        try:
            logger.info(f"WindyDaysTab theme változás: {theme_name}")
            
            # UI elemek újra-stílusozása szükség szerint
            self._apply_theme()
            
        except Exception as e:
            logger.error(f"Hiba a theme változás kezelésében: {e}")
    
    # Public methods
    
    def update_data(self, weather_data: pd.DataFrame, location: str = "Ismeretlen helyszín") -> None:
        """
        ✅ JAVÍTOTT ADATOK FRISSÍTÉSE - MEGBÍZIK A RESULTSPANEL-BEN!
        
        Args:
            weather_data: Pandas DataFrame időjárási adatokkal (ResultsPanel KONVERTÁLTA km/h-ra)
            location: Helyszín neve
        """
        try:
            logger.info(f"WindyDaysTab adatok frissítése: {location}")
            logger.info(f"✅ BEJÖVŐ ADATOK (ResultsPanel konvertálta): {len(weather_data)} sor, oszlopok: {list(weather_data.columns)}")
            
            # Wind speed ellenőrzés
            if not weather_data.empty and 'wind_speed' in weather_data.columns:
                wind_speeds = weather_data['wind_speed'].dropna()
                if len(wind_speeds) > 0:
                    logger.info(f"✅ KAPOTT WIND_SPEED (km/h): {wind_speeds.min():.1f} - {wind_speeds.max():.1f}")
                else:
                    logger.warning("⚠️ ÜRES WIND_SPEED OSZLOP")
            
            # ✅ ADATOK TÁROLÁSA (ResultsPanel már konvertálta)
            self.current_weather_data = weather_data
            self.current_location = location
            
            # Automatikus analízis ha be van kapcsolva
            if (self.auto_update_checkbox and 
                self.auto_update_checkbox.isChecked() and 
                not weather_data.empty):
                
                logger.info("✅ AUTOMATIKUS ANALÍZIS INDÍTÁSA (DUPLA KONVERZIÓ NÉLKÜL)")
                self._start_analysis()
                
        except Exception as e:
            logger.error(f"❌ Hiba az adatok frissítésében: {e}")
            self.error_occurred.emit(f"Adatok frissítési hiba: {e}")
    
    def clear_data(self) -> None:
        """Adatok és UI tartalom törlése."""
        try:
            logger.info("WindyDaysTab adatok törlése")
            
            # Adatok nullázása
            self.current_weather_data = None
            self.current_location = "Ismeretlen helyszín"
            self.current_analysis_result = None
            
            # Chart törlése
            if self.chart:
                self.chart.clear_chart()
            
            # Summary törlése
            self._set_initial_summary_message()
            
            # UI elemek állapotának visszaállítása
            if self.export_button:
                self.export_button.setEnabled(False)
            
            if self.threshold_spinbox:
                self.threshold_spinbox.setValue(int(WINDY_DAY_THRESHOLD_KMH))
                
        except Exception as e:
            logger.error(f"Hiba az adatok törlésében: {e}")
    
    def get_current_threshold(self) -> float:
        """Aktuális küszöbérték lekérdezése."""
        if self.threshold_spinbox:
            return float(self.threshold_spinbox.value())
        return WINDY_DAY_THRESHOLD_KMH
    
    def set_threshold(self, threshold: float) -> None:
        """Küszöbérték beállítása."""
        if self.threshold_spinbox:
            self.threshold_spinbox.setValue(int(threshold))


# === MODUL VÉGE ===
