#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Windy Days Chart - Interactivity

🖱️ Interaktív funkciók

Képességek:
- Hover tooltip
- Interaktivitás beállítás

Fájl: src/presentation/gui/charts/windy_days_chart/interactivity.py
"""

import logging
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _setup_chart_interactivity(
    self, bars, months: List[str], counts: List[int], percentages: List[float]
) -> None:
    """
    Chart interaktivitás beállítása.

    Args:
        self: WindyDaysChart instance
        bars: Bar chart
        months: Hónapok
        counts: Szeles napok számai
        percentages: Százalékok
    """
    try:
        # Tooltip funkció
        def on_hover(event):
            if event.inaxes:
                for i, bar in enumerate(bars):
                    if bar.contains(event)[0]:
                        # Tooltip info
                        month = months[i]
                        count = counts[i]
                        percentage = percentages[i]

                        tooltip = f"{month}: {count} szeles nap ({percentage:.1f}%)"

                        # Status bar frissítés (ha van parent widget)
                        if hasattr(self.parent(), "status_bar"):
                            self.parent().status_bar.showMessage(tooltip)

                        return

        # Event kapcsolás - 🚨 JAVÍTVA: self használata self.canvas helyett
        self.mpl_connect("motion_notify_event", on_hover)

    except Exception as e:
        logger.error(f"Hiba az interaktivitás beállításában: {e}")
