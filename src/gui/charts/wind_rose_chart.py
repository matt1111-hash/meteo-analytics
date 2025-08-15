#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Wind Rose Chart
Széllökés rózsadiagram widget professzionális polárkoordinátás vizualizációval.

🌹 WIND ROSE CHART: Szélirány és széllökés erősség kombinált megjelenítése
🎨 TÉMA INTEGRÁCIÓ: ColorPalette wind chart színek használata
🔧 KRITIKUS JAVÍTÁS: Duplikáció-mentes frissítés + SIMPLIFIED THEMEMANAGER
✅ wind_gusts_max prioritás → windspeed_10m_max fallback rendszer
✅ Kritikus széllökés küszöbök: 70, 100, 120 km/h
✅ Piros (#C43939) téma támogatás
✅ 16 fő szélirány + 6 sebesség kategória
✅ Polárkoordinátás rózsadiagram
🚨 KRITIKUS DEBUG: Explicit konzol üzenetek minden lépésnél
🎯 VÉGSŐ JAVÍTÁS: has_valid_data() - ellenőrzi van-e valódi adat a None-ok helyett!
"""

from typing import Optional, Dict, Any
import pandas as pd
import numpy as np

from PySide6.QtWidgets import QWidget

from .base_chart import WeatherChart
from ..theme_manager import get_current_colors


class WindRoseChart(WeatherChart):
    """
    🚨 KRITIKUS DEBUG: SZÉLLÖKÉS RÓZSADIAGRAM - WIND GUSTS TÁMOGATÁS + DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER.
    Szélirány és széllökés erősség kombinált megjelenítése.
    🎨 TÉMA INTEGRÁCIÓ: ColorPalette wind chart színek használata
    ✅ wind_gusts_max prioritás → windspeed_10m_max fallback rendszer
    ✅ Kritikus széllökés küszöbök: 70, 100, 120 km/h
    🚨 EXPLICIT DEBUG minden lépésnél
    🎯 VÉGSŐ JAVÍTÁS: has_valid_data() - ellenőrzi van-e valódi adat!
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(figsize=(10, 10), parent=parent)  # NÉGYZETES MÉRET
        self.chart_title = "🌹 Széllökés Rózsadiagram"  # 🌪️ WIND GUSTS CÍM
        print("🌹 DEBUG: WindRoseChart.__init__() SIKERES!")
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🚨 KRITIKUS DEBUG: Duplikáció-mentes wind rose frissítés + SIMPLIFIED THEMEMANAGER + EXPLICIT DEBUG.
        """
        print("🌹 DEBUG: WindRoseChart.update_data() - EXPLICIT DEBUG VERZIÓ STARTED!!!")
        print(f"🌹 DEBUG: Input data type: {type(data)}")
        print(f"🌹 DEBUG: Input data keys: {list(data.keys()) if isinstance(data, dict) else 'NOT DICT'}")
        
        try:
            if self._is_updating:
                print("🌹 DEBUG: WindRoseChart already updating, skipping...")
                return
            
            print("🌹 DEBUG: Setting _is_updating = True")
            self._is_updating = True
            
            print("🌹 DEBUG: Calling _extract_wind_data()...")
            df = self._extract_wind_data(data)
            print(f"🌹 DEBUG: _extract_wind_data() returned DataFrame with {len(df) if not df.empty else 0} rows")
            
            if df.empty:
                print("⚠️ DEBUG: Üres DataFrame, wind rose törlése")
                self.clear_chart()
                print("🌹 DEBUG: WindRoseChart.update_data() FINISHED - EMPTY DATA")
                self._is_updating = False
                return
            
            print("🌹 DEBUG: Setting self.current_data...")
            self.current_data = df
            print(f"🌹 DEBUG: self.current_data set successfully, type: {type(self.current_data)}")
            
            # === KRITIKUS: TELJES FIGURE TÖRLÉSE ===
            print("🧹 DEBUG: WindRose Figure.clear() - DUPLIKÁCIÓ ELLEN")
            self.figure.clear()
            
            # 🔧 TÉMA ALKALMAZÁSA
            print("🎨 DEBUG: Applying theme to WindRose...")
            current_colors = get_current_colors()
            self.figure.patch.set_facecolor(current_colors.get('surface', '#ffffff'))
            
            # Wind rose megrajzolása
            print("📊 DEBUG: Calling _plot_wind_rose()...")
            self._plot_wind_rose(df)
            
            print("🖼️ DEBUG: Calling draw()...")
            self.draw()
            
            print("🌹 DEBUG: Setting _is_updating = False")
            self._is_updating = False
            
            print("✅ DEBUG: WindRoseChart frissítés TELJESEN KÉSZ - DUPLIKÁCIÓ MENTES + THEMED")
            
        except Exception as e:
            print(f"❌ DEBUG: Wind rose chart hiba: {e}")
            import traceback
            print(f"❌ DEBUG: WindRoseChart traceback: {traceback.format_exc()}")
            self._is_updating = False
            self.clear_chart()
            self._plot_wind_rose_placeholder()
    
    def _extract_wind_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        🚨 KRITIKUS DEBUG: Széllökés adatok kinyerése rózsadiagramhoz - WIND GUSTS PRIORITÁS + FALLBACK + EXPLICIT DEBUG.
        🎯 VÉGSŐ JAVÍTÁS: has_valid_data() segédfüggvény - ellenőrzi van-e valódi adat!
        
        PRIORITÁS RENDSZER:
        1. wind_gusts_max + winddirection_10m_dominant ⭐ ELSŐDLEGES
        2. windspeed_10m_max + winddirection_10m_dominant ⭐ FALLBACK  
        3. Hibaüzenet ha egyik sem elérhető
        """
        print("🌹 DEBUG: _extract_wind_data() STARTED!!!")
        print(f"🌹 DEBUG: data type: {type(data)}")
        
        daily_data = data.get("daily", {})
        print(f"🌹 DEBUG: daily_data type: {type(daily_data)}")
        print(f"🌹 DEBUG: daily_data keys: {list(daily_data.keys()) if isinstance(daily_data, dict) else 'NOT DICT'}")
        
        dates = daily_data.get("time", [])
        winddirection = daily_data.get("wind_direction_10m_dominant", [])
        
        print(f"🌹 DEBUG: dates: {len(dates) if dates else 0} elems")
        print(f"🌹 DEBUG: winddirection: {len(winddirection) if winddirection else 0} elems")
        
        # 🌪️ WIND GUSTS PRIORITÁS: wind_gusts_max ELSŐDLEGESEN  
        wind_gusts_max = daily_data.get("wind_gusts_max", [])
        windspeed_10m_max = daily_data.get("windspeed_10m_max", [])  # Fallback
        
        print(f"🌹 DEBUG: wind_gusts_max: {len(wind_gusts_max) if wind_gusts_max else 0} elems")
        print(f"🌹 DEBUG: windspeed_10m_max: {len(windspeed_10m_max) if windspeed_10m_max else 0} elems")
        
        if wind_gusts_max:
            print(f"🌹 DEBUG: wind_gusts_max sample: {wind_gusts_max[:3] if len(wind_gusts_max) >= 3 else wind_gusts_max}")
        if windspeed_10m_max:
            print(f"🌹 DEBUG: windspeed_10m_max sample: {windspeed_10m_max[:3] if len(windspeed_10m_max) >= 3 else windspeed_10m_max}")
        if winddirection:
            print(f"🌹 DEBUG: winddirection sample: {winddirection[:3] if len(winddirection) >= 3 else winddirection}")
        
        print(f"🌹 DEBUG: WindRose data sources - wind_gusts_max: {len(wind_gusts_max) if wind_gusts_max else 0}, windspeed_10m_max: {len(windspeed_10m_max) if windspeed_10m_max else 0}, winddirection: {len(winddirection) if winddirection else 0}")
        
        # Alapadatok ellenőrzése
        if not dates or not winddirection:
            print("⚠️ DEBUG: Hiányzó alapadatok (dátum/irány) - WindRose chart nem jeleníthető meg")
            return pd.DataFrame()
        
        # 🎯 OKOS SEGÉDFÜGGVÉNY - ellenőrzi van-e valódi adat
        def has_valid_data(data_list):
            """Ellenőrzi, hogy van-e valódi szám adat a listában (nem csak None-ok)"""
            return any(x is not None and isinstance(x, (int, float)) for x in data_list)
        
        # PRIORITÁS KIÉRTÉKELÉS
        windspeed_data = []
        data_source = ""
        
        print("🌹 DEBUG: Checking wind_gusts_max priority...")
        if wind_gusts_max and len(wind_gusts_max) == len(dates) and len(winddirection) == len(dates) and has_valid_data(wind_gusts_max):
            # 🌪️ ELSŐDLEGES: wind_gusts_max + irány használata, CSAK HA VAN BENNE ÉRVÉNYES ADAT
            windspeed_data = wind_gusts_max
            data_source = "wind_gusts_max"
            self.chart_title = "🌹 Széllökés Rózsadiagram"
            print(f"✅ DEBUG: WindRose using PRIMARY source: {data_source}")
        elif windspeed_10m_max and len(windspeed_10m_max) == len(dates) and len(winddirection) == len(dates) and has_valid_data(windspeed_10m_max):
            # ⚠️ FALLBACK: windspeed_10m_max + irány használata
            print("🌹 DEBUG: wind_gusts_max not suitable, checking fallback...")
            windspeed_data = windspeed_10m_max
            data_source = "windspeed_10m_max"  
            self.chart_title = "🌹 Szél Rózsadiagram (Fallback)"
            print(f"⚠️ DEBUG: WindRose using FALLBACK source: {data_source}")
        else:
            print(f"❌ DEBUG: Nincs használható szél+irány adat - WindRose chart nem jeleníthető meg")
            print(f"   - wind_gusts_max: {len(wind_gusts_max) if wind_gusts_max else 0} elem, has_valid_data: {has_valid_data(wind_gusts_max) if wind_gusts_max else False}")
            print(f"   - windspeed_10m_max: {len(windspeed_10m_max) if windspeed_10m_max else 0} elem, has_valid_data: {has_valid_data(windspeed_10m_max) if windspeed_10m_max else False}")
            print(f"   - winddirection: {len(winddirection)} elem")
            print(f"   - dates: {len(dates)} elem")
            return pd.DataFrame()
        
        print(f"🌹 DEBUG: Creating DataFrame with {len(windspeed_data)} wind values, {len(winddirection)} directions and {len(dates)} dates...")
        
        # DataFrame létrehozása
        df = pd.DataFrame({
            'date': pd.to_datetime(dates),
            'windspeed': windspeed_data,
            'winddirection': winddirection,
            '_data_source': data_source  # Debug info
        })
        
        print(f"🌹 DEBUG: DataFrame created, shape: {df.shape}")
        
        # Csak érvényes adatok megtartása
        print("🌹 DEBUG: Dropping NaN values...")
        df_before = len(df)
        df = df.dropna()
        df_after = len(df)
        print(f"🌹 DEBUG: DataFrame after dropna: {df_before} -> {df_after} rows")
        
        # Szélirány érték tartomány ellenőrzése (0-360 fok)
        print("🌹 DEBUG: Filtering valid wind directions (0-360)...")
        valid_direction_mask = (df['winddirection'] >= 0) & (df['winddirection'] <= 360)
        df_before_direction = len(df)
        df = df[valid_direction_mask]
        df_after_direction = len(df)
        print(f"🌹 DEBUG: DataFrame after direction filter: {df_before_direction} -> {df_after_direction} rows")
        
        if df.empty:
            print(f"❌ DEBUG: Üres DataFrame {data_source} adatok után - WindRose chart nem jeleníthető meg")
        else:
            max_wind = df['windspeed'].max()
            avg_wind = df['windspeed'].mean()
            print(f"✅ DEBUG: WindRose DataFrame KÉSZ - {data_source}, max: {max_wind:.1f} km/h, avg: {avg_wind:.1f} km/h, {len(df)} rekord")
        
        print("🌹 DEBUG: _extract_wind_data() FINISHED!")
        return df
    
    def _plot_wind_rose(self, df: pd.DataFrame) -> None:
        """
        Wind rose diagram megrajzolása - DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER.
        🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ: ColorPalette wind színek használata
        """
        print("🎨 DEBUG: _plot_wind_rose() - DUPLIKÁCIÓ MENTES + SIMPLIFIED THEMEMANAGER")
        
        if df.empty:
            print("⚠️ DEBUG: Empty DataFrame, showing placeholder...")
            self._plot_wind_rose_placeholder()
            return
        
        # === KRITIKUS: POLAR KOORDINÁTA RENDSZER BEÁLLÍTÁSA ===
        print("🔄 DEBUG: Creating polar subplot...")
        self.ax = self.figure.add_subplot(111, projection='polar')
        
        # 🔧 KRITIKUS JAVÍTÁS: HELYES API HASZNÁLAT - wind színek generálása
        wind_colors = {
            'calm': self.color_palette.get_color('info', 'light') or '#a3a3a3',
            'light': self.color_palette.get_color('success', 'light') or '#86efac',
            'moderate': self.color_palette.get_color('warning', 'base') or '#f59e0b',
            'strong': self.color_palette.get_color('error', 'light') or '#f87171',
            'very_strong': self.color_palette.get_color('error', 'base') or '#dc2626',
            'extreme': self.color_palette.get_color('error', 'dark') or '#991b1b'
        }
        
        # Weather színpaletta integrálása
        weather_wind_color = self.weather_colors.get('wind', '#10b981')
        wind_colors['moderate'] = weather_wind_color
        
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')
        
        print(f"🎨 DEBUG: Using SimplifiedThemeManager wind colors: {wind_colors}")
        
        # 🌪️ SZÉLLÖKÉS SEBESSÉG KATEGÓRIÁK - ÉLETHU KÜSZÖBÖK + SIMPLIFIED THEMEMANAGER SZÍNEK
        speed_bins = [0, 25, 50, 70, 100, 120, 200]  # km/h - WIND GUSTS KÜSZÖBÖK
        speed_labels = ['0-25', '25-50', '50-70', '70-100', '100-120', '120+ km/h']  # ÉLETHU CÍMKÉK
        colors = [
            wind_colors['calm'],      # 0-25 km/h - Csendes/enyhe  
            wind_colors['light'],     # 25-50 km/h - Közepes
            wind_colors['moderate'],  # 50-70 km/h - Erős
            wind_colors['strong'],    # 70-100 km/h - Viharos 🌪️
            wind_colors['very_strong'], # 100-120 km/h - Extrém ⚠️
            wind_colors['extreme']    # 120+ km/h - Hurrikán 🚨
        ]
        
        print("🧮 DEBUG: Setting up direction categories...")
        # Irány kategóriák (16 fő irány)
        direction_bins = np.arange(0, 361, 22.5)  # 16 x 22.5° = 360°
        direction_labels = ['É', 'ÉÉK', 'ÉK', 'KÉK', 'K', 'KDK', 'DK', 'DDK', 
                           'D', 'DDNy', 'DNy', 'NyDNy', 'Ny', 'NyÉNy', 'ÉNy', 'ÉÉNy']
        
        print("📊 DEBUG: Processing wind rose data...")
        # Adatok binning-je
        wind_rose_data = []
        
        for i in range(len(direction_bins) - 1):
            dir_start = direction_bins[i]
            dir_end = direction_bins[i + 1]
            
            # Adott irányba eső szelek
            mask = ((df['winddirection'] >= dir_start) & (df['winddirection'] < dir_end))
            direction_winds = df[mask]['windspeed']
            
            if len(direction_winds) == 0:
                wind_rose_data.append([0] * len(speed_bins))
                continue
            
            # Sebesség kategóriák szerinti bontás
            speed_counts = []
            for j in range(len(speed_bins) - 1):
                speed_mask = ((direction_winds >= speed_bins[j]) & 
                             (direction_winds < speed_bins[j + 1]))
                count = len(direction_winds[speed_mask])
                speed_counts.append(count)
            
            # Utolsó kategória (120+ km/h)
            speed_counts.append(len(direction_winds[direction_winds >= speed_bins[-2]]))
            wind_rose_data.append(speed_counts)
        
        print("🌹 DEBUG: Drawing wind rose bars...")
        # Rózsadiagram megrajzolása
        theta = np.linspace(0, 2 * np.pi, len(direction_bins) - 1, endpoint=False)
        
        # Oszlopok alapja (kumulatív)
        bottom = np.zeros(len(theta))
        
        for i, (color, label) in enumerate(zip(colors, speed_labels)):
            values = [row[i] for row in wind_rose_data]
            
            # Oszlopok rajzolása
            bars = self.ax.bar(theta, values, width=np.pi / 8, bottom=bottom, 
                              color=color, alpha=0.8, label=label, 
                              edgecolor=current_colors.get('border', '#d1d5db'), linewidth=0.5)
            
            bottom += values
        
        print("🎨 DEBUG: Formatting wind rose chart...")
        # === FORMÁZÁS + SIMPLIFIED THEMEMANAGER ===
        
        # Irány címkék
        self.ax.set_xticks(theta)
        self.ax.set_xticklabels(direction_labels[:len(theta)])
        
        # 0° = É (észak) legyen felül
        self.ax.set_theta_zero_location('N')
        self.ax.set_theta_direction(-1)  # Óramutató járása
        
        # Grid és címkék + SIMPLIFIED THEMEMANAGER SZÍNEK
        grid_color = current_colors.get('border', '#d1d5db')
        self.ax.grid(True, alpha=0.3, color=grid_color)
        self.ax.set_title(self.chart_title, fontsize=16, fontweight='bold', pad=30, color=text_color)
        
        # Tick színek
        self.ax.tick_params(colors=text_color)
        
        # Legend - JAVÍTOTT POZÍCIÓ + SIMPLIFIED THEMEMANAGER SZÍNEK
        if self.legend_enabled:
            legend = self.ax.legend(bbox_to_anchor=(1.2, 1), loc='upper left', fontsize=10)
            legend.get_frame().set_facecolor(current_colors.get('surface', '#ffffff'))
            legend.get_frame().set_edgecolor(current_colors.get('border', '#d1d5db'))
        
        # Statisztika szöveg + SIMPLIFIED THEMEMANAGER SZÍNEK
        total_records = len(df)
        avg_speed = df['windspeed'].mean()
        max_speed = df['windspeed'].max()
        data_source = df['_data_source'].iloc[0] if '_data_source' in df.columns else 'unknown'
        
        # Adatforrás alapú címkézés
        if data_source == "wind_gusts_max":
            speed_label = "széllökés"
            icon = "🌪️"
        else:
            speed_label = "szélsebesség"  
            icon = "💨"
        
        stats_text = f"📊 Összesen: {total_records} mérés\n"
        stats_text += f"{icon} Átlag {speed_label}: {avg_speed:.1f} km/h\n"
        stats_text += f"🚨 Maximum {speed_label}: {max_speed:.1f} km/h\n"
        
        # Kategorizálás a maximum alapján
        if max_speed >= 120:
            stats_text += "⚠️ HURRIKÁN erősségű széllökések!"
        elif max_speed >= 100:
            stats_text += "⚠️ EXTRÉM széllökések detected!"  
        elif max_speed >= 70:
            stats_text += "🌪️ Viharos széllökések detected!"
        
        self.ax.text(0.02, 0.98, stats_text, transform=self.ax.transAxes, 
                    fontsize=10, verticalalignment='top', color=text_color,
                    bbox=dict(boxstyle="round,pad=0.3", 
                             facecolor=current_colors.get('surface_variant', '#f9fafb'), 
                             edgecolor=current_colors.get('border', '#d1d5db'), alpha=0.8))
        
        print("🔧 DEBUG: Applying tight layout...")
        self.figure.tight_layout()
        print("✅ DEBUG: Wind rose plotting COMPLETE!")
    
    def _plot_wind_rose_placeholder(self) -> None:
        """Wind rose placeholder ha nincs valódi adat - MOCK ADATOK NÉLKÜL + SIMPLIFIED THEMEMANAGER."""
        print("🌹 DEBUG: Showing wind rose placeholder...")
        # Sima axis használata placeholder-hez
        self.ax = self.figure.add_subplot(111)
        
        # 🔧 SIMPLIFIED THEMEMANAGER SZÍNEK
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')
        surface_color = current_colors.get('surface_variant', '#f9fafb')
        
        placeholder_text = "🌹 Széllökés Rózsadiagram\n\n"
        placeholder_text += "❌ Nincs széllökés/irány adat\n\n"
        placeholder_text += "A diagram megjelenítéséhez szélirány és\n"
        placeholder_text += "széllökés adatok szükségesek:\n"
        placeholder_text += "• wind_gusts_max (elsődleges) VAGY\n"
        placeholder_text += "• windspeed_10m_max (fallback)\n"
        placeholder_text += "• winddirection_10m_dominant\n\n"
        placeholder_text += "🚨 Mock adatok használata TILOS!"
        
        self.ax.text(0.5, 0.5, placeholder_text, ha='center', va='center', 
                    transform=self.ax.transAxes, fontsize=13, color=text_color,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor=surface_color, 
                             edgecolor=current_colors.get('border', '#d1d5db'), alpha=0.8))
        
        self.ax.set_title(self.chart_title, fontsize=16, fontweight='bold', pad=20, color=text_color)
        
        # Tengelyek elrejtése placeholder módban
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)