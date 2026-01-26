#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - GUI Dialogs Package
🎨 DIALOG GYŰJTEMÉNY: Anomália beállítások és egyéb dialog-ok
📦 PACKAGE INIT: Dialog-ok centralizált importálása

🚀 ELÉRHETŐ DIALOG-OK:
✅ AnomalySettingsDialog - Anomália beállítások teljes GUI
🔄 ExtremeWeatherDialog - Placeholder (kompatibilitáshoz)
"""

from .anomaly_settings_dialog import AnomalySettingsDialog

# 🔄 BACKWARD COMPATIBILITY: ExtremeWeatherDialog placeholder
try:
    # Ha létezik az eredeti ExtremeWeatherDialog, importáljuk
    from .extreme_weather_dialog import ExtremeWeatherDialog
except ImportError:
    # Ha nem létezik, placeholder osztályt hozunk létre
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
    
    class ExtremeWeatherDialog(QDialog):
        """🔄 PLACEHOLDER: ExtremeWeatherDialog kompatibilitáshoz."""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("⚡ Extrém Időjárási Események")
            self.setModal(True)
            self.resize(400, 300)
            
            layout = QVBoxLayout(self)
            
            info_label = QLabel("🚧 ExtremeWeatherDialog fejlesztés alatt...\n\n"
                               "📊 Jelenlegi funkciók:\n"
                               "• Anomália detektálás az ExtremeEventsTab-ban\n"
                               "• ⚙️ Anomália beállítások teljes GUI-val\n"
                               "• 📁 Profil menedzsment\n\n"
                               "🔄 Ez a dialog hamarosan teljes funkcionalitással!")
            layout.addWidget(info_label)
            
            close_btn = QPushButton("✅ Rendben")
            close_btn.clicked.connect(self.accept)
            layout.addWidget(close_btn)

__all__ = [
    'AnomalySettingsDialog',
    'ExtremeWeatherDialog'
]

# Package info
__version__ = "1.0.0"
__author__ = "Global Weather Analyzer Team"
__description__ = "GUI Dialog Components"

# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.info("🎨 GUI Dialogs package betöltve")
