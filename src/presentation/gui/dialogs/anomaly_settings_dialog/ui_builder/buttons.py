# mypy: ignore-errors
"""Buttons section builders."""

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget


def create_buttons_section(dialog: object) -> QWidget:
    """Alsó gombok szekció."""
    container = QWidget()
    layout = QHBoxLayout(container)

    reset_btn = QPushButton("🔄 Alapértelmezett")
    reset_btn.setToolTip("Jelenlegi profil visszaállítása alapértékekre")
    reset_btn.clicked.connect(dialog._reset_to_defaults)
    layout.addWidget(reset_btn)

    layout.addStretch()

    apply_btn = QPushButton("✅ Alkalmaz")
    apply_btn.setToolTip("Beállítások alkalmazása mentés nélkül")
    apply_btn.clicked.connect(dialog._apply_settings)
    layout.addWidget(apply_btn)

    save_btn = QPushButton("💾 Mentés")
    save_btn.setToolTip("Beállítások mentése és alkalmazása")
    save_btn.clicked.connect(dialog._save_and_apply)
    layout.addWidget(save_btn)

    cancel_btn = QPushButton("❌ Mégse")
    cancel_btn.setToolTip("Módosítások elvetése")
    cancel_btn.clicked.connect(dialog._cancel_changes)
    layout.addWidget(cancel_btn)

    return container
