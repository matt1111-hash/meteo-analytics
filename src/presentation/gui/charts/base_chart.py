#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Base Chart Widget
Alaposztály minden weather chart widget-hez ColorPalette integrációval.

🎨 TÉMA INTEGRÁCIÓ: SimplifiedThemeManager + ColorPalette használata
🔧 KRITIKUS JAVÍTÁS: Robusztus chart lifecycle management + duplikáció bugfix
🌪️ WIND GUSTS TÁMOGATÁS: Alap infrastruktúra minden chart típushoz
✅ Piros (#C43939) téma támogatás
✅ Professzionális emoji font kezelés
✅ Memory leak-ek megszüntetése
✅ Optimális legend pozíció
✅ Teljes téma szinkronizáció
🚨 KRITIKUS JAVÍTÁS: PySide6 backend használata Qt5 helyett
"""

from typing import Optional

import matplotlib

matplotlib.use('QtAgg')  # 🚨 JAVÍTOTT: PySide6 backend

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from ..color_palette import ColorPalette
from ..theme_manager import (
    get_current_colors,
    get_theme_manager,
    register_widget_for_theming,
)


class WeatherChart(FigureCanvas):
    """
    Alap időjárási grafikon widget matplotlib-tal.
    Base class a specifikus chart típusokhoz - BŐVÍTETT PROFESSZIONÁLIS VERZIÓ + SIMPLIFIED THEMEMANAGER.
    🎨 TÉMA INTEGRÁCIÓ: SimplifiedThemeManager színpaletta automatikus alkalmazása
    🔧 KRITIKUS JAVÍTÁS: Robusztus chart lifecycle management + duplikáció bugfix + HELYES API HASZNÁLAT
    🚨 PySide6 BACKEND: Qt6 támogatás Qt5 helyett
    """

    # Signalok
    chart_clicked = Signal(float, float)  # x, y koordináták
    export_requested = Signal(str)  # format (png, pdf, svg)

    def __init__(self, figsize=(12, 8), parent: Optional[QWidget] = None):
        """
        Chart widget inicializálása - TÉMA SZINKRONIZÁCIÓ JAVÍTVA.
        
        Args:
            figsize: Figure mérete (width, height) - NAGYOBB!
            parent: Szülő widget
        """
        # 🔧 KRITIKUS JAVÍTÁS: Figure színek dinamikusan téma alapján
        current_colors = get_current_colors()
        figure_bg = current_colors.get('surface', '#ffffff')

        self.figure = Figure(figsize=figsize, dpi=100, facecolor=figure_bg)
        super().__init__(self.figure)
        self.setParent(parent)

        # 🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ
        self.theme_manager = get_theme_manager()
        self.color_palette = ColorPalette()

        # 🔧 KRITIKUS JAVÍTÁS: Weather színpaletta generálás
        self.weather_colors = self.color_palette.generate_weather_palette("#C43939")  # Piros téma

        # Chart konfiguráció
        self.current_data = None
        self.chart_title = ""
        self.x_label = "Dátum"
        self.y_label = ""
        self.grid_enabled = True
        self.legend_enabled = True

        # 🔧 KRITIKUS JAVÍTÁS: Chart state tracking duplikáció ellen
        self._is_updating = False
        self._last_update_data = None

        # Font cache tracking
        self._font_cache_rebuilt = False

        # Matplotlib stílus beállítások - CSAK FONT/MÉRET, SZÍNEK KÜLÖN
        self._setup_matplotlib_style()

        # Axis referencia - TÉMA SZÍNEKKEL
        self.ax = self.figure.add_subplot(111)

        # === INITIAL THEME APPLICATION ===
        self._apply_theme_to_chart()

        # Interaktív funkciók
        self.mpl_connect('button_press_event', self._on_click)

        # 🎨 WIDGET REGISZTRÁCIÓ TÉMA KEZELÉSHEZ - AUTOMATIKUS
        register_widget_for_theming(self, "chart")

        # 🎨 TÉMA VÁLTOZÁS FELIRATKOZÁS
        self.theme_manager.theme_changed.connect(self._on_theme_changed)

        print(f"✅ DEBUG: WeatherChart initialized with theme: {self.theme_manager.get_current_theme()}")

    def _setup_matplotlib_style(self) -> None:
        """
        Matplotlib stílus beállítások - TÉMA SZINKRONIZÁCIÓ JAVÍTVA.
        🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ: Dinamikus színek témavaltáskor
        🔧 KRITIKUS JAVÍTÁS: NEM GLOBÁLIS rcParams → Figure-specifikus színek
        """
        # 🔧 KRITIKUS JAVÍTÁS: NE MÓDOSÍTSUNK GLOBÁLIS rcParams-ot
        # Helyette csak font és méret beállítások maradjanak globálisak

        # 🔧 EMOJI-TÁMOGATOTT FONTOK BEÁLLÍTÁSA - EGYSZER GLOBÁLISAN
        emoji_font_fallbacks = [
            'Segoe UI Emoji',    # Windows 10/11 emoji font
            'Apple Color Emoji', # macOS emoji font
            'Noto Color Emoji',  # Linux (Ubuntu, Fedora) emoji font
            'Noto Emoji',        # Linux alternatíva
            'Symbola',           # Linux univerzális szimbólum font
            'DejaVu Sans',       # Eredeti fallback (emoji nélkül)
            'sans-serif'         # Végső fallback
        ]

        print(f"🎨 DEBUG: Emoji font setup: {emoji_font_fallbacks[:3]}")

        # CSAK FONT ÉS MÉRET beállítások globálisan - SZÍNEK NEM!
        matplotlib.rcParams.update({
            # 🔧 KRITIKUS JAVÍTÁS: Emoji fontok elsődlegesen
            'font.family': emoji_font_fallbacks,
            'font.sans-serif': emoji_font_fallbacks,

            # Méret és stílus beállítások - PROFESSZIONÁLIS
            'font.size': 12,           # Nagyobb alapfont
            'axes.titlesize': 16,      # Nagyobb címek
            'axes.labelsize': 14,      # Nagyobb tengelycímkék
            'xtick.labelsize': 11,     # Nagyobb tick labelek
            'ytick.labelsize': 11,
            'legend.fontsize': 12,     # Nagyobb legend
            'figure.titlesize': 18,    # Nagyobb figura cím

            # Vonalstílusok és vastagságok - PROFESSZIONÁLIS
            'lines.linewidth': 2.5,    # Vastagabb vonalak
            'axes.linewidth': 1.2,     # Vastagabb tengelyek
            'grid.linewidth': 0.8,     # Vastagabb grid

            # Modern dizájn elemek
            'axes.spines.top': False,  # Modern: felső keret eltávolítása
            'axes.spines.right': False, # Modern: jobb oldali keret eltávolítása

            # 🔧 EMOJI ESPECIFIKUS BEÁLLÍTÁSOK
            'axes.unicode_minus': False,  # Unicode mínusz kezelés javítása
            'font.stretch': 'normal',     # Font stretch beállítás
            'font.weight': 'normal'       # Font súly normalizálás
        })

        # 🔧 KRITIKUS JAVÍTÁS: Font cache tisztítása - EGYSZER
        try:
            import matplotlib.font_manager as fm
            if not hasattr(self, '_font_cache_rebuilt'):
                fm._rebuild()
                self._font_cache_rebuilt = True
                print("✅ DEBUG: Matplotlib font cache újraépítve emoji fontokkal")
        except Exception as e:
            print(f"⚠️ DEBUG: Font cache újraépítés hiba (nem kritikus): {e}")

        print("✅ DEBUG: Matplotlib font/size setup complete - colors will be applied per-figure")

    def _on_theme_changed(self, theme_name: str) -> None:
        """
        🎨 TÉMA VÁLTOZÁS KEZELÉSE - TELJES CHART SZINKRONIZÁCIÓ.
        
        Args:
            theme_name: Új téma neve ("light" vagy "dark")
        """
        print(f"🎨 DEBUG: WeatherChart theme changing: {self.theme_manager.get_current_theme()} → {theme_name}")

        # Weather színpaletta újragenerálása új témával
        self.weather_colors = self.color_palette.generate_weather_palette("#C43939")  # Piros téma

        # Chart teljes újrarajzolása új színekkel
        self._redraw_with_new_theme()

        # Ha van aktuális adat, chart újrafrissítése szükséges lehet
        if self.current_data is not None:
            print("🔄 DEBUG: Re-applying data to chart with new theme colors")
            # A chart tartalmát nem rajzoljuk újra, csak a színeket frissítjük
            # Ez elkerüli a duplikált adatmegjelenítést

        print(f"✅ DEBUG: WeatherChart theme change complete: {theme_name}")

    def _redraw_with_new_theme(self) -> None:
        """
        🎨 KRITIKUS JAVÍTÁS: Chart újrarajzolása új téma színekkel - TELJES SZINKRONIZÁCIÓ.
        Témavaltáskor minden chart elem színe frissül.
        """
        try:
            if self._is_updating:
                return

            print(f"🎨 DEBUG: Redrawing chart with new theme: {self.theme_manager.get_current_theme()}")

            # === TELJES CHART TÉMA ALKALMAZÁSA ===
            self._apply_theme_to_chart()

            # === SPECIFIKUS CHART ELEMEK SZÍNFRISSÍTÉSE ===

            # Ha van plotolt data, frissítjük a vonalak és elemek színeit is
            if hasattr(self, 'ax') and self.ax:
                current_colors = get_current_colors()

                # Minden matplotlib artist (vonalak, pontok, patches) színfrissítése
                for line in self.ax.get_lines():
                    # Meglévő vonalak színének módosítása a téma alapján
                    current_color = line.get_color()
                    # Ha alapértelmezett kék, akkor frissítjük
                    if current_color in ['#1f77b4', 'blue', 'b']:  # matplotlib default blue
                        line.set_color(current_colors.get('primary', '#C43939'))  # Piros téma

                # Bar chartok színfrissítése
                for patch in self.ax.patches:
                    current_facecolor = patch.get_facecolor()
                    # Alapértelmezett színek frissítése
                    if hasattr(patch, '_original_color_category'):
                        # Ha van kategória tag, használjuk azt
                        category = patch._original_color_category
                        if category in current_colors:
                            patch.set_facecolor(current_colors[category])

                # Annotations és text elemek frissítése
                text_color = current_colors.get('on_surface', '#1f2937')
                for text in self.ax.texts:
                    text.set_color(text_color)

                # Colorbar frissítése, ha van
                if hasattr(self, '_colorbar') and self._colorbar:
                    self._colorbar.ax.tick_params(colors=text_color)
                    if hasattr(self._colorbar, 'set_label'):
                        # Colorbar label színe
                        self._colorbar.set_label(
                            self._colorbar.ax.get_ylabel(),
                            color=text_color
                        )

            # === CANVAS FRISSÍTÉSE ===
            self.draw()

            print(f"✅ DEBUG: Chart successfully redrawn with theme: {self.theme_manager.get_current_theme()}")

        except Exception as e:
            print(f"❌ DEBUG: Theme redraw error: {e}")

    def _on_click(self, event) -> None:
        """Grafikon kattintás kezelése."""
        if event.inaxes and event.xdata and event.ydata:
            self.chart_clicked.emit(event.xdata, event.ydata)

    def clear_chart(self) -> None:
        """
        🔧 KRITIKUS JAVÍTÁS: Teljes chart törlése duplikáció nélkül + TÉMA SZÍNEK ALKALMAZÁSA.
        """
        print(f"🧹 DEBUG: {self.__class__.__name__}.clear_chart() - TÉMA SZINKRONIZÁCIÓ")
        try:
            # State reset
            self._is_updating = True

            # Figure teljes törlése - KRITIKUS a duplikáció ellen
            self.figure.clear()

            # Új axis létrehozása
            self.ax = self.figure.add_subplot(111)

            # 🎨 TÉMA SZÍNEK ALKALMAZÁSA AZ ÚJ AXIS-RA
            self._apply_theme_to_chart()

            # Canvas frissítése
            self.draw()

            # State cleanup
            self.current_data = None
            self._last_update_data = None
            self._is_updating = False

            print(f"✅ DEBUG: {self.__class__.__name__} chart törölve téma színekkel: {self.theme_manager.get_current_theme()}")

        except Exception as e:
            print(f"❌ DEBUG: Chart törlési hiba: {e}")
            self._is_updating = False

    def _apply_theme_to_chart(self) -> None:
        """
        🎨 KRITIKUS JAVÍTÁS: Teljes chart téma alkalmazása figure-specifikusan.
        TÉMA SZINKRONIZÁCIÓ: matplotlib figure ↔ SimplifiedThemeManager
        """
        # 🔧 AKTUÁLIS TÉMA SZÍNEK LEKÉRÉSE
        current_colors = get_current_colors()

        print(f"🎨 DEBUG: Applying theme colors to chart: {current_colors}")

        # === FIGURE SZINTŰ SZÍNEK ===

        # Figure háttér - TÉMA ALAPJÁN
        self.figure.patch.set_facecolor(current_colors.get('surface', '#ffffff'))

        # === AXIS SZINTŰ SZÍNEK ===

        if hasattr(self, 'ax') and self.ax:
            # Axis háttér
            self.ax.set_facecolor(current_colors.get('surface', '#ffffff'))

            # Text színek - MINDEN SZÖVEG ELEM
            text_color = current_colors.get('on_surface', '#1f2937')

            # Tick labelek és axis labelek
            self.ax.tick_params(colors=text_color, which='both')

            # Axis címkék színei - ha már be vannak állítva
            if self.ax.xaxis.label.get_text():
                self.ax.xaxis.label.set_color(text_color)
            if self.ax.yaxis.label.get_text():
                self.ax.yaxis.label.set_color(text_color)

            # Chart cím színe - ha már be van állítva
            if self.ax.title.get_text():
                self.ax.title.set_color(text_color)

            # Axis spine színek
            spine_color = current_colors.get('border', '#d1d5db')
            for spine in self.ax.spines.values():
                spine.set_color(spine_color)

            # Grid színek - ha engedélyezve
            if self.grid_enabled:
                grid_color = current_colors.get('border', '#d1d5db')
                grid_alpha = 0.3 if self.theme_manager.get_current_theme() == "light" else 0.2
                self.ax.grid(True, alpha=grid_alpha, color=grid_color)

            # Legend színek - ha létezik
            legend = self.ax.get_legend()
            if legend and self.legend_enabled:
                legend.get_frame().set_facecolor(current_colors.get('surface', '#ffffff'))
                legend.get_frame().set_edgecolor(current_colors.get('border', '#d1d5db'))
                # Legend text színek
                for text in legend.get_texts():
                    text.set_color(text_color)

        print("✅ DEBUG: Chart theme colors applied successfully")

    def export_chart(self, filepath: str, format: str = 'png', dpi: int = 300) -> bool:
        """
        Grafikon exportálása fájlba.
        
        Args:
            filepath: Cél fájl útvonala
            format: Fájl formátum (png, pdf, svg)
            dpi: Felbontás
            
        Returns:
            Sikeres export-e
        """
        try:
            self.figure.savefig(filepath, format=format, dpi=dpi, bbox_inches='tight')
            return True
        except Exception as e:
            print(f"Chart export hiba: {e}")
            return False

    def update_style(self, dark_theme: bool = False) -> None:
        """
        🎨 DEPRECATED: Téma váltás kezelése - SIMPLIFIED THEMEMANAGER-RE DELEGÁLVA.
        
        Args:
            dark_theme: Sötét téma-e (DEPRECATED, használd a SimplifiedThemeManager-t)
        """
        print("⚠️ DEBUG: update_style() DEPRECATED - use SimplifiedThemeManager.set_theme() instead")

        # Backward compatibility - SimplifiedThemeManager-re delegálás
        theme_name = "dark" if dark_theme else "light"
        self.theme_manager.set_theme(theme_name)
