# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for HungarianCityUIBuilder."""

from __future__ import annotations

from .ui_builder_support import *


class HungarianCityUIBuilderPart1Mixin:  # noqa: D101
    def __init__(self, parent: QWidget):
        """
        Inicializálás.

        Args:
            parent: Szülő widget
        """
        self.parent = parent
        self.search_box: Optional[QLineEdit] = None
        self.region_combo: Optional[QComboBox] = None
        self.city_list: Optional[QListWidget] = None
        self.stats_label: Optional[QLabel] = None
        self.quick_access_buttons: List[QPushButton] = []

    def create_header(self) -> QHBoxLayout:
        """Fejléc létrehozása."""
        layout = QHBoxLayout()
        layout.setSpacing(8)

        # Magyar zászló és cím
        flag_label = QLabel("🇭🇺")
        flag_label.setStyleSheet("font-size: 24px; border: none; background: transparent;")
        layout.addWidget(flag_label)

        title_label = QLabel("Magyar Városok")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        layout.addStretch()

        # Verzió info
        version_label = QLabel("MVP v1.0")
        version_label.setStyleSheet(
            "color: gray; font-size: 10px; border: none; background: transparent;"
        )
        layout.addWidget(version_label)

        return layout

    def create_search_section(
        self, search_callback: Callable, clear_callback: Callable
    ) -> QGroupBox:
        """Keresési szakasz létrehozása."""
        group = QGroupBox("🔍 Keresés")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        # Keresőmező
        search_container = QHBoxLayout()

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 16px; border: none; background: transparent;")
        search_container.addWidget(search_icon)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            "Keresés magyar városokban... (pl. Budapest, Szeged, Debrecen)"
        )
        self.search_box.textChanged.connect(search_callback)
        self.search_box.returnPressed.connect(search_callback)
        search_container.addWidget(self.search_box)

        clear_btn = QPushButton("✖")
        clear_btn.setMaximumWidth(30)
        clear_btn.setToolTip("Keresés törlése")
        clear_btn.clicked.connect(clear_callback)
        search_container.addWidget(clear_btn)

        layout.addLayout(search_container)

        return group

    def create_filter_section(self, region_callback: Callable) -> QGroupBox:
        """Szűrési szakasz létrehozása."""
        group = QGroupBox("🗺️ Régió szűrés")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        # Régió választó
        region_layout = QHBoxLayout()

        region_label = QLabel("Régió:")
        region_layout.addWidget(region_label)

        self.region_combo = QComboBox()
        self.region_combo.addItem("🇭🇺 Összes magyar város", "Összes")

        # Régiók hozzáadása
        for region in HungarianRegions.get_all_regions():
            display_name = HungarianRegions.REGION_DISPLAY_NAMES[region]
            description = HungarianRegions.REGION_DESCRIPTIONS[region]
            self.region_combo.addItem(f"{display_name}", region)

            # Tooltip beállítása
            index = self.region_combo.count() - 1
            self.region_combo.setItemData(index, description, Qt.ToolTipRole)

        self.region_combo.currentTextChanged.connect(region_callback)
        region_layout.addWidget(self.region_combo)

        region_layout.addStretch()

        layout.addLayout(region_layout)

        return group

    def create_cities_list_section(
        self, select_callback: Callable, reload_callback: Callable
    ) -> QGroupBox:
        """Városok listája szakasz létrehozása."""
        group = QGroupBox("🏙️ Magyar városok listája")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        # Városok lista
        self.city_list = QListWidget()
        self.city_list.setMinimumHeight(300)
        self.city_list.setMaximumHeight(400)
        layout.addWidget(self.city_list)

        # Lista alatti műveletek
        actions_layout = QHBoxLayout()

        select_btn = QPushButton("✅ Kiválasztás")
        select_btn.clicked.connect(select_callback)
        actions_layout.addWidget(select_btn)

        actions_layout.addStretch()

        refresh_btn = QPushButton("🔄 Frissítés")
        refresh_btn.setToolTip("Városok listájának újratöltése")
        refresh_btn.clicked.connect(reload_callback)
        actions_layout.addWidget(refresh_btn)

        layout.addLayout(actions_layout)

        return group
