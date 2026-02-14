"""Categories section builders."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def create_categories_tab(dialog: object) -> QWidget:
    """Kategóriák testreszabása tab."""
    container = QWidget()
    layout = QVBoxLayout(container)

    info_label = QLabel("🏷️ Kategória nevek, színek és ikonok testreszabása")
    info_label.setAlignment(Qt.AlignCenter)
    info_font = QFont()
    info_font.setBold(True)
    info_label.setFont(info_font)
    layout.addWidget(info_label)

    categories_grid = create_categories_grid(dialog)
    layout.addWidget(categories_grid)

    layout.addStretch()

    return container


def create_categories_grid(dialog: object) -> QWidget:
    """Kategóriák szerkesztése grid layout."""
    container = QWidget()
    layout = QGridLayout(container)
    layout.setSpacing(15)

    dialog.category_widgets = {}

    headers = ["Kategória", "Név", "Szín", "Ikon", "Küszöb"]
    for col, header in enumerate(headers):
        label = QLabel(header)
        label.setStyleSheet("font-weight: bold; padding: 8px;")
        layout.addWidget(label, 0, col)

    categories = [
        ("normal", "Normális", "#10b981", "🌱", "< 35°C"),
        ("warning", "Figyelmeztetés", "#f59e0b", "⚠️", "35-40°C"),
        ("danger", "Veszélyes", "#dc2626", "🚨", "> 40°C"),
        ("extreme", "Extrém", "#7c2d12", "💀", "> 45°C"),
    ]

    for row, (key, name, color, icon, threshold) in enumerate(categories, 1):
        dialog.category_widgets[key] = {}

        cat_label = QLabel(key.title())
        cat_label.setStyleSheet(
            "padding: 4px; background: #f3f4f6; border-radius: 4px;"
        )
        layout.addWidget(cat_label, row, 0)

        name_edit = QLineEdit(name)
        name_edit.textChanged.connect(dialog._on_setting_changed)
        dialog.category_widgets[key]["name"] = name_edit
        layout.addWidget(name_edit, row, 1)

        color_btn = QPushButton()
        color_btn.setFixedSize(40, 30)
        color_btn.setStyleSheet(
            f"background: {color}; border: 1px solid #ccc; border-radius: 4px;"
        )
        color_btn.clicked.connect(lambda checked, k=key: dialog._choose_color(k))
        dialog.category_widgets[key]["color"] = color_btn
        dialog.category_widgets[key]["color_value"] = color
        layout.addWidget(color_btn, row, 2)

        icon_btn = QPushButton(icon)
        icon_btn.setFixedSize(40, 30)
        icon_btn.clicked.connect(lambda checked, k=key: dialog._choose_icon(k))
        dialog.category_widgets[key]["icon"] = icon_btn
        layout.addWidget(icon_btn, row, 3)

        threshold_label = QLabel(threshold)
        threshold_label.setStyleSheet("padding: 4px; color: #6b7280;")
        layout.addWidget(threshold_label, row, 4)

    return container
