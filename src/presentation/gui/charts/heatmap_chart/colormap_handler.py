#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

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


def _select_parameter_colormap(parameter: str, vmin: float, vmax: float) -> str:
    """Select colormap based on the heatmap parameter."""
    if "temperature" in parameter:
        return _select_temperature_colormap(vmin, vmax)
    if "precipitation" in parameter:
        return "Blues"
    if "wind" in parameter:
        return "Greens"
    return "viridis"


def _select_temperature_colormap(vmin: float, vmax: float) -> str:
    """Select temperature-specific colormap."""
    if vmin < 0 and vmax > 20:
        logger.debug("🌡️ Hőmérséklet: RdYlBu_r (piros=meleg, kék=hideg)")
        return "RdYlBu_r"
    if vmax <= 15:
        logger.debug("🌡️ Hőmérséklet: Blues_r (hideg)")
        return "Blues_r"
    if vmin >= 15:
        logger.debug("🌡️ Hőmérséklet: Reds (meleg)")
        return "Reds"
    logger.debug("🌡️ Hőmérséklet: viridis (alapértelmezett)")
    return "viridis"


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
    cmap = _select_parameter_colormap(self.parameter, vmin, vmax)
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    return cmap, norm
