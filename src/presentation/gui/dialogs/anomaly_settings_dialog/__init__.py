#!/usr/bin/env python3
# mypy: ignore-errors

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
    import sys  # noqa: PLC0415

    from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget  # noqa: PLC0415

    app = QApplication(sys.argv)

    main_window = QWidget()
    main_window.setWindowTitle("Anomália Beállítások Demo")
    main_window.resize(400, 200)

    layout = QVBoxLayout(main_window)

    open_btn = QPushButton("⚙️ Anomália Beállítások Megnyitása")

    def open_dialog():
        from src.presentation.gui.dialogs.anomaly_settings_dialog import (  # noqa: PLC0415
            AnomalySettingsDialog,
        )
        from src.presentation.gui.gui_composition_root import build_gui_services  # noqa: PLC0415

        services = build_gui_services()

        dialog = AnomalySettingsDialog(services.anomaly_profile_port, main_window)
        dialog.settings_changed.connect(
            lambda settings: print(f"🔧 Beállítások változtak: {settings}")
        )
        dialog.profile_changed.connect(lambda profile: print(f"📁 Profil váltva: {profile}"))
        dialog.exec()

    open_btn.clicked.connect(open_dialog)
    layout.addWidget(open_btn)

    main_window.show()

    return app.exec()


if __name__ == "__main__":
    demo_anomaly_settings_dialog()
