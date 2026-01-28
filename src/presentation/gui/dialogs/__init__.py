#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - GUI Dialogs Package
🎨 DIALOG GYŰJTEMÉNY: Anomália beállítások és egyéb dialog-ok
📦 PACKAGE INIT: Dialog-ok centralizált importálása

🚀 ELÉRHETŐ DIALOG-OK:
✅ ExtremeWeatherDialog - Extrém időjárási események
✅ AnomalySettingsDialog - Anomália beállítások teljes GUI
"""

from .anomaly_settings_dialog import AnomalySettingsDialog
from .core import ExtremeWeatherDialog

__all__ = [
    'AnomalySettingsDialog',
    'ExtremeWeatherDialog'
]

# Package info
__version__ = "1.1.0"
__author__ = "Global Weather Analyzer Team"
__description__ = "GUI Dialog Components"

# Logging setup
import logging

logger = logging.getLogger(__name__)
logger.info("🎨 GUI Dialogs package betöltve")
