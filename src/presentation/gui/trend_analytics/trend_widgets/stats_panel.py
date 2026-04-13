#!/usr/bin/env python3
# mypy: ignore-errors
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

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from .stats_card import DashboardStatsCard

logger = logging.getLogger(__name__)


def _resolve_trend_unit(parameter: str) -> str:
    """Resolve trend unit from the selected parameter."""
    lowered = parameter.lower()
    if "hőmérséklet" in lowered:
        return "°C/évtized"
    if "csapadék" in lowered:
        return "mm/évtized"
    if "szél" in lowered:
        return "km/h/évtized"
    return "/évtized"


def _resolve_value_unit(parameter: str) -> str:
    """Resolve value unit from the selected parameter."""
    lowered = parameter.lower()
    if "hőmérséklet" in lowered:
        return "°C"
    if "csapadék" in lowered:
        return "mm"
    if "szél" in lowered:
        return "km/h"
    return ""


def _build_reliability_metadata(r_squared: float) -> tuple[str, str]:
    """Build subtitle and color for reliability KPI."""
    if r_squared > 0.7:  # noqa: PLR2004
        return "Magas megbízhatóság", "#10b981"
    if r_squared > 0.4:  # noqa: PLR2004
        return "Közepes megbízhatóság", "#f59e0b"
    return "Alacsony megbízhatóság", "#ef4444"


def _build_significance_metadata(p_value: float) -> tuple[str, str, str]:
    """Build significance card content."""
    if p_value < 0.001:  # noqa: PLR2004
        return "***", f"p = {p_value:.3f}", "#059669"
    if p_value < 0.01:  # noqa: PLR2004
        return "**", f"p = {p_value:.3f}", "#10b981"
    if p_value < 0.05:  # noqa: PLR2004
        return "*", f"p = {p_value:.3f}", "#f59e0b"
    return "n.s.", f"p = {p_value:.3f}", "#6b7280"


class EnhancedStatisticsPanel(QWidget):
    """
    🎯 DASHBOARD-SZERŰ STATISZTIKÁK PANEL - KPI KÁRTYÁKKAL

    Grid layout-ban jeleníti meg a főbb KPI-ket:
    - Trend változás
    - Megbízhatóság (R²)
    - Szignifikancia
    - Értéktartomány
    """

    def __init__(self):  # noqa: D107
        super().__init__()
        self.stats_cards: dict[str, DashboardStatsCard] = {}  # ELŐBB inicializálni!
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

    def update_statistics(self, trend_data: dict) -> None:
        """
        🎯 KPI KÁRTYÁK FRISSÍTÉSE - DASHBOARD ADATOKKAL

        Args:
            trend_data: TrendDataProcessor eredményei
        """
        try:
            logger.info("🎯 DASHBOARD STATS FRISSÍTÉS KEZDÉSE")
            trend_value = trend_data["trend_per_decade"]
            r2 = trend_data["r_squared"]
            p_val = trend_data["p_value"]
            stats = trend_data["statistics"]
            parameter = trend_data["parameter"]
            cards = self._build_card_updates(parameter, trend_value, r2, p_val, stats)
            for card_key, value, subtitle, color in cards:
                self.update_card(card_key, value, subtitle, color)
            logger.info(f"✅ Dashboard stats frissítve: {len(self.stats_cards)} kártya")

        except Exception as e:
            logger.error(f"❌ Dashboard stats update hiba: {e}")
            logger.exception("Dashboard stats error stacktrace:")
            self.show_error_cards(str(e))

    def _build_card_updates(
        self,
        parameter: str,
        trend_value: float,
        r_squared: float,
        p_value: float,
        stats: dict,
    ) -> list[tuple[str, str, str, str]]:
        """Build KPI card content for a trend update."""
        trend_unit = _resolve_trend_unit(parameter)
        trend_color = "#ef4444" if trend_value < 0 else "#10b981"
        reliability_subtitle, reliability_color = _build_reliability_metadata(r_squared)
        significance_display, significance_subtitle, significance_color = (
            _build_significance_metadata(p_value)
        )
        value_unit = _resolve_value_unit(parameter)
        range_value = stats["max"] - stats["min"]
        range_subtitle = f"{stats['min']:.1f} - {stats['max']:.1f} {value_unit}".strip()
        return [
            ("🎯 Trend", f"{trend_value:+.2f}", trend_unit, trend_color),
            (
                "🎯 Megbízhatóság",
                f"{r_squared:.3f}",
                reliability_subtitle,
                reliability_color,
            ),
            (
                "🎯 Szignifikancia",
                significance_display,
                significance_subtitle,
                significance_color,
            ),
            ("📊 Tartomány", f"{range_value:.1f}", range_subtitle, "#8b5cf6"),
        ]

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

    def show_error_cards(self, error_msg: str) -> None:  # noqa: ARG002
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
