#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data Widgets - Data Handling Mixin
Adatkonverzió és update_data kezelése.
"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)


class DataHandlingMixin:
    """
    Adatkonverzió és update_data kezelése.
    """

    def update_data(self, data: Dict[str, Any]) -> None:
        """
        Táblázat adatainak frissítése - ROBUST HIBAKEZELÉSSEL.
        """
        try:
            logger.info(
                "🔄 WeatherDataTable.update_data() ELINDULT - ROBUST HIBAKEZELÉSSEL"
            )

            if not data:
                logger.error("❌ Üres adatok érkeztek a táblázatba!")
                self.clear_data()
                return

            if "daily" not in data:
                logger.error("❌ Hiányzik a 'daily' kulcs az adatokból!")
                self.clear_data()
                return

            logger.info(f"✅ Adatok szerkezete: {list(data.keys())}")
            logger.info(f"✅ Daily adatok: {list(data.get('daily', {}).keys())}")

            df = self._convert_to_dataframe(data)

            if df.empty:
                logger.error("❌ DataFrame konvertálás sikertelen vagy üres!")
                self.clear_data()
                return

            logger.info(
                f"✅ DataFrame létrehozva: {len(df)} sor, {len(df.columns)} oszlop"
            )
            logger.info(f"✅ Oszlopnevek: {list(df.columns)}")

            self.current_data = df
            self.filtered_data = df.copy()

            self.search_input.clear()
            self.column_filter.setCurrentText("Összes")
            self.current_page = 0
            self.page_spin.setValue(1)

            self.rows_per_page_combo.setCurrentText("Összes")
            self.rows_per_page = len(df)

            self.current_sort_column = -1
            self.current_sort_order = Qt.AscendingOrder

            self._update_pagination()
            self._display_current_page()

            self.csv_btn.setEnabled(True)
            self.excel_btn.setEnabled(True)

            logger.info(
                f"✅ WeatherDataTable.update_data() SIKERES! {len(df)} sor megjelenítve"
            )

        except Exception as e:
            logger.error(f"❌ WeatherDataTable.update_data() HIBA: {e}")
            logger.exception("Részletes hiba:")
            self.clear_data()

    def _convert_to_dataframe(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        API adatok DataFrame-mé konvertálása - ROBUST HIBAKEZELÉSSEL.
        """
        try:
            logger.info("🔄 _convert_to_dataframe() ELINDULT - ROBUST VERZIÓ")

            daily_data = data.get("daily", {})

            dates = daily_data.get("time", [])
            temp_max = daily_data.get("temperature_2m_max", [])
            temp_min = daily_data.get("temperature_2m_min", [])
            temp_mean = daily_data.get("temperature_2m_mean", [])
            precip = daily_data.get("precipitation_sum", [])
            windspeed = daily_data.get("windspeed_10m_max", [])

            data_lengths = {
                "dates": len(dates),
                "temp_max": len(temp_max),
                "temp_min": len(temp_min),
                "temp_mean": len(temp_mean),
                "precip": len(precip),
                "windspeed": len(windspeed),
            }

            logger.info(f"📊 Adathosszak: {data_lengths}")

            if not dates or len(dates) == 0:
                logger.error("❌ Nincs dátum adat!")
                return pd.DataFrame()

            if not temp_max or len(temp_max) == 0:
                logger.error("❌ Nincs maximum hőmérséklet adat!")
                return pd.DataFrame()

            base_length = len(dates)
            logger.info(f"✅ Alapvető hossz: {base_length} nap")

            def normalize_array(arr: List, target_length: int, fill_value=None) -> List:
                """Array normalizálása adott hosszra."""
                if len(arr) == target_length:
                    return arr
                elif len(arr) < target_length:
                    return arr + [fill_value] * (target_length - len(arr))
                else:
                    return arr[:target_length]

            dates_norm = normalize_array(dates, base_length)
            temp_max_norm = normalize_array(temp_max, base_length, None)
            temp_min_norm = normalize_array(temp_min, base_length, None)
            temp_mean_norm = normalize_array(temp_mean, base_length, None)
            precip_norm = normalize_array(precip, base_length, 0.0)
            windspeed_norm = normalize_array(windspeed, base_length, None)

            if not temp_mean or all(x is None for x in temp_mean_norm):
                logger.warning("⚠️ temperature_2m_mean hiányzik, fallback számításra...")
                temp_mean_norm = []
                for i in range(base_length):
                    if (
                        i < len(temp_max_norm)
                        and i < len(temp_min_norm)
                        and temp_max_norm[i] is not None
                        and temp_min_norm[i] is not None
                    ):
                        avg = (temp_max_norm[i] + temp_min_norm[i]) / 2
                        temp_mean_norm.append(round(avg, 1))
                    else:
                        temp_mean_norm.append(None)
                logger.info(f"🔄 Fallback számítás kész: {len(temp_mean_norm)} érték")
            else:
                logger.info(
                    f"✅ temperature_2m_mean használva: {len(temp_mean_norm)} érték"
                )

            df_data = {
                "date": dates_norm,
                "temp_max": temp_max_norm,
                "temp_min": temp_min_norm,
                "temp_mean": temp_mean_norm,
                "precipitation": precip_norm,
            }

            if windspeed_norm and any(x is not None for x in windspeed_norm):
                df_data["windspeed"] = windspeed_norm
                logger.info("✅ Szélsebesség adatok hozzáadva")
            else:
                logger.info("⚠️ Szélsebesség adatok hiányoznak")

            df = pd.DataFrame(df_data)

            if df.empty:
                logger.error("❌ Létrehozott DataFrame üres!")
                return pd.DataFrame()

            logger.info("✅ DataFrame sikeresen létrehozva:")
            logger.info(f"   - Sorok: {len(df)}")
            logger.info(f"   - Oszlopok: {len(df.columns)}")
            logger.info(f"   - Oszlopnevek: {list(df.columns)}")
            logger.info(f"   - Első 3 sor dátuma: {list(df['date'].head(3))}")

            return df

        except Exception as e:
            logger.error(f"❌ _convert_to_dataframe() HIBA: {e}")
            logger.exception("Részletes hiba:")
            return pd.DataFrame()

    def clear_data(self) -> None:
        """Táblázat törlése."""
        self.current_data = None
        self.filtered_data = None
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

        self.csv_btn.setEnabled(False)
        self.excel_btn.setEnabled(False)

        self.rows_per_page_combo.setCurrentText("Összes")
        self.rows_per_page = 1000

        self.current_sort_column = -1
        self.current_sort_order = Qt.AscendingOrder

        self._update_info_display(0, 0)

    def get_selected_row_data(self) -> Optional[Dict[str, Any]]:
        """Kiválasztott sor adatainak lekérdezése."""
        current_row = self.table.currentRow()
        if current_row >= 0 and self.filtered_data is not None:
            global_row = self.current_page * self.rows_per_page + current_row
            if global_row < len(self.filtered_data):
                row_data = self.filtered_data.iloc[global_row].to_dict()
                return row_data
        return None
