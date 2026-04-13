#!/usr/bin/env python3
# mypy: ignore-errors

"""
Trend Analytics Tab - Public API

🌐 Publikus interfész

Képességek:
- set_location: Külső lokáció beállítás
- Publikus metódusok

Fájl: src/presentation/gui/trend_analytics/trend_analytics_tab/public_api.py
"""

import logging

logger = logging.getLogger(__name__)


class TrendAnalyticsPublicAPIMixin:
    """
    Publikus API mixin a TrendAnalyticsTab számára.
    """

    def set_location(self, location_name: str, latitude: float, longitude: float) -> None:
        """
        External location setting (VÁLTOZATLAN).

        Args:
            location_name: Helyszín neve
            latitude: Szélességi fok
            longitude: Hosszúsági fok
        """
        self.location_combo.setCurrentText(location_name)
        self.on_location_changed(location_name)

        logger.info(f"📍 External location set: {location_name} ({latitude:.4f}, {longitude:.4f})")
