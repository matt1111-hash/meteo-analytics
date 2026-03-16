# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for HungarianCityUIBuilder."""

from __future__ import annotations

from .ui_builder_support import *


class HungarianCityUIBuilderPart2Mixin:
    def create_quick_access_section(self, city_callback: Callable) -> QGroupBox:
        """Gyors hozzáférés szakasz létrehozása."""
        group = QGroupBox("⚡ Gyors hozzáférés - Nagy magyar városok")
        layout = QGridLayout(group)
        layout.setSpacing(6)

        # Népszerű magyar városok
        quick_cities = [
            ("🏛️ Budapest", "Budapest", "Főváros - 1.7M lakos"),
            ("🌾 Debrecen", "Debrecen", "Cívisváros - 201k lakos"),
            ("🏭 Miskolc", "Miskolc", "Észak-Magyarország - 161k lakos"),
            ("🌊 Szeged", "Szeged", "Tisza-parti egyetemváros - 161k lakos"),
            ("⚙️ Pécs", "Pécs", "Dunántúli kulturális központ - 143k lakos"),
            ("🌍 Győr", "Győr", "Kisalföld központja - 129k lakos"),
            ("🏔️ Székesfehérvár", "Székesfehérvár", "Fejér megye székhelye - 95k lakos"),
            ("⛰️ Nyíregyháza", "Nyíregyháza", "Szabolcs-Szatmár-Bereg - 118k lakos"),
            ("🍇 Kecskemét", "Kecskemét", "Bács-Kiskun megye - 109k lakos"),
            ("🌲 Szombathely", "Szombathely", "Vas megye székhelye - 76k lakos"),
            ("💎 Veszprém", "Veszprém", "Balaton-felvidék - 57k lakos"),
            ("🍷 Kaposvár", "Kaposvár", "Somogy megye székhelye - 63k lakos"),
        ]

        self.quick_access_buttons = []

        for i, (display, city, tooltip) in enumerate(quick_cities):
            btn = QPushButton(display)
            btn.setToolTip(tooltip)
            btn.setMinimumHeight(35)
            btn.clicked.connect(lambda checked, c=city: city_callback(c))

            # Rács elrendezés: 3 város per sor
            row = i // 3
            col = i % 3
            layout.addWidget(btn, row, col)

            self.quick_access_buttons.append(btn)

        return group

    def create_statistics_section(self) -> QGroupBox:
        """Statisztikák szakasz létrehozása."""
        group = QGroupBox("📊 Statisztikák")
        layout = QVBoxLayout(group)
        layout.setSpacing(4)

        self.stats_label = QLabel("Városok betöltése...")
        self.stats_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.stats_label)

        return group

    def populate_city_list(self, cities: List[HungarianCity]) -> None:
        """Városok lista feltöltése."""
        if not self.city_list:
            return

        self.city_list.clear()

        for city in cities:
            # Lista elem szöveg
            population_text = f"{city.population:,}" if city.population else "n/a"
            region_text = city.region or "Egyéb"

            item_text = f"🏙️ {city.city} ({population_text} fő) - {region_text}"

            # Lista elem létrehozása
            item = QListWidgetItem(item_text)

            # Tooltip részletes információkkal
            tooltip = f"""
            Város: {city.city}
            Régió: {region_text}
            Népesség: {population_text} fő
            Koordináták: {city.lat:.4f}, {city.lon:.4f}
            Megye: {city.admin_name or "n/a"}
            Adatminőség: {city.data_quality_score or "n/a"}
            """
            item.setToolTip(tooltip.strip())

            # City objektum tárolása
            item.setData(Qt.UserRole, city)

            self.city_list.addItem(item)

        logger.debug(f"🏙️ {len(cities)} város megjelenítve a listában")

    def update_stats(self, stats_text: str) -> None:
        """Statisztikák szöveg frissítése."""
        if self.stats_label:
            self.stats_label.setText(stats_text)

    def get_current_region(self) -> str:
        """Jelenlegi régió lekérdezése."""
        if not self.region_combo:
            return "Összes"
        current_data = self.region_combo.currentData()
        return current_data if current_data else "Összes"

    def set_region(self, region: str) -> None:
        """Régió programozott beállítása."""
        if self.region_combo:
            for i in range(self.region_combo.count()):
                if self.region_combo.itemData(i) == region:
                    self.region_combo.setCurrentIndex(i)
                    break

    def set_search_term(self, search_term: str) -> None:
        """Keresési kifejezés programozott beállítása."""
        if self.search_box:
            self.search_box.setText(search_term)

    def clear_search_box(self) -> None:
        """Keresőmező törlése."""
        if self.search_box:
            self.search_box.clear()
