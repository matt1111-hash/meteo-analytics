#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Heatmap Chart - Colormap Handler

🎨 Colormap és normalizáció kezelése

Képességek:
- Paraméter szerinti colormap
- Dinamikus norm
- Színskála beállítás

Fájl: src/presentation/gui/charts/heatmap_chart/colormap_handler.py
"""

import logging
from typing import TYPE_CHECKING, Tuple

import matplotlib.colors as mcolors
import numpy as np

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def get_colormap_and_norm(self, calendar_matrix: np.ndarray) -> Tuple[str, object]:
    """
    Get colormap and normalization.

    Args:
        self: HeatmapCalendarChart instance
        calendar_matrix: Kalendár mátrix

    Returns:
        Tuple[str, object]: (colormap név, norm objektum)
    """
    if self._custom_cmap is not None and self._custom_norm is not None:
        logger.info("🎨 Custom colormap használata")
        return self._custom_cmap, self._custom_norm

    valid_values = calendar_matrix[~np.isnan(calendar_matrix)]
    if len(valid_values) == 0:
        logger.warning("⚠️ Nincs érvényes adat")
        return "viridis", None

    vmin = valid_values.min()
    vmax = valid_values.max()

    if "temperature" in self.parameter:
        if vmin < 0 and vmax > 20:
            cmap = "RdYlBu_r"  # REVERSE: piros=meleg, kék=hideg
            logger.debug("🌡️ Hőmérséklet: RdYlBu_r (piros=meleg, kék=hideg)")
        elif vmax <= 15:
            cmap = "Blues_r"  # Hideg: sötétkék=hidegebb
            logger.debug("🌡️ Hőmérséklet: Blues_r (hideg)")
        elif vmin >= 15:
            cmap = "Reds"  # Meleg: sötétpiros=melegebb
            logger.debug("🌡️ Hőmérséklet: Reds (meleg)")
        else:
            cmap = "viridis"
            logger.debug("🌡️ Hőmérséklet: viridis (alapértelmezett)")
    elif "precipitation" in self.parameter:
        cmap = "Blues"
    elif "wind" in self.parameter:
        cmap = "Greens"
    else:
        cmap = "viridis"

    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    return cmap, norm
