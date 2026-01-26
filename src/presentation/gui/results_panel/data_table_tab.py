#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Data Table Tab Module
📋 "Adattáblázat" TAB - Teljes képernyős táblázat kezelő
"""

import logging
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..data_widgets import WeatherDataTable
from ..theme_manager import get_theme_manager, register_widget_for_theming

# Logging konfigurálása
logger = logging.getLogger(__name__)


class DataTableTab(QWidget):
    """📋 "Adattáblázat" TAB - Teljes képernyős táblázat kezelő."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.theme_manager = get_theme_manager()
        
        self.data_table: Optional[WeatherDataTable] = None
        self.csv_btn: Optional[QPushButton] = None
        self.excel_btn: Optional[QPushButton] = None
        
        self._init_ui()
        self._register_widgets_for_theming()
        
        logger.debug("DataTableTab ColorPalette API integráció kész")
    
    def _init_ui(self) -> None:
        """UI inicializálása."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.toolbar = self._create_table_toolbar()
        layout.addWidget(self.toolbar)
        
        self.data_table = WeatherDataTable()
        layout.addWidget(self.data_table)
    
    def _create_table_toolbar(self) -> QWidget:
        """Táblázat eszköztár létrehozása."""
        toolbar = QWidget()
        toolbar.setMaximumHeight(50)
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.title = QLabel("📋 Időjárási Adatok Táblázat")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        self.title.setFont(title_font)
        layout.addWidget(self.title)
        
        layout.addStretch()
        
        self.csv_btn = QPushButton("📊 CSV")
        self.csv_btn.setEnabled(False)
        layout.addWidget(self.csv_btn)
        
        self.excel_btn = QPushButton("📈 Excel")
        self.excel_btn.setEnabled(False)
        layout.addWidget(self.excel_btn)
        
        return toolbar
    
    def _register_widgets_for_theming(self) -> None:
        """Widget-ek regisztrálása ThemeManager-hez."""
        register_widget_for_theming(self, "container")
        register_widget_for_theming(self.toolbar, "container")
        register_widget_for_theming(self.title, "text")
        register_widget_for_theming(self.csv_btn, "button")
        register_widget_for_theming(self.excel_btn, "button")
        
        logger.debug("DataTableTab - Összes widget regisztrálva ColorPalette API-hez")
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """Táblázat adatok frissítése."""
        if self.data_table:
            self.data_table.update_data(data)
            if self.csv_btn:
                self.csv_btn.setEnabled(True)
            if self.excel_btn:
                self.excel_btn.setEnabled(True)
    
    def clear_data(self) -> None:
        """Táblázat törlése."""
        if self.data_table:
            self.data_table.clear_data()
            if self.csv_btn:
                self.csv_btn.setEnabled(False)
            if self.excel_btn:
                self.excel_btn.setEnabled(False)
    
    def apply_theme(self, dark_theme: bool) -> None:
        """Téma alkalmazása."""
        if self.data_table:
            self.data_table.apply_theme(dark_theme)
