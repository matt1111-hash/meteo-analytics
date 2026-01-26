#!/usr/bin/env python3
"""
Trend Widgets Module

🎨 Dashboard widget components for trend analytics visualization

Képességek:
- DashboardStatsCard: KPI kártya komponens
- InteractiveTrendChart: Plotly-alapú interaktív chart
- EnhancedStatisticsPanel: Dashboard layout statisztikákhoz

Fájl: src/presentation/gui/trend_analytics/trend_widgets.py
"""

import logging
from typing import Dict, Optional
import numpy as np
import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objects as go

# Logging beállítás
logger = logging.getLogger(__name__)


class DashboardStatsCard(QFrame):
    """
    🎯 KPI KÁRTYA KOMPONENS - QPALETTE-ALAPÚ ROBUSZTUS FRISSÍTÉS

    Egy adott metrikát jelenít meg kártya formátumban:
    - Nagy érték szám
    - Leírás
    - Színkódolás (QPalette-tel)
    - Ikon/emoji
    - ✅ QPalette-alapú konfliktusmentes színfrissítés
    """

    def __init__(self, title: str, value: str, subtitle: str = "",
                 color: str = "#3b82f6", icon: str = "📊"):
        """
        KPI kártya inicializálása QPalette-alapú frissítési képességgel

        Args:
            title: Kártya címe
            value: Fő érték (nagy betűvel)
            subtitle: Alcím/magyarázat
            color: Téma szín
            icon: Emoji ikon
        """
        super().__init__()

        # 🔧 JAVÍTÁS: Label-ek és metaadatok osztály tagváltozóként
        self.title_text = title
        self.icon_text = icon
        self.title_label = None
        self.value_label = None
        self.subtitle_label = None
        self.icon_label = None

        self.setup_card_ui(title, icon)
        self.update_contents(value, subtitle, color)

    def setup_card_ui(self, title: str, icon: str) -> None:
        """
        🔧 CSAK EGYSZER: UI elemek létrehozása fix tulajdonságokkal

        Ebben a metódusban CSAK az elrendezést és a fix tulajdonságokat állítjuk be.
        A színeket és a tartalmat az update_contents() fogja kezelni.
        """
        # Frame alapbeállítások
        self.setFrameStyle(QFrame.Box)
        self.setMinimumSize(180, 140)
        self.setMaximumSize(220, 160)

        # Layout
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header (ikon + cím)
        header_layout = QHBoxLayout()

        self.icon_label = QLabel(icon)
        self.icon_label.setFont(QFont("Arial", 20))
        header_layout.addWidget(self.icon_label)

        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 11, QFont.Bold))
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Fő érték
        self.value_label = QLabel("--")  # Placeholder
        value_font = QFont("Arial", 24, QFont.Bold)
        self.value_label.setFont(value_font)
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)

        # Alcím
        self.subtitle_label = QLabel("--")  # Placeholder
        self.subtitle_label.setFont(QFont("Arial", 9))
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        layout.addWidget(self.subtitle_label)

        self.setLayout(layout)

    def update_contents(self, value: str, subtitle: str, color: str) -> None:
        """
        ✅ QPALETTE-ALAPÚ ROBUSZTUS FRISSÍTÉS

        A setStyleSheet konfliktusos működése helyett a Qt natív
        QPalette mechanizmusát használjuk a színek beállítására.

        Args:
            value: Új fő érték
            subtitle: Új alcím
            color: Új téma szín (hex formátum, pl. "#3b82f6")
        """
        # 1. TARTALOM FRISSÍTÉSE (ez eddig is jó volt)
        if self.value_label:
            self.value_label.setText(value)
        if self.subtitle_label:
            self.subtitle_label.setText(subtitle)

        # 2. KERET STÍLUS FRISSÍTÉSE (csak a szülő frame-hez)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 2px solid {color};
                border-radius: 12px;
            }}
        """)

        # 3. SZÖVEG SZÍNEK FRISSÍTÉSE QPALETTE-TEL (KONFLIKTUSMENTES)
        qcolor = QColor(color)

        # Title label színe
        if self.title_label:
            title_palette = self.title_label.palette()
            title_palette.setColor(QPalette.WindowText, qcolor)
            self.title_label.setPalette(title_palette)

        # Value label színe (fő érték)
        if self.value_label:
            value_palette = self.value_label.palette()
            value_palette.setColor(QPalette.WindowText, qcolor)
            self.value_label.setPalette(value_palette)

        # Subtitle label színe (szürke marad)
        if self.subtitle_label:
            subtitle_palette = self.subtitle_label.palette()
            subtitle_palette.setColor(QPalette.WindowText, QColor("#6b7280"))  # Mindig szürke
            self.subtitle_label.setPalette(subtitle_palette)

        # Icon label nem változik (emoji)

    def update_value(self, new_value: str) -> None:
        """Backward compatibility - csak érték frissítése"""
        if self.value_label:
            self.value_label.setText(new_value)


class InteractiveTrendChart(QWidget):
    """
    🎨 INTERAKTÍV PLOTLY-ALAPÚ TREND CHART KOMPONENS

    Képességek:
    - Zoom, pan, hover tooltips
    - Konfidencia intervallum árnyékolás
    - Szezonális színkódolás
    - Export funkciók
    - Responsive design
    """

    def __init__(self):
        super().__init__()
        self.trend_data: Optional[Dict] = None
        self.setup_chart()

    def setup_chart(self) -> None:
        """Plotly chart widget inicializálása"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # QWebEngineView a Plotly HTML megjelenítéshez
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(500)

        layout.addWidget(self.web_view)
        self.setLayout(layout)

        # Kezdeti üres chart
        self.show_placeholder()

        logger.info("✅ InteractiveTrendChart inicializálva")

    def show_placeholder(self) -> None:
        """Placeholder chart megjelenítése"""
        fig = go.Figure()

        fig.add_annotation(
            x=0.5, y=0.5,
            text="📈 Válassz paramétert és indítsd el a trend elemzést!",
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=16, color="#6b7280")
        )

        fig.update_layout(
            title="Trend Elemzés",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=500
        )

        html_content = fig.to_html(include_plotlyjs='cdn')
        self.web_view.setHtml(html_content)

    def update_chart(self, trend_data: Dict) -> None:
        """
        🎨 TREND CHART FRISSÍTÉSE PLOTLY-VAL

        Args:
            trend_data: TrendDataProcessor által számított eredmények
        """
        try:
            self.trend_data = trend_data
            logger.info(f"📊 PLOTLY CHART UPDATE: {trend_data['settlement_name']}")

            # Adatok kinyerése
            chart_data = trend_data['chart_data']
            dates = pd.to_datetime(chart_data['dates'])
            values = np.array(chart_data['values'])
            trend_line = np.array(chart_data['trend_line'])
            ci_upper = np.array(chart_data['ci_upper'])
            ci_lower = np.array(chart_data['ci_lower'])

            # Plotly figure létrehozása
            fig = go.Figure()

            # 🎨 95% KONFIDENCIA INTERVALLUM (árnyékolt terület)
            # 🔧 JAVÍTÁS v4.2: pandas DatetimeIndex lista konverzió
            dates_list = dates.to_list()  # Konvertálás listává
            fig.add_trace(go.Scatter(
                x=dates_list + dates_list[::-1],  # Egyszerű lista összefűzés
                y=np.concatenate([ci_upper, ci_lower[::-1]]),
                fill='toself',
                fillcolor='rgba(128, 128, 128, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='95% konfidencia',
                hoverinfo='skip'
            ))

            # 📊 HAVI ÁTLAG ADATOK (interaktív pontok)
            fig.add_trace(go.Scatter(
                x=dates,
                y=values,
                mode='markers+lines',
                name='Havi átlag',
                line=dict(color='#ff6b35', width=3),
                marker=dict(
                    size=6,
                    color='#ff6b35',
                    line=dict(width=2, color='white')
                ),
                hovertemplate='<b>%{x|%Y-%m}</b><br>' +
                             f'{trend_data["parameter"]}: %{{y:.1f}}<br>' +  # 🔧 JAVÍTÁS: dupla {{ }} a Plotly formázáshoz
                             '<extra></extra>'
            ))

            # 📈 LINEÁRIS TREND VONAL
            fig.add_trace(go.Scatter(
                x=dates,
                y=trend_line,
                mode='lines',
                name=f'Trend ({trend_data["trend_per_decade"]:+.2f}/évtized)',
                line=dict(color='#ff1493', width=3, dash='dash'),
                hovertemplate='<b>Trend vonal</b><br>' +
                             '%{{x|%Y-%m}}: %{{y:.1f}}<br>' +  # 🔧 JAVÍTÁS: dupla {{ }} a Plotly formázáshoz
                             '<extra></extra>'
            ))

            # 🎨 PROFESSIONAL LAYOUT STYLING
            settlement = trend_data['settlement_name']
            parameter = trend_data['parameter']
            time_range = trend_data['time_range']
            r2 = trend_data['r_squared']
            significance = trend_data['significance']

            # Y tengely címke paraméter alapján
            if 'hőmérséklet' in parameter.lower():
                y_title = 'Hőmérséklet (°C)'
            elif 'csapadék' in parameter.lower():
                y_title = 'Csapadék (mm)'
            elif 'szél' in parameter.lower():
                y_title = 'Szélsebesség (km/h)'
            else:
                y_title = 'Érték'

            fig.update_layout(
                title=dict(
                    text=f'📈 {settlement} - {parameter} trend elemzés ({time_range})<br>' +
                         f'<sub>R² = {r2:.3f} | {significance} | {trend_data["total_days"]:,} nap</sub>',
                    font=dict(size=16),
                    x=0.5
                ),
                xaxis=dict(
                    title='Dátum',
                    gridcolor='#e5e7eb',
                    showgrid=True
                ),
                yaxis=dict(
                    title=y_title,
                    gridcolor='#e5e7eb',
                    showgrid=True
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                hovermode='x unified',
                height=500
            )

            # Interaktív konfiguráció
            config = {
                'displayModeBar': True,
                'modeBarButtonsToAdd': [
                    'drawline',
                    'drawopenpath',
                    'drawclosedpath',
                    'drawcircle',
                    'drawrect',
                    'eraseshape'
                ],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'trend_analysis_{settlement}_{parameter}',
                    'height': 600,
                    'width': 1000,
                    'scale': 2
                }
            }

            # HTML generálása és megjelenítése
            html_content = fig.to_html(include_plotlyjs='cdn', config=config)
            self.web_view.setHtml(html_content)

            logger.info("✅ Plotly chart successfully updated")

        except Exception as e:
            logger.error(f"❌ Plotly chart update hiba: {e}")
            logger.exception("Plotly chart error stacktrace:")
            self.show_error_chart(str(e))

    def show_error_chart(self, error_message: str) -> None:
        """Hiba chart megjelenítése"""
        fig = go.Figure()

        fig.add_annotation(
            x=0.5, y=0.5,
            text=f"❌ Hiba történt:<br>{error_message}",
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=14, color="#dc2626")
        )

        fig.update_layout(
            title="Trend Elemzés - Hiba",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=500
        )

        html_content = fig.to_html(include_plotlyjs='cdn')
        self.web_view.setHtml(html_content)


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
            ("📊 Tartomány", "Nincs adat", "min - max", "#8b5cf6", "📊")
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
            trend_value = trend_data['trend_per_decade']
            if 'hőmérséklet' in trend_data['parameter'].lower():
                trend_unit = "°C/évtized"
            elif 'csapadék' in trend_data['parameter'].lower():
                trend_unit = "mm/évtized"
            elif 'szél' in trend_data['parameter'].lower():
                trend_unit = "km/h/évtized"
            else:
                trend_unit = "/évtized"

            trend_display = f"{trend_value:+.2f}"
            trend_subtitle = f"{trend_unit}"

            # 2. MEGBÍZHATÓSÁG (R²) KÁRTYA
            r2 = trend_data['r_squared']
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

            # 3. SZIGNIFIKANCIA KÁRTJA
            significance = trend_data['significance']
            p_val = trend_data['p_value']

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
            stats = trend_data['statistics']
            if 'hőmérséklet' in trend_data['parameter'].lower():
                unit = "°C"
            elif 'csapadék' in trend_data['parameter'].lower():
                unit = "mm"
            elif 'szél' in trend_data['parameter'].lower():
                unit = "km/h"
            else:
                unit = ""

            range_value = stats['max'] - stats['min']
            range_display = f"{range_value:.1f}"
            range_subtitle = f"{stats['min']:.1f} - {stats['max']:.1f} {unit}"

            # KÁRTYÁK FRISSÍTÉSE

            # Trend kártya frissítése (színkódolással)
            trend_color = "#ef4444" if trend_value < 0 else "#10b981"  # piros ha csökken, zöld ha nő
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
            ("📊 Tartomány", "Hiba", "számítási hiba", "#ef4444")
        ]

        for card_key, value, subtitle, color in error_cards_data:
            if card_key in self.stats_cards:
                # 🔧 JAVÍTÁS: Widget csere helyett tartalom frissítése
                self.stats_cards[card_key].update_contents(value, subtitle, color)
                logger.debug(f"❌ Hiba kártya frissítve: {card_key}")
