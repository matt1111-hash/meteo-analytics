#!/usr/bin/env python3
# mypy: ignore-errors

"""
Multi-City Widget - Combo Box Handler

🔄 ComboBox kezelés és state management

Képességek:
- ComboBox populate region/county mode alapján
- Selection restoration after populate
- Group title frissítése

Fájl: src/presentation/gui/panel_widgets/multi_city_widget/combo_handler.py
"""

from PySide6.QtWidgets import QComboBox, QGroupBox, QLabel

from .regional_data import get_counties_for_region


class ComboHandler:
    """
    ComboBox state és kezelés kezelése.

    Felelősség:
    - ComboBox populate aktuális mode alapján
    - Selection visszaállítás populate után
    - Group title és info label frissítése
    """

    def __init__(
        self,
        combo_box: QComboBox,
        group: QGroupBox,
        info_label: QLabel,
        apply_label_styling_fn,
    ):
        """
        ComboHandler inicializálása.

        Args:
            combo_box: QComboBox widget
            group: QGroupBox widget
            info_label: Info label widget
            apply_label_styling_fn: Label styling függvény
        """
        self.combo_box = combo_box
        self.group = group
        self.info_label = info_label
        self.apply_label_styling = apply_label_styling_fn

    def populate_combo_box(
        self,
        mode: str,
        available_regions: list[str],
        available_counties: list[str],
        selected_region: str | None,
        selected_county: str | None,
    ) -> None:
        """
        ComboBox feltöltése aktuális mode alapján.

        Args:
            mode: "region" vagy "county"
            available_regions: Régiók listája
            available_counties: Megyék listája
            selected_region: Kiválasztott régió
            selected_county: Kiválasztott megye
        """
        print(f"🔄 DEBUG: _populate_combo_box() started - mode: {mode}")

        try:
            self.combo_box.clear()

            # Első elem: placeholder
            if mode == "region":
                self.combo_box.addItem("-- Válasszon régiót --")

                # Régiók hozzáadása
                for region in available_regions:
                    counties = get_counties_for_region(region)
                    item_text = f"{region} ({len(counties)} megye)"
                    self.combo_box.addItem(item_text, region)  # userData = region név

                print(f"🏞️ DEBUG: ComboBox feltöltve {len(available_regions)} régióval")

            elif mode == "county":
                self.combo_box.addItem("-- Válasszon megyét --")

                # Megyék hozzáadása
                for county in available_counties:
                    item_text = f"{county} megye"
                    self.combo_box.addItem(item_text, county)  # userData = county név

                print(f"🏛️ DEBUG: ComboBox feltöltve {len(available_counties)} megyével")

            # ComboBox ENABLED állapot biztosítása
            self.combo_box.setEnabled(True)
            print(f"✅ DEBUG: ComboBox enabled state: {self.combo_box.isEnabled()}")

            # Selection restoration
            self.restore_selection(mode, selected_region, selected_county)

        except Exception as e:
            print(f"❌ ERROR: ComboBox populate hiba: {e}")

    def restore_selection(
        self, mode: str, selected_region: str | None, selected_county: str | None
    ) -> None:
        """
        Selection visszaállítása combo box populate után.

        Args:
            mode: "region" vagy "county"
            selected_region: Kiválasztott régió
            selected_county: Kiválasztott megye
        """
        if mode == "region" and selected_region:
            # Régió keresése és beállítása
            for i in range(1, self.combo_box.count()):  # Skip placeholder (index 0)
                if self.combo_box.itemData(i) == selected_region:
                    self.combo_box.setCurrentIndex(i)
                    print(f"🔄 DEBUG: Régió visszaállítva: {selected_region}")
                    break

        elif mode == "county" and selected_county:
            # Megye keresése és beállítása
            for i in range(1, self.combo_box.count()):  # Skip placeholder (index 0)
                if self.combo_box.itemData(i) == selected_county:
                    self.combo_box.setCurrentIndex(i)
                    print(f"🔄 DEBUG: Megye visszaállítva: {selected_county}")
                    break

    def update_group_title(self, mode: str) -> None:
        """
        Group box title frissítése mode szerint.

        Args:
            mode: "region" vagy "county"
        """
        if mode == "region":
            self.group.setTitle("🏞️ Régió Választó (Multi-City)")
        else:
            self.group.setTitle("🏛️ Megye Választó (Multi-City)")

    def update_info_label(self, mode: str, current_selection: str | None) -> None:
        """
        Info label frissítése.

        Args:
            mode: "region" vagy "county"
            current_selection: Aktuális kiválasztás
        """
        if not current_selection:
            if mode == "region":
                text = "Válasszon régiót az elemzéshez..."
            else:
                text = "Válasszon megyét az elemzéshez..."
            self.apply_label_styling(self.info_label, "secondary")
        else:
            display_text = self._get_selection_display_text(mode, current_selection)

            if mode == "region":
                text = f"🏞️ Kiválasztott régió: {display_text}"
            else:
                text = f"🏛️ Kiválasztott megye: {display_text}"

            self.apply_label_styling(self.info_label, "primary")

        self.info_label.setText(text)

    def _get_selection_display_text(self, mode: str, current_selection: str) -> str:
        """
        Kiválasztás megjelenítési szövege.

        Args:
            mode: "region" vagy "county"
            current_selection: Aktuális kiválasztás

        Returns:
            Megjelenítési szöveg
        """
        if mode == "region" and current_selection:
            counties = get_counties_for_region(current_selection)
            return f"{current_selection} ({len(counties)} megye)"
        elif mode == "county" and current_selection:
            return f"{current_selection} megye"
        else:
            return ""
