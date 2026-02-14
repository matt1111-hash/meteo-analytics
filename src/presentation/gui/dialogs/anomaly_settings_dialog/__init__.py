#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Anomaly Settings Dialog Module
🎨 TELJES GUI: Testreszabható küszöbök, profilok, kategóriák
⚙️ FUNKCIONALITÁS: Real-time preview, automatikus mentés, predefined profilok
"""

# Re-export core
from src.presentation.gui.dialogs.anomaly_settings_dialog.core import (
    AnomalySettingsDialog,
)

__all__ = ["AnomalySettingsDialog"]


# 🧪 DEMO FUNKCIÓ
def demo_anomaly_settings_dialog():
    """Demo: Anomália beállítások dialog tesztelése."""
    import sys

    from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

    app = QApplication(sys.argv)

    main_window = QWidget()
    main_window.setWindowTitle("Anomália Beállítások Demo")
    main_window.resize(400, 200)

    layout = QVBoxLayout(main_window)

    open_btn = QPushButton("⚙️ Anomália Beállítások Megnyitása")

    def open_dialog():
        from src.presentation.gui.dialogs.anomaly_settings_dialog import (
            AnomalySettingsDialog,
        )

        dialog = AnomalySettingsDialog(main_window)
        dialog.settings_changed.connect(
            lambda settings: print(f"🔧 Beállítások változtak: {settings}")
        )
        dialog.profile_changed.connect(
            lambda profile: print(f"📁 Profil váltva: {profile}")
        )
        dialog.exec()

    open_btn.clicked.connect(open_dialog)
    layout.addWidget(open_btn)

    main_window.show()

    return app.exec()


if __name__ == "__main__":
    demo_anomaly_settings_dialog()
