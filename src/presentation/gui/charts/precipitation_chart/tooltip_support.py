# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Precipitation Chart - Tooltip

💬 Tooltip funkciók

Képességek:
- Legközelebbi pont keresése
- Tooltip szöveg formázás
- Tooltip megjelenítés/elrejtés

Fájl: src/presentation/gui/charts/precipitation_chart/tooltip.py
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    pass

from src.presentation.gui.theme_manager import get_current_colors
