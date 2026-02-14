"""UI Builder - Header and Controls sections."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def create_header(parent_widget: QWidget) -> QWidget:
    """Professional header létrehozása."""
    header = QFrame()
    header.setFrameStyle(QFrame.Box)
    header.setStyleSheet("""
        QFrame {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667eea, stop:1 #764ba2);
            border-radius: 8px;
            padding: 15px;
            color: white;
        }
    """)

    layout = QVBoxLayout()

    title = QLabel("📈 Enhanced Trend Analytics Dashboard v4.2")
    title.setFont(QFont("Arial", 20, QFont.Bold))
    title.setStyleSheet("color: white; margin: 0;")
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    subtitle = QLabel(
        "Globális trend elemzés dinamikus KPI dashboard-dal - Hibamentesen javított!"
    )
    subtitle.setFont(QFont("Arial", 11))
    subtitle.setStyleSheet("color: rgba(255,255,255,0.9); margin: 5px 0 0 0;")
    subtitle.setAlignment(Qt.AlignCenter)
    layout.addWidget(subtitle)

    header.setLayout(layout)
    parent_widget.layout().addWidget(header)
    return header


def create_controls_panel(parent_widget: QWidget) -> dict:
    """Elemzési paraméterek panel."""
    panel = QFrame()
    panel.setFrameStyle(QFrame.Box)
    panel.setStyleSheet("""
        QFrame {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
        }
    """)

    layout = QVBoxLayout()

    panel_title = QLabel("⚙️ Elemzési Paraméterek")
    panel_title.setFont(QFont("Arial", 14, QFont.Bold))
    panel_title.setStyleSheet("color: #495057; margin-bottom: 10px;")
    layout.addWidget(panel_title)

    controls_layout = QHBoxLayout()

    # Lokáció
    location_group = QVBoxLayout()
    location_label = QLabel("🌍 Lokáció:")
    location_label.setFont(QFont("Arial", 10, QFont.Bold))
    location_group.addWidget(location_label)

    location_combo = QComboBox()
    location_combo.setEditable(True)
    location_combo.setPlaceholderText("Írj be település nevet...")
    location_combo.setMinimumWidth(200)
    location_group.addWidget(location_combo)
    controls_layout.addLayout(location_group)

    # Paraméter
    param_group = QVBoxLayout()
    param_label = QLabel("📊 Paraméter:")
    param_label.setFont(QFont("Arial", 10, QFont.Bold))
    param_group.addWidget(param_label)

    parameter_combo = QComboBox()
    parameter_combo.addItems(
        [
            "🥶 Minimum hőmérséklet",
            "🔥 Maximum hőmérséklet",
            "🌡️ Átlag hőmérséklet",
            "🌧️ Csapadékmennyiség",
            "💨 Szélsebesség",
            "💨 Széllökések",
        ]
    )
    parameter_combo.setCurrentText("🔥 Maximum hőmérséklet")
    param_group.addWidget(parameter_combo)
    controls_layout.addLayout(param_group)

    # Időtartam
    time_group = QVBoxLayout()
    time_label = QLabel("🕒 Időtartam:")
    time_label.setFont(QFont("Arial", 10, QFont.Bold))
    time_group.addWidget(time_label)

    time_combo = QComboBox()
    time_combo.addItems(["5 év", "10 év", "25 év", "55 év (teljes)"])
    time_combo.setCurrentText("5 év")
    time_group.addWidget(time_combo)
    controls_layout.addLayout(time_group)

    # Analyze button
    analyze_button = QPushButton("🚀 Dashboard Elemzés Indítása")
    analyze_button.setFont(QFont("Arial", 11, QFont.Bold))
    analyze_button.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #28a745, stop:1 #1e7e34);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 12px 24px;
            margin-left: 20px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #218838, stop:1 #1c7430);
        }
        QPushButton:pressed {
            background: #1e7e34;
        }
        QPushButton:disabled {
            background: #6c757d;
        }
    """)
    controls_layout.addWidget(analyze_button)

    layout.addLayout(controls_layout)

    progress_bar = QProgressBar()
    progress_bar.setVisible(False)
    progress_bar.setStyleSheet("""
        QProgressBar {
            border: 2px solid #dee2e6;
            border-radius: 5px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #007bff;
            border-radius: 3px;
        }
    """)
    layout.addWidget(progress_bar)

    panel.setLayout(layout)
    parent_widget.layout().addWidget(panel)

    return {
        "location_combo": location_combo,
        "parameter_combo": parameter_combo,
        "time_combo": time_combo,
        "analyze_button": analyze_button,
        "progress_bar": progress_bar,
    }
