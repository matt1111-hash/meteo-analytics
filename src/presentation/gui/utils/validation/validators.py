#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validation - Basic validators for dates, filenames, colors.
"""

import logging
import re
from typing import Tuple

logger = logging.getLogger(__name__)


def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, str]:
    """
    Dátum tartomány validálása.

    Args:
        start_date: Kezdő dátum (YYYY-MM-DD)
        end_date: Befejező dátum (YYYY-MM-DD)

    Returns:
        (valid, error_message) tuple
    """
    from datetime import datetime

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        if start > end:
            return False, "A kezdő dátum nem lehet későbbi a befejező dátumnál"

        if end > datetime.now():
            return False, "A befejező dátum nem lehet jövőbeli"

        if (end - start).days > 365:
            return False, "Maximum 365 napos időszak választható"

        if (end - start).days < 1:
            return False, "Minimum 1 napos időszak szükséges"

        return True, ""

    except ValueError:
        return False, "Érvénytelen dátum formátum (YYYY-MM-DD)"


def sanitize_filename(filename: str) -> str:
    """
    Fájlnév tisztítása Windows/Linux kompatibilitáshoz.

    Args:
        filename: Eredeti fájlnév

    Returns:
        Tisztított fájlnév
    """
    # Tiltott karakterek eltávolítása
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Whitespace-ek cseréje
    filename = re.sub(r"\s+", "_", filename)

    # Maximum hossz korlátozása
    if len(filename) > 200:
        filename = filename[:200]

    return filename


def validate_color_hex(color: str) -> bool:
    """
    Hex szín validálása.

    Args:
        color: Hex színkód (#RRGGBB vagy #RGB)

    Returns:
        Érvényes színkód-e
    """
    pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    return bool(re.match(pattern, color))


def get_contrast_ratio(color1: str, color2: str) -> float:
    """
    Két szín közötti kontraszt arány számítása.

    Args:
        color1: Első szín hex formátumban
        color2: Második szín hex formátumban

    Returns:
        Kontraszt arány (1.0-21.0)
    """
    # JÖVŐBELI IMPLEMENTÁCIÓ: WCAG kontraszt számítás
    # Akadálymentesség támogatáshoz
    return 4.5  # Placeholder (WCAG AA minimum)


__all__ = [
    "validate_date_range",
    "sanitize_filename",
    "validate_color_hex",
    "get_contrast_ratio",
]
