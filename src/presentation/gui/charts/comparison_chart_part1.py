# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for MultiYearComparisonChart."""

from __future__ import annotations

from .comparison_chart_support import *


class MultiYearComparisonChartPart1Mixin:
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(figsize=(14, 8), parent=parent)
        self.chart_title = "📊 Évek Közötti Összehasonlítás"
        self.comparison_years = []  # Összehasonlítandó évek listája

    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🔧 KRITIKUS JAVÍTÁS: Duplikáció-mentes multi-year comparison frissítés + SIMPLIFIED THEMEMANAGER.
        """
        print(
            "📊 DEBUG: MultiYearComparisonChart.update_data() - DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER VERZIÓ"
        )

        try:
            if self._is_updating:
                return

            self._is_updating = True

            df = self._extract_yearly_data(data)
            if df.empty:
                print("⚠️ DEBUG: Üres DataFrame, comparison törlése")
                self.clear_chart()
                return

            self.current_data = df

            # === KRITIKUS: TELJES FIGURE TÖRLÉSE ===
            print("🧹 DEBUG: MultiYear Figure.clear() - DUPLIKÁCIÓ ELLEN")
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)

            # 🎨 TÉMA ALKALMAZÁSA
            self._apply_theme_to_chart()

            self._plot_multi_year_comparison(df)

            self.draw()
            self._is_updating = False

            print(
                "✅ DEBUG: MultiYearComparisonChart frissítés kész - DUPLIKÁCIÓ MENTES + THEMED"
            )

        except Exception as e:
            print(f"❌ DEBUG: Multi-year comparison chart hiba: {e}")
            self._is_updating = False
            self._plot_comparison_placeholder()

    def _extract_yearly_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Többévi adatok kinyerése - CSAK VALÓDI API ADATOKKAL."""
        daily_data = data.get("daily", {})
        dates = daily_data.get("time", [])
        temp_max = daily_data.get("temperature_2m_max", [])
        temp_min = daily_data.get("temperature_2m_min", [])
        temp_mean = build_temp_mean_fallback(
            temp_max, temp_min, daily_data.get("temperature_2m_mean", [])
        )

        if not has_complete_temperature_payload(dates, temp_max, temp_min, temp_mean):
            print("⚠️ DEBUG: Hiányzó többévi adatok - chart nem jeleníthető meg")
            return pd.DataFrame()

        if not has_matching_temperature_lengths(dates, temp_max, temp_min, temp_mean):
            print(
                "❌ DEBUG: Eltérő hosszúságú többévi adatok - chart nem jeleníthető meg"
            )
            return pd.DataFrame()

        df = pd.DataFrame(
            {
                "date": pd.to_datetime(dates),
                "temp_max": temp_max,
                "temp_min": temp_min,
                "temp_mean": temp_mean,  # CSAK VALÓDI API ADAT!
            }
        )

        # Év és nap az évben oszlopok - ezek valódi dátumból számoltak, OK
        df["year"] = df["date"].dt.year
        df["day_of_year"] = df["date"].dt.dayofyear
        df["month_day"] = df["date"].dt.strftime("%m-%d")

        # Csak érvényes adatok megtartása
        df = df.dropna()

        if df.empty:
            print("⚠️ DEBUG: Nincs érvényes többévi adat - chart nem jeleníthető meg")

        return df
