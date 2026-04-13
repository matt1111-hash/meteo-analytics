#!/usr/bin/env python3
# mypy: ignore-errors
"""
Dashboard Stats Card Component

🎯 KPI KÁRTYA KOMPONENS - QPALETTE-ALAPÚ ROBUSZTUS FRISSÍTÉS

Képességek:
- KPI kártya megjelenítése (cím, érték, alcím)
- QPalette-alapú színkezelés
- Ikon/emoji támogatás

Fájl: src/presentation/gui/trend_analytics/trend_widgets/stats_card.py
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout


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

    def __init__(
        self,
        title: str,
        value: str,
        subtitle: str = "",
        color: str = "#3b82f6",
        icon: str = "📊",
    ):
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

        # Header (ikon + cím)  # noqa: ERA001
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
