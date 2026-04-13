#!/usr/bin/env python3
# mypy: ignore-errors

"""
🗺️ Hungarian Location Selector - Data Models
Magyar Klímaanalitika MVP - Statisztikai régió modellek
"""

from dataclasses import dataclass
from enum import Enum


class HungarianStatisticalRegion(Enum):
    """
    🔧 JAVÍTOTT: Magyar statisztikai régiók (KSH hivatalos felosztás)
    7 NUTS 2 szintű statisztikai régió - Control Panel és Multi-City Engine konzisztens!
    """

    KOZEP_MAGYARORSZAG = "kozep_magyarorszag"  # Közép-Magyarország
    KOZEP_DUNANTUL = "kozep_dunantul"  # Közép-Dunántúl
    NYUGAT_DUNANTUL = "nyugat_dunantul"  # Nyugat-Dunántúl
    DEL_DUNANTUL = "del_dunantul"  # Dél-Dunántúl
    ESZAK_MAGYARORSZAG = "eszak_magyarorszag"  # Észak-Magyarország
    ESZAK_ALFOLD = "eszak_alfold"  # Észak-Alföld
    DEL_ALFOLD = "del_alfold"  # Dél-Alföld


@dataclass
class HungarianRegionData:
    """
    🗺️ Magyar régió adatstruktúra - JAVÍTOTT 7 statisztikai régió verzió.
    """

    name: str
    display_name: str
    description: str
    counties: list[str]
    administrative_center: str
    avg_temp_annual: float
    avg_precipitation_annual: int
    characteristics: list[str]
    nuts_code: str  # NUTS 2 kód (HU10, HU21, stb.)
