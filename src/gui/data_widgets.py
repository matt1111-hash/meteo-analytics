#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Data Widgets Module - THEMEMANAGER INTEGRÁLT VERZIÓ
Táblázatos adatmegjelenítés modulja - KATTINTÁSSAL RENDEZHETŐ OSZLOPOKKAL.

🎨 THEMEMANAGER INTEGRÁCIÓ:
- Hardcoded CSS-ek eltávolítva/minimalizálva  
- Manual dark theme logika lecserélve ThemeManager-re
- Widget regisztrációk automatikus styling-hoz
- _apply_table_theme és _apply_controls_theme egyszerűsítve

🔧 KRITIKUS JAVÍTÁS: Adatfeldolgozási hibák javítva
- _convert_to_dataframe() robust hibakezelés
- Adathossz validálás
- Üres adatok kezelése
- DEBUG logging hozzáadva

FUNKCIÓK MEGTARTVA:
- Numerikus rendezés, intelligens táblázat elemek
- KÖZÉPHŐMÉRSÉKLET OSZLOP 
- Kattintással rendezhető oszlopok (növekvő/csökkenő)
"""

from typing import Optional, Dict, Any, List, Tuple
import pandas as pd
import csv
from datetime import datetime
from pathlib import Path
import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLineEdit, QComboBox, QLabel, QCheckBox,
    QGroupBox, QSpinBox, QFileDialog, QMessageBox, QProgressBar,
    QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QSortFilterProxyModel, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QFont, QColor

from ..config import GUIConfig
from .utils import GUIConstants
from .theme_manager import get_theme_manager, register_widget_for_theming

# Logging setup
logger = logging.getLogger(__name__)


# =============================================================================
# NUMERIKUS RENDEZÉST TÁMOGATÓ TÁBLÁZATELEM - VÁLTOZATLAN
# =============================================================================
class NumericTableWidgetItem(QTableWidgetItem):
    """
    Intelligens QTableWidgetItem, amely lehetővé teszi a numerikus rendezést
    akkor is, ha a megjelenített szöveg mértékegységet tartalmaz.
    
    Példa: "15.2 °C" szöveg, de 15.2 numerikus érték alapján rendez.
    """
    
    def __init__(self, display_text: str, numeric_value: float):
        """
        Args:
            display_text: Megjelenítendő szöveg (pl. "15.2 °C")
            numeric_value: Rendezéshez használt numerikus érték (pl. 15.2)
        """
        super().__init__(display_text)
        self.numeric_value = numeric_value
    
    def __lt__(self, other: 'NumericTableWidgetItem') -> bool:
        """
        Összehasonlító metódus felülírása a rendezéshez.
        A tárolt numerikus érték alapján hasonlít össze, nem a szöveg szerint.
        """
        if isinstance(other, NumericTableWidgetItem):
            return self.numeric_value < other.numeric_value
        # Fallback a szöveges összehasonlításra, ha más típusú item
        return super().__lt__(other)
    
    def data(self, role: int):
        """Qt data role kezelése - numerikus érték visszaadása rendezéshez."""
        if role == Qt.UserRole:
            return self.numeric_value
        return super().data(role)


# =============================================================================
# WEATHER TABLE MODEL - THEMEMANAGER INTEGRÁLT
# =============================================================================
class WeatherTableModel(QAbstractTableModel):
    """
    Időjárási adatok tábla modellje - THEMEMANAGER KOMPATIBILIS.
    Nagy adathalmazok hatékony kezelésére optimalizálva.
    """
    
    def __init__(self, data: Optional[pd.DataFrame] = None):
        super().__init__()
        self._data = data if data is not None else pd.DataFrame()
        self._headers = []
        self._theme_manager = get_theme_manager()
        self._update_headers()
    
    def _update_headers(self) -> None:
        """Oszlop fejlécek frissítése - SZAKMAILAG PONTOS ELNEVEZÉSSEL."""
        if not self._data.empty:
            self._headers = [
                "Dátum", "Max hőmérséklet (°C)", "Min hőmérséklet (°C)",
                "Napi átlag (°C)", "Csapadék (mm)", "Szélsebesség (km/h)"
            ]
        else:
            self._headers = []
    
    def set_theme(self, dark_theme: bool) -> None:
        """
        Téma beállítása - THEMEMANAGER DELEGÁLÁS.
        
        Args:
            dark_theme: True, ha sötét téma
        """
        theme_name = "dark" if dark_theme else "light"
        self._theme_manager.set_theme(theme_name)
        self.dataChanged.emit(QModelIndex(), QModelIndex())
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or self._data.empty:
            return None
        
        row, col = index.row(), index.column()
        
        if role == Qt.DisplayRole:
            if col == 0:  # Dátum
                return self._data.iloc[row, 0]  # date oszlop
            elif col == 1:  # Max hőmérséklet
                value = self._data.iloc[row, 1]
                return f"{value:.1f}" if pd.notna(value) else "N/A"
            elif col == 2:  # Min hőmérséklet  
                value = self._data.iloc[row, 2]
                return f"{value:.1f}" if pd.notna(value) else "N/A"
            elif col == 3:  # Átlag hőmérséklet
                value = self._data.iloc[row, 3] if len(self._data.columns) > 3 else None
                return f"{value:.1f}" if pd.notna(value) else "N/A"
            elif col == 4:  # Csapadék
                value = self._data.iloc[row, 4] if len(self._data.columns) > 4 else self._data.iloc[row, 3]
                return f"{value:.1f}" if pd.notna(value) else "0.0"
            elif col == 5:  # Szélsebesség
                value = self._data.iloc[row, 5] if len(self._data.columns) > 5 else None
                return f"{value:.1f}" if pd.notna(value) else "N/A"
        
        elif role == Qt.BackgroundRole:
            # ThemeManager színek lekérdezése
            scheme = self._theme_manager.get_color_scheme()
            if scheme:
                if row % 2 == 0:
                    return QColor(scheme.get_color("surface", "base") or "#ffffff")
                return QColor(scheme.get_color("surface", "light") or "#f5f5f5")
            # Fallback
            return QColor(255, 255, 255) if row % 2 else QColor(248, 249, 250)
        
        elif role == Qt.ForegroundRole:
            # ThemeManager szövegszín
            scheme = self._theme_manager.get_color_scheme()
            if scheme:
                return QColor(scheme.get_color("primary", "base") or "#1f2937")
            return QColor(31, 41, 55)  # Fallback
        
        elif role == Qt.TextAlignmentRole:
            if col == 0:  # Dátum
                return Qt.AlignCenter
            else:  # Számok
                return Qt.AlignRight | Qt.AlignVCenter
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if 0 <= section < len(self._headers):
                return self._headers[section]
        elif role == Qt.ForegroundRole and orientation == Qt.Horizontal:
            # Header szöveg színe ThemeManager-ből
            scheme = self._theme_manager.get_color_scheme()
            if scheme:
                return QColor(scheme.get_color("primary", "base") or "#374151")
            return QColor(55, 65, 81)  # Fallback
        return None
    
    def update_data(self, data: pd.DataFrame) -> None:
        """Adatok frissítése."""
        self.beginResetModel()
        self._data = data
        self._update_headers()
        self.endResetModel()


# =============================================================================
# FŐ WEATHER DATA TABLE WIDGET - THEMEMANAGER INTEGRÁLT + HIBAKEZELÉS JAVÍTVA
# =============================================================================
class WeatherDataTable(QWidget):
    """
    Időjárási adatok táblázatos megjelenítése - THEMEMANAGER INTEGRÁLT VERZIÓ.
    
    🎨 VÁLTOZÁSOK:
    - Hardcoded CSS-ek eltávolítva
    - Manual dark theme logika → ThemeManager delegálás
    - Widget regisztrációk automatikus styling-hoz
    - apply_theme egyszerűsítés
    
    🔧 KRITIKUS JAVÍTÁS:
    - _convert_to_dataframe() robust hibakezelés
    - Adathossz validálás
    - Üres adatok kezelése
    - DEBUG logging
    
    FUNKCIÓK MEGTARTVA:
    - Numerikus rendezés (15.2 °C < 8.5 °C helyett 8.5 < 15.2)
    - Kattintással rendezhető oszlopok
    - Növekvő/csökkenő rendezés váltása
    - KÖZÉPHŐMÉRSÉKLET OSZLOP
    """
    
    # Signalok
    row_selected = Signal(int)           # kiválasztott sor index
    data_filtered = Signal(int)          # szűrt sorok száma
    export_completed = Signal(str, bool) # filepath, success
    sorting_changed = Signal(int, str)   # column, order (asc/desc)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Javított táblázat widget inicializálása - THEMEMANAGER VERZIÓ."""
        super().__init__(parent)
        
        # ThemeManager singleton
        self._theme_manager = get_theme_manager()
        
        self.current_data: Optional[pd.DataFrame] = None
        self.filtered_data: Optional[pd.DataFrame] = None
        self.current_page = 0
        self.rows_per_page = 1000  # 🔧 JAVÍTÁS: Nagy alapértelmezett, "Összes" override-olja
        
        # Rendezési állapot követése
        self.current_sort_column = -1
        self.current_sort_order = Qt.AscendingOrder
        
        self._init_ui()
        self._connect_signals()
        self._register_widgets_for_theming()
    
    def _init_ui(self) -> None:
        """UI elemek inicializálása - MINIMAL CSS APPROACH."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Felső vezérlő panel
        self.controls = self._create_controls()
        layout.addWidget(self.controls)
        
        # === FŐ TÁBLÁZAT - RENDEZHETŐSÉGGEL ===
        self.table = QTableWidget()
        self._setup_sortable_table()
        layout.addWidget(self.table)
        
        # Alsó információs sáv
        self.info_bar = self._create_info_bar()
        layout.addWidget(self.info_bar)
    
    def _setup_sortable_table(self) -> None:
        """Táblázat beállítások rendezhető funkcióval - THEMEMANAGER KOMPATIBILIS."""
        # === KRITIKUS: RENDEZÉS ENGEDÉLYEZÉSE ===
        self.table.setSortingEnabled(True)
        
        # Alap beállítások
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Fejléc beállítások
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # === RENDEZÉSI SIGNALOK KAPCSOLÁSA ===
        header.sectionClicked.connect(self._on_header_clicked)
        
        # ThemeManager automatikus styling (CSS nélkül)
    
    def _on_header_clicked(self, logical_index: int) -> None:
        """Fejléc kattintás kezelése - rendezési állapot követése."""
        # Rendezési irány meghatározása
        if self.current_sort_column == logical_index:
            # Ugyanaz az oszlop - irány váltása
            if self.current_sort_order == Qt.AscendingOrder:
                self.current_sort_order = Qt.DescendingOrder
                order_text = "csökkenő"
            else:
                self.current_sort_order = Qt.AscendingOrder
                order_text = "növekvő"
        else:
            # Új oszlop - alapértelmezett növekvő
            self.current_sort_column = logical_index
            self.current_sort_order = Qt.AscendingOrder
            order_text = "növekvő"
        
        # Oszlop név meghatározása - SZAKMAILAG PONTOS ELNEVEZÉSSEL
        headers = ["Dátum", "Max hőmérséklet", "Min hőmérséklet", "Napi átlag", "Csapadék", "Szélsebesség"]
        column_name = headers[logical_index] if logical_index < len(headers) else f"Oszlop {logical_index}"
        
        # Rendezés végrehajtása
        self.table.sortItems(logical_index, self.current_sort_order)
        
        # Signal kibocsátása és üzenet
        self.sorting_changed.emit(logical_index, order_text)
        print(f"🔢 Táblázat rendezve: {column_name} ({order_text})")
        
        # Státusz frissítése
        if hasattr(self, 'rows_info'):
            current_text = self.rows_info.text()
            self.rows_info.setText(f"{current_text} | Rendezve: {column_name} ({order_text})")
    
    def _create_controls(self) -> QWidget:
        """Vezérlő panel létrehozása - THEMEMANAGER KOMPATIBILIS."""
        controls = QGroupBox("🔍 Táblázat vezérlők")
        layout = QHBoxLayout(controls)
        
        # Keresés
        search_layout = QHBoxLayout()
        search_label = QLabel("Keresés:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Írjon be keresési kifejezést...")
        self.search_input.textChanged.connect(self._apply_filter)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Oszlop szűrő
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Oszlop:")
        self.column_filter = QComboBox()
        self.column_filter.addItems(["Összes", "Dátum", "Hőmérséklet", "Csapadék", "Szél"])
        self.column_filter.currentTextChanged.connect(self._apply_filter)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.column_filter)
        layout.addLayout(filter_layout)
        
        # Lapozás
        pagination_layout = QHBoxLayout()
        self.page_label = QLabel("Oldal:")
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setValue(1)
        self.page_spin.valueChanged.connect(self._change_page)
        
        self.rows_per_page_combo = QComboBox()
        self.rows_per_page_combo.addItems(["50", "100", "200", "Összes"])
        self.rows_per_page_combo.setCurrentText("Összes")  # 🔧 JAVÍTÁS: "Összes" alapértelmezett
        self.rows_per_page_combo.currentTextChanged.connect(self._change_page_size)
        
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.page_spin)
        pagination_layout.addWidget(QLabel("/ oldal"))
        pagination_layout.addWidget(self.rows_per_page_combo)
        layout.addLayout(pagination_layout)
        
        # === EXPORT GOMBOK - THEMEMANAGER STYLING ===
        export_layout = QHBoxLayout()
        self.csv_btn = QPushButton("📄 CSV")
        self.csv_btn.clicked.connect(lambda: self._export_data("csv"))
        self.csv_btn.setEnabled(False)
        
        self.excel_btn = QPushButton("📊 Excel")
        self.excel_btn.clicked.connect(lambda: self._export_data("excel"))
        self.excel_btn.setEnabled(False)
        
        export_layout.addWidget(self.csv_btn)
        export_layout.addWidget(self.excel_btn)
        layout.addLayout(export_layout)
        
        return controls
    
    def _create_info_bar(self) -> QWidget:
        """Információs sáv létrehozása - THEMEMANAGER KOMPATIBILIS."""
        info_bar = QWidget()
        info_bar.setMaximumHeight(30)
        info_bar.setObjectName("info_bar")
        
        layout = QHBoxLayout(info_bar)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Sorok info
        self.rows_info = QLabel("Nincs adat")
        self.rows_info.setObjectName("rows_info")
        layout.addWidget(self.rows_info)
        
        layout.addStretch()
        
        # Export progress
        self.export_progress = QProgressBar()
        self.export_progress.setVisible(False)
        self.export_progress.setMaximumWidth(200)
        layout.addWidget(self.export_progress)
        
        return info_bar
    
    def _register_widgets_for_theming(self) -> None:
        """Widget-ek regisztrálása ThemeManager-ben."""
        print("🎨 DEBUG: Registering WeatherDataTable widgets for theming...")
        
        # Input widgets
        register_widget_for_theming(self.search_input, "input")
        register_widget_for_theming(self.column_filter, "input")
        register_widget_for_theming(self.page_spin, "input")
        register_widget_for_theming(self.rows_per_page_combo, "input")
        
        # Button widgets
        register_widget_for_theming(self.csv_btn, "button")
        register_widget_for_theming(self.excel_btn, "button")
        
        # Table widgets
        register_widget_for_theming(self.table, "table")
        
        # Container widgets
        register_widget_for_theming(self.controls, "container")
        register_widget_for_theming(self, "container")
        
        print("✅ DEBUG: WeatherDataTable widgets registered for theming")
    
    def _connect_signals(self) -> None:
        """Signal-slot kapcsolatok."""
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _apply_filter(self) -> None:
        """Szűrés alkalmazása."""
        if self.current_data is None or self.current_data.empty:
            return
        
        search_text = self.search_input.text().lower()
        column_filter = self.column_filter.currentText()
        
        # Alap DataFrame másolása
        filtered_df = self.current_data.copy()
        
        # Szöveges keresés
        if search_text:
            if column_filter == "Összes":
                # Minden oszlopban keresés
                mask = filtered_df.astype(str).apply(
                    lambda x: x.str.lower().str.contains(search_text, na=False)
                ).any(axis=1)
            elif column_filter == "Dátum":
                mask = filtered_df.iloc[:, 0].astype(str).str.lower().str.contains(search_text, na=False)
            elif column_filter == "Hőmérséklet":
                # Max, Min, Átlag hőmérséklet oszlopokban keresés
                mask = (filtered_df.iloc[:, 1].astype(str).str.contains(search_text, na=False) | 
                       filtered_df.iloc[:, 2].astype(str).str.contains(search_text, na=False) |
                       (len(filtered_df.columns) > 3 and filtered_df.iloc[:, 3].astype(str).str.contains(search_text, na=False)))
            elif column_filter == "Csapadék":
                # Csapadék oszlop (index függhet az átlag hőmérséklet jelenlététől)
                precip_col = 4 if len(filtered_df.columns) > 4 else 3
                if precip_col < len(filtered_df.columns):
                    mask = filtered_df.iloc[:, precip_col].astype(str).str.contains(search_text, na=False)
                else:
                    mask = pd.Series([False] * len(filtered_df))
            elif column_filter == "Szél":
                # Szél oszlop (utolsó oszlop)
                if len(filtered_df.columns) > 5:
                    mask = filtered_df.iloc[:, -1].astype(str).str.contains(search_text, na=False)
                else:
                    mask = pd.Series([False] * len(filtered_df))
            else:
                mask = pd.Series([True] * len(filtered_df))
            
            filtered_df = filtered_df[mask]
        
        self.filtered_data = filtered_df
        self._update_pagination()
        self._display_current_page()
        
        # Signal kibocsátása
        self.data_filtered.emit(len(filtered_df))
    
    def _change_page(self, page: int) -> None:
        """Oldal váltás."""
        self.current_page = page - 1
        self._display_current_page()
    
    def _change_page_size(self, size_text: str) -> None:
        """Oldalméret váltás."""
        if size_text == "Összes":
            self.rows_per_page = len(self.filtered_data) if self.filtered_data is not None else 1000
        else:
            self.rows_per_page = int(size_text)
        
        self.current_page = 0
        self.page_spin.setValue(1)
        self._update_pagination()
        self._display_current_page()
        
        # 🔧 JAVÍTÁS: "Összes" esetén jelezzük hogy minden egy oldalon van
        if size_text == "Összes":
            total_rows = len(self.filtered_data) if self.filtered_data is not None else 0
            print(f"✅ Táblázat beállítva: ÖSSZES {total_rows} sor egy oldalon")
    
    def _update_pagination(self) -> None:
        """Lapozás frissítése."""
        if self.filtered_data is None or self.filtered_data.empty:
            self.page_spin.setMaximum(1)
            return
        
        total_pages = max(1, (len(self.filtered_data) - 1) // self.rows_per_page + 1)
        self.page_spin.setMaximum(total_pages)
        
        if self.current_page >= total_pages:
            self.current_page = total_pages - 1
            self.page_spin.setValue(self.current_page + 1)
    
    def _display_current_page(self) -> None:
        """Aktuális oldal megjelenítése - NUMERIKUS ITEMEKKEL."""
        if self.filtered_data is None or self.filtered_data.empty:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self._update_info_display(0, 0)
            return
        
        # Aktuális oldal adatainak kiszámítása
        start_idx = self.current_page * self.rows_per_page
        end_idx = start_idx + self.rows_per_page
        page_data = self.filtered_data.iloc[start_idx:end_idx]
        
        # === KRITIKUS: NUMERIKUS ITEMEKKEL FELTÖLTÉS ===
        self._populate_table_with_numeric_items(page_data)
        self._update_info_display(len(self.filtered_data), len(page_data))
    
    def _populate_table_with_numeric_items(self, data: pd.DataFrame) -> None:
        """
        Táblázat feltöltése NumericTableWidgetItem-ekkel - THEMEMANAGER SZÍNEKKEL.
        Ez a kulcs a funkcionális rendezéshez!
        """
        rows, cols = data.shape
        
        # Oszlopok beállítása - SZAKMAILAG PONTOS FEJLÉCEKKEL
        headers = ["Dátum", "Max hőmérséklet (°C)", "Min hőmérséklet (°C)", "Napi átlag (°C)", "Csapadék (mm)"]
        if cols > 5:  # Ha van szélsebesség is
            headers.append("Szélsebesség (km/h)")
        
        self.table.setRowCount(rows)
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # ThemeManager színek lekérdezése
        scheme = self._theme_manager.get_color_scheme()
        
        # === ADATOK FELTÖLTÉSE INTELLIGENS ITEMEKKEL ===
        for i in range(rows):
            for j in range(min(cols, len(headers))):
                value = data.iloc[i, j]
                
                if j == 0:  # Dátum oszlop
                    # Dátum esetén sima QTableWidgetItem (string rendezés jó)
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    
                elif pd.isna(value):  # Hiányzó érték
                    # Hiányzó értékek kezelése
                    item = NumericTableWidgetItem("N/A", -999999)  # Nagy negatív szám a rendezéshez
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                else:  # Numerikus oszlopok
                    # === KRITIKUS: NUMERIKUS ITEM HASZNÁLATA ===
                    numeric_value = float(value)
                    
                    if j in [1, 2, 3]:  # Hőmérséklet oszlopok (max, min, átlag)
                        display_text = f"{numeric_value:.1f}"
                    elif j == 4:  # Csapadék (vagy szél ha nincs átlag)
                        display_text = f"{numeric_value:.1f}"
                    elif j == 5:  # Szél (ha van)
                        display_text = f"{numeric_value:.1f}"
                    else:
                        display_text = f"{numeric_value:.1f}"
                    
                    item = NumericTableWidgetItem(display_text, numeric_value)
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                # === THEMEMANAGER SZÍNEK ALKALMAZÁSA ===
                if scheme:
                    # 🔧 KRITIKUS JAVÍTÁS: ColorPalette API helyes használata
                    # Alternáló háttérszínek
                    if i % 2 == 0:
                        item.setBackground(QColor(scheme.get_color("surface", "base") or "#ffffff"))
                    else:
                        item.setBackground(QColor(scheme.get_color("surface", "light") or "#f5f5f5"))
                    
                    # Szövegszín
                    item.setForeground(QColor(scheme.get_color("primary", "base") or "#1f2937"))
                else:
                    # Fallback színek
                    if i % 2 == 0:
                        item.setBackground(QColor(248, 249, 250))  # Világos szürke
                    else:
                        item.setBackground(QColor(255, 255, 255))  # Fehér
                    item.setForeground(QColor(31, 41, 55))        # Sötét szöveg
                
                self.table.setItem(i, j, item)
        
        # Oszlop szélességek automatikus beállítása
        self.table.resizeColumnsToContents()
        
        # Rendezési állapot megőrzése
        if self.current_sort_column >= 0:
            self.table.sortItems(self.current_sort_column, self.current_sort_order)
    
    def _update_info_display(self, total_rows: int, displayed_rows: int) -> None:
        """Információs szöveg frissítése."""
        if total_rows == 0:
            self.rows_info.setText("Nincs megjeleníthető adat")
        else:
            # 🔧 JAVÍTÁS: "Összes" esetén egyszerűsített megjelenítés
            if self.rows_per_page_combo.currentText() == "Összes" or displayed_rows == total_rows:
                info_text = f"Összesen: {total_rows} sor (mind megjelenítve)"
            else:
                current_page = self.current_page + 1
                total_pages = max(1, (total_rows - 1) // self.rows_per_page + 1)
                
                info_text = f"Összesen: {total_rows} sor | "
                info_text += f"Megjelenítve: {displayed_rows} sor | "
                info_text += f"Oldal: {current_page}/{total_pages}"
            
            self.rows_info.setText(info_text)
    
    def _on_selection_changed(self) -> None:
        """Kiválasztás változás kezelése."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            # Globális sor index számítása
            global_row = self.current_page * self.rows_per_page + current_row
            self.row_selected.emit(global_row)
    
    def _export_data(self, format: str) -> None:
        """Adatok exportálása."""
        if self.filtered_data is None or self.filtered_data.empty:
            QMessageBox.warning(self, "Export hiba", "Nincsenek exportálható adatok.")
            return
        
        # Fájl mentési dialógus
        if format == "csv":
            file_filter = "CSV fájlok (*.csv)"
            default_ext = ".csv"
        else:  # excel
            file_filter = "Excel fájlok (*.xlsx)"
            default_ext = ".xlsx"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"weather_data_{timestamp}{default_ext}"
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, f"Adatok exportálása ({format.upper()})", 
            default_filename, file_filter
        )
        
        if not filepath:
            return
        
        # Export végrehajtása
        self._perform_export(filepath, format)
    
    def _perform_export(self, filepath: str, format: str) -> None:
        """Export végrehajtása."""
        try:
            self.export_progress.setVisible(True)
            self.export_progress.setRange(0, 100)
            self.export_progress.setValue(10)
            
            # Fejlécek beállítása - SZAKMAILAG PONTOS OSZLOPOKKAL
            export_data = self.filtered_data.copy()
            column_names = ["Dátum", "Max hőmérséklet (°C)", "Min hőmérséklet (°C)", "Napi átlag (°C)", "Csapadék (mm)"]
            
            if len(export_data.columns) > 5:
                column_names.append("Szélsebesség (km/h)")
            
            export_data.columns = column_names[:len(export_data.columns)]
            
            self.export_progress.setValue(50)
            
            # Export végrehajtása
            if format == "csv":
                export_data.to_csv(filepath, index=False, encoding='utf-8')
            else:  # excel
                export_data.to_excel(filepath, index=False, engine='openpyxl')
            
            self.export_progress.setValue(100)
            
            # Sikeres export
            QMessageBox.information(self, "Export sikeres", 
                                  f"Adatok sikeresen exportálva:\n{filepath}")
            
            self.export_completed.emit(filepath, True)
            
        except Exception as e:
            QMessageBox.critical(self, "Export hiba", f"Hiba az export során:\n{str(e)}")
            self.export_completed.emit(filepath, False)
        
        finally:
            self.export_progress.setVisible(False)
    
    # === PUBLIC METHODS ===
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        Táblázat adatainak frissítése - ROBUST HIBAKEZELÉSSEL.
        
        🔧 KRITIKUS JAVÍTÁS: Hibakezelés és debug logging hozzáadva!
        """
        try:
            logger.info("🔄 WeatherDataTable.update_data() ELINDULT - ROBUST HIBAKEZELÉSSEL")
            
            # 🔧 KRITIKUS: Bemenő adatok validálása
            if not data:
                logger.error("❌ Üres adatok érkeztek a táblázatba!")
                self.clear_data()
                return
            
            if "daily" not in data:
                logger.error("❌ Hiányzik a 'daily' kulcs az adatokból!")
                self.clear_data()
                return
            
            logger.info(f"✅ Adatok szerkezete: {list(data.keys())}")
            logger.info(f"✅ Daily adatok: {list(data.get('daily', {}).keys())}")
            
            # DataFrame konvertálás - ROBUST HIBAKEZELÉSSEL
            df = self._convert_to_dataframe(data)
            
            if df.empty:
                logger.error("❌ DataFrame konvertálás sikertelen vagy üres!")
                self.clear_data()
                return
            
            logger.info(f"✅ DataFrame létrehozva: {len(df)} sor, {len(df.columns)} oszlop")
            logger.info(f"✅ Oszlopnevek: {list(df.columns)}")
            
            # Adatok beállítása
            self.current_data = df
            self.filtered_data = df.copy()
            
            # Reset vezérlők
            self.search_input.clear()
            self.column_filter.setCurrentText("Összes")
            self.current_page = 0
            self.page_spin.setValue(1)
            
            # 🔧 JAVÍTÁS: "Összes" sor alapértelmezett új adatoknál
            self.rows_per_page_combo.setCurrentText("Összes")
            self.rows_per_page = len(df)  # Teljes adathalmaz megjelenítése
            
            # Rendezési állapot reset
            self.current_sort_column = -1
            self.current_sort_order = Qt.AscendingOrder
            
            # Megjelenítés frissítése
            self._update_pagination()
            self._display_current_page()
            
            # Export gombok engedélyezése
            self.csv_btn.setEnabled(True)
            self.excel_btn.setEnabled(True)
            
            logger.info(f"✅ WeatherDataTable.update_data() SIKERES! {len(df)} sor megjelenítve")
            
        except Exception as e:
            logger.error(f"❌ WeatherDataTable.update_data() HIBA: {e}")
            logger.exception("Részletes hiba:")
            self.clear_data()
    
    def _convert_to_dataframe(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        API adatok DataFrame-mé konvertálása - ROBUST HIBAKEZELÉSSEL.
        
        🔧 KRITIKUS JAVÍTÁS: 
        - Adathossz validálás
        - Üres adatok kezelése
        - Részletes debug logging
        - Exception handling
        
        Args:
            data: API válasz adatok
            
        Returns:
            Feldolgozott DataFrame vagy üres DataFrame hiba esetén
        """
        try:
            logger.info("🔄 _convert_to_dataframe() ELINDULT - ROBUST VERZIÓ")
            
            daily_data = data.get("daily", {})
            
            # 🔧 KRITIKUS: Alapadatok kinyerése és validálása
            dates = daily_data.get("time", [])
            temp_max = daily_data.get("temperature_2m_max", [])
            temp_min = daily_data.get("temperature_2m_min", [])
            temp_mean = daily_data.get("temperature_2m_mean", [])
            precip = daily_data.get("precipitation_sum", [])
            windspeed = daily_data.get("windspeed_10m_max", [])
            
            # 🔧 KRITIKUS: Adathossz ellenőrzés
            data_lengths = {
                'dates': len(dates),
                'temp_max': len(temp_max),
                'temp_min': len(temp_min),
                'temp_mean': len(temp_mean),
                'precip': len(precip),
                'windspeed': len(windspeed)
            }
            
            logger.info(f"📊 Adathosszak: {data_lengths}")
            
            # Alapvető validálás
            if not dates or len(dates) == 0:
                logger.error("❌ Nincs dátum adat!")
                return pd.DataFrame()
            
            if not temp_max or len(temp_max) == 0:
                logger.error("❌ Nincs maximum hőmérséklet adat!")
                return pd.DataFrame()
            
            base_length = len(dates)
            logger.info(f"✅ Alapvető hossz: {base_length} nap")
            
            # 🔧 KRITIKUS: Adatok padding/trimming azonos hosszra
            def normalize_array(arr: List, target_length: int, fill_value=None) -> List:
                """Array normalizálása adott hosszra."""
                if len(arr) == target_length:
                    return arr
                elif len(arr) < target_length:
                    # Padding
                    return arr + [fill_value] * (target_length - len(arr))
                else:
                    # Trimming
                    return arr[:target_length]
            
            # Összes array normalizálása
            dates_norm = normalize_array(dates, base_length)
            temp_max_norm = normalize_array(temp_max, base_length, None)
            temp_min_norm = normalize_array(temp_min, base_length, None)
            temp_mean_norm = normalize_array(temp_mean, base_length, None)
            precip_norm = normalize_array(precip, base_length, 0.0)
            windspeed_norm = normalize_array(windspeed, base_length, None)
            
            # 🔧 KRITIKUS: temp_mean fallback számítás ha szükséges
            if not temp_mean or all(x is None for x in temp_mean_norm):
                logger.warning("⚠️ temperature_2m_mean hiányzik, fallback számításra...")
                temp_mean_norm = []
                for i in range(base_length):
                    if (i < len(temp_max_norm) and i < len(temp_min_norm) and 
                        temp_max_norm[i] is not None and temp_min_norm[i] is not None):
                        avg = (temp_max_norm[i] + temp_min_norm[i]) / 2
                        temp_mean_norm.append(round(avg, 1))
                    else:
                        temp_mean_norm.append(None)
                logger.info(f"🔄 Fallback számítás kész: {len(temp_mean_norm)} érték")
            else:
                logger.info(f"✅ temperature_2m_mean használva: {len(temp_mean_norm)} érték")
            
            # 🔧 KRITIKUS: DataFrame létrehozása normalizált adatokkal
            df_data = {
                'date': dates_norm,
                'temp_max': temp_max_norm,
                'temp_min': temp_min_norm,
                'temp_mean': temp_mean_norm,
                'precipitation': precip_norm
            }
            
            # Szél adat hozzáadása, ha van
            if windspeed_norm and any(x is not None for x in windspeed_norm):
                df_data['windspeed'] = windspeed_norm
                logger.info("✅ Szélsebesség adatok hozzáadva")
            else:
                logger.info("⚠️ Szélsebesség adatok hiányoznak")
            
            # DataFrame létrehozása
            df = pd.DataFrame(df_data)
            
            # 🔧 KRITIKUS: DataFrame validálás
            if df.empty:
                logger.error("❌ Létrehozott DataFrame üres!")
                return pd.DataFrame()
            
            logger.info(f"✅ DataFrame sikeresen létrehozva:")
            logger.info(f"   - Sorok: {len(df)}")
            logger.info(f"   - Oszlopok: {len(df.columns)}")
            logger.info(f"   - Oszlopnevek: {list(df.columns)}")
            logger.info(f"   - Első 3 sor dátuma: {list(df['date'].head(3))}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ _convert_to_dataframe() HIBA: {e}")
            logger.exception("Részletes hiba:")
            return pd.DataFrame()
    
    def clear_data(self) -> None:
        """Táblázat törlése."""
        self.current_data = None
        self.filtered_data = None
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        
        # Vezérlők letiltása
        self.csv_btn.setEnabled(False)
        self.excel_btn.setEnabled(False)
        
        # 🔧 JAVÍTÁS: "Összes" alapértelmezett visszaállítása
        self.rows_per_page_combo.setCurrentText("Összes")
        self.rows_per_page = 1000
        
        # Rendezési állapot reset
        self.current_sort_column = -1
        self.current_sort_order = Qt.AscendingOrder
        
        self._update_info_display(0, 0)
    
    def get_selected_row_data(self) -> Optional[Dict[str, Any]]:
        """Kiválasztott sor adatainak lekérdezése."""
        current_row = self.table.currentRow()
        if current_row >= 0 and self.filtered_data is not None:
            global_row = self.current_page * self.rows_per_page + current_row
            if global_row < len(self.filtered_data):
                row_data = self.filtered_data.iloc[global_row].to_dict()
                return row_data
        return None
    
    def apply_theme(self, dark_theme: bool) -> None:
        """
        Téma alkalmazása - THEMEMANAGER DELEGÁLÓ VERZIÓ.
        
        Args:
            dark_theme: True, ha sötét téma
        """
        print(f"🎨 DEBUG: WeatherDataTable applying theme via ThemeManager: {'dark' if dark_theme else 'light'}")
        
        # ThemeManager automatikus widget styling
        theme_name = "dark" if dark_theme else "light"
        self._theme_manager.set_theme(theme_name)
        
        # Info bar speciális CSS (nem widget, hanem manual)
        scheme = self._theme_manager.get_color_scheme()
        if scheme and hasattr(self, 'info_bar'):
            # 🔧 KRITIKUS JAVÍTÁS: ColorPalette API helyes használata
            surface_variant = scheme.get_color("surface", "light") or "#f5f5f5"
            border_color = scheme.get_color("info", "light") or "#d1d5db"
            
            self.info_bar.setStyleSheet(f"""
                QWidget#info_bar {{
                    background-color: {surface_variant};
                    border-top: 1px solid {border_color};
                }}
            """)
            
            if hasattr(self, 'rows_info'):
                text_color = scheme.get_color("info", "base") or "#6b7280"
                self.rows_info.setStyleSheet(f"""
                    QLabel#rows_info {{
                        color: {text_color};
                        font-size: 11px;
                    }}
                """)
        
        # Ha van adat, újrarajzoljuk a táblázatot ThemeManager színekkel
        if self.filtered_data is not None and not self.filtered_data.empty:
            self._display_current_page()
        
        print(f"✅ DEBUG: WeatherDataTable theme applied via ThemeManager: {'dark' if dark_theme else 'light'}")
    
    def get_sorting_info(self) -> Tuple[int, str]:
        """Jelenlegi rendezési állapot lekérdezése."""
        order_text = "növekvő" if self.current_sort_order == Qt.AscendingOrder else "csökkenő"
        return (self.current_sort_column, order_text)
