#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Heatmap Chart - Colorbar Handler

🎨 Colorbar létrehozása

Képességek:
- Colorbar létrehozása
- Paraméter szerinti címkék
- Téma alkalmazás

Fájl: src/presentation/gui/charts/heatmap_chart/colorbar_handler.py
"""

import logging
from typing import TYPE_CHECKING

from ...theme_manager import get_current_colors

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _resolve_colorbar_label(parameter: str) -> str:
    """Resolve parameter-specific colorbar label."""
    if "temperature" in parameter:
        return "Hőmérséklet (°C)"
    if "precipitation" in parameter:
        return "Csapadék (mm)"
    if "wind" in parameter:
        return "Szélsebesség (km/h)"
    return "Érték"


def create_colorbar(self, im) -> None:
    """
    Create colorbar with parameter-specific label.

    Args:
        self: HeatmapCalendarChart instance
        im: Matplotlib image object
    """
    current_colors = get_current_colors()
    text_color = current_colors.get("on_surface", "#1f2937")

    try:
        if self._colorbar:
            self._colorbar.remove()
            self._colorbar = None

        self._colorbar = self.figure.colorbar(
            im, ax=self.ax, shrink=0.8, aspect=30, pad=0.02
        )
        label = _resolve_colorbar_label(self.parameter)
        self._colorbar.set_label(
            label, fontsize=12, fontweight="500", color=text_color, labelpad=15
        )
        self._colorbar.ax.tick_params(colors=text_color, labelsize=10)

    except Exception as e:
        logger.warning(f"⚠️ Colorbar hiba: {e}")
