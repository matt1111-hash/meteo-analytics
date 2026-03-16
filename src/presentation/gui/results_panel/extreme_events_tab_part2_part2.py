# ruff: noqa: F401,F403,F405,I001
# mypy: ignore-errors
"""Mixin part 2 for ExtremeEventsTab."""

from __future__ import annotations

from .extreme_events_tab_part2_support import *


class ExtremeEventsTabPart2Mixin:
    def update_data(self, data: Dict[str, Any], city_name: str = "") -> None:
        """📊 Adatok frissítése."""
        if not data:
            return
        self.current_data = data

        # Use Case hívása
        try:
            thresholds = self._get_thresholds()
            daily_data = data.get("daily", data)
            anomalies = self.use_case.execute(daily_data, thresholds, city_name)
            self._display_anomalies(anomalies)
        except Exception as e:
            logger.error(f"Hiba az anomália detektálás során: {e}")

        # Rekordok
        if self.extreme_calculator:
            dates = daily_data.get("time", daily_data.get("date", []))
            records = self.extreme_calculator.calculate_records_by_period(
                daily_data, dates, self.period_type
            )
            self._display_records(records)

    def _get_thresholds(self) -> Dict[str, float]:
        """Beállítások lekérése a profil menedzsertől."""
        if self.profile_manager:
            return self.profile_manager.get_current_settings()

        # Fallback
        return {
            "temp_hot": 35.0,
            "temp_cold": -10.0,
            "precip_high": 50.0,
            "precip_low": 5.0,
            "wind_normal": 40.0,
            "wind_strong": 60.0,
            "wind_extreme": 90.0,
            "wind_hurricane": 110.0,
        }

    def _display_anomalies(self, anomalies: Dict[str, Any]) -> None:
        """Eredmények megjelenítése a UI-n."""
        mapping = {
            "temperature": self.temp_anomaly,
            "precipitation": self.precip_anomaly,
            "wind": self.wind_anomaly,
        }

        for cat, label in mapping.items():
            anomaly = anomalies.get(cat)
            if not anomaly:
                self._update_label(label, f"{cat.capitalize()}: Normális", "success")
            else:
                self._update_label(label, anomaly.message, anomaly.severity)

    def _update_label(self, label: Optional[QLabel], text: str, status: str) -> None:
        if not label:
            return
        label.setText(text)
        colors = {
            "success": "#10b981",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "error": "#ef4444",
        }
        color = colors.get(status, "#9ca3af")
        label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _display_records(self, records: List[Any]) -> None:
        if not self.extreme_table:
            return
        self.extreme_table.setRowCount(0)
        for i, rec in enumerate(records):
            self.extreme_table.insertRow(i)
            self.extreme_table.setItem(i, 0, QTableWidgetItem(str(rec.category)))
            self.extreme_table.setItem(i, 1, QTableWidgetItem(str(rec.record_type)))
            self.extreme_table.setItem(i, 2, QTableWidgetItem(str(rec.value)))
            self.extreme_table.setItem(i, 3, QTableWidgetItem(str(rec.date)))

    def _on_anomaly_settings_clicked(self) -> None:
        try:
            from src.presentation.gui.dialogs.anomaly_settings_dialog import (
                AnomalySettingsDialog,
            )

            dialog = AnomalySettingsDialog(self)
            if dialog.exec():
                if self.current_data:
                    self.update_data(self.current_data)
        except Exception as e:
            logger.error(f"Settings dialog error: {e}")

    def _on_period_type_changed(self) -> None:
        if self.daily_radio.isChecked():
            self.period_type = "daily"
        elif self.monthly_radio.isChecked():
            self.period_type = "monthly"
        else:
            self.period_type = "yearly"
        if self.current_data:
            self.update_data(self.current_data)

    def _on_detailed_analysis_clicked(self) -> None:
        QMessageBox.information(self, "Info", "Részletes elemzés hamarosan...")

    def _register_widgets_for_theming(self) -> None:
        try:
            register_widget_for_theming(self, "container")
            register_widget_for_theming(self.title_label, "text")
        except Exception:
            pass
