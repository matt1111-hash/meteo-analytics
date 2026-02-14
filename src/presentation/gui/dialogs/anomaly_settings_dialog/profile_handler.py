#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Anomaly Settings Dialog - Profile Handler Module
Profil menedzsment logika az AnomalySettingsDialoghoz.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict

from PySide6.QtWidgets import QInputDialog, QMessageBox

if TYPE_CHECKING:
    from src.presentation.gui.dialogs.anomaly_settings_dialog.core import (
        AnomalySettingsDialog,
    )


logger = logging.getLogger(__name__)


class AnomalySettingsProfileHandler:
    """Profil kezelő osztály az AnomalySettingsDialoghoz."""

    def __init__(self, dialog: "AnomalySettingsDialog"):
        """Inicializálás."""
        self.dialog = dialog

    def load_current_profile(self) -> None:
        """Aktuális profil betöltése."""
        profiles = self.dialog.profile_manager.get_available_profiles()

        self.dialog.profile_combo.clear()
        self.dialog.profile_combo.addItems(profiles)

        current = self.dialog.profile_manager.get_active_profile()
        if current in profiles:
            self.dialog.profile_combo.setCurrentText(current)
            self.dialog.current_profile = current

        self.load_profile_settings(self.dialog.current_profile)

    def load_profile_settings(self, profile_name: str) -> None:
        """Profil beállítások betöltése a UI-ba."""
        settings = self.dialog.profile_manager.load_profile(profile_name)

        # Hőmérséklet
        self.dialog.temp_widgets["hot"].setValue(settings.get("temp_hot", 35.0))
        self.dialog.temp_widgets["cold"].setValue(settings.get("temp_cold", -10.0))

        # Csapadék
        self.dialog.precip_widgets["high"].setValue(settings.get("precip_high", 100.0))
        self.dialog.precip_widgets["low"].setValue(settings.get("precip_low", 5.0))

        # Szél
        self.dialog.wind_widgets["high"].setValue(settings.get("wind_high", 70))
        self.dialog.wind_widgets["normal"].setValue(settings.get("wind_normal", 50))
        self.dialog.wind_widgets["strong"].setValue(settings.get("wind_strong", 70))
        self.dialog.wind_widgets["extreme"].setValue(settings.get("wind_extreme", 100))
        self.dialog.wind_widgets["hurricane"].setValue(
            settings.get("wind_hurricane", 120)
        )

        self.dialog.unsaved_changes = False
        self.dialog._update_preview()

        logger.info(f"Profil beállítások betöltve: {profile_name}")

    def get_current_settings(self) -> Dict[str, Any]:
        """Aktuális UI beállítások összegyűjtése."""
        return {
            "temp_hot": self.dialog.temp_widgets["hot"].value(),
            "temp_cold": self.dialog.temp_widgets["cold"].value(),
            "precip_high": self.dialog.precip_widgets["high"].value(),
            "precip_low": self.dialog.precip_widgets["low"].value(),
            "wind_high": self.dialog.wind_widgets["high"].value(),
            "wind_normal": self.dialog.wind_widgets["normal"].value(),
            "wind_strong": self.dialog.wind_widgets["strong"].value(),
            "wind_extreme": self.dialog.wind_widgets["extreme"].value(),
            "wind_hurricane": self.dialog.wind_widgets["hurricane"].value(),
        }

    def create_new_profile(self) -> None:
        """Új profil létrehozása."""
        name, ok = QInputDialog.getText(self.dialog, "Új Profil", "Profil neve:")
        if ok and name.strip():
            if self.dialog.profile_manager.create_profile(name.strip()):
                self.load_current_profile()
                self.dialog.profile_combo.setCurrentText(name.strip())
                logger.info(f"Új profil létrehozva: {name}")
            else:
                QMessageBox.warning(
                    self.dialog, "Hiba", f"Profil '{name}' már létezik!"
                )

    def edit_profile_name(self) -> None:
        """Profil átnevezése."""
        if self.dialog.current_profile == "default":
            QMessageBox.information(
                self.dialog, "Info", "Az alapértelmezett profil nem nevezhető át!"
            )
            return

        new_name, ok = QInputDialog.getText(
            self.dialog,
            "Profil Átnevezése",
            "Új név:",
            text=self.dialog.current_profile,
        )
        if ok and new_name.strip() and new_name.strip() != self.dialog.current_profile:
            if self.dialog.profile_manager.rename_profile(
                self.dialog.current_profile, new_name.strip()
            ):
                self.load_current_profile()
                self.dialog.profile_combo.setCurrentText(new_name.strip())
                logger.info(
                    f"Profil átnevezve: {self.dialog.current_profile} → {new_name}"
                )
            else:
                QMessageBox.warning(
                    self.dialog, "Hiba", f"Profil '{new_name}' már létezik!"
                )

    def delete_profile(self) -> None:
        """Profil törlése."""
        if self.dialog.current_profile == "default":
            QMessageBox.information(
                self.dialog, "Info", "Az alapértelmezett profil nem törölhető!"
            )
            return

        reply = QMessageBox.question(
            self.dialog,
            "Profil Törlése",
            f"Biztosan törölni szeretnéd a '{self.dialog.current_profile}' profilt?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            if self.dialog.profile_manager.delete_profile(self.dialog.current_profile):
                self.load_current_profile()
                logger.info(f"Profil törölve: {self.dialog.current_profile}")
            else:
                QMessageBox.warning(self.dialog, "Hiba", "Profil törlése sikertelen!")

    def reset_to_defaults(self) -> None:
        """Alapértelmezett értékek visszaállítása."""
        reply = QMessageBox.question(
            self.dialog,
            "Alapértelmezett Visszaállítás",
            "Biztos visszaállítod az alapértelmezett értékeket?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.dialog.profile_manager.reset_profile_to_defaults(
                self.dialog.current_profile
            )
            self.load_profile_settings(self.dialog.current_profile)
            logger.info(
                f"Profil visszaállítva alapértelmezettre: {self.dialog.current_profile}"
            )
