#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Charts Container Widget
Charts konténer widget refaktorált verzió - CSAK ChartsContainer osztály.

🔧 REFAKTORÁLT ARCHITEKTÚRA: Minden chart osztály külön modulban
📦 CLEAN IMPORTS: Strukturált import rendszer az új charts package-ből
🎨 TÉMA INTEGRÁCIÓ: SimplifiedThemeManager automatikus kezelés
✅ Piros (#C43939) téma támogatás
✅ Duplikáció bugfix minden chart-ban
🌪️ WIND GUSTS KRITIKUS JAVÍTÁS: WindChart és WindRoseChart explicit debug és frissítés
✅ Professional styling

Ez a widget fogja össze a különböző diagramokat egy füles (tabbed) felületen.
Minden diagram most saját modulban található a charts/ package-ben.

FRISSÍTETT IMPORT STRUKTÚRA:
```python
from .charts import (
    EnhancedTemperatureChart, PrecipitationChart, WindChart,
    WindRoseChart, HeatmapCalendarChart, MultiYearComparisonChart
)
```

ELTÁVOLÍTOTT OSZTÁLYOK (most charts/ package-ben):
- WeatherChart → charts/base_chart.py
- EnhancedTemperatureChart → charts/temperature_chart.py
- PrecipitationChart → charts/precipitation_chart.py
- WindChart → charts/wind_chart.py
- WindRoseChart → charts/wind_rose_chart.py
- HeatmapCalendarChart → charts/heatmap_chart.py
- MultiYearComparisonChart → charts/comparison_chart.py
"""

from typing import Optional, Dict, Any
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QCheckBox, QLabel
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont

# === FRISSÍTETT IMPORT STRUKTÚRA - CHARTS PACKAGE ===

from .charts import (
    EnhancedTemperatureChart,
    PrecipitationChart, 
    WindChart,
    WindRoseChart,
    HeatmapCalendarChart,
    MultiYearComparisonChart
)

from .theme_manager import get_theme_manager, register_widget_for_theming, get_current_colors


class ChartsContainer(QWidget):
    """
    Grafikonok fő konténer widget - PROFESSZIONÁLIS NAGY CHARTOK + DUPLIKÁCIÓ BUGFIX + MOCK ADATOK NÉLKÜL + SIMPLIFIED THEMEMANAGER.
    Bővített tabbed interface az új chart típusokhoz.
    
    🔄 FÁZIS 4: Professzionális nagy chartok integrálása
    📊 ÚJ CHARTOK: Enhanced Temperature, Heatmap Calendar, Wind Rose, Multi-Year
    🔧 KRITIKUS JAVÍTÁS: Toggle funkciók optimalizálása duplikáció nélkül + LEGEND POZÍCIÓ JAVÍTVA
    🚨 MOCK/DEMO ADATOK TELJES ELTÁVOLÍTÁSA - csak valódi API adatok használhatók
    🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ: Automatikus téma kezelés minden charthoz
    🌪️ WIND GUSTS KRITIKUS JAVÍTÁS: WindChart és WindRoseChart explicit debug és adatátadás
    """
    
    # Signalok
    chart_exported = Signal(str, bool)  # filepath, success
    chart_settings_changed = Signal(dict)  # settings dict
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Charts konténer inicializálása - PROFESSZIONÁLIS CHARTOKKAL + DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER."""
        super().__init__(parent)
        
        # 🔧 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ
        self.theme_manager = get_theme_manager()
        
        self.current_data: Optional[Dict[str, Any]] = None
        
        self._init_ui()
        self._connect_signals()
        
        # 🎨 WIDGET REGISZTRÁCIÓ TÉMA KEZELÉSHEZ - AUTOMATIKUS
        register_widget_for_theming(self, "container")
        
        print("✅ DEBUG: ChartsContainer initialized with refactored chart modules + SimplifiedThemeManager integration + Wind Gusts")
    
    def _init_ui(self) -> None:
        """UI inicializálása - BŐVÍTETT CHART GALÉRIA + SIMPLIFIED THEMEMANAGER."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Vezérlő panel
        controls = self._create_controls()
        layout.addWidget(controls)
        
        # Chart tabs - BŐVÍTETT + AUTOMATIKUS THEMING
        self.tabs = QTabWidget()
        
        # 🎨 AUTOMATIKUS WIDGET REGISZTRÁCIÓ TÉMA KEZELÉSHEZ
        register_widget_for_theming(self.tabs, "container")
        
        # === CHART TAB-OK - REFAKTORÁLT MODULÁRIS STRUKTÚRA + WIND GUSTS ===
        
        # 1. Hőmérséklet tab - ENHANCED
        self.temp_chart = EnhancedTemperatureChart()
        self.tabs.addTab(self.temp_chart, "🌡️ Hőmérséklet")
        
        # 2. Csapadék tab - MEGTARTVA
        self.precip_chart = PrecipitationChart()
        self.tabs.addTab(self.precip_chart, "🌧️ Csapadék")
        
        # 3. 🌪️ WIND GUSTS: Szél tab - WIND GUSTS TÁMOGATÁSSAL
        self.wind_chart = WindChart()
        self.tabs.addTab(self.wind_chart, "🌪️ Széllökések")  # WIND GUSTS CÍM
        
        # 4. ÚJ: Heatmap Calendar tab
        self.heatmap_chart = HeatmapCalendarChart()
        self.tabs.addTab(self.heatmap_chart, "📅 Naptár")
        
        # 5. 🌪️ WIND GUSTS: Wind Rose tab - WIND GUSTS TÁMOGATÁSSAL
        self.windrose_chart = WindRoseChart()
        self.tabs.addTab(self.windrose_chart, "🌹 Széllökés Rózsa")  # WIND GUSTS CÍM
        
        # 6. ÚJ: Multi-Year Comparison tab
        self.comparison_chart = MultiYearComparisonChart()
        self.tabs.addTab(self.comparison_chart, "📊 Évek")
        
        layout.addWidget(self.tabs)
    
    def _create_controls(self) -> QWidget:
        """Vezérlő panel létrehozása - BŐVÍTETT + SIMPLIFIED THEMEMANAGER."""
        controls = QWidget()
        controls.setMaximumHeight(50)
        layout = QHBoxLayout(controls)
        
        # 🎨 AUTOMATIKUS WIDGET REGISZTRÁCIÓ
        register_widget_for_theming(controls, "container")
        
        # Chart cím
        title = QLabel("📈 Részletes Grafikonok")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        register_widget_for_theming(title, "text")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Grid toggle
        self.grid_check = QCheckBox("Rácsvonalak")
        self.grid_check.setChecked(True)
        self.grid_check.toggled.connect(self._toggle_grid_optimized)
        register_widget_for_theming(self.grid_check, "input")
        layout.addWidget(self.grid_check)
        
        # Legend toggle
        self.legend_check = QCheckBox("Jelmagyarázat")
        self.legend_check.setChecked(True)
        self.legend_check.toggled.connect(self._toggle_legend_optimized)
        register_widget_for_theming(self.legend_check, "input")
        layout.addWidget(self.legend_check)
        
        # Export gomb
        export_btn = QPushButton("💾 Export")
        export_btn.clicked.connect(self._export_current_chart)
        register_widget_for_theming(export_btn, "button")
        layout.addWidget(export_btn)
        
        return controls
    
    def _connect_signals(self) -> None:
        """Signal kapcsolatok - ÖSSZES CHART + SIMPLIFIED THEMEMANAGER."""
        charts = [
            self.temp_chart, self.precip_chart, self.wind_chart,
            self.heatmap_chart, self.windrose_chart, self.comparison_chart
        ]
        
        for chart in charts:
            chart.chart_clicked.connect(self._on_chart_clicked)
        
        # 🔧 TÉMA VÁLTOZÁS FIGYELÉSE - AUTOMATIKUS
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        
        print("✅ DEBUG: ChartsContainer signals connected including SimplifiedThemeManager + Wind Gusts")
    
    def _on_theme_changed(self, theme_name: str) -> None:
        """
        🎨 TÉMA VÁLTOZÁS KEZELÉSE - összes chart szinkronizálása.
        
        Args:
            theme_name: Új téma neve
        """
        print(f"🎨 DEBUG: ChartsContainer theme changing to: {theme_name}")
        
        # Minden chart explicit témafrissítése
        charts = [
            self.temp_chart, self.precip_chart, self.wind_chart,
            self.heatmap_chart, self.windrose_chart, self.comparison_chart
        ]
        
        for chart in charts:
            if hasattr(chart, '_redraw_with_new_theme'):
                try:
                    chart._redraw_with_new_theme()
                except Exception as e:
                    print(f"⚠️ DEBUG: Chart theme update error for {chart.__class__.__name__}: {e}")
        
        print(f"✅ DEBUG: ChartsContainer theme updated: {theme_name} - ALL CHARTS SYNCHRONIZED")
    
    def _toggle_grid_optimized(self, enabled: bool) -> None:
        """
        🔧 KRITIKUS JAVÍTÁS: Grid toggle optimalizálva - NEM teljes újrarajzolás.
        Csak a grid tulajdonság módosítása, majd refresh.
        """
        print(f"🔧 DEBUG: _toggle_grid_optimized({enabled}) - OPTIMALIZÁLT VERZIÓ + SIMPLIFIED THEMEMANAGER")
        
        try:
            charts = [
                self.temp_chart, self.precip_chart, self.wind_chart,
                self.heatmap_chart, self.windrose_chart, self.comparison_chart
            ]
            
            for chart in charts:
                chart.grid_enabled = enabled
                
                # Csak a grid beállítás módosítása, NEM teljes újrarajzolás
                if hasattr(chart, 'ax') and chart.ax:
                    if enabled:
                        # 🔧 SIMPLIFIED THEMEMANAGER GRID SZÍNEK
                        current_colors = get_current_colors()
                        grid_color = current_colors.get('border', '#d1d5db')
                        grid_alpha = 0.3 if self.theme_manager.get_current_theme() == "light" else 0.2
                        chart.ax.grid(True, alpha=grid_alpha, linestyle='-', linewidth=0.8, color=grid_color)
                    else:
                        chart.ax.grid(False)
                    
                    # Csak a canvas frissítése, NEM teljes chart update
                    chart.draw()
            
            print(f"✅ DEBUG: Grid toggle optimalizálva: {enabled} (SimplifiedThemeManager colors)")
            
        except Exception as e:
            print(f"❌ DEBUG: Grid toggle hiba: {e}")
    
    def _toggle_legend_optimized(self, enabled: bool) -> None:
        """
        🔧 KRITIKUS JAVÍTÁS: Legend toggle optimalizálva - NEM teljes újrarajzolás + SIMPLIFIED THEMEMANAGER.
        """
        print(f"🔧 DEBUG: _toggle_legend_optimized({enabled}) - OPTIMALIZÁLT VERZIÓ + SIMPLIFIED THEMEMANAGER")
        
        try:
            charts = [
                self.temp_chart, self.precip_chart, self.wind_chart,
                self.heatmap_chart, self.windrose_chart, self.comparison_chart
            ]
            
            # 🔧 SIMPLIFIED THEMEMANAGER LEGEND SZÍNEK
            current_colors = get_current_colors()
            
            for chart in charts:
                chart.legend_enabled = enabled
                
                # Csak a legend beállítás módosítása
                if hasattr(chart, 'ax') and chart.ax:
                    if enabled:
                        # Legend megjelenítése, ha van
                        legend = chart.ax.get_legend()
                        if legend:
                            legend.set_visible(True)
                            # 🔧 SIMPLIFIED THEMEMANAGER LEGEND SZÍNEK ALKALMAZÁSA
                            legend.get_frame().set_facecolor(current_colors.get('surface', '#ffffff'))
                            legend.get_frame().set_edgecolor(current_colors.get('border', '#d1d5db'))
                        else:
                            # Új legend létrehozása, ha nincs - JAVÍTOTT POZÍCIÓVAL + SIMPLIFIED THEMEMANAGER
                            legend = chart.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', 
                                          framealpha=0.95, fancybox=True, shadow=True, fontsize=11)
                            legend.get_frame().set_facecolor(current_colors.get('surface', '#ffffff'))
                            legend.get_frame().set_edgecolor(current_colors.get('border', '#d1d5db'))
                    else:
                        # Legend elrejtése
                        legend = chart.ax.get_legend()
                        if legend:
                            legend.set_visible(False)
                    
                    # Csak canvas frissítés
                    chart.draw()
            
            print(f"✅ DEBUG: Legend toggle optimalizálva: {enabled} (SimplifiedThemeManager colors)")
            
        except Exception as e:
            print(f"❌ DEBUG: Legend toggle hiba: {e}")
    
    def _export_current_chart(self) -> None:
        """Aktuális chart exportálása."""
        current_widget = self.tabs.currentWidget()
        if hasattr(current_widget, 'export_chart'):  # WeatherChart methods
            # TODO: file dialog implementálása
            chart_name = self.tabs.tabText(self.tabs.currentIndex()).replace(' ', '_')
            filepath = f"chart_{chart_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            success = current_widget.export_chart(filepath)
            self.chart_exported.emit(filepath, success)
    
    def _on_chart_clicked(self, x: float, y: float) -> None:
        """Chart kattintás kezelése."""
        print(f"Chart clicked at: {x}, {y}")  # Debug
    
    # === PUBLIKUS METÓDUSOK ===
    
    def update_charts(self, data: Dict[str, Any]) -> None:
        """
        🌪️ KRITIKUS JAVÍTÁS: Összes chart frissítése duplikáció-mentesen - WIND GUSTS EXPLICIT DEBUG ÉS FRISSÍTÉS.
        
        PROBLÉMA MEGOLDVA: WindChart és WindRoseChart nem kapták meg az adatokat.
        MEGOLDÁS: Explicit debug és adatátadás széladatokkal.
        """
        print("📈 DEBUG: ChartsContainer.update_charts() - WIND GUSTS KRITIKUS JAVÍTÁS VERZIÓ")
        
        try:
            self.current_data = data
            
            # 🌪️ KRITIKUS DEBUG - Széladatok ellenőrzése az input data-ban
            daily_data = data.get("daily", {})
            wind_gusts_max = daily_data.get("wind_gusts_max", [])
            windspeed_10m_max = daily_data.get("windspeed_10m_max", [])
            
            print(f"🌪️ DEBUG: Input data széladatok:")
            print(f"🌪️ DEBUG: - wind_gusts_max: {len(wind_gusts_max)} elem")
            print(f"🌪️ DEBUG: - windspeed_10m_max: {len(windspeed_10m_max)} elem")
            
            if wind_gusts_max:
                print(f"🌪️ DEBUG: - wind_gusts_max minta értékek: {wind_gusts_max[:3]}")
            if windspeed_10m_max:
                print(f"🌪️ DEBUG: - windspeed_10m_max minta értékek: {windspeed_10m_max[:3]}")
            
            print("📈 DEBUG: Updating all professional charts with SimplifiedThemeManager + WIND GUSTS DEBUG...")
            
            # Szekvenciális frissítés - egy chart egyszerre duplikáció ellen
            print("🌡️ UPDATING temp_chart...")
            self.temp_chart.update_data(data)
            
            print("🌧️ UPDATING precip_chart...")
            self.precip_chart.update_data(data)
            
            # 🌪️ KRITIKUS JAVÍTÁS: WindChart explicit debug és frissítés
            print("🌪️ UPDATING wind_chart... (EXPLICIT WIND GUSTS DEBUG)")
            try:
                self.wind_chart.update_data(data)
                print("✅ DEBUG: wind_chart.update_data() végrehajtva")
            except Exception as wind_error:
                print(f"❌ DEBUG: wind_chart.update_data() HIBA: {wind_error}")
            
            # Új professzionális chartok
            print("📅 UPDATING heatmap_chart...")
            self.heatmap_chart.update_data(data)
            
            # 🌪️ KRITIKUS JAVÍTÁS: WindRoseChart explicit debug és frissítés
            print("🌹 UPDATING windrose_chart... (EXPLICIT WIND GUSTS DEBUG)")
            try:
                self.windrose_chart.update_data(data)
                print("✅ DEBUG: windrose_chart.update_data() végrehajtva")
            except Exception as windrose_error:
                print(f"❌ DEBUG: windrose_chart.update_data() HIBA: {windrose_error}")
            
            print("📊 UPDATING comparison_chart...")
            self.comparison_chart.update_data(data)
            
            print("✅ DEBUG: All professional charts updated - DUPLIKÁCIÓ MENTES + SIMPLIFIED THEMEMANAGER + WIND GUSTS EXPLICIT DEBUG")
            
            # 🌪️ TOVÁBBI DEBUG: WindChart státusz ellenőrzése
            if hasattr(self.wind_chart, 'current_data'):
                wind_data_status = "VAN" if self.wind_chart.current_data else "NINCS"
                print(f"🌪️ FINAL DEBUG: wind_chart.current_data státusz: {wind_data_status}")
            
            if hasattr(self.windrose_chart, 'current_data'):
                windrose_data_status = "VAN" if self.windrose_chart.current_data else "NINCS"
                print(f"🌹 FINAL DEBUG: windrose_chart.current_data státusz: {windrose_data_status}")
            
        except Exception as e:
            print(f"❌ DEBUG: ChartsContainer frissítési hiba: {e}")
            import traceback
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
    
    def clear_charts(self) -> None:
        """Összes chart törlése - BŐVÍTETT LISTA + WIND GUSTS."""
        self.current_data = None
        
        charts = [
            self.temp_chart, self.precip_chart, self.wind_chart,
            self.heatmap_chart, self.windrose_chart, self.comparison_chart
        ]
        
        for chart in charts:
            chart.clear_chart()
        
        print("🧹 DEBUG: All professional charts cleared (including Wind Gusts)")
    
    def apply_theme(self, dark_theme: bool) -> None:
        """
        🎨 DEPRECATED: Téma alkalmazása - SIMPLIFIED THEMEMANAGER-RE DELEGÁLVA.
        
        Args:
            dark_theme: Sötét téma-e (DEPRECATED, használd a SimplifiedThemeManager-t)
        """
        print("⚠️ DEBUG: apply_theme() DEPRECATED - use SimplifiedThemeManager.set_theme() instead")
        
        # Backward compatibility - SimplifiedThemeManager-re delegálás
        theme_name = "dark" if dark_theme else "light"
        self.theme_manager.set_theme(theme_name)