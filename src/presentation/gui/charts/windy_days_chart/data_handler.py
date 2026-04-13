#!/usr/bin/env python3
# mypy: ignore-errors

"""
Windy Days Chart - Data Handler

📊 Adat frissítés és validáció

Képességek:
- Adatok frissítése
- Validáció

Fájl: src/presentation/gui/charts/windy_days_chart/data_handler.py
"""

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def update_data(self, chart_data: dict[str, Any]) -> None:
    """
    Chart adatok frissítése és újrarajzolás.

    Args:
        self: WindyDaysChart instance
        chart_data: Dictionary a chart adatokkal
    """
    from .plotting import _plot_windy_days_chart

    try:
        logger.info("WindyDaysChart adatok frissítése")

        # Adatok kinyerése
        self.chart_data = chart_data.get("chart_data", {})
        self.threshold_kmh = chart_data.get("threshold_kmh", 43.0)
        self.location_name = chart_data.get("location_name", "Ismeretlen helyszín")

        # Ellenőrzés
        if not _has_valid_data(self):
            logger.warning("Nincs érvényes adat a WindyDaysChart-hoz")
            from .helpers import _plot_no_data_message

            _plot_no_data_message(self)
            return

        # Új chart rajzolása
        _plot_windy_days_chart(self)

        logger.info(f"WindyDaysChart frissítve: {len(self.chart_data.get('months', []))} hónap")

    except Exception as e:
        logger.error(f"Hiba a WindyDaysChart adatok frissítésében: {e}")
        from .helpers import _plot_error_message

        _plot_error_message(self, str(e))


def _has_valid_data(self) -> bool:
    """
    Ellenőrzi hogy van-e érvényes adat a chart-hoz.

    Args:
        self: WindyDaysChart instance

    Returns:
        bool: Van-e érvényes adat
    """
    try:
        months = self.chart_data.get("months", [])
        counts = self.chart_data.get("counts", [])

        return (
            len(months) > 0
            and len(counts) > 0
            and len(months) == len(counts)
            and any(count > 0 for count in counts)
        )
    except Exception:
        return False
