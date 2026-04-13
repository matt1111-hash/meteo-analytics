# ruff: noqa: F403, F405, I001
# mypy: ignore-errors
"""Mixin part 1 for ExtremeEventsTab."""

from __future__ import annotations

from .extreme_events_tab_support import (
    _extreme_calculator_available,
    _profile_manager_available,
)
from .extreme_events_tab_part2_support import *


class ExtremeEventsTabPart1Mixin:  # noqa: D101
    def __init__(self, parent: Optional[QWidget] = None):  # noqa: D107
        super().__init__(parent)

        self.theme_manager = get_theme_manager()
        self.profile_manager = get_anomaly_profile_port() if _profile_manager_available else None
        self.use_case = DetectAnomaliesUseCase()
        self.extreme_calculator = ExtremeCalculator() if _extreme_calculator_available else None

        self.current_data: Optional[Dict[str, Any]] = None
        self.period_type: str = "daily"

        # UI komponensek
        self.temp_anomaly: Optional[QLabel] = None
        self.precip_anomaly: Optional[QLabel] = None
        self.wind_anomaly: Optional[QLabel] = None
        self.records_text: Optional[QTextEdit] = None
        self.extreme_table: Optional[QTableWidget] = None

        self._init_ui()
        self._register_widgets_for_theming()

        logger.info("ExtremeEventsTab inicializálva (Clean Architecture)")

    def _init_ui(self) -> None:
        """🎨 UI inicializálása."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Cím - kompakt
        self.title_label = QLabel("⚡ Extrém Időjárási Események")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(13)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Anomália beállítások gomb - kisebb
        self.settings_btn = QPushButton("⚙️ Anomália beállítások")
        self.settings_btn.setMaximumHeight(30)
        self.settings_btn.clicked.connect(self._on_anomaly_settings_clicked)
        layout.addWidget(self.settings_btn)

        # Anomália szekció
        self.anomaly_section = self._create_anomaly_section()
        layout.addWidget(self.anomaly_section)

        # SPLITTER: felső rész (rekordok) és alsó rész (gomb)
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)

        # Rekordok szekció (felső) - dinamikus méret
        self.records_section = self._create_records_section()
        self.splitter.addWidget(self.records_section)

        # Alsó konténer (gomb) - nincs fix méret
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 5, 0, 0)
        self.detailed_btn = QPushButton("🔍 Részletes elemzés")
        self.detailed_btn.setMaximumHeight(30)
        self.detailed_btn.clicked.connect(self._on_detailed_analysis_clicked)
        bottom_layout.addWidget(self.detailed_btn)
        self.splitter.addWidget(bottom_widget)

        # Nincs setStretchFactor, nincs setSizes - a felhasználó szabályozza
        layout.addWidget(self.splitter)

    def _create_anomaly_section(self) -> QGroupBox:
        section = QGroupBox("🔍 Anomália Detektálás")
        layout = QGridLayout(section)

        self.temp_anomaly = QLabel("🌡️ Hőmérséklet: -")
        self.precip_anomaly = QLabel("🌧️ Csapadék: -")
        self.wind_anomaly = QLabel("🌪️ Szél: -")

        layout.addWidget(self.temp_anomaly, 0, 0)
        layout.addWidget(self.precip_anomaly, 0, 1)
        layout.addWidget(self.wind_anomaly, 0, 2)

        return section

    def _create_records_section(self) -> QGroupBox:
        section = QGroupBox("🏆 Rekordok és Szélsőértékek")
        layout = QVBoxLayout(section)

        # Periódus választó
        period_layout = QHBoxLayout()
        self.period_group = QButtonGroup(self)

        self.daily_radio = QRadioButton("Napi")
        self.monthly_radio = QRadioButton("Havi")
        self.yearly_radio = QRadioButton("Éves")

        self.daily_radio.setChecked(True)
        for rb in [self.daily_radio, self.monthly_radio, self.yearly_radio]:
            self.period_group.addButton(rb)
            period_layout.addWidget(rb)
            rb.toggled.connect(self._on_period_type_changed)

        layout.addLayout(period_layout)

        self.extreme_table = QTableWidget()
        self.extreme_table.setColumnCount(4)
        self.extreme_table.setHorizontalHeaderLabels(["Kategória", "Típus", "Érték", "Dátum"])
        # Egyedi oszlopszélességek - a kategória és típus szövegei hosszabbak
        self.extreme_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.extreme_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.extreme_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.extreme_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        # De az érték és dátum oszlopok ne legyenek túl szélesek
        self.extreme_table.horizontalHeader().setMinimumSectionSize(60)
        self.extreme_table.horizontalHeader().setStretchLastSection(True)
        # Dinamikus sorok - automatikusan kitölti a helyet
        self.extreme_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.extreme_table.verticalHeader().setDefaultSectionSize(22)
        self.extreme_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.extreme_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # SizePolicy: expanding, kitölti a rendelkezésre álló helyet
        from PySide6.QtWidgets import QSizePolicy  # noqa: PLC0415

        self.extreme_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.extreme_table)

        return section
