#!/usr/bin/env python3
# mypy: ignore-errors
"""
Interactive Trend Chart Component

🎨 INTERAKTÍV PLOTLY-ALAPÚ TREND CHART KOMPONENS

Képességek:
- Zoom, pan, hover tooltips
- Konfidencia intervallum árnyékolás
- Szezonális színkódolás
- Export funkciók
- Responsive design

Fájl: src/presentation/gui/trend_analytics/trend_widgets/trend_chart.py
"""

import logging

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PySide6.QtWidgets import QTextBrowser, QVBoxLayout, QWidget

from src.presentation.gui.runtime_environment import is_headless_qt_platform

logger = logging.getLogger(__name__)


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

    def __init__(self):  # noqa: D107
        super().__init__()
        self.trend_data: dict | None = None
        self.setup_chart()

    def setup_chart(self) -> None:
        """Plotly chart widget inicializálása"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = self._create_html_view()
        self.web_view.setMinimumHeight(500)

        layout.addWidget(self.web_view)
        self.setLayout(layout)

        # Kezdeti üres chart
        self.show_placeholder()

        logger.info("✅ InteractiveTrendChart inicializálva")

    def _create_html_view(self) -> QWidget:
        """Create a WebEngine view unless the process runs headless."""
        if is_headless_qt_platform():
            view = QTextBrowser()
            view.setOpenExternalLinks(True)
            return view

        from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: PLC0415

        return QWebEngineView()

    def show_placeholder(self) -> None:
        """Placeholder chart megjelenítése"""
        fig = go.Figure()

        fig.add_annotation(
            x=0.5,
            y=0.5,
            text="📈 Válassz paramétert és indítsd el a trend elemzést!",
            xref="paper",
            yref="paper",
            showarrow=False,
            font={"size": 16, "color": "#6b7280"},
        )

        fig.update_layout(
            title="Trend Elemzés",
            xaxis={"visible": False},
            yaxis={"visible": False},
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=500,
        )

        html_content = fig.to_html(include_plotlyjs="cdn")
        self.web_view.setHtml(html_content)

    def update_chart(self, trend_data: dict) -> None:
        """
        🎨 TREND CHART FRISSÍTÉSE PLOTLY-VAL

        Args:
            trend_data: TrendDataProcessor által számított eredmények
        """
        try:
            self.trend_data = trend_data
            logger.info(f"📊 PLOTLY CHART UPDATE: {trend_data['settlement_name']}")

            # Adatok kinyerése
            chart_data = trend_data["chart_data"]
            dates = pd.to_datetime(chart_data["dates"])
            values = np.array(chart_data["values"])
            trend_line = np.array(chart_data["trend_line"])
            ci_upper = np.array(chart_data["ci_upper"])
            ci_lower = np.array(chart_data["ci_lower"])

            # Plotly figure létrehozása
            fig = go.Figure()

            # 🎨 95% KONFIDENCIA INTERVALLUM (árnyékolt terület)
            # 🔧 JAVÍTÁS v4.2: pandas DatetimeIndex lista konverzió
            dates_list = dates.to_list()  # Konvertálás listává
            fig.add_trace(
                go.Scatter(
                    x=dates_list + dates_list[::-1],  # Egyszerű lista összefűzés
                    y=np.concatenate([ci_upper, ci_lower[::-1]]),
                    fill="toself",
                    fillcolor="rgba(128, 128, 128, 0.2)",
                    line={"color": "rgba(255,255,255,0)"},
                    name="95% konfidencia",
                    hoverinfo="skip",
                )
            )

            # 📊 HAVI ÁTLAG ADATOK (interaktív pontok)
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=values,
                    mode="markers+lines",
                    name="Havi átlag",
                    line={"color": "#ff6b35", "width": 3},
                    marker={"size": 6, "color": "#ff6b35", "line": {"width": 2, "color": "white"}},
                    hovertemplate="<b>%{x|%Y-%m}</b><br>"
                    + f"{trend_data['parameter']}: %{{y:.1f}}<br>"  # 🔧 JAVÍTÁS: dupla {{ }} a Plotly formázáshoz
                    + "<extra></extra>",
                )
            )

            # 📈 LINEÁRIS TREND VONAL
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=trend_line,
                    mode="lines",
                    name=f"Trend ({trend_data['trend_per_decade']:+.2f}/évtized)",
                    line={"color": "#ff1493", "width": 3, "dash": "dash"},
                    hovertemplate="<b>Trend vonal</b><br>"
                    + "%{{x|%Y-%m}}: %{{y:.1f}}<br>"  # 🔧 JAVÍTÁS: dupla {{ }} a Plotly formázáshoz
                    + "<extra></extra>",
                )
            )

            # 🎨 PROFESSIONAL LAYOUT STYLING
            settlement = trend_data["settlement_name"]
            parameter = trend_data["parameter"]
            time_range = trend_data["time_range"]
            r2 = trend_data["r_squared"]
            significance = trend_data["significance"]

            # Y tengely címke paraméter alapján
            if "hőmérséklet" in parameter.lower():
                y_title = "Hőmérséklet (°C)"
            elif "csapadék" in parameter.lower():
                y_title = "Csapadék (mm)"
            elif "szél" in parameter.lower():
                y_title = "Szélsebesség (km/h)"
            else:
                y_title = "Érték"

            fig.update_layout(
                title={
                    "text": f"📈 {settlement} - {parameter} trend elemzés ({time_range})<br>"
                    + f"<sub>R² = {r2:.3f} | {significance} | {trend_data['total_days']:,} nap</sub>",
                    "font": {"size": 16},
                    "x": 0.5,
                },
                xaxis={"title": "Dátum", "gridcolor": "#e5e7eb", "showgrid": True},
                yaxis={"title": y_title, "gridcolor": "#e5e7eb", "showgrid": True},
                plot_bgcolor="white",
                paper_bgcolor="white",
                font={"family": "Arial, sans-serif", "size": 12},
                legend={
                    "orientation": "h",
                    "yanchor": "bottom",
                    "y": 1.02,
                    "xanchor": "right",
                    "x": 1,
                },
                hovermode="x unified",
                height=500,
            )

            # Interaktív konfiguráció
            config = {
                "displayModeBar": True,
                "modeBarButtonsToAdd": [
                    "drawline",
                    "drawopenpath",
                    "drawclosedpath",
                    "drawcircle",
                    "drawrect",
                    "eraseshape",
                ],
                "toImageButtonOptions": {
                    "format": "png",
                    "filename": f"trend_analysis_{settlement}_{parameter}",
                    "height": 600,
                    "width": 1000,
                    "scale": 2,
                },
            }

            # HTML generálása és megjelenítése
            html_content = fig.to_html(include_plotlyjs="cdn", config=config)
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
            x=0.5,
            y=0.5,
            text=f"❌ Hiba történt:<br>{error_message}",
            xref="paper",
            yref="paper",
            showarrow=False,
            font={"size": 14, "color": "#dc2626"},
        )

        fig.update_layout(
            title="Trend Elemzés - Hiba",
            xaxis={"visible": False},
            yaxis={"visible": False},
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=500,
        )

        html_content = fig.to_html(include_plotlyjs="cdn")
        self.web_view.setHtml(html_content)
