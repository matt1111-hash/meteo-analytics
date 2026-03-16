# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for AnalyticsView."""

from __future__ import annotations

from .core_support import *


class AnalyticsViewPart2Mixin:
    def update_with_multi_city_result(self, result: "AnalyticsResult"):
        """
        ✅ ÚJ: Frissíti a nézetet a MainWindow-tól kapott elemzési eredménnyel.
        """
        logger.info(
            f"✅ ANALYTICS_VIEW: Eredmény fogadva a MainWindow-tól: {len(result.city_results) if result and result.city_results else 0} város."
        )

        try:
            if not result or not result.city_results:
                self._update_status("❌ Nincs Multi-City eredmény")
                return

            # Fake single-city data létrehozása a heatmap-ekhez
            fake_data = (
                self.multi_city_handler.create_fake_single_city_data_from_multi_city(
                    result
                )
            )

            # Heatmap-ek frissítése
            if self.climate_tabs and fake_data:
                self.climate_tabs.update_data(fake_data)

            # Fake rekordok (Multi-City eredményekből)
            fake_records = self.multi_city_handler.create_fake_records_from_multi_city(
                result
            )
            if self.record_summary:
                self.record_summary.update_records(fake_records)

            # Status frissítése
            self._update_status(
                f"✅ Multi-City eredmény feldolgozva: {len(result.city_results)} város"
            )

            logger.info(
                f"✅ Multi-City result processed in AnalyticsView: {len(result.city_results)} cities"
            )

        except Exception as e:
            logger.error(f"❌ Multi-City result processing error: {e}")
            self._update_status(f"❌ Multi-City eredmény feldolgozási hiba: {e}")
            self.error_occurred.emit(f"Multi-City eredmény hiba: {e}")

    def clear_data(self) -> None:
        """Adatok törlése és UI visszaállítása."""
        logger.info(
            "Konstans heatmap dashboard + DEDICATED WIND CHARTOK adatok törlése"
        )

        self.current_data = None
        self.current_location = None

        # UI visszaállítása
        self.location_info_label.setText("Nincs kiválasztott lokáció")

        # Statisztikák törlése
        stats_content = QLabel("Töltse be az adatokat")
        stats_content.setAlignment(Qt.AlignCenter)
        stats_content.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 20px;
                font-size: 12px;
            }
        """)
        self.statistics_area.setWidget(stats_content)

        self._update_status(
            "Válasszon lokációt a bal oldali panelen vagy használja a Régió Elemzést"
        )

    def on_location_changed(self, location) -> None:
        """Lokáció változás kezelése."""
        try:
            logger.info(f"Konstans heatmap dashboard lokáció változás: {location}")
            self.current_location = location

            # Lokáció info frissítése
            if hasattr(location, "display_name"):
                display_name = location.display_name
                coords = location.coordinates
            elif isinstance(location, dict):
                display_name = location.get("name", "Ismeretlen")
                lat = location.get("latitude", 0.0)
                lon = location.get("longitude", 0.0)
                coords = (lat, lon)
            else:
                display_name = str(location)
                coords = (0.0, 0.0)

            if coords:
                location_text = (
                    f"📍 {display_name}\n🗺️ [{coords[0]:.3f}, {coords[1]:.3f}]"
                )
            else:
                location_text = f"📍 {display_name}"

            self.location_info_label.setText(location_text)
            self._update_status(f"Lokáció beállítva: {display_name}")

        except Exception as e:
            logger.error(f"Lokció változás hiba: {e}")
            self.error_occurred.emit(f"Lokció hiba: {str(e)}")

    def on_analysis_start(self) -> None:
        """Elemzés indítása."""
        logger.info(
            "Konstans heatmap dashboard + DEDICATED WIND CHARTOK elemzés indítása"
        )
        self.analysis_started.emit()
        self._update_status(
            "⏳ Konstans heatmap dashboard + DEDICATED WIND CHARTOK elemzés folyamatban..."
        )

    def _update_status(self, message: str) -> None:
        """Állapot üzenet frissítése."""
        if self.status_label:
            self.status_label.setText(message)
        logger.info(
            f"Konstans heatmap dashboard + DEDICATED WIND CHARTOK állapot: {message}"
        )

    # === TÉMA API ===

    def update_theme(self) -> None:
        """Téma manuális frissítése."""
        self._apply_current_theme()

    def get_current_data(self) -> Optional[Dict[str, Any]]:
        """Jelenlegi adatok lekérdezése."""
        return self.current_data

    def get_current_location(self):
        """Jelenlegi lokáció lekérdezése."""
        return self.current_location
