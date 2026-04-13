#!/usr/bin/env python3
# mypy: ignore-errors

"""
Universal Location Selector - Location Card

🎨 Kiválasztott lokáció megjelenítő kártya

Képességek:
- Lokáció név és részletek megjelenítése
- Magyar flag (🇭🇺) és globális flag (🌍) támogatás
- Hover effekt és modern stílus

Fájl: src/presentation/gui/universal_location_selector/location_card.py
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QLabel, QSizePolicy, QVBoxLayout


class LocationCard(QFrame):
    """🎨 Kiválasztott lokáció megjelenítő kártya - MAGYAR KOMPATIBILIS"""

    def __init__(self, parent=None):  # noqa: D107
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setMinimumHeight(80)
        self.setMaximumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        # Cím
        self.title_label = QLabel("Nincs kiválasztva")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)

        # Részletek
        self.details_label = QLabel("Válassz egy lokációt a keresésből")
        details_font = QFont()
        details_font.setPointSize(11)
        self.details_label.setFont(details_font)
        self.details_label.setStyleSheet("color: #64748B;")
        self.details_label.setWordWrap(True)
        layout.addWidget(self.details_label)

        # Modern styling
        self.setStyleSheet("""
            LocationCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8FAFC);
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                margin: 4px;
            }
            LocationCard:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F8FAFC, stop:1 #F1F5F9);
                border: 2px solid #CBD5E1;
            }
        """)

    def set_location(self, name: str, details: str, is_hungarian: bool = False) -> None:
        """
        🇭🇺 Lokáció beállítása MAGYAR TÁMOGATÁSSAL

        Args:
            name: Lokáció neve
            details: Részletes leírás
            is_hungarian: Magyar-e a lokáció
        """
        flag = "🇭🇺" if is_hungarian else "🌍"
        self.title_label.setText(f"{flag} {name}")
        self.details_label.setText(details)

    def clear(self) -> None:
        """Kártya törlése"""
        self.title_label.setText("Nincs kiválasztva")
        self.details_label.setText("Válassz egy lokációt a keresésből")
