"""
Szeles napok oszlopdiagram chart komponens.

Ez a modul havi szeles napok számát ábrázoló oszlopdiagramot valósít meg,
a meglévő chart rendszer pattern-jeit követve.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from .base_chart import WeatherChart
from ..theme_manager import ProfessionalThemeManager

logger = logging.getLogger(__name__)


class WindyDaysChart(WeatherChart):
    """
    Szeles napok havi oszlopdiagram chart komponens.
    
    Megjeleníti a havi szeles napok számát oszlopdiagramon,
    színkódolással és interaktív elemekkel.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Inicializálás."""
        super().__init__(parent)
        
        self.chart_title = "Havi Szeles Napok (>43 km/h)"
        self.chart_type = "windy_days"
        
        # Chart-specifikus adatok
        self.chart_data: Dict[str, List] = {
            'months': [],
            'counts': [],
            'percentages': [],
            'labels': []
        }
        
        self.threshold_kmh = 43.0
        self.location_name = "Ismeretlen helyszín"
        
        logger.info("WindyDaysChart inicializálva")
    
    def update_data(self, chart_data: Dict[str, Any]) -> None:
        """
        Chart adatok frissítése és újrarajzolás.
        
        Args:
            chart_data: Dictionary a chart adatokkal
        """
        try:
            logger.info("WindyDaysChart adatok frissítése")
            
            # Adatok kinyerése
            self.chart_data = chart_data.get('chart_data', {})
            self.threshold_kmh = chart_data.get('threshold_kmh', 43.0)
            self.location_name = chart_data.get('location_name', 'Ismeretlen helyszín')
            
            # Ellenőrzés
            if not self._has_valid_data():
                logger.warning("Nincs érvényes adat a WindyDaysChart-hoz")
                self._plot_no_data_message()
                return
            
            # Új chart rajzolása
            self._plot_windy_days_chart()
            
            logger.info(f"WindyDaysChart frissítve: {len(self.chart_data.get('months', []))} hónap")
            
        except Exception as e:
            logger.error(f"Hiba a WindyDaysChart adatok frissítésében: {e}")
            self._plot_error_message(str(e))
    
    def _has_valid_data(self) -> bool:
        """Ellenőrzi hogy van-e érvényes adat a chart-hoz."""
        try:
            months = self.chart_data.get('months', [])
            counts = self.chart_data.get('counts', [])
            
            return (
                len(months) > 0 and 
                len(counts) > 0 and 
                len(months) == len(counts) and
                any(count > 0 for count in counts)
            )
        except Exception:
            return False
    
    def _plot_windy_days_chart(self) -> None:
        """Szeles napok oszlopdiagram rajzolása."""
        try:
            # Canvas tisztítása
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            # Adatok kinyerése
            months = self.chart_data.get('months', [])
            counts = self.chart_data.get('counts', [])
            percentages = self.chart_data.get('percentages', [])
            
            if not months or not counts:
                self._plot_no_data_message()
                return
            
            # Színpaletta a szeles napok számának megfelelően
            colors = self._get_bar_colors(counts)
            
            # X tengely pozíciók
            x_positions = np.arange(len(months))
            
            # Oszlopdiagram
            bars = ax.bar(
                x_positions, 
                counts,
                color=colors,
                alpha=0.8,
                edgecolor='white',
                linewidth=1.2
            )
            
            # Értékek megjelenítése az oszlopok tetején
            self._add_value_labels(ax, bars, counts, percentages)
            
            # Tengelyek beállítása
            self._setup_chart_axes(ax, months, counts)
            
            # Chart címe és címkék
            self._setup_chart_labels(ax)
            
            # Grid és stílus
            self._apply_chart_styling(ax)
            
            # Theme alkalmazása
            self._apply_theme_to_chart()
            
            # Interaktivitás
            self._setup_chart_interactivity(bars, months, counts, percentages)
            
            # Canvas frissítése - 🚨 JAVÍTVA: self.draw() használata self.canvas.draw() helyett
            self.draw()
            
            logger.info("Szeles napok oszlopdiagram sikeresen rajzolva")
            
        except Exception as e:
            logger.error(f"Hiba a szeles napok chart rajzolásában: {e}")
            self._plot_error_message(str(e))
    
    def _get_bar_colors(self, counts: List[int]) -> List[str]:
        """
        Oszlopok színeinek meghatározása a szeles napok száma alapján.
        
        Args:
            counts: Szeles napok számai
            
        Returns:
            Lista hex színkódokkal
        """
        try:
            if not counts:
                return []
            
            theme_manager = ProfessionalThemeManager()
            
            # Színkategóriák a szeles napok száma alapján
            max_count = max(counts) if counts else 1
            
            colors = []
            for count in counts:
                if count == 0:
                    # Nincs szeles nap - szürke
                    color = theme_manager.get_color('muted')
                elif count <= max_count * 0.3:
                    # Kevés szeles nap - zöld
                    color = theme_manager.get_color('success')
                elif count <= max_count * 0.6:
                    # Közepes szeles nap - sárga
                    color = theme_manager.get_color('warning')
                else:
                    # Sok szeles nap - piros
                    color = theme_manager.get_color('danger')
                
                colors.append(color)
            
            return colors
            
        except Exception as e:
            logger.error(f"Hiba a színek meghatározásában: {e}")
            # Fallback szín
            return ['#3498db'] * len(counts)
    
    def _add_value_labels(self, ax, bars, counts: List[int], percentages: List[float]) -> None:
        """Értékek hozzáadása az oszlopok tetejére."""
        try:
            for bar, count, percentage in zip(bars, counts, percentages):
                height = bar.get_height()
                
                # Érték szöveg
                if count > 0:
                    label_text = f"{count}\n({percentage:.1f}%)"
                else:
                    label_text = "0"
                
                ax.text(
                    bar.get_x() + bar.get_width()/2., 
                    height + max(counts) * 0.02,
                    label_text,
                    ha='center', 
                    va='bottom',
                    fontsize=9,
                    weight='bold'
                )
                
        except Exception as e:
            logger.error(f"Hiba az értékcímkék hozzáadásában: {e}")
    
    def _setup_chart_axes(self, ax, months: List[str], counts: List[int]) -> None:
        """Chart tengelyek beállítása."""
        try:
            # X tengely
            ax.set_xticks(range(len(months)))
            ax.set_xticklabels(months, rotation=45, ha='right')
            ax.set_xlabel('Hónap', fontweight='bold')
            
            # Y tengely
            max_count = max(counts) if counts else 10
            ax.set_ylim(0, max_count * 1.2)
            ax.set_ylabel('Szeles Napok Száma', fontweight='bold')
            
            # Y tengely egész számok
            ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
            
        except Exception as e:
            logger.error(f"Hiba a tengelyek beállításában: {e}")
    
    def _setup_chart_labels(self, ax) -> None:
        """Chart cím és címkék beállítása."""
        try:
            # Főcím
            title = f"Havi Szeles Napok - {self.location_name}"
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            # Alcím a küszöbértékkel
            subtitle = f"Küszöbérték: {self.threshold_kmh} km/h"
            ax.text(
                0.5, 0.98, subtitle,
                transform=ax.transAxes,
                ha='center', va='top',
                fontsize=10, style='italic'
            )
            
        except Exception as e:
            logger.error(f"Hiba a címkék beállításában: {e}")
    
    def _apply_chart_styling(self, ax) -> None:
        """Chart stílus és grid alkalmazása."""
        try:
            # Grid
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)
            
            # Spines styling
            for spine in ax.spines.values():
                spine.set_color('#cccccc')
                spine.set_linewidth(0.8)
            
            # Tight layout
            self.figure.tight_layout()
            
        except Exception as e:
            logger.error(f"Hiba a chart stílus alkalmazásában: {e}")
    
    def _setup_chart_interactivity(self, bars, months: List[str], 
                                  counts: List[int], percentages: List[float]) -> None:
        """Chart interaktivitás beállítása."""
        try:
            # Tooltip funkció
            def on_hover(event):
                if event.inaxes:
                    for i, bar in enumerate(bars):
                        if bar.contains(event)[0]:
                            # Tooltip info
                            month = months[i]
                            count = counts[i]
                            percentage = percentages[i]
                            
                            tooltip = f"{month}: {count} szeles nap ({percentage:.1f}%)"
                            
                            # Status bar frissítés (ha van parent widget)
                            if hasattr(self.parent(), 'status_bar'):
                                self.parent().status_bar.showMessage(tooltip)
                            
                            return
            
            # Event kapcsolás - 🚨 JAVÍTVA: self használata self.canvas helyett
            self.mpl_connect('motion_notify_event', on_hover)
            
        except Exception as e:
            logger.error(f"Hiba az interaktivitás beállításában: {e}")
    
    def _plot_no_data_message(self) -> None:
        """Üzenet megjelenítése ha nincs adat."""
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            ax.text(
                0.5, 0.5,
                f'Nincs elérhető szélsebességi adat\n\n'
                f'Küszöbérték: {self.threshold_kmh} km/h\n'
                f'Helyszín: {self.location_name}',
                transform=ax.transAxes,
                ha='center', va='center',
                fontsize=12,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.5)
            )
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # 🚨 JAVÍTVA: self.draw() használata self.canvas.draw() helyett
            self.draw()
            
        except Exception as e:
            logger.error(f"Hiba a 'nincs adat' üzenet rajzolásában: {e}")
    
    def _plot_error_message(self, error_msg: str) -> None:
        """Hibaüzenet megjelenítése."""
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            ax.text(
                0.5, 0.5,
                f'Hiba történt a chart rajzolásában:\n\n{error_msg}',
                transform=ax.transAxes,
                ha='center', va='center',
                fontsize=10, color='red',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="mistyrose", alpha=0.7)
            )
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # 🚨 JAVÍTVA: self.draw() használata self.canvas.draw() helyett
            self.draw()
            
        except Exception as e:
            logger.error(f"Hiba a hibaüzenet rajzolásában: {e}")
    
    def clear_chart(self) -> None:
        """Chart törlése."""
        try:
            self.figure.clear()
            # 🚨 JAVÍTVA: self.draw() használata self.canvas.draw() helyett
            self.draw()
            
            # Adatok törlése
            self.chart_data = {
                'months': [],
                'counts': [],
                'percentages': [],
                'labels': []
            }
            
            logger.info("WindyDaysChart törölve")
            
        except Exception as e:
            logger.error(f"Hiba a chart törlésében: {e}")
    
    def export_chart(self, file_path: str, dpi: int = 300) -> bool:
        """
        Chart exportálása fájlba.
        
        Args:
            file_path: Export fájl útvonala
            dpi: Felbontás DPI-ben
            
        Returns:
            True ha sikeres, False egyébként
        """
        try:
            if not self._has_valid_data():
                logger.warning("Nincs exportálható adat")
                return False
            
            self.figure.savefig(
                file_path,
                dpi=dpi,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )
            
            logger.info(f"WindyDaysChart exportálva: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Hiba a chart exportálásában: {e}")
            return False
    
    def get_chart_info(self) -> Dict[str, Any]:
        """Chart információk lekérdezése."""
        return {
            'type': 'windy_days',
            'title': self.chart_title,
            'has_data': self._has_valid_data(),
            'data_points': len(self.chart_data.get('months', [])),
            'threshold_kmh': self.threshold_kmh,
            'location': self.location_name
        }


def create_windy_days_chart(parent: Optional[QWidget] = None) -> WindyDaysChart:
    """
    WindyDaysChart példány létrehozása.
    
    Args:
        parent: Szülő widget
        
    Returns:
        WindyDaysChart példány
    """
    return WindyDaysChart(parent)


# Demo és tesztelési funkciók
def demo_windy_days_chart():
    """Demo a WindyDaysChart tesztelésére."""
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    
    app = QApplication(sys.argv)
    
    # Test adatok
    demo_data = {
        'chart_data': {
            'months': ['Január', 'Február', 'Március', 'Április', 'Május', 'Június'],
            'counts': [12, 8, 15, 6, 3, 9],
            'percentages': [38.7, 28.6, 48.4, 20.0, 9.7, 30.0],
            'labels': [
                'Január: 12 szeles nap (38.7%)',
                'Február: 8 szeles nap (28.6%)',
                'Március: 15 szeles nap (48.4%)',
                'Április: 6 szeles nap (20.0%)',
                'Május: 3 szeles nap (9.7%)',
                'Június: 9 szeles nap (30.0%)'
            ]
        },
        'threshold_kmh': 43.0,
        'location_name': 'Budapest'
    }
    
    # Main window
    window = QMainWindow()
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Chart
    chart = create_windy_days_chart()
    chart.update_data(demo_data)
    
    layout.addWidget(chart)
    window.setCentralWidget(central_widget)
    window.setWindowTitle("WindyDaysChart Demo")
    window.resize(800, 600)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    demo_windy_days_chart()
