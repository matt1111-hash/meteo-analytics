#!/usr/bin/env python3
# mypy: ignore-errors

"""
Results Panel Utils Module

🔧 Utility osztályok az eredmény panelhez

Képességek:
- WindGustsConstants: Széllökés kategóriák és küszöbök
- DataFrameExtractor: API válasz feldolgozás
- WindGustsAnalyzer: Széllökés elemzés

Fájl: src/presentation/gui/results_panel/utils/__init__.py
"""

import logging

from .dataframe_extractor import DataFrameExtractor
from .wind_analyzer import WindGustsAnalyzer

# Re-export for backward compatibility
from .wind_constants import WindGustsConstants

__all__ = ["DataFrameExtractor", "WindGustsAnalyzer", "WindGustsConstants"]

logger = logging.getLogger(__name__)
logger.info(
    "✅ Results panel utils loaded: WindGustsConstants, DataFrameExtractor, WindGustsAnalyzer"
)
