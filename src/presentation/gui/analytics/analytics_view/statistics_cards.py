#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analytics View - Statistics Cards Module
Statisztika kártyák létrehozása az AnalyticsViewhoz.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from src.presentation.gui.analytics.analytics_statistics import AnalyticsStatistics

if TYPE_CHECKING:
    from src.presentation.gui.analytics.analytics_view.core import AnalyticsView


logger = logging.getLogger(__name__)


class AnalyticsViewStatisticsCards:
    """Statisztika kártyák kezelő osztály."""

    def __init__(self, view: "AnalyticsView"):
        """Inicializálás."""
        self.view = view

    def process_and_display_statistics(
        self, data: Dict[str, Any], total_days: int
    ) -> None:
        """🚨 JAVÍTOTT: Statisztikák feldolgozása és megjelenítése - KOMPAKT KÁRTYÁS RENDSZER."""
        try:
            logger.info(
                "🚨 _process_and_display_statistics() MEGHÍVVA - STATISZTIKÁK JAVÍTÁS"
            )

            # Statisztikai adatok számítása
            stats_data = AnalyticsStatistics.calculate_statistics_data(data, total_days)

            # Kompakt kártyás widget létrehozása
            stats_widget = self.create_statistics_cards_widget(stats_data)

            # 🚨 KRITIKUS: Statisztikák widget beállítása a scroll area-ba
            self.view.statistics_area.setWidget(stats_widget)

            logger.info("✅ Statisztikák sikeresen megjelenítve a bal oldali panelen")

        except Exception as e:
            logger.error(f"Statisztika feldolgozási hiba: {e}", exc_info=True)
            # Hiba esetén alapértelmezett üzenet
            error_widget = QLabel(f"❌ Statisztika hiba: {str(e)}")
            error_widget.setAlignment(Qt.AlignCenter)
            error_widget.setStyleSheet("color: red; padding: 20px;")
            self.view.statistics_area.setWidget(error_widget)

    def create_statistics_cards_widget(self, stats: Dict[str, Any]) -> QWidget:
        """🎯 KOMPAKT KÁRTYÁS STATISZTIKA WIDGET LÉTREHOZÁSA."""
        try:
            main_widget = QWidget()
            layout = QVBoxLayout(main_widget)
            layout.setContentsMargins(4, 4, 4, 4)
            layout.setSpacing(8)

            if not stats:
                no_data_label = QLabel("❌ Nincsenek adatok")
                no_data_label.setAlignment(Qt.AlignCenter)
                no_data_label.setStyleSheet(
                    "color: #666; font-style: italic; padding: 20px; font-size: 12px;"
                )
                layout.addWidget(no_data_label)
                return main_widget

            # === 1. HŐMÉRSÉKLET KÁRTYA ===
            temp_card = self._create_statistic_card(
                "🌡️ HŐMÉRSÉKLETI STATISZTIKÁK",
                [
                    f"• Átlag hőmérséklet: {stats.get('temp_avg', 0):.1f}°C"
                    if stats.get("temp_avg")
                    else "• Átlag hőmérséklet: N/A",
                    f"• Min/Max: {stats.get('temp_min', 0):.1f}°C / {stats.get('temp_max', 0):.1f}°C"
                    if stats.get("temp_min") and stats.get("temp_max")
                    else "• Min/Max: N/A",
                    f"• Fagyos napok: {stats.get('freezing_days', 0)} nap",
                    f"• Hőséghullám (>30°C): {stats.get('hot_days', 0)} nap",
                    f"• Hőmérséklet ingadozás: {stats.get('temp_range_avg', 0):.1f}°C"
                    if stats.get("temp_range_avg")
                    else "• Hőmérséklet ingadozás: N/A",
                ],
            )
            layout.addWidget(temp_card)

            # === 2. CSAPADÉK KÁRTYA ===
            precip_card = self._create_statistic_card(
                "🌧️ CSAPADÉK ELEMZÉS",
                [
                    f"• Átlag csapadék: {stats.get('precip_avg', 0):.1f}mm/nap"
                    if stats.get("precip_avg")
                    else "• Átlag csapadék: N/A",
                    f"• Száraz napok: {stats.get('dry_days', 0)} nap ({stats.get('dry_percentage', 0):.0f}%)",
                    f"• Esős napok: {stats.get('rainy_days', 0)} nap ({stats.get('rainy_percentage', 0):.0f}%)",
                    f"• Összes csapadék: {stats.get('annual_precip', 0):.0f}mm/év"
                    if stats.get("annual_precip")
                    else "• Összes csapadék: N/A",
                    f"• Leghosszabb száraz: {stats.get('longest_dry_streak', 0)} nap",
                ],
            )
            layout.addWidget(precip_card)

            # === 3. SZÉL KÁRTYA ===
            wind_card = self._create_statistic_card(
                "💨 SZÉL BEAUFORT ELEMZÉS",
                [
                    f"• Átlag szélsebesség: {stats.get('wind_avg', 0):.1f} km/h"
                    if stats.get("wind_avg")
                    else "• Átlag szélsebesség: N/A",
                    f"• Max széllökés: {stats.get('windgust_max', 0):.1f} km/h"
                    if stats.get("windgust_max")
                    else f"• Max szélsebesség: {stats.get('wind_max', 0):.1f} km/h"
                    if stats.get("wind_max")
                    else "• Max szél: N/A",
                    f"• Szélcsend (0-1): {stats.get('wind_calm', 0)} nap",
                    f"• Gyenge szél (2-3): {stats.get('wind_light', 0)} nap",
                    f"• Mérsékelt (4-5): {stats.get('wind_moderate', 0)} nap",
                    f"• Erős szél (6+): {stats.get('wind_strong', 0)} nap",
                ],
            )
            layout.addWidget(wind_card)

            # === 4. IDŐSZAK KÁRTYA ===
            period_card = self._create_statistic_card(
                "📊 IDŐSZAK & RENDSZER INFO",
                [
                    f"• Időtartam: {stats.get('start_date', 'N/A')} - {stats.get('end_date', 'N/A')}",
                    f"• Napok száma: {stats.get('total_days', 0)} nap",
                    "• Konstans felbontás: 365 bin",
                    f"• Bin méret: ~{stats.get('bin_size', 1)} nap/téglalap",
                    "• Beaufort 13 fokozat színek",
                ],
            )
            layout.addWidget(period_card)

            # Stretch hozzáadása az aljára
            layout.addStretch()

            return main_widget

        except Exception as e:
            logger.error(f"Kártyás widget létrehozási hiba: {e}")
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel(f"❌ Widget hiba: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_layout.addWidget(error_label)
            return error_widget

    def _create_statistic_card(self, title: str, items: List[str]) -> QWidget:
        """📋 EGYEDI STATISZTIKA KÁRTYA LÉTREHOZÁSA."""
        card = QWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # Cím
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #C43939;
                margin-bottom: 3px;
            }
        """)
        layout.addWidget(title_label)

        # Elválasztó vonal
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #ddd;")
        layout.addWidget(separator)

        # Adatok
        for item in items:
            item_label = QLabel(item)
            item_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #333;
                    padding-left: 4px;
                    line-height: 1.5;
                }
            """)
            layout.addWidget(item_label)

        # Kártya styling
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin: 2px;
            }
        """)

        return card
