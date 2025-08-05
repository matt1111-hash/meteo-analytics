#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Heatmap Calendar Chart - VÉGLEGES JAVÍTOTT VERZIÓ
🎯 TELJES TÉGLALAPOK + CUSTOM COLORMAP + 365 KONSTANS AGGREGÁCIÓ

🔧 KRITIKUS JAVÍTÁSOK:
✅ imshow → pcolormesh: TELJES TÉGLALAPOK (nem vékony csíkok)
✅ Custom colormap támogatás (_custom_cmap, _custom_norm)
✅ 365 konstans téglalap minden időszakra (aggregáció)
✅ Dinamikus paraméter kezelés (temperature/precipitation/wind)
✅ Meteorológiai színskálák integráció (0mm=fehér, 0km/h=fehér)
✅ Robusztus hibakezelés és logging
✅ Kalendár mátrix (7 nap × 53 hét = 365+ cellák)

📅 HEATMAP LOGIKA: Konstans 365 téglalap tetszőleges időszakra
🎨 SZÍNSKÁLA: Custom meteorológiai + standard colormap-ek
🔧 RENDERING: pcolormesh vektorgrafikus téglalapok

Fájl helye: src/gui/charts/heatmap_chart.py
"""

from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
import matplotlib.colors as mcolors
import logging

from PySide6.QtWidgets import QWidget

from .base_chart import WeatherChart
from ..theme_manager import get_current_colors

logger = logging.getLogger(__name__)


class HeatmapCalendarChart(WeatherChart):
    """
    🔧 VÉGLEGES JAVÍTOTT VERZIÓ: pcolormesh + custom colormap + 365 konstans téglalap
    
    FELELŐSSÉGEK:
    - ✅ TELJES TÉGLALAPOK renderelése (pcolormesh)
    - ✅ Custom meteorológiai színskálák fogadása
    - ✅ Dinamikus paraméter kezelés (hőmérséklet/csapadék/szél)
    - ✅ 365 konstans téglalap logika aggregációval
    - ✅ Kalendár mátrix építés (7×53 cellák)
    - ✅ 0 értékek helyes színezése
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(figsize=(20, 12), parent=parent)  # EXTRA NAGY MÉRET
        self.chart_title = "📅 Konstans Heatmap"
        self.parameter = "temperature_2m_mean"  # Alapértelmezett paraméter
        
        # 🔧 Colorbar tracking (duplikáció ellen)
        self._colorbar = None
        
        # ✅ CUSTOM COLORMAP TÁMOGATÁS
        self._custom_cmap = None
        self._custom_norm = None
        
        logger.info("HeatmapCalendarChart VÉGLEGES VERZIÓ inicializálva (pcolormesh + custom colormap)")
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🔧 VÉGLEGES: pcolormesh + custom colormap + 365 konstans téglalap
        """
        logger.info(f"📅 HeatmapCalendarChart.update_data() - VÉGLEGES VERZIÓ (param: {self.parameter})")
        
        try:
            if self._is_updating:
                logger.debug("⚠️ Heatmap update már folyamatban, skip")
                return
            
            self._is_updating = True
            
            # Napi adatok kinyerése
            df = self._extract_daily_data(data)
            if df.empty:
                logger.warning(f"⚠️ Üres DataFrame ({self.parameter}), heatmap törlése")
                self.clear_chart()
                return
            
            self.current_data = df
            
            # === KRITIKUS: TELJES FIGURE TÖRLÉSE ===
            logger.debug("🧹 Figure.clear() - DUPLIKÁCIÓ ELLENI VÉDELEM")
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            self._colorbar = None  # Colorbar referencia reset
            
            # 🎨 Téma alkalmazása
            self._apply_theme_to_chart()
            
            # ✅ VÉGLEGES HEATMAP RENDERELÉS
            self._plot_365_constant_heatmap(df)
            
            self.draw()
            self._is_updating = False
            
            logger.info(f"✅ HeatmapCalendarChart VÉGLEGES frissítés kész - {self.parameter}")
            
        except Exception as e:
            logger.error(f"❌ Heatmap calendar chart hiba ({self.parameter}): {e}", exc_info=True)
            self._is_updating = False
            self.clear_chart()
    
    def _extract_daily_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        ✅ DINAMIKUS paraméter kezelés - MINDEN időjárási paraméter támogatása
        """
        daily_data = data.get("daily", {})
        dates = daily_data.get("time", [])
        
        # ✅ DINAMIKUS PARAMÉTER LEKÉRÉSE
        parameter_values = daily_data.get(self.parameter, [])
        
        logger.debug(f"🔍 Paraméter keresése: {self.parameter}")
        logger.debug(f"  📊 Dates: {len(dates)} elem")
        logger.debug(f"  📈 Values: {len(parameter_values)} elem")
        
        # 🚨 KRITIKUS: CSAK VALÓDI API ADATOK
        if not dates or not parameter_values:
            logger.warning(f"⚠️ Hiányzó {self.parameter} adatok")
            return pd.DataFrame()
        
        # Adatstruktúra hosszak ellenőrzése
        if len(dates) != len(parameter_values):
            logger.error(f"❌ Eltérő hosszúságú {self.parameter} adatok")
            logger.error(f"  Dates: {len(dates)}, Values: {len(parameter_values)}")
            return pd.DataFrame()
        
        # ✅ DINAMIKUS DATAFRAME LÉTREHOZÁS
        df = pd.DataFrame({
            'date': pd.to_datetime(dates),
            self.parameter: parameter_values
        })
        
        # NaN értékek eltávolítása
        original_count = len(df)
        df = df.dropna()
        
        if len(df) < original_count:
            logger.debug(f"📊 {original_count - len(df)} NaN érték eltávolítva")
        
        if df.empty:
            logger.warning(f"⚠️ Nincs érvényes {self.parameter} adat")
        else:
            logger.info(f"✅ {len(df)} érvényes {self.parameter} adat betöltve")
        
        return df
    
    def _plot_365_constant_heatmap(self, df: pd.DataFrame) -> None:
        """
        🎯 VÉGLEGES: 365 konstans téglalap + pcolormesh + custom colormap
        
        LOGIKA:
        1. Adatok aggregálása 365 értékre (konstans felbontás)
        2. 7×53 kalendár mátrix építése (365+ cellák)
        3. Custom colormap prioritás (meteorológiai színek)
        4. pcolormesh teljes téglalap renderelés
        5. Dinamikus tengelyek és colorbar
        """
        logger.info(f"🎨 _plot_365_constant_heatmap() - VÉGLEGES VERZIÓ ({self.parameter})")
        
        if df.empty or self.parameter not in df.columns:
            self._plot_heatmap_placeholder()
            return
        
        # === 1. DÁTUMTARTOMÁNY ELEMZÉS ===
        
        min_date = df['date'].min()
        max_date = df['date'].max()
        total_days = (max_date - min_date).days + 1
        
        logger.info(f"🗓️ Időszak: {min_date} - {max_date} ({total_days} nap)")
        
        # === 2. KONSTANS 365 AGGREGÁCIÓ ===
        
        values_365 = self._aggregate_to_365(df[self.parameter].tolist(), total_days)
        
        logger.info(f"📊 Aggregáció: {total_days} nap → 365 érték")
        logger.debug(f"📈 Aggregált értékek: min={np.nanmin(values_365):.2f}, max={np.nanmax(values_365):.2f}")
        
        # === 3. KALENDÁR MÁTRIX ÉPÍTÉSE (7×53) ===
        
        calendar_matrix = self._build_calendar_matrix(values_365)
        
        logger.debug(f"🎯 Kalendár mátrix shape: {calendar_matrix.shape}")
        
        # === 4. ADATOK VALIDÁLÁSA ===
        
        valid_data_count = np.sum(~np.isnan(calendar_matrix))
        total_cells = calendar_matrix.size
        
        logger.info(f"📊 Heatmap cellák: {valid_data_count}/{total_cells} kitöltve")
        
        if valid_data_count < 10:
            logger.warning(f"⚠️ Túl kevés valódi adat ({valid_data_count}) - placeholder megjelenítése")
            self._plot_heatmap_placeholder()
            return
        
        # === 5. SZÍNSKÁLA BEÁLLÍTÁSA ===
        
        cmap, norm = self._get_colormap_and_norm(calendar_matrix)
        
        # === 6. ✅ PCOLORMESH TELJES TÉGLALAP RENDERELÉS ===
        
        logger.info("🎨 PCOLORMESH rendering - TELJES TÉGLALAPOK")
        
        # Koordináták a cellák széleihez (53 hét + 1, 7 nap + 1)
        x_edges = np.arange(54) - 0.5  # 53 hét + 1 = 54 él
        y_edges = np.arange(8) - 0.5   # 7 nap + 1 = 8 él
        
        # ✅ PCOLORMESH - vektorgrafikus téglalapok + RÁCS VONALAK
        im = self.ax.pcolormesh(x_edges, y_edges, calendar_matrix, 
                               cmap=cmap, norm=norm, shading='flat',
                               edgecolors='lightgray', linewidths=0.5)
        
        logger.debug("✅ pcolormesh renderelés kész - TELJES TÉGLALAPOK")
        
        # === 7. TENGELYEK ÉS CÍMKÉK ===
        
        self._setup_axes_and_labels(min_date, max_date)
        
        # === 8. COLORBAR LÉTREHOZÁSA ===
        
        self._create_colorbar(im)
        
        # === 9. FORMÁZÁS ===
        
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')
        
        # Dinamikus cím
        period_text = self._format_period_text(min_date, max_date, total_days)
        full_title = f"{self.chart_title}{period_text}"
        
        self.ax.set_title(full_title, fontsize=18, fontweight='bold', pad=20, color=text_color)
        
        # Grid eltávolítása (pcolormesh-nél nem szükséges)
        self.ax.grid(False)
        
        # Layout optimalizálás
        self.figure.tight_layout()
        
        logger.info(f"✅ 365 konstans heatmap kész - TELJES TÉGLALAPOK, {valid_data_count} adat")
    
    def _aggregate_to_365(self, values: list, total_days: int) -> np.ndarray:
        """
        🎯 KONSTANS 365 AGGREGÁCIÓ - bármely időszakot 365 értékre
        
        LOGIKA:
        - Bin méret = total_days / 365.0
        - Hőmérséklet: átlag/bin
        - Csapadék: összeg/bin  
        - Szél: maximum/bin
        """
        if total_days <= 365:
            # Rövid időszak: kitöltés 365-re (ismétlés vagy NaN)
            result = np.full(365, np.nan)
            result[:len(values)] = values
            
            logger.debug(f"📊 Rövid időszak: {len(values)} → 365 (kitöltés)")
            return result
        
        # Hosszú időszak: aggregáció 365 bin-re
        bin_size = total_days / 365.0
        aggregated = np.full(365, np.nan)
        
        for i in range(365):
            start_idx = int(i * bin_size)
            end_idx = int((i + 1) * bin_size)
            
            if start_idx < len(values):
                bin_values = values[start_idx:min(end_idx, len(values))]
                clean_values = [v for v in bin_values if v is not None and not np.isnan(v)]
                
                if clean_values:
                    # Paraméter-specifikus aggregáció
                    if 'temperature' in self.parameter:
                        aggregated[i] = np.mean(clean_values)  # Hőmérséklet: átlag
                    elif 'precipitation' in self.parameter:
                        aggregated[i] = np.sum(clean_values)   # Csapadék: összeg
                    elif 'wind' in self.parameter:
                        aggregated[i] = np.max(clean_values)   # Szél: maximum
                    else:
                        aggregated[i] = np.mean(clean_values)  # Alapértelmezett: átlag
        
        logger.debug(f"📊 Hosszú aggregáció: {total_days} nap → 365 bin (bin_size={bin_size:.2f})")
        
        return aggregated
    
    def _build_calendar_matrix(self, values_365: np.ndarray) -> np.ndarray:
        """
        🗓️ 7×53 kalendár mátrix építése 365 értékből
        
        STRUKTÚRA:
        - 7 sor (hétfő-vasárnap)
        - 53 oszlop (hetek)
        - 365 értéket elhelyezzük kronologikusan
        """
        # 7 nap × 53 hét = 371 cella (365+ érték tárolására)
        calendar_matrix = np.full((7, 53), np.nan)
        
        # 365 értéket helyezzük el sorfolytonosan
        for i, value in enumerate(values_365):
            if i >= 7 * 53:  # Biztonsági határérték
                break
                
            week = i // 7
            day = i % 7
            
            if week < 53:
                calendar_matrix[day, week] = value
        
        # 🌧️ CSAPADÉK és 💨 SZÉL: NaN → 0 (fehér szín biztosításához)
        if 'precipitation' in self.parameter or 'wind' in self.parameter:
            calendar_matrix = np.nan_to_num(calendar_matrix, nan=0.0)
            logger.debug(f"🔧 NaN értékek 0-ra állítva ({self.parameter})")
        
        logger.debug(f"🗓️ Kalendár mátrix: {calendar_matrix.shape}, {np.sum(~np.isnan(calendar_matrix))} kitöltött cella")
        
        return calendar_matrix
    
    def _get_colormap_and_norm(self, calendar_matrix: np.ndarray) -> tuple:
        """
        🎨 Színskála és normalizálás meghatározása
        
        PRIORITÁS:
        1. Custom colormap (_custom_cmap, _custom_norm) - meteorológiai színek
        2. Paraméter-specifikus colormap (hőmérséklet/csapadék/szél)
        3. Alapértelmezett viridis
        """
        
        # ✅ 1. CUSTOM COLORMAP PRIORITÁS (meteorológiai színek)
        if self._custom_cmap is not None and self._custom_norm is not None:
            logger.info(f"🎨 Custom colormap használata: {type(self._custom_cmap).__name__}")
            return self._custom_cmap, self._custom_norm
        
        # 2. AUTOMATIC COLORMAP VÁLASZTÁS
        valid_values = calendar_matrix[~np.isnan(calendar_matrix)]
        if len(valid_values) == 0:
            logger.warning("⚠️ Nincs érvényes adat - alapértelmezett viridis")
            return 'viridis', None
            
        vmin = valid_values.min()
        vmax = valid_values.max()
        
        # 🔧 PARAMÉTER-SPECIFIKUS COLORMAP
        if 'temperature' in self.parameter:
            if vmin < 0 and vmax > 20:  # Teljes szezonális spektrum
                cmap = 'RdYlBu_r'  # Piros-Sárga-Kék (fordított)
                logger.debug("🌡️ Hőmérséklet: RdYlBu_r (szezonális)")
            elif vmax <= 15:  # Főleg hideg időszak
                cmap = 'Blues'
                logger.debug("🌡️ Hőmérséklet: Blues (hideg)")
            elif vmin >= 15:  # Főleg meleg időszak
                cmap = 'Reds'
                logger.debug("🌡️ Hőmérséklet: Reds (meleg)")
            else:
                cmap = 'viridis'
                logger.debug("🌡️ Hőmérséklet: viridis (alapértelmezett)")
        elif 'precipitation' in self.parameter:
            cmap = 'Blues'  # Kék skála csapadékhoz
            logger.debug("🌧️ Csapadék: Blues")
        elif 'wind' in self.parameter:
            cmap = 'Greens'  # Zöld skála szélhez
            logger.debug("💨 Szél: Greens")
        else:
            cmap = 'viridis'
            logger.debug("🎨 Egyéb paraméter: viridis")
        
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
        
        logger.info(f"🎨 Auto colormap: {cmap}, tartomány: {vmin:.2f} - {vmax:.2f}")
        
        return cmap, norm
    
    def _setup_axes_and_labels(self, min_date: pd.Timestamp, max_date: pd.Timestamp) -> None:
        """
        🏷️ Tengelyek és címkék beállítása - INTELLIGENS IDŐSZAK ALAPJÁN
        """
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')
        
        total_days = (max_date - min_date).days + 1
        
        # === X TENGELY - INTELLIGENS CÍMKÉZÉS IDŐSZAK ALAPJÁN ===
        
        # Hetek száma (53 maxmium)
        total_weeks = 53
        
        if total_days <= 400:  # ~1 év vagy kevesebb
            # HAVI CÍMKÉK rövid időszakra
            tick_interval = 4  # ~havi címkék (4 hét = ~1 hónap)
            x_ticks = np.arange(2, total_weeks, tick_interval)  # 2, 6, 10, 14...
            
            x_labels = []
            for week_idx in x_ticks:
                # Évszak alapú címkék
                month_approx = int((week_idx * 12) / 52) + 1  # 1-12 hónap
                month_names = ['Jan', 'Feb', 'Már', 'Ápr', 'Máj', 'Jún', 
                              'Júl', 'Aug', 'Sze', 'Okt', 'Nov', 'Dec']
                if 1 <= month_approx <= 12:
                    x_labels.append(month_names[month_approx - 1])
                else:
                    x_labels.append(f"H{week_idx}")
            
        elif total_days <= 1100:  # ~2-3 év
            # ÉVSZAK CÍMKÉK közepes időszakra
            tick_interval = 13  # ~évszakonkénti címkék (13 hét = ~évszak)
            x_ticks = np.arange(6, total_weeks, tick_interval)  # 6, 19, 32, 45
            
            x_labels = ['Tavasz', 'Nyár', 'Ősz', 'Tél'][:len(x_ticks)]
            
        else:  # 3+ év - HOSSZÚ IDŐSZAK
            # ÁV CÍMKÉK hosszú időszakra
            tick_interval = 26  # ~félévenkénti címkék (26 hét = ~fél év)
            x_ticks = np.arange(13, total_weeks, tick_interval)  # 13, 39
            
            x_labels = ['Fél év', 'Teljes év'][:len(x_ticks)]
        
        self.ax.set_xticks(x_ticks)
        self.ax.set_xticklabels(x_labels, color=text_color, rotation=0, ha='center')
        
        # X tengely címke - IDŐSZAK ALAPJÁN
        if total_days <= 400:
            xlabel = 'Hónapok (365 napos konstans felbontás)'
        elif total_days <= 1100:
            xlabel = 'Évszakok (365 napos konstans felbontás)'
        else:
            xlabel = f'Időszak ({total_days} nap → 365 konstans felbontás)'
            
        self.ax.set_xlabel(xlabel, color=text_color, fontsize=12)
        
        # === Y TENGELY - NAPOK (változatlan) ===
        
        self.ax.set_yticks(range(7))
        self.ax.set_yticklabels([
            'Hétfő', 'Kedd', 'Szerda', 'Csütörtök', 'Péntek', 'Szombat', 'Vasárnap'
        ], color=text_color)
        
        # Y tengely fordítása (hétfő legyen felül)
        self.ax.invert_yaxis()
        
        # === TENGELYEK TARTOMÁNYÁNAK BEÁLLÍTÁSA ===
        
        self.ax.set_xlim(-0.5, 52.5)  # 53 hét (0-52)
        self.ax.set_ylim(-0.5, 6.5)   # 7 nap (0-6)
        
        logger.debug(f"🏷️ Tengelyek beállítva - {total_days} napra ({xlabel})")
    
    def _create_colorbar(self, im) -> None:
        """
        🎨 Colorbar létrehozása paraméter-specifikus címkével
        """
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')
        
        try:
            # Meglévő colorbar törlése
            if self._colorbar:
                self._colorbar.remove()
                self._colorbar = None
                
            # Új colorbar létrehozása
            self._colorbar = self.figure.colorbar(im, ax=self.ax, shrink=0.8, aspect=30, pad=0.02)
            
            # ✅ PARAMÉTER-SPECIFIKUS CÍMKE
            if 'temperature' in self.parameter:
                label = 'Hőmérséklet (°C)'
            elif 'precipitation' in self.parameter:
                label = 'Csapadék (mm)'
            elif 'wind' in self.parameter:
                label = 'Szélsebesség (km/h)'
            else:
                label = 'Érték'
            
            self._colorbar.set_label(label, fontsize=12, fontweight='500', color=text_color, labelpad=15)
            self._colorbar.ax.tick_params(colors=text_color, labelsize=10)
            
            logger.debug(f"✅ Colorbar létrehozva: {label}")
            
        except Exception as e:
            # Colorbar hiba nem kritikus
            logger.warning(f"⚠️ Colorbar létrehozási hiba (nem kritikus): {e}")
    
    def _format_period_text(self, min_date: pd.Timestamp, max_date: pd.Timestamp, total_days: int) -> str:
        """
        📅 Időszak szöveg formázása címhez
        """
        years = sorted(set([min_date.year, max_date.year]))
        
        if len(years) == 1:
            # Egy éven belüli időszak
            if (min_date.month == 1 and min_date.day == 1 and 
                max_date.month == 12 and max_date.day == 31):
                return f" ({years[0]})"  # Teljes év
            else:
                return f" ({min_date.strftime('%Y.%m.%d')} - {max_date.strftime('%m.%d')})"
        else:
            # Több évet átfogó időszak
            return f" ({min_date.strftime('%Y.%m')} - {max_date.strftime('%Y.%m')}, {total_days} nap)"
    
    def _plot_heatmap_placeholder(self) -> None:
        """
        📋 Heatmap placeholder ha nincs elegendő adat
        """
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')
        surface_color = current_colors.get('surface_variant', '#f9fafb')
        
        placeholder_text = f'📅 Konstans Heatmap (365 téglalap)\n\n'
        placeholder_text += f'❌ Nincs elegendő adat\n\n'
        placeholder_text += f'Paraméter: {self.parameter}\n\n'
        placeholder_text += f'A heatmap megjelenítéséhez\nlegalább 10 valódi adat\nszükséges az API-ból.\n\n'
        placeholder_text += f'🎯 VÉGLEGES VERZIÓ:\n'
        placeholder_text += f'• pcolormesh renderelés\n'
        placeholder_text += f'• Custom colormap támogatás\n'
        placeholder_text += f'• 365 konstans téglalap'
        
        self.ax.text(0.5, 0.5, placeholder_text, 
                    ha='center', va='center', transform=self.ax.transAxes,
                    fontsize=12, color=text_color, linespacing=1.5,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor=surface_color, 
                             edgecolor=current_colors.get('border', '#d1d5db')))
        
        self.ax.set_title(f"{self.chart_title} - Nincs Adat", fontsize=18, fontweight='bold', pad=20, color=text_color)
        
        # Tengelyek elrejtése placeholder módban
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        
        logger.debug("📋 Heatmap placeholder megjelenítve")


# Modul szintű export
__all__ = ['HeatmapCalendarChart']
