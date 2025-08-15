#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - API Settings Widget
API beállítások widget (Timeout, Cache, Timezone)

🎯 CLEAN ARCHITECTURE REFAKTOR - 5. LÉPÉS
Felelősség: CSAK az API beállítások kezelése
- Single Responsibility: API configuration settings
- Clean Interface: get_state(), set_state(), api_settings_changed signal
- Multi-Year optimalizált beállítások
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox, 
    QCheckBox, QSpinBox
)
from PySide6.QtCore import Signal

from ..theme_manager import get_theme_manager, register_widget_for_theming


class ApiSettingsWidget(QWidget):
    """
    ⚙️ API BEÁLLÍTÁSOK WIDGET - CLEAN ARCHITECTURE
    
    Felelősség:
    - API timeout beállítás (multi-year batch optimalizált)
    - Automatikus timezone detection
    - Data caching enable/disable
    - Settings validation és persistence
    
    Interface:
    - api_settings_changed = Signal(dict) - settings változás
    - get_state() -> dict - aktuális állapot
    - set_state(dict) - állapot beállítása
    - is_valid() -> bool - valid beállítások
    """
    
    # === KIMENŐ SIGNALOK ===
    api_settings_changed = Signal(dict)  # settings dict
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        ApiSettingsWidget inicializálása.
        
        Args:
            parent: Szülő widget
        """
        super().__init__(parent)
        
        # Theme manager
        self.theme_manager = get_theme_manager()
        
        # State
        self._updating_state = False
        
        # UI init
        self._init_ui()
        self._connect_signals()
        self._register_for_theming()
        
        print("⚙️ DEBUG: ApiSettingsWidget inicializálva - Multi-Year Optimized")
    
    def _init_ui(self) -> None:
        """UI elemek létrehozása."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Group box
        self.group = QGroupBox("⚙️ API Beállítások")
        form_layout = QFormLayout(self.group)
        form_layout.setContentsMargins(12, 16, 12, 12)
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(8)
        
        # Automatikus timezone
        self.auto_timezone = QCheckBox()
        self.auto_timezone.setChecked(True)
        self.auto_timezone.setMinimumHeight(20)
        self.auto_timezone.setToolTip("Automatikus időzóna detektálás lokáció alapján")
        form_layout.addRow("Automatikus időzóna:", self.auto_timezone)
        
        # Data caching
        self.cache_data = QCheckBox()
        self.cache_data.setChecked(True)
        self.cache_data.setMinimumHeight(20)
        self.cache_data.setToolTip("API válaszok gyorsítótárazása a teljesítmény javításához")
        form_layout.addRow("Adatok cache-elése:", self.cache_data)
        
        # API timeout - Multi-year batch optimalizált
        self.api_timeout = QSpinBox()
        self.api_timeout.setRange(30, 300)  # 30 sec - 5 min
        self.api_timeout.setValue(60)  # 60 sec default multi-year batch-hez
        self.api_timeout.setSuffix(" másodperc")
        self.api_timeout.setMinimumHeight(28)
        self.api_timeout.setToolTip("API timeout - multi-year batch lekérdezésekhez nagyobb érték ajánlott")
        form_layout.addRow("API timeout:", self.api_timeout)
        
        # Size constraints
        self.group.setMinimumHeight(120)
        self.group.setMaximumHeight(140)
        
        layout.addWidget(self.group)
    
    def _connect_signals(self) -> None:
        """Signal-slot kapcsolatok."""
        self.auto_timezone.toggled.connect(self._on_settings_changed)
        self.cache_data.toggled.connect(self._on_settings_changed)
        self.api_timeout.valueChanged.connect(self._on_settings_changed)
    
    def _register_for_theming(self) -> None:
        """Theme manager regisztráció."""
        register_widget_for_theming(self, "container")
        register_widget_for_theming(self.group, "container")
        register_widget_for_theming(self.auto_timezone, "input")
        register_widget_for_theming(self.cache_data, "input")
        register_widget_for_theming(self.api_timeout, "input")
    
    # === SIGNAL HANDLERS ===
    
    def _on_settings_changed(self) -> None:
        """API settings változás kezelése."""
        if self._updating_state:
            return
        
        settings = self._get_current_settings()
        
        print(f"⚙️ DEBUG: API settings changed: {settings}")
        
        # Signal kibocsátása
        self.api_settings_changed.emit(settings)
    
    def _get_current_settings(self) -> Dict[str, Any]:
        """Aktuális beállítások lekérdezése."""
        return {
            "timezone": "auto" if self.auto_timezone.isChecked() else "UTC",
            "cache": self.cache_data.isChecked(),
            "timeout": self.api_timeout.value()
        }
    
    # === PUBLIKUS INTERFACE ===
    
    def get_state(self) -> Dict[str, Any]:
        """Aktuális állapot lekérdezése."""
        settings = self._get_current_settings()
        
        return {
            "auto_timezone": self.auto_timezone.isChecked(),
            "cache_data": self.cache_data.isChecked(),
            "api_timeout": self.api_timeout.value(),
            "settings": settings,
            "is_valid": self.is_valid()
        }
    
    def set_state(self, state: Dict[str, Any]) -> bool:
        """Állapot beállítása."""
        try:
            self._updating_state = True
            
            # Checkbox states
            auto_timezone = state.get("auto_timezone", True)
            cache_data = state.get("cache_data", True)
            api_timeout = state.get("api_timeout", 60)
            
            # Validation
            if not isinstance(auto_timezone, bool):
                auto_timezone = True
            if not isinstance(cache_data, bool):
                cache_data = True
            if not isinstance(api_timeout, int) or not (30 <= api_timeout <= 300):
                api_timeout = 60
            
            # Set values
            self.auto_timezone.setChecked(auto_timezone)
            self.cache_data.setChecked(cache_data)
            self.api_timeout.setValue(api_timeout)
            
            print(f"✅ DEBUG: ApiSettingsWidget state set: timeout={api_timeout}s, cache={cache_data}, auto_tz={auto_timezone}")
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Failed to set ApiSettingsWidget state: {e}")
            return False
        finally:
            self._updating_state = False
    
    def is_valid(self) -> bool:
        """Beállítások validálása."""
        # Timeout range check
        timeout = self.api_timeout.value()
        if not (30 <= timeout <= 300):
            return False
        
        return True
    
    def get_api_settings(self) -> Dict[str, Any]:
        """API beállítások lekérdezése (compatibility)."""
        return self._get_current_settings()
    
    def set_api_settings(self, settings: Dict[str, Any]) -> bool:
        """API beállítások beállítása (compatibility)."""
        try:
            state = {
                "auto_timezone": settings.get("timezone") == "auto",
                "cache_data": settings.get("cache", True),
                "api_timeout": settings.get("timeout", 60)
            }
            
            return self.set_state(state)
            
        except Exception as e:
            print(f"❌ ERROR: Failed to set API settings: {e}")
            return False
    
    def set_enabled(self, enabled: bool) -> None:
        """Widget engedélyezése/letiltása."""
        self.group.setEnabled(enabled)
        self.auto_timezone.setEnabled(enabled)
        self.cache_data.setEnabled(enabled)
        self.api_timeout.setEnabled(enabled)
        
        print(f"⚙️ DEBUG: ApiSettingsWidget enabled state: {enabled}")
    
    def get_timeout_value(self) -> int:
        """Timeout érték lekérdezése."""
        return self.api_timeout.value()
    
    def set_timeout_value(self, timeout: int) -> bool:
        """Timeout érték beállítása."""
        if 30 <= timeout <= 300:
            self.api_timeout.setValue(timeout)
            return True
        return False
    
    def is_cache_enabled(self) -> bool:
        """Cache engedélyezve van-e."""
        return self.cache_data.isChecked()
    
    def set_cache_enabled(self, enabled: bool) -> None:
        """Cache engedélyezése/letiltása."""
        self.cache_data.setChecked(enabled)
    
    def is_auto_timezone_enabled(self) -> bool:
        """Auto timezone engedélyezve van-e."""
        return self.auto_timezone.isChecked()
    
    def set_auto_timezone_enabled(self, enabled: bool) -> None:
        """Auto timezone engedélyezése/letiltása."""
        self.auto_timezone.setChecked(enabled)
    
    # === SIZE HINT ===
    
    def sizeHint(self):
        """Preferált méret."""
        return self.group.sizeHint()
    
    def minimumSizeHint(self):
        """Minimum méret."""
        return self.group.minimumSizeHint()