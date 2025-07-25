#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🇭🇺 ENHANCED Universal Location Selector - Magyar Prioritással
Magyar Klímaanalitika MVP - DUAL DATABASE Integráció

🚀 ÚJ FUNKCIÓK:
✅ search_unified() - KOMBINÁLT keresés (3178 magyar + 44k globális)
✅ Magyar flag-ek (🇭🇺) és globális flag-ek (🌍)
✅ Settlement type megjelenítés (város/nagyközség/község)
✅ Magyar prioritás - magyar települések előre
✅ Hierarchikus keresés - minden magyar település típus
✅ Egyszerűsített UI - 1 panel (3 tab helyett)

KERESÉSI LOGIKA:
- "Kiskunhalas" → 🇭🇺 Kiskunhalas, Bács-Kiskun megye (város) 
- "Abaliget" → 🇭🇺 Abaliget, Baranya megye (község)
- "Budapest" → 🇭🇺 Budapest (főváros) + 🌍 Budapest, Hungary
- "London" → 🌍 London, England, United Kingdom

Fájl helye: src/gui/universal_location_selector.py
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, 
    QListWidgetItem, QLabel, QPushButton, QFrame, QSizePolicy, 
    QScrollArea, QGroupBox
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QFont
from typing import Dict, List, Optional, Any
import logging

from ..data.models import UniversalLocation, LocationType
from ..data.city_manager import CityManager, City
from .theme_manager import register_widget_for_theming

logger = logging.getLogger(__name__)


class LocationCard(QFrame):
    """🎨 Kiválasztott lokáció megjelenítő kártya - MAGYAR KOMPATIBILIS"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setMinimumHeight(80)
        self.setMaximumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)
        
        # Cím
        self.title_label = QLabel("Nincs kiválasztva")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)
        
        # Részletek
        self.details_label = QLabel("Válassz egy lokációt a keresésből")
        details_font = QFont()
        details_font.setPointSize(11)
        self.details_label.setFont(details_font)
        self.details_label.setStyleSheet("color: #64748B;")
        self.details_label.setWordWrap(True)
        layout.addWidget(self.details_label)
        
        # Modern styling
        self.setStyleSheet("""
            LocationCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8FAFC);
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                margin: 4px;
            }
            LocationCard:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F8FAFC, stop:1 #F1F5F9);
                border: 2px solid #CBD5E1;
            }
        """)
    
    def set_location(self, name: str, details: str, is_hungarian: bool = False):
        """🇭🇺 Lokáció beállítása MAGYAR TÁMOGATÁSSAL"""
        flag = "🇭🇺" if is_hungarian else "🌍"
        self.title_label.setText(f"{flag} {name}")
        self.details_label.setText(details)
    
    def clear(self):
        """Kártya törlése"""
        self.title_label.setText("Nincs kiválasztva")
        self.details_label.setText("Válassz egy lokációt a keresésből")


class UniversalLocationSelector(QWidget):
    """
    🇭🇺 ENHANCED Universal Location Selector - DUAL DATABASE
    
    KOMBINÁLT KERESÉS:
    - 3178+ magyar település (falvak, községek, városok)
    - 44k+ globális város
    - Magyar prioritás működik
    - Flag-ek és settlement type-ok
    
    SIGNALOK:
    - search_requested(str): keresés indítva
    - city_selected(str, float, float, dict): lokáció kiválasztva
    - location_changed(UniversalLocation): lokáció változott
    """
    
    # Signalok
    search_requested = Signal(str)
    city_selected = Signal(str, float, float, dict)
    location_changed = Signal(object)
    
    def __init__(self, city_manager: Optional[CityManager] = None, parent=None):
        super().__init__(parent)
        
        self.city_manager = city_manager or CityManager()
        self.current_location: Optional[UniversalLocation] = None
        
        # Search timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
        
        self._setup_ui()
        self._connect_signals()
        
        register_widget_for_theming(self, "container")
        
        logger.info("🇭🇺 Enhanced Universal Location Selector inicializálva (DUAL DATABASE)")
    
    def _setup_ui(self):
        """🎨 Enhanced UI létrehozása - MAGYAR PRIORITÁSSAL"""
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # === HEADER ===
        header_label = QLabel("🇭🇺 Magyar + Globális Lokáció Keresés")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(16)
        header_label.setFont(header_font)
        header_label.setStyleSheet("color: #1E293B; margin-bottom: 8px;")
        layout.addWidget(header_label)
        
        # === SEARCH GROUP ===
        search_group = QGroupBox("🔍 Kombinált Keresés")
        search_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #1E293B;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background: #FFFFFF;
            }
        """)
        search_layout = QVBoxLayout(search_group)
        search_layout.setContentsMargins(12, 16, 12, 12)
        search_layout.setSpacing(12)
        
        # Modern search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🇭🇺 Magyar települések + 🌍 44k globális város... (pl. Kiskunhalas, Abaliget, London)")
        self.search_input.setMinimumHeight(40)
        self.search_input.setMaximumHeight(44)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #FFFFFF;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: #1E293B;
            }
            QLineEdit:hover {
                border: 2px solid #CBD5E1;
            }
            QLineEdit:focus {
                border: 2px solid #3B82F6;
                background: #FFFFFF;
            }
            QLineEdit::placeholder {
                color: #94A3B8;
            }
        """)
        search_layout.addWidget(self.search_input)
        
        # Status label
        self.status_label = QLabel("💡 Kezdj el gépelni a kereséshez...")
        self.status_label.setStyleSheet("""
            color: #64748B; 
            font-style: italic;
            background: #F8FAFC;
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid #E2E8F0;
            font-size: 12px;
        """)
        search_layout.addWidget(self.status_label)
        
        layout.addWidget(search_group)
        
        # === RESULTS GROUP ===
        results_group = QGroupBox("📋 Keresési Eredmények")
        results_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #1E293B;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background: #FFFFFF;
            }
        """)
        results_layout = QVBoxLayout(results_group)
        results_layout.setContentsMargins(12, 16, 12, 12)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(200)
        self.results_list.setMaximumHeight(250)
        self.results_list.setStyleSheet("""
            QListWidget {
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px;
            }
            QListWidget::item {
                background: #FFFFFF;
                border: 1px solid #F1F5F9;
                border-radius: 6px;
                padding: 12px;
                margin: 4px 0px;
                font-size: 13px;
            }
            QListWidget::item:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F8FAFC, stop:1 #F1F5F9);
                border: 1px solid #CBD5E1;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border: 1px solid #1D4ED8;
            }
        """)
        results_layout.addWidget(self.results_list)
        
        layout.addWidget(results_group)
        
        # === SELECTED LOCATION GROUP ===
        selection_group = QGroupBox("🎯 Kiválasztott Lokáció")
        selection_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #1E293B;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background: #FFFFFF;
            }
        """)
        selection_layout = QVBoxLayout(selection_group)
        selection_layout.setContentsMargins(12, 16, 12, 12)
        
        # Location card
        self.location_card = LocationCard()
        selection_layout.addWidget(self.location_card)
        
        # Confirm button
        self.confirm_button = QPushButton("✅ Lokáció Megerősítése")
        self.confirm_button.setMinimumHeight(40)
        self.confirm_button.setMaximumHeight(44)
        self.confirm_button.setEnabled(False)
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2563EB, stop:1 #1D4ED8);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1D4ED8, stop:1 #1E40AF);
            }
            QPushButton:disabled {
                background: #E2E8F0;
                color: #94A3B8;
            }
        """)
        selection_layout.addWidget(self.confirm_button)
        
        layout.addWidget(selection_group)
        
        # Stretch
        layout.addStretch()
        
        # 🎯 KOMPAKT SIZING
        self.setMinimumSize(300, 450)  # 420px → 300px szélesség
        self.setMaximumHeight(550)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
    
    def _connect_signals(self):
        """Signal kapcsolatok"""
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.results_list.itemDoubleClicked.connect(self._on_result_selected)
        self.results_list.itemClicked.connect(self._on_result_clicked)
        self.confirm_button.clicked.connect(self._on_confirm_selection)
    
    def _on_search_text_changed(self, text: str):
        """Keresés szöveg változáskor"""
        if len(text) < 2:
            self.results_list.clear()
            self.status_label.setText("💡 Legalább 2 karakter szükséges...")
            self.confirm_button.setEnabled(False)
            return
            
        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms késleltetés
        self.status_label.setText("🔍 Keresés...")
    
    def _perform_search(self):
        """🚀 KOMBINÁLT KERESÉS - Magyar + Globális"""
        query = self.search_input.text().strip()
        if len(query) < 2:
            return
            
        try:
            self.search_requested.emit(query)
            
            # 🇭🇺 KULCS VÁLTOZÁS: search_unified() hívása
            results = self.city_manager.search_unified(query, limit=20, hungarian_priority=True)
            
            self._display_results(results)
            
            if not results:
                self.status_label.setText(f"❌ Nincs találat a '{query}' keresésre")
            else:
                # Eredmény típusok számlálása
                hungarian_count = sum(1 for city in results if city.is_hungarian)
                global_count = len(results) - hungarian_count
                
                if hungarian_count > 0 and global_count > 0:
                    self.status_label.setText(f"✅ {hungarian_count} magyar + {global_count} globális = {len(results)} találat")
                elif hungarian_count > 0:
                    self.status_label.setText(f"✅ {hungarian_count} magyar találat")
                else:
                    self.status_label.setText(f"✅ {global_count} globális találat")
                
        except Exception as e:
            logger.error(f"Keresési hiba: {e}")
            self.status_label.setText("❌ Keresési hiba történt")
    
    def _display_results(self, results: List[City]):
        """🇭🇺 Keresési eredmények megjelenítése MAGYAR PRIORITÁSSAL"""
        self.results_list.clear()
        
        for city in results[:20]:  # Első 20 eredmény
            try:
                # Alap adatok
                name = city.city
                lat = city.lat
                lon = city.lon
                is_hungarian = city.is_hungarian
                
                # 🇭🇺 MAGYAR SPECIFIKUS FORMATTING
                if is_hungarian:
                    flag = "🇭🇺"
                    
                    # Display név: "Kiskunhalas, Bács-Kiskun megye"
                    if city.megye:
                        display_name = f"{name}, {city.megye} megye"
                    else:
                        display_name = name
                    
                    # Settlement type info
                    settlement_info = ""
                    if city.settlement_type:
                        settlement_info = f" ({city.settlement_type})"
                    
                    # Population info
                    pop_info = ""
                    if city.population:
                        pop_info = f"\n👥 {city.population:,} lakos"
                    
                    display_text = f"{flag} {display_name}{settlement_info}{pop_info}\n🗺️ [{lat:.3f}, {lon:.3f}]"
                    
                else:
                    # 🌍 GLOBÁLIS FORMATTING (eredeti)
                    flag = "🌍"
                    country = city.country or ''
                    region = city.admin_name or ''
                    
                    display_text = f"{flag} {name}"
                    if region and region != name:
                        display_text += f"\n📍 {region}"
                    if country:
                        display_text += f", {country}"
                    display_text += f"\n🗺️ [{lat:.3f}, {lon:.3f}]"
                
                # List item létrehozása
                item = QListWidgetItem(display_text)
                city_dict = city.to_dict()
                item.setData(Qt.UserRole, city_dict)
                self.results_list.addItem(item)
                
            except Exception as e:
                logger.warning(f"Eredmény feldolgozási hiba: {e}")
    
    def _on_result_clicked(self, item: QListWidgetItem):
        """Eredményre kattintás (preview) - MAGYAR TÁMOGATÁSSAL"""
        try:
            result_data = item.data(Qt.UserRole)
            if result_data:
                name = result_data.get('city', 'Ismeretlen')
                country = result_data.get('country', '')
                region = result_data.get('admin_name', '')
                lat = float(result_data.get('lat', 0.0))
                lon = float(result_data.get('lon', 0.0))
                is_hungarian = result_data.get('is_hungarian', False)
                
                # 🇭🇺 MAGYAR SPECIFIKUS DETAILS
                details_parts = []
                
                if is_hungarian:
                    # Magyar település részletek
                    settlement_type = result_data.get('settlement_type')
                    if settlement_type:
                        details_parts.append(f"Típus: {settlement_type}")
                    
                    megye = result_data.get('megye')
                    if megye:
                        details_parts.append(f"Megye: {megye}")
                    
                    jaras = result_data.get('jaras')
                    if jaras:
                        details_parts.append(f"Járás: {jaras}")
                    
                    population = result_data.get('population')
                    if population:
                        details_parts.append(f"Lakosság: {population:,}")
                        
                else:
                    # Globális város részletek (eredeti)
                    if region and region != name:
                        details_parts.append(f"Régió: {region}")
                    if country:
                        details_parts.append(f"Ország: {country}")
                
                details_parts.append(f"Koordináták: [{lat:.4f}, {lon:.4f}]")
                details = "\n".join(details_parts)
                
                # Card frissítése
                self.location_card.set_location(name, details, is_hungarian)
                self.confirm_button.setEnabled(True)
                
                logger.info(f"Eredmény preview: {name} ({'magyar' if is_hungarian else 'globális'})")
                
        except Exception as e:
            logger.error(f"Preview hiba: {e}")
    
    def _on_result_selected(self, item: QListWidgetItem):
        """Eredmény dupla kattintás (azonnali kiválasztás)"""
        self._on_result_clicked(item)  # Preview
        self._on_confirm_selection()   # Azonnali megerősítés
    
    def _on_confirm_selection(self):
        """Lokáció megerősítése"""
        try:
            current_item = self.results_list.currentItem()
            if not current_item:
                return
                
            result_data = current_item.data(Qt.UserRole)
            if not result_data:
                return
            
            name = result_data.get('city', 'Ismeretlen')
            lat = float(result_data.get('lat', 0.0))
            lon = float(result_data.get('lon', 0.0))
            is_hungarian = result_data.get('is_hungarian', False)
            
            # UniversalLocation objektum létrehozása
            location = UniversalLocation(
                type=LocationType.CITY,
                identifier=name,
                display_name=name,
                coordinates=(lat, lon)
            )
            
            self.current_location = location
            
            # Signalok küldése
            self.city_selected.emit(name, lat, lon, result_data)
            self.location_changed.emit(location)
            
            flag = "🇭🇺" if is_hungarian else "🌍"
            logger.info(f"Lokáció megerősítve: {flag} {name} [{lat:.4f}, {lon:.4f}]")
            
        except Exception as e:
            logger.error(f"Megerősítési hiba: {e}")
    
    # === PUBLIKUS API ===
    
    def get_current_location(self) -> Optional[UniversalLocation]:
        """Jelenlegi lokáció lekérdezése"""
        return self.current_location
    
    def set_current_location(self, location: UniversalLocation):
        """Lokáció programmatic beállítása"""
        self.current_location = location
        self.location_changed.emit(location)
        
        # UI frissítése
        if location:
            lat, lon = location.coordinates
            details = f"Koordináták: [{lat:.4f}, {lon:.4f}]"
            self.location_card.set_location(location.display_name, details)
            self.confirm_button.setEnabled(True)
    
    def clear_selection(self):
        """Kiválasztás törlése"""
        self.current_location = None
        self.search_input.clear()
        self.results_list.clear()
        self.location_card.clear()
        self.confirm_button.setEnabled(False)
        self.status_label.setText("💡 Kezdj el gépelni a kereséshez...")
    
    def focus_search(self):
        """Fókusz a keresőmezőre"""
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def get_search_text(self) -> str:
        """Jelenlegi keresés szöveg"""
        return self.search_input.text()
    
    def set_search_text(self, text: str):
        """Keresés szöveg beállítása"""
        self.search_input.setText(text)
