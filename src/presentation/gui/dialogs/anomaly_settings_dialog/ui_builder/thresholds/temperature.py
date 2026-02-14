"""Temperature threshold section builder."""

from PySide6.QtWidgets import QDoubleSpinBox, QGroupBox, QLabel, QVBoxLayout

from ...utils import AnomalyConstants


def create_temperature_section(dialog: object) -> QGroupBox:
    """Hőmérséklet küszöbök szekció."""
    group = QGroupBox("🌡️ Hőmérséklet Küszöbök")
    layout = QVBoxLayout(group)

    dialog.temp_widgets = {}

    hot_spinbox = QDoubleSpinBox()
    hot_spinbox.setRange(-50.0, 60.0)
    hot_spinbox.setSuffix(" °C")
    hot_spinbox.setDecimals(1)
    hot_spinbox.setValue(AnomalyConstants.TEMP_HOT_THRESHOLD)
    hot_spinbox.valueChanged.connect(dialog._on_setting_changed)
    dialog.temp_widgets["hot"] = hot_spinbox
    layout.addWidget(QLabel("🔥 Meleg küszöb:"))
    layout.addWidget(hot_spinbox)

    cold_spinbox = QDoubleSpinBox()
    cold_spinbox.setRange(-50.0, 40.0)
    cold_spinbox.setSuffix(" °C")
    cold_spinbox.setDecimals(1)
    cold_spinbox.setValue(AnomalyConstants.TEMP_COLD_THRESHOLD)
    cold_spinbox.valueChanged.connect(dialog._on_setting_changed)
    dialog.temp_widgets["cold"] = cold_spinbox
    layout.addWidget(QLabel("❄️ Hideg küszöb:"))
    layout.addWidget(cold_spinbox)

    info_label = QLabel(
        "💡 Meleg küszöb felett 'forró', hideg alatt 'fagyos' kategória."
    )
    info_label.setStyleSheet("color: #6b7280; font-size: 11px;")
    layout.addWidget(info_label)

    return group
