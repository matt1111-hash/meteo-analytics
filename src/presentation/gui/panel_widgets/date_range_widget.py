#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Date Range Widget
Dátum tartomány választó widget (Multi-Year + Manual mode)

🎯 CLEAN ARCHITECTURE REFAKTOR - 3. LÉPÉS
Felelősség: CSAK a dátum tartomány kezelése
- Single Responsibility: Date range selection (time_range + manual modes)
- Clean Interface: get_state(), set_state(), date_range_changed signal
- Multi-Year Batch Support: 1/5/10/25/55 év opcióval
"""

from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, 
    QRadioButton, QComboBox, QDateEdit, QPushButton, QLabel
)
from PySide6.QtCore import Signal, Qt, QDate
from PySide6.QtGui import QFont

from ..theme_manager import get_theme_manager, register_widget_for_theming


class DateRangeWidget(QWidget):
    """
    📅 DÁTUM TARTOMÁNY WIDGET - CLEAN ARCHITECTURE
    
    Felelősség:
    - Date mode selection (time_range vs manual_dates)
    - Multi-year dropdown (1/5/10/25/55 év)
    - Manual date pickers + quick buttons
    - Computed dates calculation
    - Date validation
    
    Interface:
    - date_range_changed = Signal(str, str) - start_date, end_date
    - date_mode_changed = Signal(str) - "time_range" vagy "manual_dates"
    - get_state() -> dict - aktuális állapot
    - set_state(dict) - állapot beállítása
    - is_valid() -> bool - valid dátum tartomány
    """
    
    # === KIMENŐ SIGNALOK ===
    date_range_changed = Signal(str, str)  # start_date, end_date (ISO format)
    date_mode_changed = Signal(str)  # "time_range" vagy "manual_dates"
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        DateRangeWidget inicializálása.
        
        Args:
            parent: Szülő widget
        """
        super().__init__(parent)
        
        # Theme manager
        self.theme_manager = get_theme_manager()
        
        # State
        self.date_mode = "time_range"  # "time_range" vagy "manual_dates"
        self._updating_state = False
        
        # UI init
        self._init_ui()
        self._connect_signals()
        self._register_for_theming()
        
        # Initial computation
        self._update_computed_dates()
        
        print("📅 DEBUG: DateRangeWidget inicializálva - Multi-Year Batch Support")
    
    def _init_ui(self) -> None:
        """UI elemek létrehozása."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Time range group
        self._create_time_range_group(layout)
        
        # Manual dates group
        self._create_manual_dates_group(layout)
    
    def _create_time_range_group(self, parent_layout) -> None:
        """Time range csoport létrehozása."""
        self.time_range_group = QGroupBox("⏰ Időtartam (Multi-Year)")
        group_layout = QVBoxLayout(self.time_range_group)
        group_layout.setContentsMargins(12, 16, 12, 12)
        group_layout.setSpacing(12)
        
        # Mode selector radio buttons
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(16)
        
        self.time_range_radio = QRadioButton("Időtartam választó")
        self.time_range_radio.setChecked(True)
        self.time_range_radio.setToolTip("Automatikus dátum számítás időtartam alapján")
        self.time_range_radio.setMinimumHeight(24)
        mode_layout.addWidget(self.time_range_radio)
        
        self.manual_dates_radio = QRadioButton("Manuális dátumok")
        self.manual_dates_radio.setToolTip("Pontos dátumok kézi megadása")
        self.manual_dates_radio.setMinimumHeight(24)
        mode_layout.addWidget(self.manual_dates_radio)
        
        group_layout.addLayout(mode_layout)
        
        # Időtartam dropdown
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(8)
        
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems([
            "1 év",      # 🚀 ÚJ OPCIÓ
            "5 év",
            "10 év", 
            "25 év",
            "55 év (teljes)"
        ])
        self.time_range_combo.setCurrentText("1 év")  # Default
        self.time_range_combo.setMinimumHeight(32)
        self.time_range_combo.setToolTip("Automatikus dátum számítás a mai naptól visszafelé")
        
        form_layout.addRow("Időtartam:", self.time_range_combo)
        group_layout.addLayout(form_layout)
        
        # Computed dates info
        self.computed_dates_info = QLabel("Számított időszak: 2024-08-13 → 2025-08-13")
        self.computed_dates_info.setWordWrap(True)
        self.computed_dates_info.setMinimumHeight(40)
        group_layout.addWidget(self.computed_dates_info)
        
        # Size constraints
        self.time_range_group.setMinimumHeight(140)
        self.time_range_group.setMaximumHeight(180)
        
        parent_layout.addWidget(self.time_range_group)
    
    def _create_manual_dates_group(self, parent_layout) -> None:
        """Manual dates csoport létrehozása."""
        self.manual_dates_group = QGroupBox("📅 Manuális Dátumok (Opcionális)")
        group_layout = QFormLayout(self.manual_dates_group)
        group_layout.setContentsMargins(12, 16, 12, 12)
        group_layout.setVerticalSpacing(12)
        group_layout.setHorizontalSpacing(8)
        
        # Start date
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setDate(QDate.currentDate().addYears(-1))
        self.start_date.setMinimumHeight(32)
        group_layout.addRow("Kezdő dátum:", self.start_date)
        
        # End date
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setMinimumHeight(32)
        group_layout.addRow("Befejező dátum:", self.end_date)
        
        # Quick buttons row 1
        quick_layout1 = QHBoxLayout()
        quick_layout1.setSpacing(8)
        
        self.last_month_btn = QPushButton("Előző hónap")
        self.last_month_btn.setMinimumHeight(28)
        quick_layout1.addWidget(self.last_month_btn)
        
        self.last_year_btn = QPushButton("Előző év")
        self.last_year_btn.setMinimumHeight(28)
        quick_layout1.addWidget(self.last_year_btn)
        
        self.last_1year_btn = QPushButton("1 év")
        self.last_1year_btn.setMinimumHeight(28)
        quick_layout1.addWidget(self.last_1year_btn)
        
        self.last_5years_btn = QPushButton("5 év")
        self.last_5years_btn.setMinimumHeight(28)
        quick_layout1.addWidget(self.last_5years_btn)
        
        group_layout.addRow("Gyors:", quick_layout1)
        
        # Quick buttons row 2
        quick_layout2 = QHBoxLayout()
        quick_layout2.setSpacing(8)
        
        self.last_10years_btn = QPushButton("10 év")
        self.last_10years_btn.setMinimumHeight(28)
        quick_layout2.addWidget(self.last_10years_btn)
        
        self.last_25years_btn = QPushButton("25 év")
        self.last_25years_btn.setMinimumHeight(28)
        quick_layout2.addWidget(self.last_25years_btn)
        
        self.last_55years_btn = QPushButton("55 év")
        self.last_55years_btn.setMinimumHeight(28)
        quick_layout2.addWidget(self.last_55years_btn)
        
        group_layout.addRow("Multi-year:", quick_layout2)
        
        # Size constraints
        self.manual_dates_group.setMinimumHeight(160)
        self.manual_dates_group.setMaximumHeight(200)
        
        # Kezdetben disabled
        self._set_manual_dates_enabled(False)
        
        parent_layout.addWidget(self.manual_dates_group)
    
    def _connect_signals(self) -> None:
        """Signal-slot kapcsolatok."""
        # Mode change
        self.time_range_radio.toggled.connect(self._on_date_mode_changed)
        self.manual_dates_radio.toggled.connect(self._on_date_mode_changed)
        
        # Time range combo
        self.time_range_combo.currentTextChanged.connect(self._on_time_range_changed)
        
        # Manual dates
        self.start_date.dateChanged.connect(self._on_manual_date_changed)
        self.end_date.dateChanged.connect(self._on_manual_date_changed)
        
        # Quick buttons
        self.last_month_btn.clicked.connect(self._set_last_month)
        self.last_year_btn.clicked.connect(self._set_last_year)
        self.last_1year_btn.clicked.connect(lambda: self._set_years_back(1))
        self.last_5years_btn.clicked.connect(lambda: self._set_years_back(5))
        self.last_10years_btn.clicked.connect(lambda: self._set_years_back(10))
        self.last_25years_btn.clicked.connect(lambda: self._set_years_back(25))
        self.last_55years_btn.clicked.connect(lambda: self._set_years_back(55))
    
    def _register_for_theming(self) -> None:
        """Theme manager regisztráció."""
        register_widget_for_theming(self, "container")
        register_widget_for_theming(self.time_range_group, "container")
        register_widget_for_theming(self.manual_dates_group, "container")
        
        # Radio buttons
        register_widget_for_theming(self.time_range_radio, "input")
        register_widget_for_theming(self.manual_dates_radio, "input")
        
        # Combo és date edits
        register_widget_for_theming(self.time_range_combo, "input")
        register_widget_for_theming(self.start_date, "input")
        register_widget_for_theming(self.end_date, "input")
        
        # Buttons
        for btn in [self.last_month_btn, self.last_year_btn, self.last_1year_btn, 
                   self.last_5years_btn, self.last_10years_btn, self.last_25years_btn, 
                   self.last_55years_btn]:
            register_widget_for_theming(btn, "button")
        
        # Labels
        self._apply_label_styling(self.computed_dates_info, "secondary")
    
    def _apply_label_styling(self, label: QLabel, style_type: str) -> None:
        """Label styling alkalmazása."""
        color_palette = self.theme_manager.get_color_scheme()
        if not color_palette:
            return
        
        if style_type == "secondary":
            color = color_palette.get_color("info", "light") or "#9ca3af"
            font_size = "11px"
        else:
            color = color_palette.get_color("primary", "base") or "#2563eb"
            font_size = "12px"
        
        css = f"QLabel {{ color: {color}; font-size: {font_size}; }}"
        label.setStyleSheet(css)
        
        register_widget_for_theming(label, "text")
    
    # === SIGNAL HANDLERS ===
    
    def _on_date_mode_changed(self) -> None:
        """Date mode változás kezelése."""
        if self._updating_state:
            return
        
        old_mode = self.date_mode
        
        if self.time_range_radio.isChecked():
            self.date_mode = "time_range"
            self._set_manual_dates_enabled(False)
            self._update_computed_dates()
        else:
            self.date_mode = "manual_dates"
            self._set_manual_dates_enabled(True)
        
        print(f"📅 DEBUG: Date mode changed: {old_mode} → {self.date_mode}")
        
        # Signals
        self.date_mode_changed.emit(self.date_mode)
        start_date, end_date = self._get_effective_date_range()
        self.date_range_changed.emit(start_date, end_date)
    
    def _on_time_range_changed(self, time_range_text: str) -> None:
        """Time range combo változás kezelése."""
        if self._updating_state:
            return
        
        print(f"📅 DEBUG: Time range changed: {time_range_text}")
        
        if self.date_mode == "time_range":
            self._update_computed_dates()
            
            # Date range signal
            start_date, end_date = self._get_effective_date_range()
            self.date_range_changed.emit(start_date, end_date)
    
    def _on_manual_date_changed(self) -> None:
        """Manual date változás kezelése."""
        if self._updating_state:
            return
        
        # Validation
        start = self.start_date.date()
        end = self.end_date.date()
        
        if start > end:
            # Auto-fix
            if self.sender() == self.start_date:
                self.end_date.setDate(start)
            else:
                self.start_date.setDate(end)
        
        # Signal csak manual mode-ban
        if self.date_mode == "manual_dates":
            start_date, end_date = self._get_effective_date_range()
            self.date_range_changed.emit(start_date, end_date)
            print(f"📅 DEBUG: Manual dates changed: {start_date} → {end_date}")
    
    # === HELPER METHODS ===
    
    def _update_computed_dates(self) -> None:
        """Computed dates frissítése."""
        try:
            time_range_text = self.time_range_combo.currentText()
            
            # Évek számának kinyerése
            if "1 év" in time_range_text:
                years = 1
            elif "55 év" in time_range_text:
                years = 55
            elif "25 év" in time_range_text:
                years = 25
            elif "10 év" in time_range_text:
                years = 10
            elif "5 év" in time_range_text:
                years = 5
            else:
                years = 1  # Default
            
            # Dátumok számítása
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=years * 365)
            
            # Info label frissítése
            self.computed_dates_info.setText(
                f"Számított időszak: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')} ({years} év)"
            )
            
            print(f"📅 DEBUG: Computed dates: {start_date} → {end_date} ({years} years)")
            
        except Exception as e:
            print(f"❌ ERROR: Computed dates update error: {e}")
            self.computed_dates_info.setText("Dátum számítási hiba")
    
    def _set_manual_dates_enabled(self, enabled: bool) -> None:
        """Manual date controls engedélyezése/letiltása."""
        self.start_date.setEnabled(enabled)
        self.end_date.setEnabled(enabled)
        
        # Quick buttons
        for btn in [self.last_month_btn, self.last_year_btn, self.last_1year_btn,
                   self.last_5years_btn, self.last_10years_btn, self.last_25years_btn,
                   self.last_55years_btn]:
            btn.setEnabled(enabled)
        
        # Time range combo ellenkező
        self.time_range_combo.setEnabled(not enabled)
    
    def _get_effective_date_range(self) -> Tuple[str, str]:
        """Effektív dátum tartomány lekérdezése."""
        if self.date_mode == "time_range":
            # Automatikus számítás
            time_range_text = self.time_range_combo.currentText()
            
            if "1 év" in time_range_text:
                years = 1
            elif "55 év" in time_range_text:
                years = 55
            elif "25 év" in time_range_text:
                years = 25
            elif "10 év" in time_range_text:
                years = 10
            elif "5 év" in time_range_text:
                years = 5
            else:
                years = 1  # Default
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=years * 365)
            
            return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        
        else:
            # Manual dátumok
            start_date = self.start_date.date().toString(Qt.ISODate)
            end_date = self.end_date.date().toString(Qt.ISODate)
            
            return start_date, end_date
    
    # === QUICK BUTTON HANDLERS ===
    
    def _set_last_month(self) -> None:
        """Előző hónap beállítása."""
        today = QDate.currentDate()
        last_month = today.addMonths(-1)
        self.start_date.setDate(last_month)
        self.end_date.setDate(today)
    
    def _set_last_year(self) -> None:
        """Előző év beállítása."""
        today = QDate.currentDate()
        last_year = today.addYears(-1)
        self.start_date.setDate(last_year)
        self.end_date.setDate(today)
    
    def _set_years_back(self, years: int) -> None:
        """N évet visszamenő dátum beállítása."""
        today = QDate.currentDate()
        start = today.addYears(-years)
        end = today
        
        self.start_date.setDate(start)
        self.end_date.setDate(end)
        
        print(f"📅 DEBUG: Set {years} years back: {start.toString()} → {end.toString()}")
    
    # === PUBLIKUS INTERFACE ===
    
    def get_state(self) -> Dict[str, Any]:
        """Aktuális állapot lekérdezése."""
        start_date, end_date = self._get_effective_date_range()
        
        return {
            "date_mode": self.date_mode,
            "time_range": self.time_range_combo.currentText() if self.date_mode == "time_range" else None,
            "start_date": start_date,
            "end_date": end_date,
            "is_valid": self.is_valid()
        }
    
    def set_state(self, state: Dict[str, Any]) -> bool:
        """Állapot beállítása."""
        try:
            self._updating_state = True
            
            # Date mode
            date_mode = state.get("date_mode", "time_range")
            if date_mode == "time_range":
                self.time_range_radio.setChecked(True)
            else:
                self.manual_dates_radio.setChecked(True)
            
            self.date_mode = date_mode
            self._set_manual_dates_enabled(date_mode == "manual_dates")
            
            # Time range combo
            time_range = state.get("time_range")
            if time_range and date_mode == "time_range":
                index = self.time_range_combo.findText(time_range)
                if index >= 0:
                    self.time_range_combo.setCurrentIndex(index)
            
            # Manual dates
            if date_mode == "manual_dates":
                start_date = state.get("start_date")
                end_date = state.get("end_date")
                
                if start_date:
                    qdate = QDate.fromString(start_date, Qt.ISODate)
                    if qdate.isValid():
                        self.start_date.setDate(qdate)
                
                if end_date:
                    qdate = QDate.fromString(end_date, Qt.ISODate)
                    if qdate.isValid():
                        self.end_date.setDate(qdate)
            
            # Update computed dates
            if date_mode == "time_range":
                self._update_computed_dates()
            
            print(f"✅ DEBUG: DateRangeWidget state set: {date_mode}")
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Failed to set DateRangeWidget state: {e}")
            return False
        finally:
            self._updating_state = False
    
    def is_valid(self) -> bool:
        """Dátum tartomány validálása."""
        try:
            start_date, end_date = self._get_effective_date_range()
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Start <= End
            if start > end:
                return False
            
            # Minimum 1 nap
            if (end - start).days < 1:
                return False
            
            # Maximum 60 év (praktikus limit)
            if (end - start).days > 60 * 365:
                return False
            
            return True
            
        except ValueError:
            return False
    
    def get_date_range(self) -> Tuple[str, str]:
        """Dátum tartomány lekérdezése (compatibility)."""
        return self._get_effective_date_range()
    
    def get_date_mode(self) -> str:
        """Date mode lekérdezése."""
        return self.date_mode
    
    def set_enabled(self, enabled: bool) -> None:
        """Widget engedélyezése/letiltása."""
        self.time_range_group.setEnabled(enabled)
        self.manual_dates_group.setEnabled(enabled)
        
        print(f"📅 DEBUG: DateRangeWidget enabled state: {enabled}")
    
    # === SIZE HINT ===
    
    def sizeHint(self):
        """Preferált méret."""
        return self.time_range_group.sizeHint()
    
    def minimumSizeHint(self):
        """Minimum méret."""
        return self.time_range_group.minimumSizeHint()