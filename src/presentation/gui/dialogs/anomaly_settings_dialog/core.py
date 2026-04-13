#!/usr/bin/env python3
# mypy: ignore-errors

"""
Anomaly Settings Dialog - Core Module
Fő AnomalySettingsDialog osztály.
"""

import logging

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QDialog, QMessageBox, QVBoxLayout
from src.domain.ports import AnomalyProfilePort
from src.infrastructure.container import get_anomaly_profile_port

from ...theme_manager import get_theme_manager, register_widget_for_theming
from .preview_handler import AnomalySettingsPreviewHandler
from .profile_handler import AnomalySettingsProfileHandler
from .ui_builder import AnomalySettingsUIBuilder

logger = logging.getLogger(__name__)


class AnomalySettingsDialog(QDialog):
    """
    🎨 Anomália Beállítások Dialog - Teljes GUI Kezelés
    """

    # Signals
    settings_changed = Signal(dict)
    profile_changed = Signal(str)

    def __init__(self, parent=None):
        """Anomália beállítások dialog inicializálása (CA compliant - uses port)."""
        super().__init__(parent)

        self.theme_manager = get_theme_manager()
        self.profile_manager: AnomalyProfilePort = get_anomaly_profile_port()

        # Belső állapot
        self.current_profile: str = "default"
        self.unsaved_changes: bool = False
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self._update_preview)

        # Handler osztályok
        self.ui_builder = AnomalySettingsUIBuilder(self)
        self.profile_handler = AnomalySettingsProfileHandler(self)
        self.preview_handler = AnomalySettingsPreviewHandler(self)

        # UI komponensek tárolása (a UI builder által létrehozva)
        self.profile_combo = None
        self.temp_widgets = {}
        self.precip_widgets = {}
        self.wind_widgets = {}
        self.category_widgets = {}
        self.preview_text = None

        self._setup_dialog()
        self._init_ui()
        self.profile_handler.load_current_profile()
        self._register_for_theming()

        logger.info("🎨 AnomalySettingsDialog inicializálva")

    def _setup_dialog(self) -> None:
        """Dialog alapbeállítások."""
        self.setWindowTitle("⚙️ Anomália Beállítások")
        self.setModal(True)
        self.resize(800, 600)
        self.setMinimumSize(600, 400)

        # Window icon és flags
        self.setWindowFlags(
            Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint
        )

    def _init_ui(self) -> None:
        """UI felépítése."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Fejléc (cím + profil választó)
        header_section = self.ui_builder.create_header_section()
        layout.addWidget(header_section)

        # Fő tartalom (tab widget)
        main_tabs = self.ui_builder.create_main_tabs()
        layout.addWidget(main_tabs)

        # Gombok (mentés, mégse, alkalmazás)  # noqa: ERA001
        buttons_section = self.ui_builder.create_buttons_section()
        layout.addWidget(buttons_section)

    def _register_for_theming(self) -> None:
        """Widget-ek regisztrálása témakezéléshez."""
        register_widget_for_theming(self, "container")
        logger.debug("AnomalySettingsDialog - Widgets regisztrálva témakezéléshez")

    # ===== EVENT HANDLERS =====

    def _on_profile_changed(self, profile_name: str) -> None:
        """Profil váltás eseménykezelő."""
        if profile_name and profile_name != self.current_profile:
            self.current_profile = profile_name
            self.profile_handler.load_profile_settings(profile_name)
            self.profile_changed.emit(profile_name)
            logger.info(f"Profil váltva: {profile_name}")

    def _on_setting_changed(self) -> None:
        """Beállítás változás eseménykezelő."""
        self.unsaved_changes = True
        self.preview_timer.start(500)  # 500ms delay a preview frissítéshez

    def _choose_color(self, category_key: str) -> None:
        """Szín választó dialog."""
        self.preview_handler.choose_color(category_key)

    def _choose_icon(self, category_key: str) -> None:
        """Ikon választó."""
        self.preview_handler.choose_icon(category_key)

    def _run_test(self, test_type: str) -> None:
        """Teszt futtatása az előnézetben."""
        self.preview_handler.run_test(test_type)

    def _update_preview(self) -> None:
        """Előnézet frissítése."""
        self.preview_handler.update_preview()

    def _get_current_settings(self) -> dict:
        """Aktuális UI beállítások összegyűjtése."""
        return self.profile_handler.get_current_settings()

    # ===== PROFILE MANAGEMENT =====

    def _load_profile_settings(self, profile_name: str) -> None:
        """Profil beállítások betöltése a UI-ba."""
        self.profile_handler.load_profile_settings(profile_name)

    def _create_new_profile(self) -> None:
        """Új profil létrehozása."""
        self.profile_handler.create_new_profile()

    def _edit_profile_name(self) -> None:
        """Profil átnevezése."""
        self.profile_handler.edit_profile_name()

    def _delete_profile(self) -> None:
        """Profil törlése."""
        self.profile_handler.delete_profile()

    # ===== SAVE/LOAD/APPLY =====

    def _reset_to_defaults(self) -> None:
        """Alapértelmezett értékek visszaállítása."""
        self.profile_handler.reset_to_defaults()

    def _apply_settings(self) -> None:
        """Beállítások alkalmazása mentés nélkül."""
        settings = self._get_current_settings()
        self.settings_changed.emit(settings)
        logger.info("Beállítások alkalmazva (mentés nélkül)")

    def _save_and_apply(self) -> None:
        """Beállítások mentése és alkalmazása."""
        settings = self._get_current_settings()

        if self.profile_manager.save_profile(self.current_profile, settings):
            self.profile_manager.set_active_profile(self.current_profile)
            self.settings_changed.emit(settings)
            self.unsaved_changes = False
            self._update_preview()

            QMessageBox.information(
                self,
                "Siker",
                f"Beállítások mentve a '{self.current_profile}' profilba!",
            )
            logger.info(f"Beállítások mentve és alkalmazva: {self.current_profile}")
        else:
            QMessageBox.warning(self, "Hiba", "Beállítások mentése sikertelen!")

    def _cancel_changes(self) -> None:
        """Módosítások elvetése."""
        if self.unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Módosítások Elvetése",
                "Vannak nem mentett módosítások. Biztos elveted őket?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.No:
                return

        self.reject()

    def closeEvent(self, event) -> None:
        """Dialog bezárás esemény."""
        self._cancel_changes()
        event.accept()
