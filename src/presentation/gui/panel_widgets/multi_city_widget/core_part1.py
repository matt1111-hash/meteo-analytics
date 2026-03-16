# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for MultiCityWidget."""

from __future__ import annotations

from .core_support import *


class MultiCityWidgetPart1Mixin:
    def __init__(self, city_manager: CityManagerPort, parent: Optional[QWidget] = None):
        """
        MultiCityWidget inicializálása (CA compliant - uses CityManagerPort).

        Args:
            city_manager: CityManagerPort instance (magyar adatok lekérdezéshez)
            parent: Szülő widget
        """
        super().__init__(parent)

        # Dependencies
        self.city_manager = city_manager
        self.theme_manager = get_theme_manager()

        # State
        self._current_mode = "region"  # "region" vagy "county"
        self._selected_region: Optional[str] = None
        self._selected_county: Optional[str] = None
        self._updating_state = False

        # Data sources
        self._available_regions = get_hungarian_regions()
        self._available_counties = []  # Betöltjük később

        # UI init
        self._init_ui()
        self._load_data()
        self._connect_signals()
        self._register_for_theming()

        # ComboBox inicializálása
        self._combo_handler.populate_combo_box(
            self._current_mode,
            self._available_regions,
            self._available_counties,
            self._selected_region,
            self._selected_county,
        )
        self._combo_handler.update_group_title(self._current_mode)
        self._combo_handler.update_info_label(
            self._current_mode, self._get_current_selection()
        )

        print(
            "🏙️ DEBUG: MultiCityWidget (DROPDOWN) inicializálva - Clean Architecture + COMBO FIX"
        )

    def _init_ui(self) -> None:
        """UI elemek létrehozása."""
        ui_elements = create_multi_city_ui(self, self.theme_manager)

        self.group = ui_elements["group"]
        self.combo_box = ui_elements["combo_box"]
        self.info_label = ui_elements["info_label"]
        self.clear_btn = ui_elements["clear_btn"]

        # Combo handler inicializálása
        self._combo_handler = ComboHandler(
            self.combo_box,
            self.group,
            self.info_label,
            lambda label, style_type: apply_label_styling(
                label, self.theme_manager, style_type
            ),
        )

    def _load_data(self) -> None:
        """Magyar régiók és megyék adatainak betöltése."""
        try:
            # Megyék betöltése city_manager-ből
            self._available_counties = self.city_manager.get_hungarian_counties()
            print(f"🏛️ DEBUG: Betöltött megyék: {len(self._available_counties)} db")
            print(
                f"📋 DEBUG: Megyék listája: {self._available_counties[:5]}..."
            )  # Első 5

        except Exception as e:
            print(f"❌ ERROR: Adatok betöltési hiba: {e}")
            self._available_counties = []

    def _connect_signals(self) -> None:
        """Signal-slot kapcsolatok."""
        self.combo_box.currentTextChanged.connect(self._on_combo_selection_changed)
        self.clear_btn.clicked.connect(self._clear_selection)

    def _register_for_theming(self) -> None:
        """Theme manager regisztráció."""
        register_widget_for_theming(
            self.theme_manager,
            self,
            self.group,
            self.combo_box,
            self.clear_btn,
            self.info_label,
        )

    # === ANALYSIS MODE MANAGEMENT ===

    def set_analysis_mode(self, mode: str) -> None:
        """
        Analysis mode beállítása.

        Args:
            mode: "region" vagy "county"
        """
        if mode not in ["region", "county"]:
            print(f"❌ ERROR: Invalid analysis mode: {mode}")
            return

        if mode == self._current_mode:
            print(f"🔄 DEBUG: Mode already set to {mode}, skipping...")
            return  # Nincs változás

        print(f"🔄 DEBUG: Analysis mode váltás: {self._current_mode} → {mode}")

        self._current_mode = mode

        self._combo_handler.populate_combo_box(
            self._current_mode,
            self._available_regions,
            self._available_counties,
            self._selected_region,
            self._selected_county,
        )
        self._combo_handler.update_group_title(self._current_mode)
        self._combo_handler.update_info_label(
            self._current_mode, self._get_current_selection()
        )

        print(f"✅ DEBUG: Analysis mode váltás befejezve: {mode}")

    # === COMBO BOX SIGNAL HANDLER ===

    def _on_combo_selection_changed(self, text: str) -> None:
        """ComboBox selection változás kezelése."""
        if self._updating_state:
            print(f"⏸️ DEBUG: Skipping combo change (updating state): {text}")
            return

        current_index = self.combo_box.currentIndex()
        print(
            f"🔄 DEBUG: Combo selection changed - index: {current_index}, text: '{text}'"
        )

        # Placeholder választás (index 0) - törlés
        if current_index == 0:
            print("🔄 DEBUG: Placeholder selected - clearing selection")
            self._clear_current_selection()
            return

        # Érvényes választás
        selected_data = self.combo_box.currentData()
        print(f"✅ DEBUG: Valid selection - data: {selected_data}")

        if self._current_mode == "region":
            self._selected_region = selected_data
            self._selected_county = None  # Clear other mode
            print(f"🏞️ DEBUG: Régió kiválasztva: {self._selected_region}")

        elif self._current_mode == "county":
            self._selected_county = selected_data
            self._selected_region = None  # Clear other mode
            print(f"🏛️ DEBUG: Megye kiválasztva: {self._selected_county}")

        self._combo_handler.update_info_label(
            self._current_mode, self._get_current_selection()
        )
        self._update_clear_button()
        self._emit_selection_changed()
