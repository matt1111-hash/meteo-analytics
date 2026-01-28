#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - GUI Dialogs Module - THEMEMANAGER INTEGRÁLT VERZIÓ
Időjárási alkalmazás dialógus ablakokat tartalmazó modulja.

🎨 THEMEMANAGER INTEGRÁCIÓ:
- utils.StyleSheets import eltávolítva
- Widget regisztrációk automatikus styling-hoz
- Hardcoded CSS-ek minimalizálva
- Centralizált téma kezelés

Ez a modul tartalmazza az alkalmazás különböző dialógus ablakait,
elsősorban az extrém időjárási események megjelenítésére szolgáló
ExtremeWeatherDialog osztályt.

Portolva: PyQt5 → PySide6 + ThemeManager integráció
Architektúra: Moduláris design, centralizált styling

🔧 JAVÍTÁS: close_button attribute error megoldva
🔧 KRITIKUS JAVÍTÁS: Konstruktor típus hiba javítva QDialog → QWidget
🔧 IMPORT BUGFIX: QColor import hozzáadva
"""

from typing import Any, Dict, List, Optional

import pandas as pd
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .theme_manager import get_theme_manager, register_widget_for_theming
from .utils import GUIConstants


class ExtremeWeatherDialog(QDialog):
    """
    Extrém időjárási események megjelenítésére szolgáló dialógus ablak - THEMEMANAGER INTEGRÁLT.
    
    🎨 VÁLTOZÁSOK:
    - utils.StyleSheets függőség eltávolítva
    - Widget regisztrációk ThemeManager-ben
    - Automatikus téma kezelés
    - CSS minimalizálás
    
    🔧 BUGFIX:
    - close_button attribute error javítva
    - Widget referenciák megfelelően elmentve
    
    🔧 KRITIKUS JAVÍTÁS:
    - Konstruktor típus hiba: QDialog → QWidget (QMainWindow kompatibilitás)
    
    🔧 IMPORT BUGFIX:
    - QColor import hozzáadva (PySide6.QtGui)
    
    FUNKCIONALITÁS MEGTARTVA:
    - Napi és havi extrém értékek megjelenítése
    - Interaktív váltás napi/havi nézet között
    - Statisztikai számítások (max/min/átlag/hőingás)
    - Táblázatos megjelenítés
    """

    def __init__(self, parent: Optional[QWidget], data: Dict[str, Any], city_name: str):
        """
        Dialógus inicializálása - THEMEMANAGER VERZIÓ + KONSTRUKTOR JAVÍTÁS.
        
        Args:
            parent: Szülő widget (QWidget - QMainWindow kompatibilis!)
            data: Open-Meteo API válasz adatok
            city_name: Település neve
            
        🔧 KRITIKUS JAVÍTÁS: QDialog → QWidget típus a parent paraméterben
        Most már működik QMainWindow szülővel is!
        """
        super().__init__(parent)

        # ThemeManager singleton lekérdezése
        self._theme_manager = get_theme_manager()

        self.data = data
        self.city_name = city_name
        self.period_type = "daily"  # Alapértelmezett: napi adatok

        self._setup_window()
        self._init_ui()
        self._register_widgets_for_theming()
        self._calculate_extremes()

    def _setup_window(self) -> None:
        """Ablak alapbeállításai - THEMEMANAGER KOMPATIBILIS."""
        self.setWindowTitle(f"Extrém időjárási események - {self.city_name}")
        self.setMinimumSize(
            GUIConstants.DIALOG_MIN_WIDTH,
            GUIConstants.DIALOG_MIN_HEIGHT
        )

        # ThemeManager automatikus styling (szülő CSS öröklés helyett)

    def _init_ui(self) -> None:
        """UI elemek inicializálása - MINIMAL CSS APPROACH."""
        layout = QVBoxLayout(self)
        layout.setSpacing(GUIConstants.LAYOUT_SPACING)

        # Periódus kiválasztó panel
        period_group = self._create_period_selection_group()
        layout.addWidget(period_group)

        # Extrém értékek táblázata
        self.extreme_table = self._create_extreme_table()
        layout.addWidget(self.extreme_table)

        # Bezárás gomb - JAVÍTVA: self.close_button mentése
        self.close_button = self._create_close_button()
        layout.addWidget(self.close_button)

    def _create_period_selection_group(self) -> QGroupBox:
        """Periódus kiválasztó widget létrehozása - THEMEMANAGER KOMPATIBILIS."""
        period_group = QGroupBox("Időszak típusa")
        period_layout = QHBoxLayout(period_group)

        # Gomb csoport a kölcsönös kizáráshoz
        self.period_type_group = QButtonGroup()

        # Radio gombok
        self.daily_radio = QRadioButton("Napi adatok")
        self.monthly_radio = QRadioButton("Havi adatok")

        # Alapértelmezett kiválasztás
        self.daily_radio.setChecked(True)

        # Gombok hozzáadása a csoporthoz
        self.period_type_group.addButton(self.daily_radio)
        self.period_type_group.addButton(self.monthly_radio)

        # Layout-hoz adás
        period_layout.addWidget(self.daily_radio)
        period_layout.addWidget(self.monthly_radio)
        period_layout.addStretch()

        # Eseménykezelők
        self.daily_radio.toggled.connect(self._on_period_type_changed)
        self.monthly_radio.toggled.connect(self._on_period_type_changed)

        return period_group

    def _create_extreme_table(self) -> QTableWidget:
        """Extrém értékek táblázatának létrehozása - THEMEMANAGER KOMPATIBILIS."""
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Kategória", "Érték", "Dátum"])

        # Táblázat beállítások (stílus nélkül - ThemeManager kezeli)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.verticalHeader().setVisible(False)

        return table

    def _create_close_button(self) -> QPushButton:
        """
        Bezárás gomb létrehozása - THEMEMANAGER KOMPATIBILIS.
        
        🔧 JAVÍTÁS: Most már self.close_button-ként mentjük
        """
        close_button = QPushButton("Bezárás")
        close_button.clicked.connect(self.accept)
        close_button.setMinimumHeight(GUIConstants.BUTTON_HEIGHT)
        return close_button

    def _register_widgets_for_theming(self) -> None:
        """
        Widget-ek regisztrálása ThemeManager-ben.
        
        🔧 JAVÍTÁS: self.close_button most már létezik
        """
        print("🎨 DEBUG: Registering ExtremeWeatherDialog widgets for theming...")

        # Container widgets
        register_widget_for_theming(self, "dialog")

        # Radio button widgets (chart style)
        register_widget_for_theming(self.daily_radio, "chart")
        register_widget_for_theming(self.monthly_radio, "chart")

        # Table widget
        register_widget_for_theming(self.extreme_table, "table")

        # Button widget - JAVÍTVA: self.close_button referencia OK
        register_widget_for_theming(self.close_button, "button")

        print("✅ DEBUG: ExtremeWeatherDialog widgets registered for theming")

    def _on_period_type_changed(self) -> None:
        """Periódus típus változásának kezelése."""
        self.period_type = "daily" if self.daily_radio.isChecked() else "monthly"
        self._calculate_extremes()

    def _calculate_extremes(self) -> None:
        """
        Extrém időjárási értékek kiszámítása és táblázat frissítése.
        Delegálja a számítást a megfelelő privát metódushoz.
        """
        try:
            # Alapadatok kinyerése
            df = self._extract_weather_dataframe()
            if df.empty:
                self._show_no_data_message()
                return

            # Extrém értékek számítása a kiválasztott periódus alapján
            if self.period_type == "monthly":
                extremes = self._calculate_monthly_extremes(df)
            else:
                extremes = self._calculate_daily_extremes(df)

            # Táblázat feltöltése
            self._populate_extreme_table(extremes)

        except Exception as e:
            print(f"Hiba az extrém értékek kiszámítása közben: {e}")
            self._show_calculation_error()

    def _extract_weather_dataframe(self) -> pd.DataFrame:
        """
        Időjárási adatok kinyerése a raw API válaszból DataFrame formába.
        
        Returns:
            Feldolgozott DataFrame vagy üres DataFrame hiba esetén
        """
        try:
            daily_data = self.data.get("daily", {})

            # Alapadatok kinyerése
            dates = daily_data.get("time", [])
            temp_max = daily_data.get("temperature_2m_max", [])
            temp_min = daily_data.get("temperature_2m_min", [])
            precip = daily_data.get("precipitation_sum", [])
            windspeed = daily_data.get("windspeed_10m_max", [])

            # DataFrame létrehozása
            df = pd.DataFrame({
                'date': dates,
                'temp_max': temp_max,
                'temp_min': temp_min,
                'precipitation': precip,
                'windspeed': windspeed if windspeed else [None] * len(dates)
            })

            # Dátum oszlop konvertálása
            df['date_obj'] = pd.to_datetime(df['date'])
            df['year'] = df['date_obj'].dt.year
            df['month'] = df['date_obj'].dt.month
            df['formatted_date'] = df['date_obj'].dt.strftime('%Y-%m-%d')

            return df

        except Exception as e:
            print(f"Hiba az adatok kinyerése közben: {e}")
            return pd.DataFrame()

    def _calculate_daily_extremes(self, df: pd.DataFrame) -> List[Dict[str, str]]:
        """
        Napi extrém értékek számítása.
        
        Args:
            df: Időjárási adatok DataFrame
            
        Returns:
            Lista az extrém értékekről
        """
        extremes = []

        # Legmelegebb nap
        max_temp_idx = df['temp_max'].idxmax()
        extremes.append({
            'category': 'Legmelegebb nap',
            'value': f"{df.iloc[max_temp_idx]['temp_max']:.1f} °C",
            'date': df.iloc[max_temp_idx]['formatted_date']
        })

        # Leghidegebb nap
        min_temp_idx = df['temp_min'].idxmin()
        extremes.append({
            'category': 'Leghidegebb nap',
            'value': f"{df.iloc[min_temp_idx]['temp_min']:.1f} °C",
            'date': df.iloc[min_temp_idx]['formatted_date']
        })

        # Legnagyobb napi hőingás
        df['temp_range'] = df['temp_max'] - df['temp_min']
        max_range_idx = df['temp_range'].idxmax()
        extremes.append({
            'category': 'Legnagyobb napi hőingás',
            'value': f"{df.iloc[max_range_idx]['temp_range']:.1f} °C",
            'date': df.iloc[max_range_idx]['formatted_date']
        })

        # Legcsapadékosabb nap
        max_precip_idx = df['precipitation'].idxmax()
        extremes.append({
            'category': 'Legcsapadékosabb nap',
            'value': f"{df.iloc[max_precip_idx]['precipitation']:.1f} mm",
            'date': df.iloc[max_precip_idx]['formatted_date']
        })

        # Legszelesebb nap (ha van adat)
        if not df['windspeed'].isna().all():
            max_wind_idx = df['windspeed'].idxmax()
            extremes.append({
                'category': 'Legszelesebb nap',
                'value': f"{df.iloc[max_wind_idx]['windspeed']:.1f} km/h",
                'date': df.iloc[max_wind_idx]['formatted_date']
            })

        # Időszak átlaghőmérséklete
        avg_temp = (df['temp_max'].mean() + df['temp_min'].mean()) / 2
        extremes.append({
            'category': 'Időszak átlaghőmérséklete',
            'value': f"{avg_temp:.1f} °C",
            'date': '-'
        })

        return extremes

    def _calculate_monthly_extremes(self, df: pd.DataFrame) -> List[Dict[str, str]]:
        """
        Havi extrém értékek számítása.
        
        Args:
            df: Időjárási adatok DataFrame
            
        Returns:
            Lista az extrém értékekről
        """
        extremes = []

        # Havi aggregáció
        monthly_data = df.groupby(['year', 'month']).agg({
            'temp_max': 'max',
            'temp_min': 'min',
            'precipitation': 'sum',
            'windspeed': 'max' if not df['windspeed'].isna().all() else 'mean'
        }).reset_index()

        # Hónap nevek
        month_names = {
            1: 'Január', 2: 'Február', 3: 'Március', 4: 'Április',
            5: 'Május', 6: 'Június', 7: 'Július', 8: 'Augusztus',
            9: 'Szeptember', 10: 'Október', 11: 'November', 12: 'December'
        }

        monthly_data['month_name'] = monthly_data['month'].map(month_names)

        # Legmelegebb hónap (max hőmérséklet alapján)
        max_temp_idx = monthly_data['temp_max'].idxmax()
        extremes.append({
            'category': 'Legmelegebb hónap (max)',
            'value': f"{monthly_data.iloc[max_temp_idx]['temp_max']:.1f} °C",
            'date': f"{monthly_data.iloc[max_temp_idx]['month_name']} {monthly_data.iloc[max_temp_idx]['year']}"
        })

        # Leghidegebb hónap
        min_temp_idx = monthly_data['temp_min'].idxmin()
        extremes.append({
            'category': 'Leghidegebb hónap',
            'value': f"{monthly_data.iloc[min_temp_idx]['temp_min']:.1f} °C",
            'date': f"{monthly_data.iloc[min_temp_idx]['month_name']} {monthly_data.iloc[min_temp_idx]['year']}"
        })

        # Legcsapadékosabb hónap
        max_precip_idx = monthly_data['precipitation'].idxmax()
        extremes.append({
            'category': 'Legcsapadékosabb hónap',
            'value': f"{monthly_data.iloc[max_precip_idx]['precipitation']:.1f} mm",
            'date': f"{monthly_data.iloc[max_precip_idx]['month_name']} {monthly_data.iloc[max_precip_idx]['year']}"
        })

        # Legszelesebb hónap (ha van adat)
        if not df['windspeed'].isna().all():
            max_wind_idx = monthly_data['windspeed'].idxmax()
            extremes.append({
                'category': 'Legszelesebb hónap',
                'value': f"{monthly_data.iloc[max_wind_idx]['windspeed']:.1f} km/h",
                'date': f"{monthly_data.iloc[max_wind_idx]['month_name']} {monthly_data.iloc[max_wind_idx]['year']}"
            })

        # Időszak átlaghőmérséklete
        avg_temp = (df['temp_max'].mean() + df['temp_min'].mean()) / 2
        extremes.append({
            'category': 'Időszak átlaghőmérséklete',
            'value': f"{avg_temp:.1f} °C",
            'date': '-'
        })

        return extremes

    def _populate_extreme_table(self, extremes: List[Dict[str, str]]) -> None:
        """
        Extrém értékek táblázatának feltöltése - THEMEMANAGER SZÍNEKKEL.
        
        Args:
            extremes: Extrém értékek listája
        """
        self.extreme_table.setRowCount(len(extremes))

        # ThemeManager színek lekérdezése
        scheme = self._theme_manager.get_color_scheme()

        for i, extreme in enumerate(extremes):
            # Item-ek létrehozása
            category_item = QTableWidgetItem(extreme['category'])
            value_item = QTableWidgetItem(extreme['value'])
            date_item = QTableWidgetItem(extreme['date'])

            # ThemeManager színek alkalmazása item-ekre
            if scheme:
                # 🔧 KRITIKUS JAVÍTÁS: ColorPalette API helyes használata
                # Alternáló háttérszínek
                if i % 2 == 0:
                    bg_color = QColor(scheme.get_color("surface", "base") or "#ffffff")
                else:
                    bg_color = QColor(scheme.get_color("surface", "light") or "#f5f5f5")

                # Szövegszín
                text_color = QColor(scheme.get_color("primary", "base") or "#000000")

                for item in [category_item, value_item, date_item]:
                    item.setBackground(bg_color)
                    item.setForeground(text_color)

            # Táblázat feltöltése
            self.extreme_table.setItem(i, 0, category_item)
            self.extreme_table.setItem(i, 1, value_item)
            self.extreme_table.setItem(i, 2, date_item)

        # Oszlopok szélességének automatikus beállítása
        self.extreme_table.resizeColumnsToContents()

    def _show_no_data_message(self) -> None:
        """Nincs adat üzenet megjelenítése."""
        self.extreme_table.setRowCount(1)
        self.extreme_table.setItem(0, 0, QTableWidgetItem("Nincs megjeleníthető adat"))
        self.extreme_table.setItem(0, 1, QTableWidgetItem("-"))
        self.extreme_table.setItem(0, 2, QTableWidgetItem("-"))

    def _show_calculation_error(self) -> None:
        """Számítási hiba üzenet megjelenítése."""
        self.extreme_table.setRowCount(1)
        self.extreme_table.setItem(0, 0, QTableWidgetItem("Hiba a számítás során"))
        self.extreme_table.setItem(0, 1, QTableWidgetItem("Ellenőrizze az adatokat"))
        self.extreme_table.setItem(0, 2, QTableWidgetItem("-"))

    def apply_theme(self, dark_theme: bool) -> None:
        """
        Téma alkalmazása - THEMEMANAGER DELEGÁLÓ VERZIÓ.
        
        Args:
            dark_theme: True, ha sötét téma
        """
        print(f"🎨 DEBUG: ExtremeWeatherDialog applying theme via ThemeManager: {'dark' if dark_theme else 'light'}")

        # ThemeManager automatikus widget styling
        theme_name = "dark" if dark_theme else "light"
        self._theme_manager.set_theme(theme_name)

        # Ha van extrém adat, újrarajzoljuk a táblázatot ThemeManager színekkel
        if hasattr(self, 'extreme_table') and self.extreme_table.rowCount() > 0:
            # Re-populate with current data to apply new colors
            self._calculate_extremes()

        print(f"✅ DEBUG: ExtremeWeatherDialog theme applied via ThemeManager: {'dark' if dark_theme else 'light'}")
