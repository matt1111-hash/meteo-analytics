#!/usr/bin/env python3
"""
Enhanced Statistics Panel Component

🎯 DASHBOARD-SZERŰ STATISZTIKÁK PANEL - KPI KÁRTYÁKKAL

Képességek:
- Grid layout alapú KPI kártyák elrendezése
- Trend adatok alapján történő frissítés
- Hiba kezelése és placeholder kártyák

Fájl: src/presentation/gui/trend_analytics/trend_widgets/stats_panel.py
"""

import logging
from typing import Dict

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from .stats_card import DashboardStatsCard

logger = logging.getLogger(__name__)


class EnhancedStatisticsPanel(QWidget):
    """
    🎯 DASHBOARD-SZERŰ STATISZTIKÁK PANEL - KPI KÁRTYÁKKAL

    Grid layout-ban jeleníti meg a főbb KPI-ket:
    - Trend változás
    - Megbízhatóság (R²)
    - Szignifikancia
    - Értéktartomány
    """

    def __init__(self):
        super().__init__()
        self.stats_cards: Dict[str, DashboardStatsCard] = {}  # ELŐBB inicializálni!
        self.setup_stats_panel()

    def setup_stats_panel(self) -> None:
        """Statisztikák panel UI beállítása"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Panel cím
        title_label = QLabel("📊 Trend Mutatók")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #1f2937; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # KPI kártyák grid-je
        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(10)

        layout.addLayout(self.cards_grid)
        layout.addStretch()

        self.setLayout(layout)

        # Placeholder kártyák
        self.show_placeholder_cards()

        logger.info("✅ EnhancedStatisticsPanel inicializálva")

    def show_placeholder_cards(self) -> None:
        """Placeholder KPI kártyák megjelenítése"""
        placeholder_cards = [
            ("🎯 Trend", "Nincs adat", "per évtized", "#3b82f6", "📈"),
            ("🎯 Megbízhatóság", "Nincs adat", "R² érték", "#10b981", "🎯"),
            ("🎯 Szignifikancia", "Nincs adat", "statisztikai", "#f59e0b", "⚡"),
            ("📊 Tartomány", "Nincs adat", "min - max", "#8b5cf6", "📊"),
        ]

        for i, (title, value, subtitle, color, icon) in enumerate(placeholder_cards):
            card = DashboardStatsCard(title, value, subtitle, color, icon)
            row, col = divmod(i, 2)
            self.cards_grid.addWidget(card, row, col)
            self.stats_cards[title] = card

    def update_statistics(self, trend_data: Dict) -> None:
        """
        🎯 KPI KÁRTYÁK FRISSÍTÉSE - DASHBOARD ADATOKKAL

        Args:
            trend_data: TrendDataProcessor eredményei
        """
        try:
            logger.info("🎯 DASHBOARD STATS FRISSÍTÉS KEZDÉSE")

            # 1. TREND VÁLTOZÁS KÁRTYA
            trend_value = trend_data["trend_per_decade"]
            if "hőmérséklet" in trend_data["parameter"].lower():
                trend_unit = "°C/évtized"
            elif "csapadék" in trend_data["parameter"].lower():
                trend_unit = "mm/évtized"
            elif "szél" in trend_data["parameter"].lower():
                trend_unit = "km/h/évtized"
            else:
                trend_unit = "/évtized"

            trend_display = f"{trend_value:+.2f}"
            trend_subtitle = f"{trend_unit}"

            # 2. MEGBÍZHATÓSÁG (R²) KÁRTYA
            r2 = trend_data["r_squared"]
            if r2 > 0.7:
                reliability_level = "Magas"
                r2_color = "#10b981"  # zöld
            elif r2 > 0.4:
                reliability_level = "Közepes"
                r2_color = "#f59e0b"  # sárga
            else:
                reliability_level = "Alacsony"
                r2_color = "#ef4444"  # piros

            r2_display = f"{r2:.3f}"
            r2_subtitle = f"{reliability_level} megbízhatóság"

            # 3. SZIGNIFIKANCIA KÁRTYA
            p_val = trend_data["p_value"]

            if p_val < 0.001:
                sig_display = "***"
                sig_color = "#059669"  # sötét zöld
            elif p_val < 0.01:
                sig_display = "**"
                sig_color = "#10b981"  # zöld
            elif p_val < 0.05:
                sig_display = "*"
                sig_color = "#f59e0b"  # sárga
            else:
                sig_display = "n.s."
                sig_color = "#6b7280"  # szürke

            sig_subtitle = f"p = {p_val:.3f}"

            # 4. ÉRTÉKTARTOMÁNY KÁRTYA
            stats = trend_data["statistics"]
            if "hőmérséklet" in trend_data["parameter"].lower():
                unit = "°C"
            elif "csapadék" in trend_data["parameter"].lower():
                unit = "mm"
            elif "szél" in trend_data["parameter"].lower():
                unit = "km/h"
            else:
                unit = ""

            range_value = stats["max"] - stats["min"]
            range_display = f"{range_value:.1f}"
            range_subtitle = f"{stats['min']:.1f} - {stats['max']:.1f} {unit}"

            # KÁRTYÁK FRISSÍTÉSE

            # Trend kártya frissítése (színkódolással)
            trend_color = (
                "#ef4444" if trend_value < 0 else "#10b981"
            )  # piros ha csökken, zöld ha nő
            self.update_card("🎯 Trend", trend_display, trend_subtitle, trend_color)

            # Megbízhatóság kártya
            self.update_card("🎯 Megbízhatóság", r2_display, r2_subtitle, r2_color)

            # Szignifikancia kártya
            self.update_card("🎯 Szignifikancia", sig_display, sig_subtitle, sig_color)

            # Tartomány kártya
            self.update_card("📊 Tartomány", range_display, range_subtitle, "#8b5cf6")

            logger.info(f"✅ Dashboard stats frissítve: {len(self.stats_cards)} kártya")

        except Exception as e:
            logger.error(f"❌ Dashboard stats update hiba: {e}")
            logger.exception("Dashboard stats error stacktrace:")
            self.show_error_cards(str(e))

    def update_card(self, card_key: str, value: str, subtitle: str, color: str) -> None:
        """
        ✅ EGYSZERŰSÍTETT KÁRTYA FRISSÍTÉS - Tartalom frissítése widget csere helyett

        Args:
            card_key: Kártya azonosító
            value: Új fő érték
            subtitle: Új alcím
            color: Új téma szín
        """
        card_widget = self.stats_cards.get(card_key)
        if card_widget:
            # 🔧 JAVÍTÁS: Widget csere helyett tartalom frissítése
            card_widget.update_contents(value, subtitle, color)
            logger.debug(f"✅ Kártya frissítve: {card_key} = {value}")
        else:
            logger.warning(f"⚠️ Nem található kártya a frissítéshez: '{card_key}'")

    def show_error_cards(self, error_msg: str) -> None:
        """
        ✅ EGYSZERŰSÍTETT HIBA KÁRTYÁK - Tartalom frissítése widget csere helyett

        Args:
            error_msg: Hiba üzenet
        """
        error_cards_data = [
            ("🎯 Trend", "Hiba", "számítási hiba", "#ef4444"),
            ("🎯 Megbízhatóság", "Hiba", "számítási hiba", "#ef4444"),
            ("🎯 Szignifikancia", "Hiba", "számítási hiba", "#ef4444"),
            ("📊 Tartomány", "Hiba", "számítási hiba", "#ef4444"),
        ]

        for card_key, value, subtitle, color in error_cards_data:
            if card_key in self.stats_cards:
                # 🔧 JAVÍTÁS: Widget csere helyett tartalom frissítése
                self.stats_cards[card_key].update_contents(value, subtitle, color)
                logger.debug(f"❌ Hiba kártya frissítve: {card_key}")
