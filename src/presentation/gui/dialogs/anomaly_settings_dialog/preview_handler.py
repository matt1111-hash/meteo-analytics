#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Anomaly Settings Dialog - Preview Handler Module
Előnézet és teszt logika az AnomalySettingsDialoghoz.
"""

import logging
from typing import TYPE_CHECKING, Dict

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QInputDialog

if TYPE_CHECKING:
    from src.presentation.gui.dialogs.anomaly_settings_dialog.core import (
        AnomalySettingsDialog,
    )


logger = logging.getLogger(__name__)


class AnomalySettingsPreviewHandler:
    """Előnézet és teszt kezelő osztály az AnomalySettingsDialoghoz."""

    def __init__(self, dialog: "AnomalySettingsDialog"):
        """Inicializálás."""
        self.dialog = dialog

    def choose_color(self, category_key: str) -> None:
        """Szín választó dialog."""
        current_color = self.dialog.category_widgets[category_key]["color_value"]
        color = QColorDialog.getColor(
            QColor(current_color), self.dialog, f"Szín választás - {category_key}"
        )

        if color.isValid():
            hex_color = color.name()
            self.dialog.category_widgets[category_key]["color_value"] = hex_color
            self.dialog.category_widgets[category_key]["color"].setStyleSheet(
                f"background: {hex_color}; border: 1px solid #ccc; border-radius: 4px;"
            )
            self.dialog._on_setting_changed()

    def choose_icon(self, category_key: str) -> None:
        """Ikon választó (egyszerű emoji lista)."""
        icons = ["🌱", "⚠️", "🚨", "💀", "🔥", "❄️", "🌧️", "🌪️", "☀️", "⛅", "🌈", "⚡"]

        icon, ok = QInputDialog.getItem(
            self.dialog,
            f"Ikon választás - {category_key}",
            "Válassz ikont:",
            icons,
            0,
            False,
        )

        if ok and icon:
            self.dialog.category_widgets[category_key]["icon"].setText(icon)
            self.dialog._on_setting_changed()

    def run_test(self, test_type: str) -> None:
        """Teszt futtatása az előnézetben."""
        test_data = {
            "hot_day": {
                "temp_max": 42.5,
                "temp_min": 28.0,
                "precipitation": 0.0,
                "wind_speed": 15.0,
            },
            "cold_day": {
                "temp_max": -15.0,
                "temp_min": -25.0,
                "precipitation": 5.0,
                "wind_speed": 35.0,
            },
            "rainy_day": {
                "temp_max": 22.0,
                "temp_min": 16.0,
                "precipitation": 125.0,
                "wind_speed": 25.0,
            },
            "windy_day": {
                "temp_max": 18.0,
                "temp_min": 12.0,
                "precipitation": 2.0,
                "wind_speed": 85.0,
            },
        }

        data = test_data.get(test_type, {})
        self.simulate_anomaly_detection(data)

    def simulate_anomaly_detection(self, test_data: Dict[str, float]) -> None:
        """Anomália detektálás szimulálása a teszt adatokkal."""
        current_settings = self.dialog._get_current_settings()

        results = []

        # Hőmérséklet teszt
        temp_max = test_data.get("temp_max", 20.0)
        if temp_max > current_settings["temp_hot"]:
            results.append(f"🔥 FORRÓ: {temp_max}°C > {current_settings['temp_hot']}°C")
        elif temp_max < current_settings["temp_cold"]:
            results.append(f"❄️ HIDEG: {temp_max}°C < {current_settings['temp_cold']}°C")
        else:
            results.append(f"🌡️ NORMÁLIS: {temp_max}°C")

        # Csapadék teszt
        precip = test_data.get("precipitation", 0.0)
        if precip > current_settings["precip_high"]:
            results.append(f"🌊 ESŐS: {precip}mm > {current_settings['precip_high']}mm")
        elif precip < current_settings["precip_low"]:
            results.append(f"🏜️ SZÁRAZ: {precip}mm < {current_settings['precip_low']}mm")
        else:
            results.append(f"🌧️ NORMÁLIS: {precip}mm")

        # Szél teszt
        wind = test_data.get("wind_speed", 0.0)
        if wind > current_settings["wind_hurricane"]:
            results.append(f"🌀 ORKÁN: {wind}km/h")
        elif wind > current_settings["wind_extreme"]:
            results.append(f"🌪️ EXTRÉM: {wind}km/h")
        elif wind > current_settings["wind_strong"]:
            results.append(f"🌬️ ERŐS: {wind}km/h")
        elif wind > current_settings["wind_normal"]:
            results.append(f"💨 MÉRSÉKELT: {wind}km/h")
        else:
            results.append(f"🌿 CSENDES: {wind}km/h")

        # Eredmények megjelenítése
        self.dialog.preview_text.setText("\n".join(results))

    def update_preview(self) -> None:
        """Előnézet frissítése."""
        settings = self.dialog._get_current_settings()

        preview_text = f"""
🎯 AKTUÁLIS BEÁLLÍTÁSOK:

🌡️ HŐMÉRSÉKLET:
• Forró küszöb: > {settings["temp_hot"]}°C
• Hideg küszöb: < {settings["temp_cold"]}°C

🌧️ CSAPADÉK:
• Magas küszöb: > {settings["precip_high"]}mm
• Alacsony küszöb: < {settings["precip_low"]}mm

🌪️ SZÉL KATEGÓRIÁK:
• Szeles küszöb: > {settings["wind_high"]}km/h
• Normális: < {settings["wind_normal"]}km/h
• Erős: {settings["wind_normal"]}-{settings["wind_strong"]}km/h
• Extrém: {settings["wind_strong"]}-{settings["wind_extreme"]}km/h
• Orkán: > {settings["wind_hurricane"]}km/h

📁 Aktív profil: {self.dialog.current_profile}
{"⚠️ Nem mentett változások!" if self.dialog.unsaved_changes else "✅ Mentett állapot"}
        """

        if self.dialog.preview_text:
            self.dialog.preview_text.setText(preview_text.strip())
