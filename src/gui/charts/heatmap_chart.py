#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Heatmap Calendar Chart
🎯 CLEAN HEATMAP - TOOLTIP NÉLKÜL

📋 FUNKCIÓK:
✅ Calendar heatmap renderelés
✅ Valódi hónap címkék
✅ 365 konstans felbontás
✅ Meteorológiai színskálák

📍 Fájl helye: src/gui/charts/heatmap_chart.py
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
    🎯 HEATMAP CHART - CLEAN VERZIÓ
    
    FELELŐSSÉGEK:
    - ✅ TELJES TÉGLALAP renderelése (pcolormesh)
    - ✅ Custom meteorológiai színskálák
    - ✅ Dinamikus paraméter kezelés (hőmérséklet/csapadék/szél)
    - ✅ 365 konstans téglalap logika aggregációval
    - ✅ Kalendár mátrix építés (7×53 cellák)
    - ✅ Valódi hónap címkék
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(figsize=(20, 12), parent=parent)
        self.chart_title = "📅 Konstans Heatmap"
        self.parameter = "temperature_2m_mean"
        
        # Colorbar tracking
        self._colorbar = None
        
        # Custom colormap support
        self._custom_cmap = None
        self._custom_norm = None
        
        # Calendar data
        self._calendar_matrix = None
        self._min_date = None
        self._max_date = None
        self._total_days = 0
        self._first_day_weekday = 0
        
        logger.info("HeatmapCalendarChart inicializálva - CLEAN VERZIÓ")
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """Data update"""
        logger.info(f"📅 HeatmapCalendarChart.update_data() (param: {self.parameter})")
        
        try:
            if self._is_updating:
                logger.debug("⚠️ Heatmap update már folyamatban, skip")
                return
            
            self._is_updating = True
            
            # Extract daily data
            df = self._extract_daily_data(data)
            if df.empty:
                logger.warning(f"⚠️ Üres DataFrame ({self.parameter}), heatmap törlése")
                self.clear_chart()
                return
            
            self.current_data = df
            
            # Clear figure
            logger.debug("🧹 Figure.clear() - DUPLIKÁCIÓ ELLENI VÉDELEM")
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            self._colorbar = None
            
            # Apply theme
            self._apply_theme_to_chart()
            
            # Plot heatmap
            self._plot_365_constant_heatmap(df)
            
            self.draw()
            self._is_updating = False
            
            logger.info(f"✅ HeatmapCalendarChart frissítés kész - {self.parameter}")
            
        except Exception as e:
            logger.error(f"❌ Heatmap calendar chart hiba ({self.parameter}): {e}", exc_info=True)
            self._is_updating = False
            self.clear_chart()
    
    def _extract_daily_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Extract daily data for parameter"""
        daily_data = data.get("daily", {})
        dates = daily_data.get("time", [])
        parameter_values = daily_data.get(self.parameter, [])
        
        logger.debug(f"🔍 Paraméter keresése: {self.parameter}")
        logger.debug(f"  📊 Dates: {len(dates)} elem")
        logger.debug(f"  📈 Values: {len(parameter_values)} elem")
        
        if not dates or not parameter_values:
            logger.warning(f"⚠️ Hiányzó {self.parameter} adatok")
            return pd.DataFrame()
        
        if len(dates) != len(parameter_values):
            logger.error(f"❌ Eltérő hosszúságú {self.parameter} adatok")
            return pd.DataFrame()
        
        df = pd.DataFrame({
            'date': pd.to_datetime(dates),
            self.parameter: parameter_values
        })
        
        df = df.dropna()
        
        if df.empty:
            logger.warning(f"⚠️ Nincs érvényes {self.parameter} adat")
        else:
            logger.info(f"✅ {len(df)} érvényes {self.parameter} adat betöltve")
        
        return df
    
    def _plot_365_constant_heatmap(self, df: pd.DataFrame) -> None:
        """Plot 365 constant heatmap"""
        logger.info(f"🎨 _plot_365_constant_heatmap() ({self.parameter})")
        
        if df.empty or self.parameter not in df.columns:
            self._plot_heatmap_placeholder()
            return
        
        # Date range analysis
        self._min_date = df['date'].min()
        self._max_date = df['date'].max()
        self._total_days = (self._max_date - self._min_date).days + 1
        self._first_day_weekday = self._min_date.weekday()
        
        logger.info(f"🗓️ Időszak: {self._min_date} - {self._max_date} ({self._total_days} nap)")
        
        # Aggregate to 365 values
        values_365 = self._aggregate_to_365(df[self.parameter].tolist(), self._total_days)
        
        # Build calendar matrix
        self._calendar_matrix = self._build_calendar_matrix(values_365, self._min_date)
        
        logger.debug(f"🎯 Kalendár mátrix shape: {self._calendar_matrix.shape}")
        logger.debug(f"📅 Valódi dátum címkék használata")
        
        # Validate data
        valid_data_count = np.sum(~np.isnan(self._calendar_matrix))
        
        if valid_data_count < 10:
            logger.warning(f"⚠️ Túl kevés valódi adat ({valid_data_count})")
            self._plot_heatmap_placeholder()
            return
        
        # Get colormap
        cmap, norm = self._get_colormap_and_norm(self._calendar_matrix)
        
        # Render pcolormesh
        x_edges = np.arange(54) - 0.5
        y_edges = np.arange(8) - 0.5
        
        im = self.ax.pcolormesh(x_edges, y_edges, self._calendar_matrix, 
                               cmap=cmap, norm=norm, shading='flat',
                               edgecolors='lightgray', linewidths=0.5)
        
        # Setup axes and labels
        self._setup_axes_and_labels(self._min_date, self._max_date)
        
        # Create colorbar
        self._create_colorbar(im)
        
        # Formatting
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')
        
        period_text = self._format_period_text(self._min_date, self._max_date, self._total_days)
        full_title = f"{self.chart_title}{period_text}"
        
        self.ax.set_title(full_title, fontsize=18, fontweight='bold', pad=20, color=text_color)
        self.ax.grid(False)
        self.figure.tight_layout()
        
        logger.info(f"✅ 365 konstans heatmap kész - {valid_data_count} adat")
    
    def _get_temperature_category(self, temp: float) -> str:
        """Temperature categorization"""
        if temp >= 35:
            return "🔥 Extrém forró"
        elif temp >= 30:
            return "🌞 Forró"
        elif temp >= 25:
            return "☀️ Meleg"
        elif temp >= 20:
            return "🌤️ Kellemes"
        elif temp >= 15:
            return "🌥️ Hűvös"
        elif temp >= 10:
            return "🌫️ Hideg"
        elif temp >= 0:
            return "❄️ Fagyos"
        else:
            return "🧊 Extrém hideg"
    
    def _get_precipitation_category(self, precip: float) -> str:
        """Precipitation categorization"""
        if precip >= 50:
            return "⛈️ Viharos zápo"
        elif precip >= 20:
            return "🌧️ Erős esőzés"
        elif precip >= 10:
            return "🌦️ Közepes esőzés"
        elif precip >= 2:
            return "🌦️ Gyenge esőzés"
        elif precip >= 0.5:
            return "💧 Szitálás"
        else:
            return "☀️ Száraz időjárás"
    
    def _get_wind_category(self, wind: float) -> str:
        """Wind speed categorization"""
        if wind >= 119:
            return "🌪️ Orkán erősségű szél"
        elif wind >= 90:
            return "💨 Viharos szél"
        elif wind >= 61:
            return "🌬️ Erős szél"
        elif wind >= 43:
            return "🍃 Élénk szél"
        elif wind >= 20:
            return "🌿 Mérsékelt szél"
        elif wind >= 10:
            return "🕊️ Gyenge szél"
        else:
            return "🌅 Szélcsend"
    
    def _aggregate_to_365(self, values: list, total_days: int) -> np.ndarray:
        """
        Aggregate any timespan to 365 values.
        If timespan is <= 365 days, it uses the original data without aggregation.
        """
        if total_days <= 365:
            # Nincs szükség aggregációra, az eredeti adatokat használjuk
            logger.debug(f"📊 Rövid időszak: {len(values)} nap, nincs aggregáció.")
            return np.array(values)

        # Hosszú időszak esetén aggregálunk
        bin_size = total_days / 365.0
        aggregated = np.full(365, np.nan)
        
        for i in range(365):
            start_idx = int(i * bin_size)
            end_idx = int((i + 1) * bin_size)
            
            if start_idx < len(values):
                bin_values = values[start_idx:min(end_idx, len(values))]
                clean_values = [v for v in bin_values if v is not None and not np.isnan(v)]
                
                if clean_values:
                    if 'temperature' in self.parameter:
                        aggregated[i] = np.mean(clean_values)
                    elif 'precipitation' in self.parameter:
                        aggregated[i] = np.sum(clean_values)
                    elif 'wind' in self.parameter:
                        aggregated[i] = np.max(clean_values)
                    else:
                        aggregated[i] = np.mean(clean_values)
        
        logger.debug(f"📊 Hosszú aggregáció: {total_days} nap → 365 bin")
        return aggregated
    
    def _build_calendar_matrix(self, values: np.ndarray, start_date: pd.Timestamp) -> np.ndarray:
        """
        Build 7x53 calendar matrix, considering the start day's weekday.
        """
        # A hét első napjának megkeresése (0=Hétfő, 6=Vasárnap)
        first_day_weekday = start_date.weekday()
        
        # A teljes naptár mérete: az eltolás + az adatok hossza
        total_cells = first_day_weekday + len(values)
        
        # Feltöltjük a teljes listát NaN-okkal
        full_year_values = np.full(total_cells, np.nan)
        
        # Beillesztjük a valódi adatokat a megfelelő helyre
        full_year_values[first_day_weekday:] = values
        
        # Létrehozzuk a 7x53-as mátrixot
        calendar_matrix = np.full((7, 53), np.nan)
        
        num_weeks = (total_cells + 6) // 7
        
        for week in range(min(num_weeks, 53)):
            start_idx = week * 7
            end_idx = start_idx + 7
            week_data = full_year_values[start_idx:end_idx]
            
            # Biztosítjuk, hogy a hét adatai 7 eleműek legyenek
            padded_week_data = np.pad(week_data, (0, 7 - len(week_data)), 'constant', constant_values=np.nan)
            calendar_matrix[:, week] = padded_week_data
            
        if 'precipitation' in self.parameter or 'wind' in self.parameter:
            calendar_matrix = np.nan_to_num(calendar_matrix, nan=0.0)
        
        logger.debug(f"🗓️ OKOS Kalendár mátrix: {calendar_matrix.shape}, első nap: {start_date.strftime('%A')}")
        return calendar_matrix
    
    def _get_colormap_and_norm(self, calendar_matrix: np.ndarray) -> tuple:
        """Get colormap and normalization"""
        if self._custom_cmap is not None and self._custom_norm is not None:
            logger.info(f"🎨 Custom colormap használata")
            return self._custom_cmap, self._custom_norm
        
        valid_values = calendar_matrix[~np.isnan(calendar_matrix)]
        if len(valid_values) == 0:
            logger.warning("⚠️ Nincs érvényes adat")
            return 'viridis', None
            
        vmin = valid_values.min()
        vmax = valid_values.max()
        
        if 'temperature' in self.parameter:
            if vmin < 0 and vmax > 20:
                cmap = 'RdYlBu_r'  # REVERSE: piros=meleg, kék=hideg
                logger.debug("🌡️ Hőmérséklet: RdYlBu_r (piros=meleg, kék=hideg)")
            elif vmax <= 15:
                cmap = 'Blues_r'  # Hideg: sötétkék=hidegebb
                logger.debug("🌡️ Hőmérséklet: Blues_r (hideg)")
            elif vmin >= 15:
                cmap = 'Reds'  # Meleg: sötétpiros=melegebb  
                logger.debug("🌡️ Hőmérséklet: Reds (meleg)")
            else:
                cmap = 'viridis'
                logger.debug("🌡️ Hőmérséklet: viridis (alapértelmezett)")
        elif 'precipitation' in self.parameter:
            cmap = 'Blues'
        elif 'wind' in self.parameter:
            cmap = 'Greens'
        else:
            cmap = 'viridis'
        
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
        return cmap, norm
    
    def _setup_axes_and_labels(self, min_date: pd.Timestamp, max_date: pd.Timestamp) -> None:
        """Setup axes VALÓDI DÁTUMOKKAL"""
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')
        
        total_days = (max_date - min_date).days + 1
        
        # X TENGELY - VALÓDI HÓNAPOK A VALÓDI POZÍCIÓBAN
        x_ticks = []
        x_labels = []
        
        # Végigmegyünk a heteken és keressük a hónap váltásokat
        current_date = min_date
        seen_months = set()
        
        hungarian_months = [
            '', 'Jan', 'Feb', 'Már', 'Ápr', 'Máj', 'Jún',
            'Júl', 'Aug', 'Sze', 'Okt', 'Nov', 'Dec'
        ]
        
        # 53 hét végigiterálása
        for week_idx in range(53):
            # Hét első napjának kiszámítása
            days_from_start = week_idx * 7 - self._first_day_weekday
            
            if days_from_start >= 0 and days_from_start < total_days:
                week_date = min_date + pd.Timedelta(days=days_from_start)
                month_key = (week_date.year, week_date.month)
                
                # Ha új hónap, jelöljük
                if month_key not in seen_months and week_idx % 4 == 0:  # Minden 4. héten
                    seen_months.add(month_key)
                    x_ticks.append(week_idx)
                    
                    month_name = hungarian_months[week_date.month]
                    if week_date.year != min_date.year:
                        x_labels.append(f"{month_name}\n{week_date.year}")
                    else:
                        x_labels.append(month_name)
        
        # Ha túl kevés címke, alapértelmezett
        if len(x_ticks) < 3:
            x_ticks = np.arange(6, 53, 8)
            x_labels = []
            for week_idx in x_ticks:
                days_from_start = week_idx * 7 - self._first_day_weekday
                if days_from_start >= 0 and days_from_start < total_days:
                    week_date = min_date + pd.Timedelta(days=days_from_start)
                    month_name = hungarian_months[week_date.month]
                    x_labels.append(month_name)
                else:
                    x_labels.append(f"H{week_idx}")
        
        self.ax.set_xticks(x_ticks)
        self.ax.set_xticklabels(x_labels, color=text_color, rotation=0, ha='center')
        self.ax.set_xlabel('Valódi hónapok (helyes pozíciók)', color=text_color, fontsize=12)
        
        # Y TENGELY - HÉTKÖZNAPOK
        self.ax.set_yticks(range(7))
        self.ax.set_yticklabels([
            'Hétfő', 'Kedd', 'Szerda', 'Csütörtök', 'Péntek', 'Szombat', 'Vasárnap'
        ], color=text_color)
        self.ax.invert_yaxis()
        
        self.ax.set_xlim(-0.5, 52.5)
        self.ax.set_ylim(-0.5, 6.5)
    
    def _create_colorbar(self, im) -> None:
        """Create colorbar with parameter-specific label"""
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')
        
        try:
            if self._colorbar:
                self._colorbar.remove()
                self._colorbar = None
                
            self._colorbar = self.figure.colorbar(im, ax=self.ax, shrink=0.8, aspect=30, pad=0.02)
            
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
            
        except Exception as e:
            logger.warning(f"⚠️ Colorbar hiba: {e}")
    
    def _format_period_text(self, min_date: pd.Timestamp, max_date: pd.Timestamp, total_days: int) -> str:
        """Format period text for title"""
        years = sorted(set([min_date.year, max_date.year]))
        
        if len(years) == 1:
            if (min_date.month == 1 and min_date.day == 1 and 
                max_date.month == 12 and max_date.day == 31):
                return f" ({years[0]})"
            else:
                return f" ({min_date.strftime('%Y.%m.%d')} - {max_date.strftime('%m.%d')})"
        else:
            return f" ({min_date.strftime('%Y.%m')} - {max_date.strftime('%Y.%m')}, {total_days} nap)"
    
    def _plot_heatmap_placeholder(self) -> None:
        """Plot placeholder when insufficient data"""
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')
        surface_color = current_colors.get('surface_variant', '#f9fafb')
        
        placeholder_text = f'📅 Konstans Heatmap (365 téglalap)\n\n'
        placeholder_text += f'❌ Nincs elegendő adat\n\n'
        placeholder_text += f'Paraméter: {self.parameter}\n\n'
        placeholder_text += f'A heatmap megjelenítéséhez\nlegalább 10 valódi adat\nszükséges az API-ból.\n\n'
        placeholder_text += f'🎯 FUNKCIÓK:\n'
        placeholder_text += f'• Valódi hónap címkék\n'
        placeholder_text += f'• 365 konstans felbontás\n'
        placeholder_text += f'• Meteorológiai színskálák\n'
        placeholder_text += f'📊 Clean heatmap!'
        
        self.ax.text(0.5, 0.5, placeholder_text, 
                    ha='center', va='center', transform=self.ax.transAxes,
                    fontsize=12, color=text_color, linespacing=1.5,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor=surface_color, 
                             edgecolor=current_colors.get('border', '#d1d5db')))
        
        self.ax.set_title(f"{self.chart_title} - Nincs Adat", fontsize=18, fontweight='bold', pad=20, color=text_color)
        
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)


# Module export
__all__ = ['HeatmapCalendarChart']