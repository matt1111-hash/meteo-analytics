# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for core.py."""

from __future__ import annotations

from .core_part1 import MultiCityWidgetPart1Mixin
from .core_part2 import MultiCityWidgetPart2Mixin
from .core_support import *


class MultiCityWidget(
    MultiCityWidgetPart1Mixin,
    MultiCityWidgetPart2Mixin,
    QWidget,
    MultiCityWidgetPublicAPI,
):
    """
    🏙️ MULTI-CITY VÁLASZTÓ WIDGET - DROPDOWN VERSION

    Felelősség:
    - Magyar régiók/megyék dropdown választás (QComboBox)
    - Analysis type alapú mode váltás (region vs county)
    - Single selection state management
    - Selection info display (pl. "Közép-Magyarország (2 megye)")

    Interface:
    - selection_changed = Signal(dict) - kiválasztás változás
    - get_state() -> dict - aktuális állapot
    - set_state(dict) - állapot beállítása
    - is_valid() -> bool - van-e kiválasztás
    - set_analysis_mode(str) - "region" vagy "county" mode
    """

    # === KIMENŐ SIGNAL ===
    selection_changed = Signal(
        dict
    )  # {"mode": "region", "selected": "Közép-Magyarország", "is_valid": True}
