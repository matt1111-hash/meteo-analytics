#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Detailed Charts Tab Module
📈 "Részletes Diagramok" TAB - Nagy, professzionális chartok
🔧 MODULÁRIS BONTÁS: chart_widgets.py → chart_container.py import frissítés
"""

import logging
from typing import Optional, Dict, Any

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal

from ..chart_container import ChartsContainer
from ..theme_manager import get_theme_manager, register_widget_for_theming

# Logging konfigurálása
logger = logging.getLogger(__name__)


class DetailedChartsTab(QWidget):
    """
    📈 "Részletes Diagramok" TAB - Nagy, professzionális chartok.
    🔧 MODULÁRIS BONTÁS: chart_widgets.py → chart_container.py import frissítés
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        logger.debug("DetailedChartsTab inicializálás START")
        
        # === THEMEMANAGER INICIALIZÁLÁSA ===
        self.theme_manager = get_theme_manager()
        
        self.charts_container: Optional[ChartsContainer] = None
        
        # UI inicializálása
        self._init_ui()
        
        # === THEMEMANAGER REGISZTRÁCIÓ ===
        self._register_widgets_for_theming()
        
        logger.debug("DetailedChartsTab inicializálás BEFEJEZVE")
    
    def _init_ui(self) -> None:
        """UI inicializálása - nagy chartok."""
        logger.debug("DetailedChartsTab._init_ui() START")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Charts container
        logger.debug("ChartsContainer létrehozása...")
        self.charts_container = ChartsContainer()
        
        if self.charts_container:
            logger.debug("ChartsContainer sikeresen létrehozva!")
            layout.addWidget(self.charts_container)
        else:
            logger.error("ChartsContainer létrehozása SIKERTELEN!")
        
        logger.debug("DetailedChartsTab._init_ui() BEFEJEZVE")
    
    def _register_widgets_for_theming(self) -> None:
        """Widget-ek regisztrálása ThemeManager-hez."""
        register_widget_for_theming(self, "container")
        logger.debug("DetailedChartsTab - Widget regisztrálva ColorPalette API-hez")
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        Részletes chartok frissítése.
        
        Args:
            data: OpenMeteo API válasz
        """
        logger.info("DetailedChartsTab.update_data() MEGHÍVVA!")
        
        # === CHARTS CONTAINER ELLENŐRZÉS ===
        if self.charts_container:
            logger.debug("charts_container EXISTS - calling update_charts...")
            
            try:
                self.charts_container.update_charts(data)
                logger.info("charts_container.update_charts() SIKERES!")
                
            except Exception as e:
                logger.error(f"HIBA a charts_container.update_charts() hívásban: {e}")
        else:
            logger.error("charts_container is None! - Ez a probléma oka!")
    
    def clear_data(self) -> None:
        """Chartok törlése."""
        logger.debug("DetailedChartsTab.clear_data() MEGHÍVVA")
        
        if self.charts_container:
            logger.debug("charts_container létezik - clear_charts() hívása...")
            self.charts_container.clear_charts()
            logger.debug("clear_charts() BEFEJEZVE")
        else:
            logger.error("charts_container is None - nem lehet törölni!")
    
    def apply_theme(self, dark_theme: bool) -> None:
        """Téma alkalmazása."""
        logger.debug(f"DetailedChartsTab.apply_theme({dark_theme}) MEGHÍVVA")
        
        if self.charts_container:
            logger.debug("charts_container létezik - apply_theme() hívása...")
            self.charts_container.apply_theme(dark_theme)
            logger.debug("apply_theme() BEFEJEZVE")
        else:
            logger.error("charts_container is None - nem lehet témát alkalmazni!")
