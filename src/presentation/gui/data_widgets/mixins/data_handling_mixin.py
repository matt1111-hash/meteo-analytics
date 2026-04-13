#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Data Widgets - Data Handling Mixin
Adatkonverzió és update_data kezelése.
"""

import logging
from typing import Any

import pandas as pd
from PySide6.QtCore import Qt

from .data_handling_support import (
    build_dataframe_payload,
    log_dataframe_summary,
    log_mean_source,
    validate_required_daily_data,
)

logger = logging.getLogger(__name__)


class DataHandlingMixin:
    """
    Adatkonverzió és update_data kezelése.
    """

    def update_data(self, data: dict[str, Any]) -> None:
        """
        Táblázat adatainak frissítése - ROBUST HIBAKEZELÉSSEL.
        """
        try:
            logger.info("🔄 WeatherDataTable.update_data() ELINDULT - ROBUST HIBAKEZELÉSSEL")

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

            logger.info(f"✅ DataFrame létrehozva: {len(df)} sor, {len(df.columns)} oszlop")
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

            logger.info(f"✅ WeatherDataTable.update_data() SIKERES! {len(df)} sor megjelenítve")

        except Exception as e:
            logger.error(f"❌ WeatherDataTable.update_data() HIBA: {e}")
            logger.exception("Részletes hiba:")
            self.clear_data()

    def _convert_to_dataframe(self, data: dict[str, Any]) -> pd.DataFrame:
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

            if not validate_required_daily_data(dates, temp_max):
                return pd.DataFrame()

            base_length = len(dates)
            logger.info(f"✅ Alapvető hossz: {base_length} nap")
            df_data = build_dataframe_payload(daily_data, base_length)
            if "windspeed" in df_data:
                logger.info("✅ Szélsebesség adatok hozzáadva")
            else:
                logger.info("⚠️ Szélsebesség adatok hiányoznak")
            log_mean_source(temp_mean, df_data)

            df = pd.DataFrame(df_data)

            if df.empty:
                logger.error("❌ Létrehozott DataFrame üres!")
                return pd.DataFrame()

            log_dataframe_summary(df)
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

    def get_selected_row_data(self) -> dict[str, Any] | None:
        """Kiválasztott sor adatainak lekérdezése."""
        current_row = self.table.currentRow()
        if current_row >= 0 and self.filtered_data is not None:
            global_row = self.current_page * self.rows_per_page + current_row
            if global_row < len(self.filtered_data):
                row_data = self.filtered_data.iloc[global_row].to_dict()
                return row_data
        return None
