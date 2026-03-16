# mypy: ignore-errors
"""Wind threshold section builder."""

from PySide6.QtWidgets import QGroupBox, QLabel, QSpinBox, QVBoxLayout

from ...utils import AnomalyConstants


def create_wind_section(dialog: object) -> QGroupBox:
    """Szél kategóriák szekció."""
    group = QGroupBox("🌪️ Szél Kategóriák")
    layout = QVBoxLayout(group)

    dialog.wind_widgets = {}

    windy_spinbox = QSpinBox()
    windy_spinbox.setRange(10, 200)
    windy_spinbox.setSuffix(" km/h")
    windy_spinbox.setValue(AnomalyConstants.WIND_HIGH_THRESHOLD)
    windy_spinbox.valueChanged.connect(dialog._on_setting_changed)
    dialog.wind_widgets["high"] = windy_spinbox
    layout.addWidget(QLabel("💨 Szeles küszöb:"))
    layout.addWidget(windy_spinbox)

    categories = [
        ("Mérsékelt", 50, "normal"),
        ("Erős", 70, "strong"),
        ("Extrém", 100, "extreme"),
        ("Orkán", 120, "hurricane"),
    ]

    for name, default_value, key in categories:
        spinbox = QSpinBox()
        spinbox.setRange(20, 300)
        spinbox.setSuffix(" km/h")
        spinbox.setValue(default_value)
        spinbox.valueChanged.connect(dialog._on_setting_changed)
        dialog.wind_widgets[key] = spinbox

        icon = {"normal": "🌿", "strong": "🌬️", "extreme": "🌪️", "hurricane": "🌀"}[key]
        layout.addWidget(QLabel(f"{icon} {name}:"))
        layout.addWidget(spinbox)

    info_label = QLabel("💡 Szélsebesség kategóriák szélvihar elemzéshez.")
    info_label.setStyleSheet("color: #6b7280; font-size: 11px;")
    layout.addWidget(info_label)

    return group
