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
"""

# Re-export types
from src.presentation.gui.hungarian_city_selector.types import (
    HungarianCity,
    HungarianRegions
)

# Re-export core
from src.presentation.gui.hungarian_city_selector.core import HungarianCitySelector

__all__ = [
    'HungarianCitySelector',
    'HungarianCity',
    'HungarianRegions'
]
