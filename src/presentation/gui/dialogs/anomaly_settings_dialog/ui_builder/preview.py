# mypy: ignore-errors
"""Preview section builders."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


def create_preview_tab(dialog: object) -> QWidget:
    """Előnézet tab."""
    container = QWidget()
    layout = QVBoxLayout(container)

    preview_label = QLabel("👁️ Aktuális Beállítások Előnézete")
    preview_label.setAlignment(Qt.AlignCenter)
    preview_font = QFont()
    preview_font.setBold(True)
    preview_label.setFont(preview_font)
    layout.addWidget(preview_label)

    dialog.preview_text = QTextEdit()
    dialog.preview_text.setReadOnly(True)
    dialog.preview_text.setMaximumHeight(300)
    layout.addWidget(dialog.preview_text)

    test_section = create_test_section(dialog)
    layout.addWidget(test_section)

    layout.addStretch()

    return container


def create_test_section(dialog: object) -> QGroupBox:
    """Teszt adatok szekció az előnézethez."""
    group = QGroupBox("🧪 Teszt Adatok")
    layout = QHBoxLayout(group)

    test_btn1 = QPushButton("🔥 Forró Nap Teszt")
    test_btn1.clicked.connect(lambda: dialog._run_test("hot_day"))
    layout.addWidget(test_btn1)

    test_btn2 = QPushButton("❄️ Hideg Nap Teszt")
    test_btn2.clicked.connect(lambda: dialog._run_test("cold_day"))
    layout.addWidget(test_btn2)

    test_btn3 = QPushButton("🌧️ Esős Nap Teszt")
    test_btn3.clicked.connect(lambda: dialog._run_test("rainy_day"))
    layout.addWidget(test_btn3)

    test_btn4 = QPushButton("🌪️ Viharos Nap Teszt")
    test_btn4.clicked.connect(lambda: dialog._run_test("windy_day"))
    layout.addWidget(test_btn4)

    return group
