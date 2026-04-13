#!/usr/bin/env python3
# mypy: ignore-errors

"""
Precipitation Chart - Data Handler

📊 Adat kinyerés és frissítés

Képességek:
- Adatok kinyerése
- Chart frissítése

Fájl: src/presentation/gui/charts/precipitation_chart/data_handler.py
"""

from typing import TYPE_CHECKING, Any

import pandas as pd

if TYPE_CHECKING:
    pass


def _extract_precipitation_data(self, data: dict[str, Any]) -> pd.DataFrame:  # noqa: ARG001
    """
    Csapadék adatok kinyerése.

    Args:
        self: PrecipitationChart instance
        data: Bemeneti adatok

    Returns:
        DataFrame with precipitation data
    """
    daily_data = data.get("daily", {})
    dates = daily_data.get("time", [])
    precipitation = daily_data.get("precipitation_sum", [])

    if not dates or not precipitation:
        return pd.DataFrame()

    df = pd.DataFrame({"date": pd.to_datetime(dates), "precipitation": precipitation})

    return df


def update_data(self, data: dict[str, Any]) -> None:
    """
    🔧 KRITIKUS JAVÍTÁS: Duplikáció-mentes csapadék chart frissítés + SIMPLIFIED THEMEMANAGER.

    Args:
        self: PrecipitationChart instance
        data: Bemeneti adatok
    """
    from .plotting import _plot_precipitation

    print(
        "🌧️ DEBUG: PrecipitationChart.update_data() - DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER VERZIÓ"
    )

    try:
        if self._is_updating:
            return

        self._is_updating = True

        df = _extract_precipitation_data(self, data)
        if df.empty:
            print("⚠️ DEBUG: Üres DataFrame, csapadék chart törlése")
            self.clear_chart()
            return

        self.current_data = df

        # === KRITIKUS: TELJES FIGURE TÖRLÉSE ===
        print("🧹 DEBUG: Precipitation Figure.clear() - DUPLIKÁCIÓ ELLEN")
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)

        # 🎨 TÉMA ALKALMAZÁSA
        self._apply_theme_to_chart()

        _plot_precipitation(self, df)

        self.draw()
        self._is_updating = False

        print(
            "✅ DEBUG: PrecipitationChart frissítés kész - DUPLIKÁCIÓ MENTES + THEMED + TOOLTIP READY"
        )

    except Exception as e:
        print(f"❌ DEBUG: Csapadék chart hiba: {e}")
        self._is_updating = False
        self.clear_chart()
