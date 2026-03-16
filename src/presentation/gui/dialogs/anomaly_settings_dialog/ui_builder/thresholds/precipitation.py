# mypy: ignore-errors
"""Precipitation threshold section builder."""

from PySide6.QtWidgets import QDoubleSpinBox, QGroupBox, QLabel, QVBoxLayout

from ...utils import AnomalyConstants


def create_precipitation_section(dialog: object) -> QGroupBox:
    """Csapadék küszöbök szekció."""
    group = QGroupBox("🌧️ Csapadék Küszöbök")
    layout = QVBoxLayout(group)

    dialog.precip_widgets = {}

    high_spinbox = QDoubleSpinBox()
    high_spinbox.setRange(0.0, 500.0)
    high_spinbox.setSuffix(" mm")
    high_spinbox.setDecimals(1)
    high_spinbox.setValue(AnomalyConstants.PRECIP_HIGH_THRESHOLD)
    high_spinbox.valueChanged.connect(dialog._on_setting_changed)
    dialog.precip_widgets["high"] = high_spinbox
    layout.addWidget(QLabel("🌊 Magas küszöb:"))
    layout.addWidget(high_spinbox)

    low_spinbox = QDoubleSpinBox()
    low_spinbox.setRange(0.0, 50.0)
    low_spinbox.setSuffix(" mm")
    low_spinbox.setDecimals(1)
    low_spinbox.setValue(AnomalyConstants.PRECIP_LOW_THRESHOLD)
    low_spinbox.valueChanged.connect(dialog._on_setting_changed)
    dialog.precip_widgets["low"] = low_spinbox
    layout.addWidget(QLabel("🏜️ Alacsony küszöb:"))
    layout.addWidget(low_spinbox)

    info_label = QLabel(
        "💡 Magas küszöb felett 'esős', alacsony alatt 'száraz' kategória."
    )
    info_label.setStyleSheet("color: #6b7280; font-size: 11px;")
    layout.addWidget(info_label)

    return group
