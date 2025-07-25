#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Heatmap Calendar Chart
Heatmap naptár chart widget tetszőleges dátumtartományú vizualizációval.

📅 HEATMAP CALENDAR CHART: Éves/tetszőleges időszakú hőmérsékleti adatok naptár formátumban
🎨 TÉMA INTEGRÁCIÓ: ColorPalette heatmap színek használata
🔧 KRITIKUS JAVÍTÁS: Duplikáció-mentes frissítés + tetszőleges dátumtartomány támogatás
✅ Piros (#C43939) téma támogatás
✅ Dinamikus címgenerálás időszak alapján
✅ Folytonos hétmátrix létrehozása
✅ Intelligens színskála választás
✅ Colorbar kezelés
"""

from typing import Optional, Dict, Any
import pandas as pd
import numpy as np

from PySide6.QtWidgets import QWidget

from .base_chart import WeatherChart
from ..theme_manager import get_current_colors


class HeatmapCalendarChart(WeatherChart):
    """
    🔧 KRITIKUS JAVÍTÁS: Heatmap naptár chart - DUPLIKÁCIÓ BUGFIX VERZIÓ + SIMPLIFIED THEMEMANAGER.
    Éves/tetszőleges időszakú hőmérsékleti adatok naptár formátumban.
    🎨 TÉMA INTEGRÁCIÓ: ColorPalette heatmap színek használata
    Az eredeti probléma: többszörös colorbar és grid duplikálódás.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(figsize=(16, 10), parent=parent)  # EXTRA NAGY MÉRET
        self.chart_title = "📅 Éves Hőmérséklet Naptár"
        self.parameter = "temperature_2m_mean"  # Alapértelmezett paraméter
        # 🔧 DUPLIKÁCIÓ BUGFIX: Colorbar tracking
        self._colorbar = None
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🔧 KRITIKUS JAVÍTÁS: Duplikáció-mentes heatmap frissítés + SIMPLIFIED THEMEMANAGER.
        """
        print("📅 DEBUG: HeatmapCalendarChart.update_data() - DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER VERZIÓ")
        
        try:
            if self._is_updating:
                print("⚠️ DEBUG: Heatmap update már folyamatban, skip")
                return
            
            self._is_updating = True
            
            df = self._extract_daily_data(data)
            if df.empty:
                print("⚠️ DEBUG: Üres DataFrame, heatmap törlése")
                self.clear_chart()
                return
            
            self.current_data = df
            
            # === KRITIKUS: TELJES FIGURE TÖRLÉSE DUPLIKÁCIÓ ELLEN ===
            print("🧹 DEBUG: Heatmap Figure.clear() - DUPLIKÁCIÓ ELLENI VÉDELEM")
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            self._colorbar = None  # Colorbar referencia reset
            
            # 🎨 TÉMA ALKALMAZÁSA
            self._apply_theme_to_chart()
            
            # Heatmap megrajzolása
            self._plot_heatmap_calendar(df)
            
            self.draw()
            self._is_updating = False
            
            print("✅ DEBUG: HeatmapCalendarChart frissítés kész - DUPLIKÁCIÓ MENTES + THEMED")
            
        except Exception as e:
            print(f"❌ DEBUG: Heatmap calendar chart hiba: {e}")
            self._is_updating = False
            self.clear_chart()
    
    def _extract_daily_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Napi adatok kinyerése heatmap-hez - CSAK VALÓDI API ADATOKKAL."""
        daily_data = data.get("daily", {})
        dates = daily_data.get("time", [])
        temp_mean = daily_data.get("temperature_2m_mean", [])
        temp_max = daily_data.get("temperature_2m_max", [])
        temp_min = daily_data.get("temperature_2m_min", [])
        
        # 🚨 KRITIKUS: CSAK VALÓDI API ADATOK! Számított értékek TILTOTTAK!
        if not dates or not temp_mean:
            print("⚠️ DEBUG: Hiányzó heatmap adatok - chart nem jeleníthető meg")
            return pd.DataFrame()
        
        # Adatstruktúra hosszak ellenőrzése
        if len(dates) != len(temp_mean):
            print("❌ DEBUG: Eltérő hosszúságú heatmap adatok - chart nem jeleníthető meg")
            return pd.DataFrame()
        
        df = pd.DataFrame({
            'date': pd.to_datetime(dates),
            'temperature_2m_mean': temp_mean,  # CSAK VALÓDI API ADAT!
            'temperature_2m_max': temp_max if temp_max and len(temp_max) == len(dates) else None,
            'temperature_2m_min': temp_min if temp_min and len(temp_min) == len(dates) else None
        })
        
        # Csak a kötelező oszlopokat tartjuk meg
        df = df[['date', 'temperature_2m_mean']].dropna()
        
        if df.empty:
            print("⚠️ DEBUG: Nincs érvényes heatmap adat - chart nem jeleníthető meg")
        
        return df
    
    def _plot_heatmap_calendar(self, df: pd.DataFrame) -> None:
        """
        🔧 KRITIKUS JAVÍTÁS: Tetszőleges dátumtartomány heatmap - NEM CSAK NAPTÁRI ÉV.
        🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ: ColorPalette heatmap színskála használata
        
        TÁMOGATOTT DÁTUMTARTOMÁNYOK:
        - Teljes naptári év: 2024.01.01 - 2024.12.31
        - Tetszőleges időszak: 2024.05.01 - 2025.05.01
        - Több évet átfogó: 2023.07.01 - 2025.03.15
        """
        print("🎨 DEBUG: _plot_heatmap_calendar() - TETSZŐLEGES DÁTUMTARTOMÁNY TÁMOGATÁS")
        
        if df.empty or self.parameter not in df.columns:
            self._plot_heatmap_placeholder()
            return
        
        # === DÁTUMTARTOMÁNY ELEMZÉS ===
        
        min_date = df['date'].min()
        max_date = df['date'].max()
        total_days = (max_date - min_date).days + 1
        
        # Évek listája az időszakban
        years = sorted(df['date'].dt.year.unique())
        
        if len(years) == 0:
            self._plot_heatmap_placeholder()
            return
        
        # === DINAMIKUS CÍM GENERÁLÁS ===
        
        if len(years) == 1:
            # Egy éven belüli időszak
            if min_date.month == 1 and min_date.day == 1 and max_date.month == 12 and max_date.day == 31:
                title_suffix = f" ({years[0]})"  # Teljes év
            else:
                title_suffix = f" ({min_date.strftime('%Y.%m.%d')} - {max_date.strftime('%Y.%m.%d')})"
        else:
            # Több évet átfogó időszak
            title_suffix = f" ({min_date.strftime('%Y.%m.%d')} - {max_date.strftime('%Y.%m.%d')})"
        
        print(f"🗓️ DEBUG: Heatmap időszak: {min_date} - {max_date} ({total_days} nap)")
        
        # === FOLYTONOS HÉTMÁTRIX LÉTREHOZÁSA ===
        
        # Első hét kezdete (hétfő)
        first_monday = min_date - pd.Timedelta(days=min_date.weekday())
        
        # Utolsó hét vége (vasárnap)
        last_sunday = max_date + pd.Timedelta(days=6-max_date.weekday())
        
        # Teljes hetek száma
        total_weeks = ((last_sunday - first_monday).days // 7) + 1
        
        print(f"📊 DEBUG: Hétmátrix: {total_weeks} hét ({first_monday} - {last_sunday})")
        
        # Heatmap mátrix - teljes időszakot lefedi
        calendar_data = np.full((total_weeks, 7), np.nan)
        
        # === ADATOK ELHELYEZÉSE A MÁTRIXBAN ===
        
        for _, row in df.iterrows():
            date = row['date']
            temp = row[self.parameter]
            
            # CSAK VALÓDI HŐMÉRSÉKLET ÉRTÉKEK
            if pd.isna(temp):
                continue
            
            # Hét száma az első hétfőtől számítva
            week_index = (date - first_monday).days // 7
            day_of_week = date.weekday()  # 0=hétfő, 6=vasárnap
            
            # Biztonsági ellenőrzés
            if 0 <= week_index < total_weeks and 0 <= day_of_week < 7:
                calendar_data[week_index, day_of_week] = temp
        
        # === ADATOK ELLENŐRZÉSE ===
        
        valid_data_count = np.sum(~np.isnan(calendar_data))
        if valid_data_count < 10:
            print(f"⚠️ DEBUG: Túl kevés valódi adat ({valid_data_count}) - heatmap nem jeleníthető meg")
            self._plot_heatmap_placeholder()
            return
        
        # === SZÍNSKÁLA BEÁLLÍTÁSA ===
        
        valid_temps = df[self.parameter].dropna()
        if len(valid_temps) == 0:
            self._plot_heatmap_placeholder()
            return
            
        vmin = valid_temps.min()
        vmax = valid_temps.max()
        
        # 🔧 COLORPALETTE SZÍNTÉRKÉP VÁLASZTÁS
        if vmin < 0 and vmax > 20:  # Teljes szezonális spektrum
            cmap = 'RdYlBu_r'  # Red-Yellow-Blue reversed
        elif vmax <= 15:  # Főleg hideg időszak
            cmap = 'Blues'
        elif vmin >= 15:  # Főleg meleg időszak
            cmap = 'Reds'
        else:
            cmap = 'viridis'
        
        print(f"🎨 DEBUG: Colormap: {cmap}, Data range: {vmin:.1f}°C - {vmax:.1f}°C")
        
        # === HEATMAP MEGRAJZOLÁSA ===
        
        print("🎨 DEBUG: Heatmap rendering - teljes dátumtartomány")
        im = self.ax.imshow(calendar_data.T, cmap=cmap, aspect='auto', 
                           vmin=vmin, vmax=vmax, origin='upper')
        
        # === TENGELYEK BEÁLLÍTÁSA ===
        
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')
        
        # X tengely - hetek
        if total_weeks <= 20:
            # Rövid időszak - minden hét
            x_ticks = range(0, total_weeks, 1)
            x_labels = [(first_monday + pd.Timedelta(weeks=i)).strftime('%m.%d') for i in x_ticks]
        else:
            # Hosszú időszak - minden 4. hét
            x_ticks = range(0, total_weeks, 4)
            x_labels = [(first_monday + pd.Timedelta(weeks=i)).strftime('%m.%d') for i in x_ticks]
        
        self.ax.set_xticks(x_ticks)
        self.ax.set_xticklabels(x_labels, color=text_color, rotation=45)
        self.ax.set_xlabel('Dátum', color=text_color)
        
        # Y tengely - napok
        self.ax.set_yticks(range(7))
        self.ax.set_yticklabels(['Hétfő', 'Kedd', 'Szerda', 'Csütörtök', 'Péntek', 'Szombat', 'Vasárnap'], color=text_color)
        
        # === COLORBAR LÉTREHOZÁSA ===
        
        print("🎨 DEBUG: Colorbar létrehozás")
        try:
            # Meglévő colorbar törlése
            if self._colorbar:
                self._colorbar.remove()
                self._colorbar = None
                
            self._colorbar = self.figure.colorbar(im, ax=self.ax, shrink=0.8, aspect=30)
            self._colorbar.set_label('Hőmérséklet (°C)', fontsize=12, fontweight='500', color=text_color)
            self._colorbar.ax.tick_params(colors=text_color)
            
            print("✅ DEBUG: Colorbar sikeresen létrehozva")
        except Exception as e:
            print(f"⚠️ DEBUG: Colorbar hiba (nem kritikus): {e}")
        
        # === FORMÁZÁS ===
        
        self.ax.set_title(f"{self.chart_title}{title_suffix}", fontsize=18, fontweight='bold', pad=20, color=text_color)
        
        # Grid
        self.ax.set_xticks(np.arange(-0.5, total_weeks, 1), minor=True)
        self.ax.set_yticks(np.arange(-0.5, 7, 1), minor=True)
        
        grid_color = current_colors.get('surface', '#ffffff')
        self.ax.grid(which='minor', color=grid_color, linestyle='-', linewidth=1)
        
        # Layout
        self.figure.tight_layout()
        
        print(f"✅ DEBUG: Heatmap complete - {total_weeks} hét, {valid_data_count} adat")
    
    def _plot_heatmap_placeholder(self) -> None:
        """Heatmap placeholder ha nincs elegendő valódi adat - MOCK ADATOK NÉLKÜL + SIMPLIFIED THEMEMANAGER."""
        # 🔧 SIMPLIFIED THEMEMANAGER SZÍNEK
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')
        surface_color = current_colors.get('surface_variant', '#f9fafb')
        
        self.ax.text(0.5, 0.5, '📅 Heatmap Naptár\n\n❌ Nincs elegendő valódi adat\n\nA naptár megjelenítéséhez\nlegalább 10 valódi hőmérséklet\nadat szükséges az API-ból.\n\n🚨 Mock adatok használata TILOS!', 
                    ha='center', va='center', transform=self.ax.transAxes,
                    fontsize=14, color=text_color,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=surface_color, edgecolor=current_colors.get('border', '#d1d5db')))
        
        self.ax.set_title(self.chart_title, fontsize=18, fontweight='bold', pad=20, color=text_color)
        
        # Tengelyek elrejtése placeholder módban
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)