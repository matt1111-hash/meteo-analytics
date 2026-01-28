#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utils - Initialization

🔧 Modul inicializálás és validáció

Képességek:
- Utils modul inicializálása
- Validáció

Fájl: src/presentation/gui/utils/initialization.py
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from .api_helpers import get_source_display_name, validate_api_source_available
from .constants import AnomalyConstants, DataConstants
from .validation import (
    validate_dual_api_constants,
    validate_gui_constants,
    validate_wind_gusts_constants,
)

logger = logging.getLogger(__name__)


def initialize_utils_module() -> bool:
    """
    Utils modul inicializálása és validálása.

    Returns:
        Inicializálás sikerességét jelző bool
    """
    try:
        logger.info("utils.py modul inicializálása (DUAL-API + WIND GUSTS + PROVIDER TRACKING + BACKWARD COMPATIBILITY)...")

        # Konstansok validálása
        gui_valid = validate_gui_constants()
        wind_valid = validate_wind_gusts_constants()
        dual_api_valid = validate_dual_api_constants()

        # Validációs eredmények ellenőrzése
        all_valid = (
            all(gui_valid.values()) and
            all(wind_valid.values()) and
            all(dual_api_valid.values())
        )

        if all_valid:
            logger.info("✅ utils.py modul sikeresen inicializálva (DUAL-API + WIND GUSTS + PROVIDER TRACKING + BACKWARD COMPATIBILITY)")
            logger.info(f"🌪️ Wind thresholds - Strong: {AnomalyConstants.WIND_HIGH_THRESHOLD}, Extreme: {AnomalyConstants.WIND_EXTREME_THRESHOLD}")
            logger.info(f"🌍 Data sources: {len(DataConstants.DATA_SOURCE_PRIORITY)} APIs configured")
            logger.info("🌍 Provider tracking functions loaded")
            logger.info("🔧 Backward compatibility aliases: get_display_name_for_source ✅")

            # API availability check
            for source in DataConstants.DATA_SOURCE_PRIORITY:
                available = validate_api_source_available(source)
                display_name = get_source_display_name(source)
                status = "✅" if available else "❌"
                logger.info(f"🔗 {display_name}: {status}")

            return True
        else:
            logger.error("❌ utils.py modul validálási hibák:")
            for key, value in {**gui_valid, **wind_valid, **dual_api_valid}.items():
                if not value:
                    logger.error(f"  - {key}: FAILED")
            return False

    except Exception as e:
        logger.error(f"❌ utils.py modul inicializálási hiba: {e}")
        return False
