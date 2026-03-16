#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

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


def _log_utils_success() -> None:
    """Log successful utils initialization details."""
    logger.info(
        "✅ utils.py modul sikeresen inicializálva (DUAL-API + WIND GUSTS + PROVIDER TRACKING + BACKWARD COMPATIBILITY)"
    )
    logger.info(
        "🌪️ Wind thresholds - Strong: %s, Extreme: %s",
        AnomalyConstants.WIND_HIGH_THRESHOLD,
        AnomalyConstants.WIND_EXTREME_THRESHOLD,
    )
    logger.info(
        "🌍 Data sources: %s APIs configured",
        len(DataConstants.DATA_SOURCE_PRIORITY),
    )
    logger.info("🌍 Provider tracking functions loaded")
    logger.info("🔧 Backward compatibility aliases: get_display_name_for_source ✅")


def _log_api_availability() -> None:
    """Log availability for all configured data sources."""
    for source in DataConstants.DATA_SOURCE_PRIORITY:
        available = validate_api_source_available(source)
        display_name = get_source_display_name(source)
        status = "✅" if available else "❌"
        logger.info("🔗 %s: %s", display_name, status)


def _log_utils_validation_failures(
    gui_valid: dict[str, bool],
    wind_valid: dict[str, bool],
    dual_api_valid: dict[str, bool],
) -> None:
    """Log failing validation keys."""
    logger.error("❌ utils.py modul validálási hibák:")
    for key, value in {**gui_valid, **wind_valid, **dual_api_valid}.items():
        if not value:
            logger.error("  - %s: FAILED", key)


def initialize_utils_module() -> bool:
    """
    Utils modul inicializálása és validálása.

    Returns:
        Inicializálás sikerességét jelző bool
    """
    try:
        logger.info(
            "utils.py modul inicializálása (DUAL-API + WIND GUSTS + PROVIDER TRACKING + BACKWARD COMPATIBILITY)..."
        )

        # Konstansok validálása
        gui_valid = validate_gui_constants()
        wind_valid = validate_wind_gusts_constants()
        dual_api_valid = validate_dual_api_constants()

        # Validációs eredmények ellenőrzése
        all_valid = (
            all(gui_valid.values())
            and all(wind_valid.values())
            and all(dual_api_valid.values())
        )

        if all_valid:
            _log_utils_success()
            _log_api_availability()
            return True
        _log_utils_validation_failures(gui_valid, wind_valid, dual_api_valid)
        return False

    except Exception as e:
        logger.error(f"❌ utils.py modul inicializálási hiba: {e}")
        return False
