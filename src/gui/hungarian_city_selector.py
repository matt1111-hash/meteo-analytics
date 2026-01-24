#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hungarian City Selector Widget - Magyar Klímaanalitika MVP
165 magyar város dinamikus választó widget

🇭🇺 FUNKCIONALITÁS:
- 165 magyar város betöltése cities.db-ből  
- Régió alapú szűrés (Alföld, Dunántúl, Közép-Magyarország, Északi-régió)
- Keresési funkció magyar városnevekben  
- Népesség szerinti rendezés
- ThemeManager integráció
- Signal-based kommunikáció

🔗 INTEGRÁCIÓ:
- Dashboard + ControlPanel kompatibilis
- city_selected signal → Controller
- region_selected signal → Analytics
- Meglévő signal chain kompatibilis

Fájl helye: src/gui/hungarian_city_selector.py
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QComboBox, QListWidget,
    QListWidgetItem, QPushButton, QFrame, QScrollArea,
    QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap

from .theme_manager import get_theme_manager, register_widget_for_theming, get_current_colors

# Logging
logger = logging.getLogger(__name__)


@dataclass
class HungarianCity:
    """Magyar város adatstruktúra"""
    city: str
    country: str
    country_code: str
    lat: float
    lon: float
    population: Optional[int] = None
    admin_name: Optional[str] = None
    meteostat_station_id: Optional[str] = None
    data_quality_score: Optional[float] = None
    region: Optional[str] = None


class HungarianRegions:
    """
    🇭🇺 Magyar régiók osztályozása és mappingje
    """
    
    # Régió mappingek népszerű városok alapján
    REGION_MAPPING = {
        # Alföld
        'Debrecen': 'Alföld',
        'Szeged': 'Alföld', 
        'Kecskemét': 'Alföld',
        'Nyíregyháza': 'Alföld',
        'Békéscsaba': 'Alföld',
        'Szolnok': 'Alföld',
        'Orosháza': 'Alföld',
        'Cegléd': 'Alföld',
        'Hodmezovasarhely': 'Alföld',
        'Jászberény': 'Alföld',
        
        # Dunántúl
        'Pécs': 'Dunántúl',
        'Győr': 'Dunántúl',
        'Székesfehérvár': 'Dunántúl',
        'Szombathely': 'Dunántúl',
        'Kaposvár': 'Dunántúl',
        'Veszprém': 'Dunántúl',
        'Zalaegerszeg': 'Dunántúl',
        'Nagykanizsa': 'Dunántúl',
        'Sopron': 'Dunántúl',
        'Tatabánya': 'Dunántúl',
        'Dunaújváros': 'Dunántúl',
        'Ajka': 'Dunántúl',
        
        # Közép-Magyarország  
        'Budapest': 'Közép-Magyarország',
        'Gödöllő': 'Közép-Magyarország',
        'Vác': 'Közép-Magyarország',
        'Szentendre': 'Közép-Magyarország',
        
        # Északi-régió
        'Miskolc': 'Északi-régió',
        'Eger': 'Északi-régió',
        'Salgótarján': 'Északi-régió',
        'Gyöngyös': 'Északi-régió',
        'Balassagyarmat': 'Északi-régió'
    }
    
    REGION_DISPLAY_NAMES = {
        'Alföld': '🌾 Alföld',
        'Dunántúl': '🏔️ Dunántúl', 
        'Közép-Magyarország': '🏛️ Közép-Magyarország',
        'Északi-régió': '⛰️ Északi-régió',
        'Egyéb': '🏘️ Egyéb'
    }
    
    REGION_DESCRIPTIONS = {
        'Alföld': 'Nagy Magyar Alföld - síkvidéki klíma',
        'Dunántúl': 'Dunántúli-dombság és középhegység',
        'Közép-Magyarország': 'Főváros és agglomeráció', 
        'Északi-régió': 'Északi-középhegység vidéke',
        'Egyéb': 'Egyéb területek'
    }
    
    @classmethod
    def get_region_for_city(cls, city_name: str) -> str:
        """
        Város régió besorolásának meghatározása.
        
        Args:
            city_name: Magyar város neve
            
        Returns:
            Régió neve vagy 'Egyéb'
        """
        return cls.REGION_MAPPING.get(city_name, 'Egyéb')
    
    @classmethod
    def get_all_regions(cls) -> List[str]:
        """Összes régió listája"""
        return list(cls.REGION_DISPLAY_NAMES.keys())
    
    @classmethod
    def get_cities_by_region(cls, region: str, cities: List[HungarianCity]) -> List[HungarianCity]:
        """
        Városok szűrése régió alapján.
        
        Args:
            region: Régió neve
            cities: Összes város listája
            
        Returns:
            Szűrt városok listája
        """
        if region == 'Összes':
            return cities
            
        filtered_cities = []
        for city in cities:
            city_region = cls.get_region_for_city(city.city)
            if city_region == region:
                filtered_cities.append(city)
        
        return filtered_cities


class HungarianCitySelector(QWidget):
    """
    🇭🇺 Hungarian City Selector Widget - Magyar Klímaanalitika MVP
    
    165 magyar város dinamikus választó widget teljes funkcionalitással:
    - Adatbázis integráció (cities.db)
    - Régió alapú szűrés
    - Keresési funkció
    - ThemeManager integráció
    - Signal-based kommunikáció
    """
    
    # Signalok
    city_selected = Signal(str, float, float, dict)      # name, lat, lon, metadata
    region_selected = Signal(str, list)                  # region_name, cities
    search_completed = Signal(int)                       # results_count
    data_loaded = Signal(int)                           # cities_count
    error_occurred = Signal(str)                        # error_message
    
    def __init__(self, db_path: str = "src/data/cities.db", parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Konfiguráció
        self.db_path = Path(db_path)
        self.theme_manager = get_theme_manager()
        
        # Adatok
        self.hungarian_cities: List[HungarianCity] = []
        self.filtered_cities: List[HungarianCity] = []
        self.current_region = 'Összes'
        self.current_search_term = ''
        
        # UI elemek referenciái
        self.search_box: Optional[QLineEdit] = None
        self.region_combo: Optional[QComboBox] = None
        self.city_list: Optional[QListWidget] = None
        self.stats_label: Optional[QLabel] = None
        self.quick_access_buttons: List[QPushButton] = []
        
        # Keresési debounce timer
        self.search_timer: Optional[QTimer] = None
        
        # UI építése
        self._setup_ui()
        self._setup_theme()
        self._setup_search_timer()
        
        # Adatok betöltése
        self._load_hungarian_cities()
        
        logger.info("🇭🇺 HungarianCitySelector widget inicializálva")
    
    def _setup_ui(self) -> None:
        """UI komponensek felépítése"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)
        
        # === FEJLÉC ===
        header_layout = self._create_header()
        main_layout.addLayout(header_layout)
        
        # === KERESÉSI SZAKASZ ===
        search_group = self._create_search_section()
        main_layout.addWidget(search_group)
        
        # === SZŰRÉSI SZAKASZ ===
        filter_group = self._create_filter_section()
        main_layout.addWidget(filter_group)
        
        # === VÁROSOK LISTÁJA ===
        cities_group = self._create_cities_list_section()
        main_layout.addWidget(cities_group)
        
        # === GYORS HOZZÁFÉRÉS ===
        quick_group = self._create_quick_access_section()
        main_layout.addWidget(quick_group)
        
        # === STATISZTIKÁK ===
        stats_group = self._create_statistics_section()
        main_layout.addWidget(stats_group)
        
        # Rugalmas tér
        main_layout.addStretch()
    
    def _create_header(self) -> QHBoxLayout:
        """Fejléc létrehozása"""
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        # Magyar zászló és cím
        flag_label = QLabel("🇭🇺")
        flag_label.setStyleSheet("font-size: 24px; border: none; background: transparent;")
        layout.addWidget(flag_label)
        
        title_label = QLabel("Magyar Városok")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Verzió info
        version_label = QLabel("MVP v1.0")
        version_label.setStyleSheet("color: gray; font-size: 10px; border: none; background: transparent;")
        layout.addWidget(version_label)
        
        return layout
    
    def _create_search_section(self) -> QGroupBox:
        """Keresési szakasz létrehozása"""
        group = QGroupBox("🔍 Keresés")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        # Keresőmező
        search_container = QHBoxLayout()
        
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 16px; border: none; background: transparent;")
        search_container.addWidget(search_icon)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Keresés magyar városokban... (pl. Budapest, Szeged, Debrecen)")
        self.search_box.textChanged.connect(self._on_search_text_changed)
        self.search_box.returnPressed.connect(self._trigger_search)
        search_container.addWidget(self.search_box)
        
        clear_btn = QPushButton("✖")
        clear_btn.setMaximumWidth(30)
        clear_btn.setToolTip("Keresés törlése")
        clear_btn.clicked.connect(self._clear_search)
        search_container.addWidget(clear_btn)
        
        layout.addLayout(search_container)
        
        return group
    
    def _create_filter_section(self) -> QGroupBox:
        """Szűrési szakasz létrehozása"""
        group = QGroupBox("🗺️ Régió szűrés")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        # Régió választó
        region_layout = QHBoxLayout()
        
        region_label = QLabel("Régió:")
        region_layout.addWidget(region_label)
        
        self.region_combo = QComboBox()
        self.region_combo.addItem("🇭🇺 Összes magyar város", "Összes")
        
        # Régiók hozzáadása
        for region in HungarianRegions.get_all_regions():
            display_name = HungarianRegions.REGION_DISPLAY_NAMES[region]
            description = HungarianRegions.REGION_DESCRIPTIONS[region]
            self.region_combo.addItem(f"{display_name}", region)
            
            # Tooltip beállítása
            index = self.region_combo.count() - 1
            self.region_combo.setItemData(index, description, Qt.ToolTipRole)
        
        self.region_combo.currentTextChanged.connect(self._on_region_changed)
        region_layout.addWidget(self.region_combo)
        
        region_layout.addStretch()
        
        layout.addLayout(region_layout)
        
        return group
    
    def _create_cities_list_section(self) -> QGroupBox:
        """Városok listája szakasz létrehozása"""
        group = QGroupBox("🏙️ Magyar városok listája")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        # Városok lista
        self.city_list = QListWidget()
        self.city_list.setMinimumHeight(300)
        self.city_list.setMaximumHeight(400)
        self.city_list.itemDoubleClicked.connect(self._on_city_selected)
        layout.addWidget(self.city_list)
        
        # Lista alatti műveletek
        actions_layout = QHBoxLayout()
        
        select_btn = QPushButton("✅ Kiválasztás")
        select_btn.clicked.connect(self._select_current_city)
        actions_layout.addWidget(select_btn)
        
        actions_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Frissítés")
        refresh_btn.setToolTip("Városok listájának újratöltése")
        refresh_btn.clicked.connect(self._reload_cities)
        actions_layout.addWidget(refresh_btn)
        
        layout.addLayout(actions_layout)
        
        return group
    
    def _create_quick_access_section(self) -> QGroupBox:
        """Gyors hozzáférés szakasz létrehozása"""
        group = QGroupBox("⚡ Gyors hozzáférés - Nagy magyar városok")
        layout = QGridLayout(group)
        layout.setSpacing(6)
        
        # Népszerű magyar városok
        quick_cities = [
            ("🏛️ Budapest", "Budapest", "Főváros - 1.7M lakos"),
            ("🌾 Debrecen", "Debrecen", "Cívisváros - 201k lakos"),
            ("🏭 Miskolc", "Miskolc", "Észak-Magyarország - 161k lakos"),
            ("🌊 Szeged", "Szeged", "Tisza-parti egyetemváros - 161k lakos"),
            ("⚙️ Pécs", "Pécs", "Dunántúli kulturális központ - 143k lakos"),
            ("🌍 Győr", "Győr", "Kisalföld központja - 129k lakos"),
            ("🏔️ Székesfehérvár", "Székesfehérvár", "Fejér megye székhelye - 95k lakos"),
            ("⛰️ Nyíregyháza", "Nyíregyháza", "Szabolcs-Szatmár-Bereg - 118k lakos"),
            ("🍇 Kecskemét", "Kecskemét", "Bács-Kiskun megye - 109k lakos"),
            ("🌲 Szombathely", "Szombathely", "Vas megye székhelye - 76k lakos"),
            ("💎 Veszprém", "Veszprém", "Balaton-felvidék - 57k lakos"),
            ("🍷 Kaposvár", "Kaposvár", "Somogy megye székhelye - 63k lakos")
        ]
        
        self.quick_access_buttons = []
        
        for i, (display, city, tooltip) in enumerate(quick_cities):
            btn = QPushButton(display)
            btn.setToolTip(tooltip)
            btn.setMinimumHeight(35)
            btn.clicked.connect(lambda checked, c=city: self._select_quick_city(c))
            
            # Rács elrendezés: 3 város per sor
            row = i // 3
            col = i % 3
            layout.addWidget(btn, row, col)
            
            self.quick_access_buttons.append(btn)
        
        return group
    
    def _create_statistics_section(self) -> QGroupBox:
        """Statisztikák szakasz létrehozása"""
        group = QGroupBox("📊 Statisztikák")
        layout = QVBoxLayout(group)
        layout.setSpacing(4)
        
        self.stats_label = QLabel("Városok betöltése...")
        self.stats_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.stats_label)
        
        return group
    
    def _setup_theme(self) -> None:
        """Téma beállítása"""
        # Widget regisztrációk ThemeManager-hez
        register_widget_for_theming(self, "container")
        register_widget_for_theming(self.search_box, "input")
        register_widget_for_theming(self.region_combo, "input")
        register_widget_for_theming(self.city_list, "table")
        
        # Quick access gombok regisztrálása
        for btn in self.quick_access_buttons:
            register_widget_for_theming(btn, "button")
        
        # Téma változás figyelése
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        
        # Kezdeti téma alkalmazása
        self._apply_current_theme()
    
    def _setup_search_timer(self) -> None:
        """Keresési debounce timer beállítása"""
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._trigger_search)
    
    def _load_hungarian_cities(self) -> None:
        """
        Magyar városok betöltése a cities.db adatbázisból
        """
        try:
            logger.info(f"🇭🇺 Magyar városok betöltése: {self.db_path}")
            
            if not self.db_path.exists():
                error_msg = f"Cities adatbázis nem található: {self.db_path}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                self._update_stats("❌ Adatbázis hiba")
                return
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Magyar városok lekérdezése
                query = """
                SELECT city, country, country_code, lat, lon, population, 
                       admin_name, meteostat_station_id, data_quality_score
                FROM cities 
                WHERE country_code = 'HU' AND country = 'Hungary'
                ORDER BY 
                    CASE WHEN population IS NOT NULL THEN population ELSE 0 END DESC,
                    city ASC
                """
                
                cursor.execute(query)
                results = cursor.fetchall()
                
                # HungarianCity objektumok létrehozása
                self.hungarian_cities = []
                for row in results:
                    city = HungarianCity(
                        city=row[0],
                        country=row[1], 
                        country_code=row[2],
                        lat=row[3],
                        lon=row[4],
                        population=row[5],
                        admin_name=row[6],
                        meteostat_station_id=row[7],
                        data_quality_score=row[8],
                        region=HungarianRegions.get_region_for_city(row[0])
                    )
                    self.hungarian_cities.append(city)
                
                logger.info(f"✅ {len(self.hungarian_cities)} magyar város betöltve")
                
                # UI frissítése
                self._populate_city_list()
                self._update_stats_from_data()
                
                # Signal
                self.data_loaded.emit(len(self.hungarian_cities))
                
        except Exception as e:
            error_msg = f"Hiba a magyar városok betöltésekor: {e}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            self._update_stats("❌ Betöltési hiba")
    
    def _populate_city_list(self) -> None:
        """Városok lista feltöltése a szűrt eredményekkel"""
        if not self.city_list:
            return
        
        self.city_list.clear()
        
        # Aktuális szűrt városok
        cities_to_show = self.filtered_cities if self.filtered_cities else self.hungarian_cities
        
        for city in cities_to_show:
            # Lista elem szöveg
            population_text = f"{city.population:,}" if city.population else "n/a"
            region_text = city.region or "Egyéb"
            
            item_text = f"🏙️ {city.city} ({population_text} fő) - {region_text}"
            
            # Lista elem létrehozása
            item = QListWidgetItem(item_text)
            
            # Tooltip részletes információkkal
            tooltip = f"""
            Város: {city.city}
            Régió: {region_text}
            Népesség: {population_text} fő
            Koordináták: {city.lat:.4f}, {city.lon:.4f}
            Megye: {city.admin_name or 'n/a'}
            Adatminőség: {city.data_quality_score or 'n/a'}
            """
            item.setToolTip(tooltip.strip())
            
            # City objektum tárolása
            item.setData(Qt.UserRole, city)
            
            self.city_list.addItem(item)
        
        logger.debug(f"🏙️ {len(cities_to_show)} város megjelenítve a listában")
    
    def _update_stats_from_data(self) -> None:
        """Statisztikák frissítése betöltött adatok alapján"""
        total_cities = len(self.hungarian_cities)
        
        if total_cities == 0:
            self._update_stats("❌ Nincsenek betöltött városok")
            return
        
        # Régió statisztikák
        region_stats = {}
        population_sum = 0
        population_count = 0
        
        for city in self.hungarian_cities:
            # Régió számolás
            region = city.region or 'Egyéb'
            region_stats[region] = region_stats.get(region, 0) + 1
            
            # Népesség számolás
            if city.population:
                population_sum += city.population
                population_count += 1
        
        # Statisztika szöveg összeállítása
        stats_text = f"📊 MAGYAR VÁROSOK STATISZTIKA:\n"
        stats_text += f"  • Összes város: {total_cities}\n"
        stats_text += f"  • Összlakosság: {population_sum:,} fő ({population_count} városban)\n"
        stats_text += f"  • Átlaglakosság: {population_sum // population_count if population_count > 0 else 0:,} fő\n\n"
        
        stats_text += f"📍 RÉGIÓK SZERINTI MEGOSZLÁS:\n"
        for region, count in sorted(region_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_cities) * 100
            display_name = HungarianRegions.REGION_DISPLAY_NAMES.get(region, f"❓ {region}")
            stats_text += f"  • {display_name}: {count} város ({percentage:.1f}%)\n"
        
        self._update_stats(stats_text)
    
    def _update_stats(self, stats_text: str) -> None:
        """Statisztikák szöveg frissítése"""
        if self.stats_label:
            self.stats_label.setText(stats_text)
    
    # === EVENT HANDLERS ===
    
    def _on_search_text_changed(self, text: str) -> None:
        """Keresés szöveg változásának kezelése"""
        self.current_search_term = text.strip()
        
        if len(self.current_search_term) >= 2:
            # Debounce: 300ms késleltetés
            self.search_timer.stop()
            self.search_timer.start(300)
        elif len(self.current_search_term) == 0:
            # Üres keresés esetén összes megjelenítése
            self._clear_search()
        else:
            self.search_timer.stop()
    
    def _trigger_search(self) -> None:
        """Keresés végrehajtása"""
        if not self.current_search_term:
            self._clear_search()
            return
        
        logger.debug(f"🔍 Keresés indítása: '{self.current_search_term}'")
        
        # Keresés a városok között
        search_term_lower = self.current_search_term.lower()
        self.filtered_cities = []
        
        for city in self.hungarian_cities:
            if search_term_lower in city.city.lower():
                self.filtered_cities.append(city)
        
        # Régió szűrés alkalmazása a keresési eredményekre
        if self.current_region != 'Összes':
            self.filtered_cities = HungarianRegions.get_cities_by_region(
                self.current_region, self.filtered_cities
            )
        
        # Lista frissítése
        self._populate_city_list()
        
        # Statisztika frissítése
        found_count = len(self.filtered_cities)
        self._update_stats(f"🔍 Keresési eredmények: {found_count} város találva\nKeresési kifejezés: '{self.current_search_term}'\nRégió szűrés: {self.current_region}")
        
        # Signal
        self.search_completed.emit(found_count)
        
        logger.info(f"✅ Keresés befejezve: {found_count} város találva")
    
    def _clear_search(self) -> None:
        """Keresés törlése"""
        self.current_search_term = ''
        if self.search_box:
            self.search_box.clear()
        
        # Csak régió szűrés marad aktív
        if self.current_region != 'Összes':
            self.filtered_cities = HungarianRegions.get_cities_by_region(
                self.current_region, self.hungarian_cities
            )
        else:
            self.filtered_cities = []
        
        self._populate_city_list()
        self._update_stats_from_data()
        
        logger.debug("🧹 Keresés törölve")
    
    def _on_region_changed(self) -> None:
        """Régió változás kezelése"""
        if not self.region_combo:
            return
        
        # Aktuális régió lekérése
        current_data = self.region_combo.currentData()
        self.current_region = current_data if current_data else 'Összes'
        
        logger.debug(f"🗺️ Régió váltás: {self.current_region}")
        
        # Szűrés alkalmazása
        if self.current_region == 'Összes':
            if self.current_search_term:
                # Ha van keresési kifejezés, azt alkalmazzuk
                self._trigger_search()
            else:
                # Különben minden város
                self.filtered_cities = []
                self._populate_city_list()
                self._update_stats_from_data()
        else:
            # Régió alapú szűrés
            base_cities = self.hungarian_cities
            
            # Ha van keresési kifejezés, először azt alkalmazzuk
            if self.current_search_term:
                search_term_lower = self.current_search_term.lower()
                base_cities = [city for city in base_cities if search_term_lower in city.city.lower()]
            
            # Régió szűrés
            self.filtered_cities = HungarianRegions.get_cities_by_region(self.current_region, base_cities)
            self._populate_city_list()
            
            # Statisztika frissítése
            region_display = HungarianRegions.REGION_DISPLAY_NAMES.get(self.current_region, self.current_region)
            found_count = len(self.filtered_cities)
            stats_text = f"🗺️ Régió szűrés: {region_display}\n{found_count} város a régióban"
            if self.current_search_term:
                stats_text += f"\nKeresési kifejezés: '{self.current_search_term}'"
            self._update_stats(stats_text)
        
        # Signal - régió kiválasztás
        region_cities = self.filtered_cities if self.filtered_cities else self.hungarian_cities
        self.region_selected.emit(self.current_region, [city.city for city in region_cities])
    
    def _on_city_selected(self, item: QListWidgetItem) -> None:
        """Város kiválasztás kezelése (dupla kattintás)"""
        city = item.data(Qt.UserRole)
        if isinstance(city, HungarianCity):
            self._emit_city_selected(city)
    
    def _select_current_city(self) -> None:
        """Jelenlegi kiválasztott város elfogadása"""
        if not self.city_list:
            return
        
        current_item = self.city_list.currentItem()
        if current_item:
            self._on_city_selected(current_item)
        else:
            logger.warning("⚠️ Nincs kiválasztott város")
    
    def _select_quick_city(self, city_name: str) -> None:
        """Gyors hozzáférésű város kiválasztása"""
        # Város keresése a betöltött adatok között
        for city in self.hungarian_cities:
            if city.city == city_name:
                self._emit_city_selected(city)
                return
        
        logger.warning(f"⚠️ Gyors hozzáférésű város nem található: {city_name}")
    
    def _emit_city_selected(self, city: HungarianCity) -> None:
        """
        City selected signal kibocsátása
        
        Args:
            city: Kiválasztott HungarianCity objektum
        """
        # Metadata összeállítása
        metadata = {
            'name': city.city,
            'latitude': city.lat,
            'longitude': city.lon,
            'country': city.country,
            'country_code': city.country_code,
            'population': city.population,
            'admin_name': city.admin_name,
            'region': city.region,
            'meteostat_station_id': city.meteostat_station_id,
            'data_quality_score': city.data_quality_score,
            'source': 'hungarian_city_selector',
            'display_name': f"{city.city}, Magyarország",
            'preferred_source': 'open-meteo'  # Magyar városokhoz Open-Meteo optimális
        }
        
        # Signal kibocsátása
        self.city_selected.emit(city.city, city.lat, city.lon, metadata)
        
        logger.info(f"✅ Város kiválasztva: {city.city} ({city.lat:.4f}, {city.lon:.4f})")
    
    def _reload_cities(self) -> None:
        """Városok listájának újratöltése"""
        logger.info("🔄 Magyar városok újratöltése...")
        self.hungarian_cities.clear()
        self.filtered_cities.clear()
        if self.city_list:
            self.city_list.clear()
        self._update_stats("🔄 Újratöltés...")
        self._load_hungarian_cities()
    
    # === THEME HANDLING ===
    
    def _apply_current_theme(self) -> None:
        """Jelenlegi téma alkalmazása"""
        colors = get_current_colors()
        
        # Fő widget háttér
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {colors.get('surface', '#ffffff')};
                color: {colors.get('on_surface', '#000000')};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {colors.get('border', '#ccc')};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 6px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px 0 6px;
                color: {colors.get('primary', '#0066cc')};
            }}
        """)
    
    def _on_theme_changed(self, theme_name: str) -> None:
        """Téma változás kezelése"""
        self._apply_current_theme()
        logger.debug(f"🎨 HungarianCitySelector téma frissítve: {theme_name}")
    
    # === PUBLIC API ===
    
    def get_loaded_cities_count(self) -> int:
        """Betöltött városok számának lekérdezése"""
        return len(self.hungarian_cities)
    
    def get_filtered_cities_count(self) -> int:
        """Szűrt városok számának lekérdezése"""
        return len(self.filtered_cities) if self.filtered_cities else len(self.hungarian_cities)
    
    def get_current_region(self) -> str:
        """Jelenlegi régió lekérdezése"""
        return self.current_region
    
    def get_current_search_term(self) -> str:
        """Jelenlegi keresési kifejezés lekérdezése"""
        return self.current_search_term
    
    def set_region(self, region: str) -> None:
        """Régió programozott beállítása"""
        if self.region_combo:
            for i in range(self.region_combo.count()):
                if self.region_combo.itemData(i) == region:
                    self.region_combo.setCurrentIndex(i)
                    break
    
    def set_search_term(self, search_term: str) -> None:
        """Keresési kifejezés programozott beállítása"""
        if self.search_box:
            self.search_box.setText(search_term)
            self._trigger_search()
    
    def clear_all_filters(self) -> None:
        """Összes szűrő törlése"""
        self.set_region('Összes')
        self.set_search_term('')
    
    def get_city_by_name(self, city_name: str) -> Optional[HungarianCity]:
        """
        Város keresése név alapján
        
        Args:
            city_name: Város neve
            
        Returns:
            HungarianCity objektum vagy None
        """
        for city in self.hungarian_cities:
            if city.city.lower() == city_name.lower():
                return city
        return None
    
    def select_city_by_name(self, city_name: str) -> bool:
        """
        Város kiválasztása név alapján (programozott)
        
        Args:
            city_name: Város neve
            
        Returns:
            True, ha sikerült a kiválasztás
        """
        city = self.get_city_by_name(city_name)
        if city:
            self._emit_city_selected(city)
            return True
        return False
    
    def get_available_regions(self) -> List[str]:
        """Elérhető régiók listájának lekérdezése"""
        return HungarianRegions.get_all_regions()
    
    def get_cities_by_region_name(self, region: str) -> List[HungarianCity]:
        """
        Városok lekérdezése régió alapján
        
        Args:
            region: Régió neve
            
        Returns:
            HungarianCity objektumok listája
        """
        return HungarianRegions.get_cities_by_region(region, self.hungarian_cities)


# Export
__all__ = ['HungarianCitySelector', 'HungarianCity', 'HungarianRegions']