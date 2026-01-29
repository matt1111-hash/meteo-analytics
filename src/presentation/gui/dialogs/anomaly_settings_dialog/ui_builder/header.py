"""Header section builders."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from ...utils import AnomalyConstants


def create_header_section(dialog: object) -> QWidget:
    """Fejléc szekció: cím + profil választó."""
    container = QWidget()
    layout = QHBoxLayout(container)

    title_label = QLabel("⚙️ Anomália Beállítások")
    title_font = QFont()
    title_font.setBold(True)
    title_font.setPointSize(18)
    title_label.setFont(title_font)
    layout.addWidget(title_label)

    layout.addStretch()

    profile_section = create_profile_section(dialog)
    layout.addWidget(profile_section)

    return container


def create_profile_section(dialog: object) -> object:
    """Profil választó és menedzsment gombok."""
    from PySide6.QtWidgets import QComboBox, QGroupBox

    group = QGroupBox("📁 Profilok")
    layout = QHBoxLayout(group)

    layout.addWidget(QLabel("Aktív profil:"))

    dialog.profile_combo = QComboBox()
    dialog.profile_combo.setMinimumWidth(150)
    dialog.profile_combo.currentTextChanged.connect(dialog._on_profile_changed)
    layout.addWidget(dialog.profile_combo)

    new_btn = QPushButton("🆕 Új")
    new_btn.setToolTip("Új profil létrehozása")
    new_btn.clicked.connect(dialog._create_new_profile)
    layout.addWidget(new_btn)

    edit_btn = QPushButton("✏️ Szerk")
    edit_btn.setToolTip("Profil átnevezése")
    edit_btn.clicked.connect(dialog._edit_profile_name)
    layout.addWidget(edit_btn)

    delete_btn = QPushButton("🗑️ Törlés")
    delete_btn.setToolTip("Profil törlése")
    delete_btn.clicked.connect(dialog._delete_profile)
    layout.addWidget(delete_btn)

    return group
