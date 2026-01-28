#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Wind Gusts Chart
Széllökés grafikon widget professzionális vizualizációval.

🌪️ MAGYAR METEOROLÓGIAI SZABVÁNY: 43-61-90-119 km/h küszöbök
🎨 TÉMA INTEGRÁCIÓ: ColorPalette wind színek használata
🔧 KRITIKUS JAVÍTÁS: Magyar szélsebesség-kategóriák + SIMPLIFIED THEMEMANAGER
🎯 TOOLTIP INTEGRÁCIÓ: WeatherTooltipMixin - MAGYAR METEOROLÓGIAI TARTALOM!
✅ wind_gusts_10m_max prioritás → windspeed_10m_max fallback rendszer
✅ Magyar szélkategóriák: Erős szél (43), Viharos szél (61), Erős vihar (90), Orkán (119)
✅ Piros (#C43939) téma támogatás
✅ Élethi széllökés megjelenítés VALÓDI API adatokkal
✅ Professzionális kategorizálás magyar terminológiával
✅ INTERAKTÍV TOOLTIP FUNKCIÓK: Beaufort skála + széljárás leírások
🚨 KRITIKUS DEBUG: Explicit konzol üzenetek minden lépésnél
🎯 VÉGSŐ JAVÍTÁS: has_valid_data() - ellenőrzi van-e valódi adat a None-ok helyett!
🔧 KRITIKUS FIX v4.7: API KULCSOK KONZISZTENCIA JAVÍTÁS!
"""

from datetime import datetime
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, MonthLocator
from PySide6.QtWidgets import QWidget

from ..theme_manager import get_current_colors
from .base_chart import WeatherChart
from .tooltip_mixin import WeatherTooltipMixin  # 🎯 TOOLTIP MIXIN IMPORT


class WindChart(WeatherChart, WeatherTooltipMixin):  # 🎯 MIXIN HOZZÁADÁSA
    """
    🌪️ KRITIKUS DEBUG: MAGYAR METEOROLÓGIAI SZABVÁNY: Széllökés grafikon widget - MAGYAR SZÉLKATEGÓRIÁK + SIMPLIFIED THEMEMANAGER + TOOLTIP.
    🎨 TÉMA INTEGRÁCIÓ: ColorPalette wind színek használata
    🎯 TOOLTIP ENHANCEMENT: WeatherTooltipMixin integráció - MAGYAR METEOROLÓGIAI TARTALOM
    ✅ wind_gusts_10m_max prioritás → windspeed_10m_max fallback rendszer
    ✅ Magyar szélkategóriák: Erős szél (43), Viharos szél (61), Erős vihar (90), Orkán (119)
    ✅ Élethi széllökés megjelenítés VALÓDI API adatokkal
    🚨 EXPLICIT DEBUG minden lépésnél
    🎯 VÉGSŐ JAVÍTÁS: has_valid_data() - ellenőrzi van-e valódi adat!
    🔧 KRITIKUS FIX v4.7: API kulcsok konzisztencia javítása!
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(figsize=(12, 6), parent=parent)
        self.chart_title = "🌪️ Széllökések változása"  # 🌪️ WIND GUSTS CÍM
        self.y_label = "Széllökések (km/h)"  # 🌪️ WIND GUSTS LABEL

        # 🎯 TOOLTIP AKTIVÁLÁS - OPT-IN RENDSZER
        self.enable_tooltips(hover_tolerance=15)
        print("🎯 DEBUG: WindChart tooltip-ok aktiválva!")
        print("🌪️ DEBUG: WindChart.__init__() SIKERES!")

    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🚨 KRITIKUS DEBUG: Duplikáció-mentes szél chart frissítés + SIMPLIFIED THEMEMANAGER + EXPLICIT DEBUG.
        """
        print("🌪️ DEBUG: WindChart.update_data() - EXPLICIT DEBUG VERZIÓ STARTED!!!")
        print(f"🌪️ DEBUG: Input data type: {type(data)}")
        print(f"🌪️ DEBUG: Input data keys: {list(data.keys()) if isinstance(data, dict) else 'NOT DICT'}")

        try:
            if self._is_updating:
                print("🌪️ DEBUG: WindChart already updating, skipping...")
                return

            print("🌪️ DEBUG: Setting _is_updating = True")
            self._is_updating = True

            print("🌪️ DEBUG: Calling _extract_wind_data()...")
            df = self._extract_wind_data(data)
            print(f"🌪️ DEBUG: _extract_wind_data() returned DataFrame with {len(df) if not df.empty else 0} rows")

            if df.empty:
                print("⚠️ DEBUG: Üres DataFrame, szél chart törlése")
                self.clear_chart()
                print("🌪️ DEBUG: WindChart.update_data() FINISHED - EMPTY DATA")
                self._is_updating = False
                return

            print("🌪️ DEBUG: Setting self.current_data...")
            self.current_data = df
            print(f"🌪️ DEBUG: self.current_data set successfully, type: {type(self.current_data)}")

            # === KRITIKUS: TELJES FIGURE TÖRLÉSE ===
            print("🧹 DEBUG: Wind Figure.clear() - DUPLIKÁCIÓ ELLEN")
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)

            # 🎨 TÉMA ALKALMAZÁSA
            print("🎨 DEBUG: Applying theme to WindChart...")
            self._apply_theme_to_chart()

            print("📊 DEBUG: Calling _plot_wind()...")
            self._plot_wind(df)

            print("🖼️ DEBUG: Calling draw()...")
            self.draw()

            print("🌪️ DEBUG: Setting _is_updating = False")
            self._is_updating = False

            print("✅ DEBUG: WindChart frissítés TELJESEN KÉSZ - MAGYAR SZABVÁNY + THEMED + TOOLTIP READY")

        except Exception as e:
            print(f"❌ DEBUG: Szél chart hiba: {e}")
            import traceback
            print(f"❌ DEBUG: WindChart traceback: {traceback.format_exc()}")
            self._is_updating = False
            self.clear_chart()

    def _extract_wind_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        🚨 KRITIKUS DEBUG: Széllökés adatok kinyerése - WIND GUSTS PRIORITÁS + FALLBACK + EXPLICIT DEBUG.
        🎯 VÉGSŐ JAVÍTÁS: has_valid_data() segédfüggvény - ellenőrzi van-e valódi adat!
        🔧 KRITIKUS FIX v4.7: API KULCSOK KONZISZTENCIA JAVÍTÁS!
        
        PRIORITÁS RENDSZER:
        1. wind_gusts_10m_max (óránkénti→napi max széllökések) ⭐ ELSŐDLEGES
        2. windspeed_10m_max (napi max szélsebesség) ⭐ FALLBACK
        3. Hibaüzenet ha egyik sem elérhető
        """
        print("🌪️ DEBUG: _extract_wind_data() STARTED!!!")
        print(f"🌪️ DEBUG: data type: {type(data)}")

        daily_data = data.get("daily", {})
        print(f"🌪️ DEBUG: daily_data type: {type(daily_data)}")
        print(f"🌪️ DEBUG: daily_data keys: {list(daily_data.keys()) if isinstance(daily_data, dict) else 'NOT DICT'}")

        dates = daily_data.get("time", [])
        print(f"🌪️ DEBUG: dates: {len(dates) if dates else 0} elems")

        # 🔧 KRITIKUS FIX v4.7: API KULCSOK KONZISZTENCIA JAVÍTÁS!
        # ✅ HELYES KULCSOK - weather_client.py-val konzisztens
        wind_gusts_10m_max = daily_data.get("wind_gusts_10m_max", [])  # ✅ JAVÍTOTT: windgusts_10m_max → wind_gusts_10m_max
        windspeed_10m_max = daily_data.get("windspeed_10m_max", [])  # Fallback

        print(f"🌪️ DEBUG: wind_gusts_10m_max: {len(wind_gusts_10m_max) if wind_gusts_10m_max else 0} elems")
        print(f"🌪️ DEBUG: windspeed_10m_max: {len(windspeed_10m_max) if windspeed_10m_max else 0} elems")

        if wind_gusts_10m_max:
            print(f"🌪️ DEBUG: wind_gusts_10m_max sample: {wind_gusts_10m_max[:3] if len(wind_gusts_10m_max) >= 3 else wind_gusts_10m_max}")
        if windspeed_10m_max:
            print(f"🌪️ DEBUG: windspeed_10m_max sample: {windspeed_10m_max[:3] if len(windspeed_10m_max) >= 3 else windspeed_10m_max}")

        print(f"🌪️ DEBUG: WindChart data sources - wind_gusts_10m_max: {len(wind_gusts_10m_max) if wind_gusts_10m_max else 0}, windspeed_10m_max: {len(windspeed_10m_max) if windspeed_10m_max else 0}")

        # Elérhető adatok ellenőrzése
        if not dates:
            print("⚠️ DEBUG: Nincs dátum adat - WindChart nem jeleníthető meg")
            return pd.DataFrame()

        # 🎯 OKOS SEGÉDFÜGGVÉNY - ellenőrzi van-e valódi adat
        def has_valid_data(data_list):
            """Ellenőrzi, hogy van-e valódi szám adat a listában (nem csak None-ok)"""
            return any(x is not None and isinstance(x, (int, float)) for x in data_list)

        # PRIORITÁS KIÉRTÉKELÉS
        windspeed_data = []
        data_source = ""

        print("🌪️ DEBUG: Checking wind_gusts_10m_max priority...")
        if wind_gusts_10m_max and len(wind_gusts_10m_max) == len(dates) and has_valid_data(wind_gusts_10m_max):
            # 🌪️ ELSŐDLEGES: wind_gusts_10m_max, CSAK HA VAN BENNE ÉRVÉNYES ADAT
            windspeed_data = wind_gusts_10m_max
            data_source = "wind_gusts_10m_max"
            self.chart_title = "🌪️ Széllökések változása"
            self.y_label = "Széllökések (km/h)"
            print(f"✅ DEBUG: WindChart using PRIMARY source: {data_source}")
        elif windspeed_10m_max and len(windspeed_10m_max) == len(dates) and has_valid_data(windspeed_10m_max):
            # ⚠️ FALLBACK: windspeed_10m_max használata
            print("🌪️ DEBUG: wind_gusts_10m_max not suitable, checking fallback...")
            windspeed_data = windspeed_10m_max
            data_source = "windspeed_10m_max"
            self.chart_title = "💨 Szélsebesség változása (Fallback)"
            self.y_label = "Szélsebesség (km/h)"
            print(f"⚠️ DEBUG: WindChart using FALLBACK source: {data_source}")
        else:
            print("❌ DEBUG: Nincs használható szél adat - WindChart nem jeleníthető meg")
            print(f"   - wind_gusts_10m_max: {len(wind_gusts_10m_max) if wind_gusts_10m_max else 0} elem, has_valid_data: {has_valid_data(wind_gusts_10m_max) if wind_gusts_10m_max else False}")
            print(f"   - windspeed_10m_max: {len(windspeed_10m_max) if windspeed_10m_max else 0} elem, has_valid_data: {has_valid_data(windspeed_10m_max) if windspeed_10m_max else False}")
            print(f"   - dates: {len(dates)} elem")
            return pd.DataFrame()

        print(f"🌪️ DEBUG: Creating DataFrame with {len(windspeed_data)} wind values and {len(dates)} dates...")

        # DataFrame létrehozása
        df = pd.DataFrame({
            'date': pd.to_datetime(dates),
            'windspeed': windspeed_data,
            '_data_source': data_source  # Debug info
        })

        print(f"🌪️ DEBUG: DataFrame created, shape: {df.shape}")

        # NaN értékek kezelése
        print("🌪️ DEBUG: Dropping NaN values...")
        df_before = len(df)
        df = df.dropna()
        df_after = len(df)
        print(f"🌪️ DEBUG: DataFrame after dropna: {df_before} -> {df_after} rows")

        if df.empty:
            print(f"❌ DEBUG: Üres DataFrame {data_source} adatok után - WindChart nem jeleníthető meg")
        else:
            max_wind = df['windspeed'].max()
            avg_wind = df['windspeed'].mean()
            print(f"✅ DEBUG: WindChart DataFrame KÉSZ - {data_source}, max: {max_wind:.1f} km/h, avg: {avg_wind:.1f} km/h")

        print("🌪️ DEBUG: _extract_wind_data() FINISHED!")
        return df

    def _plot_wind(self, df: pd.DataFrame) -> None:
        """
        🌪️ MAGYAR METEOROLÓGIAI SZABVÁNY: Széllökés grafikon rajzolása - MAGYAR SZÉLKATEGÓRIÁK + SIMPLIFIED THEMEMANAGER.
        🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ: ColorPalette wind színek használata
        ✅ Magyar szélkategóriák: Erős szél (43), Viharos szél (61), Erős vihar (90), Orkán (119)
        """
        print("🎨 DEBUG: _plot_wind() - MAGYAR SZÉLKATEGÓRIÁK + SIMPLIFIED THEMEMANAGER")

        # 🔧 KRITIKUS JAVÍTÁS: HELYES API HASZNÁLAT - magyar szélkategória színek
        wind_colors = {
            'moderate': self.color_palette.get_color('success', 'base') or '#10b981',      # Gyenge-mérsékelt szél
            'light': self.color_palette.get_color('success', 'light') or '#86efac',       # Kitöltés szín
            'strong': self.color_palette.get_color('warning', 'base') or '#f59e0b',       # Erős szél (43)
            'stormy': self.color_palette.get_color('warning', 'dark') or '#d97706',       # Viharos szél (61)
            'severe_storm': self.color_palette.get_color('error', 'light') or '#f87171',  # Erős vihar (90)
            'hurricane': self.color_palette.get_color('error', 'base') or '#dc2626'       # Orkán (119)
        }

        # Weather színpaletta integrálása
        weather_wind_color = self.weather_colors.get('wind', '#10b981')
        wind_colors['moderate'] = weather_wind_color

        current_colors = get_current_colors()

        print(f"🎨 DEBUG: Using Magyar szabvány wind colors: {wind_colors}")

        # Adatforrás ellenőrzése
        data_source = df['_data_source'].iloc[0] if '_data_source' in df.columns else 'unknown'

        # === SZÉLLÖKÉS VONAL + TERÜLET DIAGRAM ===

        # Alapvonal és kitöltés
        line_label = "Max széllökések" if data_source == "wind_gusts_10m_max" else "Max szélsebesség (fallback)"
        self.ax.plot(df['date'], df['windspeed'], color=wind_colors['moderate'], linewidth=2.5, alpha=0.9, label=line_label)
        self.ax.fill_between(df['date'], 0, df['windspeed'], alpha=0.3, color=wind_colors['light'])

        # === 🌪️ MAGYAR METEOROLÓGIAI SZABVÁNY - SZÉLKATEGÓRIÁK ===

        max_wind = df['windspeed'].max() if not df.empty else 50

        # 43 km/h - Erős szél (magyar szabvány szerint)
        if max_wind >= 30:  # Csak akkor jelenítsük meg, ha releváns
            self.ax.axhline(y=43, color=wind_colors['strong'], linestyle='--', alpha=0.8, linewidth=2,
                           label='🌬️ Erős szél (43 km/h)')

        # 61 km/h - Viharos szél (magyar szabvány)
        if max_wind >= 45:
            self.ax.axhline(y=61, color=wind_colors['stormy'], linestyle='--', alpha=0.8, linewidth=2,
                           label='🌪️ Viharos szél (61 km/h)')

        # 90 km/h - Erős vihar (magyar szabvány)
        if max_wind >= 70:
            self.ax.axhline(y=90, color=wind_colors['severe_storm'], linestyle='--', alpha=0.8, linewidth=2,
                           label='⚠️ Erős vihar (90 km/h)')

        # 119 km/h - Orkán (magyar szabvány)
        if max_wind >= 100:
            self.ax.axhline(y=119, color=wind_colors['hurricane'], linestyle='--', alpha=0.9, linewidth=2.5,
                           label='🚨 Orkán (119 km/h)')

        # === MAGYAR SZÉLKATEGÓRIÁK ANNOTÁCIÓ ===

        # Maximum széllökés kiemelése magyar kategóriával
        if not df.empty:
            max_wind_idx = df['windspeed'].idxmax()
            max_wind_date = df.loc[max_wind_idx, 'date']
            max_wind_val = df.loc[max_wind_idx, 'windspeed']

            # Magyar kategorizálás
            if max_wind_val >= 119:
                category_icon = "🚨"
                category_text = "ORKÁN"
                annotation_color = wind_colors['hurricane']
            elif max_wind_val >= 90:
                category_icon = "⚠️"
                category_text = "ERŐS VIHAR"
                annotation_color = wind_colors['severe_storm']
            elif max_wind_val >= 61:
                category_icon = "🌪️"
                category_text = "VIHAROS SZÉL"
                annotation_color = wind_colors['stormy']
            elif max_wind_val >= 43:
                category_icon = "🌬️"
                category_text = "ERŐS SZÉL"
                annotation_color = wind_colors['strong']
            else:
                category_icon = "💨"
                category_text = "MÉRSÉKELT SZÉL"
                annotation_color = wind_colors['moderate']

            # Annotáció a csúcsponthoz
            self.ax.annotate(f'{category_icon} {max_wind_val:.1f} km/h\n({category_text})',
                            xy=(max_wind_date, max_wind_val),
                            xytext=(15, 25), textcoords='offset points',
                            bbox=dict(boxstyle='round,pad=0.5', facecolor=current_colors.get('surface_variant', '#f9fafb'),
                                     edgecolor=annotation_color, alpha=0.9),
                            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2', color=annotation_color, lw=2))

        # Formázás
        self._format_wind_chart(df)

    def _format_wind_chart(self, df: pd.DataFrame) -> None:
        """Szél chart formázása + SIMPLIFIED THEMEMANAGER."""
        # 🔧 SIMPLIFIED THEMEMANAGER SZÍNEK
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')

        self.ax.set_title(self.chart_title, fontweight='bold', pad=20, color=text_color)
        self.ax.set_xlabel(self.x_label, color=text_color)
        self.ax.set_ylabel(self.y_label, color=text_color)

        # Tick színek
        self.ax.tick_params(colors=text_color)

        # Dátum formázás
        self.ax.xaxis.set_major_locator(MonthLocator())
        self.ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))

        # Y tengely formázás - magyar szélkategóriákhoz optimalizált
        max_wind = df['windspeed'].max() if not df.empty else 50

        # Y-tengely tartomány optimalizálása magyar küszöbökhöz
        if max_wind >= 119:
            y_max = max_wind * 1.1  # Orkán feletti értékekhez
        elif max_wind >= 90:
            y_max = 130  # Orkán küszöbig
        elif max_wind >= 61:
            y_max = 100  # Erős vihar küszöbig
        elif max_wind >= 43:
            y_max = 75   # Viharos szél küszöbig
        else:
            y_max = 55   # Erős szél küszöbig

        self.ax.set_ylim(0, y_max)

        # Grid és legend + SIMPLIFIED THEMEMANAGER
        if self.grid_enabled:
            grid_color = current_colors.get('border', '#d1d5db')
            grid_alpha = 0.3 if self.theme_manager.get_current_theme() == "light" else 0.2
            self.ax.grid(True, alpha=grid_alpha, linestyle='-', linewidth=0.5, color=grid_color)

        if self.legend_enabled:
            legend = self.ax.legend(loc='upper left', framealpha=0.9)
            legend.get_frame().set_facecolor(current_colors.get('surface', '#ffffff'))
            legend.get_frame().set_edgecolor(current_colors.get('border', '#d1d5db'))

        # Layout optimalizálás
        self.figure.autofmt_xdate()
        self.figure.tight_layout()

        print("✅ DEBUG: Wind chart formázva + TOOLTIP READY")

    def _find_closest_chart_point(self, event) -> Optional[Dict[str, Any]]:
        """
        🎯 WIND CHART SPECIFIKUS PONT KERESÉS - TOOLTIP MIXIN OVERRIDE
        
        🔧 WIND CHART KOMPATIBILITÁS:
        - windspeed oszlop kezelése
        - Pixel-based távolság számítás
        - Professional wind tooltip adatok
        """
        try:
            if not hasattr(self, 'current_data') or self.current_data is None or self.current_data.empty:
                return None

            df = self.current_data

            # Matplotlib dátum koordináták
            if 'date' not in df.columns or 'windspeed' not in df.columns:
                return None

            import matplotlib.dates as mdates
            plot_dates = mdates.date2num(df['date'])
            windspeeds = df['windspeed']

            # Mouse pozíció display koordinátákban
            mouse_x_display, mouse_y_display = self.ax.transData.transform((event.xdata, event.ydata))

            closest_idx = None
            min_distance = float('inf')

            # Minden adatponthoz távolság számítás
            for i, (x_val, y_val) in enumerate(zip(plot_dates, windspeeds)):
                if pd.isna(y_val):  # Skip NaN values
                    continue

                # Adatpont display koordinátái
                point_x_display, point_y_display = self.ax.transData.transform((x_val, y_val))

                # Pixel távolság
                distance = np.sqrt((mouse_x_display - point_x_display)**2 +
                                 (mouse_y_display - point_y_display)**2)

                if distance < min_distance:
                    min_distance = distance
                    closest_idx = i

            # Tolerance check
            if closest_idx is not None and min_distance <= self._hover_tolerance:

                # Pont adatok összeállítása - WIND SPECIFIKUS
                point_data = {
                    'index': closest_idx,
                    'date': df.iloc[closest_idx]['date'],
                    'windspeed': df.iloc[closest_idx]['windspeed'],
                    'primary_temp': df.iloc[closest_idx]['windspeed'],  # Mixin kompatibilitás
                    'primary_temp_column': 'windspeed',                # Mixin kompatibilitás
                    'pixel_distance': min_distance,
                    'data_source': df.iloc[closest_idx]['_data_source'] if '_data_source' in df.columns else 'unknown',
                    'chart_type': 'wind'
                }

                return point_data

        except Exception as e:
            print(f"⚠️ DEBUG: Wind point calculation error: {e}")

        return None

    def _format_tooltip_text(self, point_data: Dict[str, Any]) -> str:
        """
        📝 WIND CHART TOOLTIP FORMÁZÁS
        
        💨 PROFESSIONAL WIND TOOLTIP:
        - Magyar szélkategóriák és Beaufort skála
        - Széljárás leírások
        - Meteorológiai hatások
        - Magyar weather ikonok
        """
        date = point_data['date']
        windspeed = point_data['windspeed']
        data_source = point_data.get('data_source', 'unknown')

        # Dátum formázás
        if isinstance(date, datetime):
            date_str = date.strftime('%Y-%m-%d (%A)')
        else:
            date_str = str(date)

        # 💨 MAGYAR SZÉLKATEGÓRIÁK ÉS BEAUFORT SKÁLA
        if windspeed >= 119:
            wind_icon = "🚨"
            category = "ORKÁN"
            beaufort = "12"
            description = "Pusztító szélerő"
            effects = "🏠 Épületek rongálódnak, fák kidőlnek"
            intensity = "Rendkívül veszélyes"
        elif windspeed >= 90:
            wind_icon = "⚠️"
            category = "Erős vihar"
            beaufort = "10-11"
            description = "Heves viharos szél"
            effects = "🌳 Nagy fák törnek, tetőcserepek repülnek"
            intensity = "Nagyon veszélyes"
        elif windspeed >= 61:
            wind_icon = "🌪️"
            category = "Viharos szél"
            beaufort = "8-9"
            description = "Viharos erősségű szél"
            effects = "🚗 Járművezetés nehéz, ágak törnek"
            intensity = "Veszélyes"
        elif windspeed >= 43:
            wind_icon = "🌬️"
            category = "Erős szél"
            beaufort = "6-7"
            description = "Erős széljárás"
            effects = "☂️ Esernyő nehezen használható"
            intensity = "Figyelmeztető"
        elif windspeed >= 28:
            wind_icon = "💨"
            category = "Mérsékelt szél"
            beaufort = "4-5"
            description = "Élénk széljárás"
            effects = "🍃 Por és papír felemelkedik"
            intensity = "Mérsékelt"
        elif windspeed >= 12:
            wind_icon = "🌱"
            category = "Gyenge szél"
            beaufort = "2-3"
            description = "Gyenge széljárás"
            effects = "🌿 Levelek mozognak, zászlók lengnek"
            intensity = "Kellemes"
        elif windspeed >= 1:
            wind_icon = "🍃"
            category = "Szellő"
            beaufort = "1"
            description = "Alig érezhető szellő"
            effects = "🌾 Füst iránya látható"
            intensity = "Gyenge"
        else:
            wind_icon = "😴"
            category = "Szélcsend"
            beaufort = "0"
            description = "Nincs légmozgás"
            effects = "🕯️ Láng egyenesen ég"
            intensity = "Nincs szél"

        # 📊 SZÉLMÉRÉS TÍPUSA
        measurement_type = "Széllökések" if data_source == "wind_gusts_10m_max" else "Szélsebesség (átlag)"
        measurement_icon = "⚡" if data_source == "wind_gusts_10m_max" else "🌀"

        # 🧭 SZÉLJÁRÁS RÉSZLETEK
        wind_details = []

        if windspeed > 50:
            wind_details.append("🏠 Épületek beltéri tartózkodás ajánlott")
            wind_details.append("🚫 Kültéri tevékenység kerülendő")
        elif windspeed > 30:
            wind_details.append("🚗 Óvatos közlekedés szükséges")
            wind_details.append("🌳 Fákra figyeljen")
        elif windspeed > 15:
            wind_details.append("🥾 Kültéri sportokhoz alkalmas")
            wind_details.append("⛵ Vitorlázáshoz jó körülmények")
        elif windspeed > 5:
            wind_details.append("🚴 Kerékpározáshoz ideális")
            wind_details.append("🏃 Futáshoz kellemes")

        # Tooltip szöveg összeállítása
        tooltip_lines = [
            f"📅 {date_str}",
            "",  # Üres sor a strukturáláshoz
            f"{wind_icon} {measurement_type}: {windspeed:.1f} km/h",
            f"🏷️ {category}",
            f"📊 Beaufort skála: {beaufort}",
            f"🌬️ {description}",
            "",
            f"📈 Intenzitás: {intensity}",
            effects,
        ]

        # Széljárás részletek hozzáadása
        if wind_details:
            tooltip_lines.append("")
            tooltip_lines.extend(wind_details)

        # Adatforrás jelzése (ha fallback)
        if data_source == "windspeed_10m_max":
            tooltip_lines.extend([
                "",
                "ℹ️ Fallback adatforrás (átlag szélsebesség)"
            ])

        return '\n'.join(tooltip_lines)

    def _show_tooltip(self, event, point_data: Dict[str, Any]) -> None:
        """
        💬 WIND CHART TOOLTIP POSITIONING
        
        🎨 WIND CHART SPECIFIC TOOLTIP:
        - Professional design
        - Wind-specific formatting
        - 🎯 SMART POSITIONING: Avoits chart edges
        """
        if not hasattr(self, 'ax'):
            return

        # Előző tooltip törlése
        self._hide_tooltip()

        # Tooltip szöveg formázása
        tooltip_text = self._format_tooltip_text(point_data)

        # Koordináták meghatározása
        import matplotlib.dates as mdates
        x_pos = mdates.date2num(point_data['date'])
        y_pos = point_data['windspeed']

        # 🎯 SMART POSITIONING LOGIC
        # Chart területének boundaries
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # Pont pozíciója a chart területen (0-1 scale)
        x_relative = (x_pos - xlim[0]) / (xlim[1] - xlim[0])
        y_relative = (y_pos - ylim[0]) / (ylim[1] - ylim[0])

        # Dynamic offset számítás
        if y_relative > 0.7:  # Felső 30%-ban
            # Tooltip lefelé
            offset_y = -80
            va_align = 'top'
            print(f"🔽 DEBUG: Wind tooltip lefelé - y_relative: {y_relative:.2f}")
        else:
            # Tooltip felfelé (alapértelmezett)
            offset_y = 50
            va_align = 'bottom'
            print(f"🔼 DEBUG: Wind tooltip felfelé - y_relative: {y_relative:.2f}")

        if x_relative > 0.8:  # Jobb 20%-ban
            # Tooltip balra
            offset_x = -120
            ha_align = 'right'
            print(f"⬅️ DEBUG: Wind tooltip balra - x_relative: {x_relative:.2f}")
        else:
            # Tooltip jobbra (alapértelmezett)
            offset_x = 40
            ha_align = 'left'
            print(f"➡️ DEBUG: Wind tooltip jobbra - x_relative: {x_relative:.2f}")

        # Current colors
        current_colors = get_current_colors()

        # 💨 WIND THEMED TOOLTIP
        self.tooltip_annotation = self.ax.annotate(
            tooltip_text,
            xy=(x_pos, y_pos),
            xytext=(offset_x, offset_y),  # 🎯 DYNAMIC OFFSET
            textcoords='offset points',
            bbox=dict(
                boxstyle='round,pad=1.0',
                facecolor='lightblue',  # 💨 Wind theme
                edgecolor=current_colors.get('border', '#34495E'),
                linewidth=2,
                alpha=0.95
            ),
            arrowprops=dict(
                arrowstyle='->',
                color=current_colors.get('border', '#34495E'),
                lw=2,
                alpha=0.8
            ),
            fontsize=10,
            fontweight='bold',
            ha=ha_align,      # 🎯 DYNAMIC HORIZONTAL ALIGNMENT
            va=va_align,      # 🎯 DYNAMIC VERTICAL ALIGNMENT
            zorder=1000       # Top layer
        )

        self._tooltip_visible = True
        self._tooltip_annotation = self.tooltip_annotation

        # Canvas frissítése
        if hasattr(self, 'draw_idle'):
            self.draw_idle()

    def _hide_tooltip(self) -> None:
        """
        🙈 Tooltip elrejtése - CLEAN HIDING
        """
        if hasattr(self, '_tooltip_annotation') and self._tooltip_annotation:
            try:
                self._tooltip_annotation.remove()
            except Exception as e:
                print(f"⚠️ DEBUG: Wind tooltip remove error: {e}")

            self._tooltip_annotation = None
            self._tooltip_visible = False

            # Canvas frissítése
            if hasattr(self, 'draw_idle'):
                self.draw_idle()
