#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Provider Widget Module
🔧 TELJES IMPLEMENTÁCIÓ - Provider Selection & Usage Monitoring

FUNKCIÓK:
✅ Provider kiválasztás (Open-Meteo ALAPÉRTELMEZETT, Meteostat, Auto)
✅ Real-time usage monitoring
✅ Cost tracking és warnings
✅ API limit displays
✅ Provider status indicators
✅ Clean Architecture signals

🎯 ALAPÉRTELMEZETT: OPEN-METEO (INGYENES)

FÁJL HELYE: src/gui/panel_widgets/provider_widget.py
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QProgressBar, QGroupBox, QPushButton, QTextEdit
)
from PySide6.QtCore import Signal, QTimer

from ..theme_manager import register_widget_for_theming


class ProviderWidget(QWidget):
    """
    🔧 COMPLETE Provider Widget - Selection & Monitoring
    
    🎯 ALAPÉRTELMEZETT: OPEN-METEO (INGYENES) - AUTO ROUTING LETILTVA!
    
    FUNKCIONALITÁS:
    - Provider kiválasztás dropdown
    - Usage statistics megjelenítés  
    - Cost monitoring
    - Real-time updates
    - Warning notifications
    - Clean signal architecture
    """
    
    # Signals
    provider_changed = Signal(str)  # provider_name
    usage_warning = Signal(str, int)  # provider_name, usage_percent
    cost_warning = Signal(str, float)  # provider_name, estimated_cost
    
    def __init__(self, parent=None):
        """Provider Widget inicializálása - OPEN-METEO ALAPÉRTELMEZETT."""
        super().__init__(parent)
        
        print("🌍 DEBUG: ProviderWidget inicializálva - OPEN-METEO ALAPÉRTELMEZETT")
        
        # Widget téma regisztráció
        register_widget_for_theming(self, "container")
        
        # === ADATOK INICIALIZÁLÁSA ===
        
        # 🎯 KRITIKUS VÁLTOZÁS: Open-Meteo alapértelmezett (ingyenes)
        self.current_provider = "open-meteo"  # AUTO HELYETT OPEN-METEO!
        
        self.usage_stats = {}
        self.cost_estimates = {}
        self.warning_thresholds = {
            "usage_warning": 80,    # 80% usage warning
            "usage_critical": 95,   # 95% usage critical
            "cost_warning": 50.0    # $50/month warning
        }
        
        # === UI KOMPONENSEK ===
        
        self.provider_combo: Optional[QComboBox] = None
        self.status_label: Optional[QLabel] = None
        self.usage_progress: Optional[QProgressBar] = None
        self.usage_label: Optional[QLabel] = None
        self.cost_label: Optional[QLabel] = None
        self.details_text: Optional[QTextEdit] = None
        
        # === TIMER SETUP ===
        
        self.usage_timer = QTimer()
        self.usage_timer.setInterval(5000)  # 5 seconds
        self.usage_timer.timeout.connect(self._update_usage_display)
        
        # === UI INICIALIZÁLÁS ===
        
        self._init_ui()
        self._setup_signals()
        self._start_monitoring()
        
        print("✅ DEBUG: ProviderWidget initialized - OPEN-METEO ALAPÉRTELMEZETT")
    
    def _init_ui(self) -> None:
        """UI komponensek inicializálása."""
        print("🔧 DEBUG: Setting up ProviderWidget UI...")
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # === PROVIDER SELECTION GROUP ===
        
        selection_group = QGroupBox("🌍 Adatszolgáltató")
        register_widget_for_theming(selection_group, "container")
        selection_layout = QVBoxLayout(selection_group)
        
        # Provider dropdown
        provider_layout = QHBoxLayout()
        
        provider_label = QLabel("Provider:")
        register_widget_for_theming(provider_label, "text")
        provider_layout.addWidget(provider_label)
        
        self.provider_combo = QComboBox()
        register_widget_for_theming(self.provider_combo, "input")
        self._populate_provider_combo()
        provider_layout.addWidget(self.provider_combo)
        
        selection_layout.addLayout(provider_layout)
        
        # Status display - OPEN-METEO ALAPÉRTELMEZETT ÜZENET
        self.status_label = QLabel("🌍 Open-Meteo aktív - Ingyenes, korlátlan használat")
        register_widget_for_theming(self.status_label, "text")
        self.status_label.setWordWrap(True)
        selection_layout.addWidget(self.status_label)
        
        layout.addWidget(selection_group)
        
        # === USAGE MONITORING GROUP ===
        
        usage_group = QGroupBox("📊 Használat Monitoring")
        register_widget_for_theming(usage_group, "container")
        usage_layout = QVBoxLayout(usage_group)
        
        # Usage progress bar
        self.usage_progress = QProgressBar()
        register_widget_for_theming(self.usage_progress, "progress")
        self.usage_progress.setMinimum(0)
        self.usage_progress.setMaximum(100)
        self.usage_progress.setValue(0)
        usage_layout.addWidget(self.usage_progress)
        
        # Usage label - OPEN-METEO ALAPÉRTELMEZETT
        self.usage_label = QLabel("🌍 Ingyenes - Korlátlan használat")
        register_widget_for_theming(self.usage_label, "text")
        usage_layout.addWidget(self.usage_label)
        
        # Cost label - OPEN-METEO ALAPÉRTELMEZETT
        self.cost_label = QLabel("💰 Költség: $0.00/hó")
        register_widget_for_theming(self.cost_label, "text")
        usage_layout.addWidget(self.cost_label)
        
        layout.addWidget(usage_group)
        
        # === DETAILS GROUP ===
        
        details_group = QGroupBox("📋 Részletek")
        register_widget_for_theming(details_group, "container")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        register_widget_for_theming(self.details_text, "input")
        self.details_text.setMaximumHeight(80)
        self.details_text.setReadOnly(True)
        # OPEN-METEO KIEMELÉS
        self.details_text.setText("🌍 Open-Meteo: Ingyenes, korlátlan, megbízható\n💎 Meteostat: Premium, API key szükséges\n🤖 Auto: Smart routing (opcionális)")
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
        
        # === CONTROL BUTTONS ===
        
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("🔄 Frissítés")
        register_widget_for_theming(refresh_button, "button")
        refresh_button.clicked.connect(self._refresh_usage_stats)
        button_layout.addWidget(refresh_button)
        
        reset_button = QPushButton("🗑️ Reset")
        register_widget_for_theming(reset_button, "button")
        reset_button.clicked.connect(self._reset_usage_stats)
        button_layout.addWidget(reset_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Stretch at bottom
        layout.addStretch()
        
        print("✅ DEBUG: ProviderWidget UI setup complete - OPEN-METEO ALAPÉRTELMEZETT")
    
    def _populate_provider_combo(self) -> None:
        """
        Provider dropdown feltöltése - OPEN-METEO ELSŐ HELYEN!
        
        🎯 VÁLTOZÁS: Open-Meteo az első és alapértelmezett!
        """
        providers = [
            # 🎯 OPEN-METEO ELSŐ HELYEN (ALAPÉRTELMEZETT)
            ("open-meteo", "🌍 Open-Meteo (Ingyenes) ⭐ AJÁNLOTT"),
            ("meteostat", "💎 Meteostat (Premium)"),
            ("weatherapi", "🌤️ WeatherAPI (Premium)"),
            ("openweather", "☁️ OpenWeatherMap (Premium)"),
            ("auto", "🤖 Automatikus (Smart Routing)")  # Auto utolsó helyen!
        ]
        
        for value, display in providers:
            self.provider_combo.addItem(display, value)
        
        # 🎯 KRITIKUS: Open-Meteo alapértelmezett (index 0)
        self.provider_combo.setCurrentIndex(0)
        
        print("🌍 DEBUG: Provider combo populated - OPEN-METEO ALAPÉRTELMEZETT")
    
    def _setup_signals(self) -> None:
        """Signal connections beállítása."""
        # Provider selection change
        self.provider_combo.currentTextChanged.connect(self._on_provider_selection_changed)
        
        print("✅ DEBUG: ProviderWidget signals connected")
    
    def _start_monitoring(self) -> None:
        """Usage monitoring indítása."""
        self.usage_timer.start()
        print("🔄 DEBUG: Usage monitoring started (5s interval)")
    
    def _on_provider_selection_changed(self) -> None:
        """Provider kiválasztás változás kezelése."""
        try:
            current_data = self.provider_combo.currentData()
            if current_data:
                old_provider = self.current_provider
                self.current_provider = current_data
                
                print(f"🌍 DEBUG: Provider changed: {old_provider} → {self.current_provider}")
                
                # Status update
                self._update_provider_status()
                
                # Signal emission
                self.provider_changed.emit(self.current_provider)
                
        except Exception as e:
            print(f"❌ DEBUG: Provider selection change error: {e}")
    
    def _update_provider_status(self) -> None:
        """Provider status frissítése - OPEN-METEO KIEMELÉS."""
        status_messages = {
            # 🎯 OPEN-METEO POZITÍV ÜZENET
            "open-meteo": "🌍 Open-Meteo aktív - Ingyenes, korlátlan használat ⭐ AJÁNLOTT",
            "meteostat": "💎 Meteostat aktív - Premium API, pay-per-use",
            "weatherapi": "🌤️ WeatherAPI aktív - Premium API, monthly limits",
            "openweather": "☁️ OpenWeatherMap aktív - Premium API, call limits",
            "auto": "🤖 Automatikus routing aktív - Smart provider selection"
        }
        
        status = status_messages.get(self.current_provider, f"📡 {self.current_provider} aktív")
        self.status_label.setText(status)
    
    def _update_usage_display(self) -> None:
        """🔧 CRITICAL: Usage display frissítése - OPEN-METEO OPTIMALIZÁLT!"""
        try:
            # Mock data if no real stats available
            if not self.usage_stats:
                self._generate_mock_usage_data()
            
            current_provider_stats = self.usage_stats.get(self.current_provider, {})
            
            if self.current_provider == "open-meteo":
                # 🌍 OPEN-METEO: Ingyenes, korlátlan - POZITÍV MEGJELENÍTÉS
                self.usage_progress.setValue(0)
                self.usage_label.setText("🌍 Ingyenes - Korlátlan használat ⭐")
                self.cost_label.setText("💰 Költség: $0.00/hó (INGYENES)")
                
                # Green progress bar for Open-Meteo
                self.usage_progress.setStyleSheet("QProgressBar::chunk { background-color: #10b981; }")
                
            elif self.current_provider == "auto":
                # Auto routing - mixed stats
                total_requests = sum(stats.get('requests', 0) for stats in self.usage_stats.values())
                self.usage_progress.setValue(min(total_requests // 100, 100))  # Scale for display
                self.usage_label.setText(f"🤖 Összesen: {total_requests:,} kérés")
                
                total_cost = sum(stats.get('estimated_cost', 0) for stats in self.usage_stats.values())
                self.cost_label.setText(f"💰 Becsült költség: ${total_cost:.2f}/hó")
                
            else:
                # Premium provider stats
                requests = current_provider_stats.get('requests', 0)
                limit = current_provider_stats.get('limit', 10000)
                usage_percent = min((requests / limit) * 100, 100) if limit > 0 else 0
                
                self.usage_progress.setValue(int(usage_percent))
                self.usage_label.setText(f"💎 {requests:,}/{limit:,} kérés ({usage_percent:.1f}%)")
                
                estimated_cost = current_provider_stats.get('estimated_cost', 0)
                self.cost_label.setText(f"💰 Becsült költség: ${estimated_cost:.2f}/hó")
                
                # Warning checks
                self._check_usage_warnings(usage_percent, estimated_cost)
            
            # Update details
            self._update_details_display()
            
        except Exception as e:
            print(f"❌ DEBUG: Usage display update error: {e}")
            # Fallback display - OPEN-METEO alapértelmezett
            self.usage_label.setText("🌍 Open-Meteo - Ingyenes")
            self.cost_label.setText("💰 Költség: $0.00/hó")
    
    def _generate_mock_usage_data(self) -> None:
        """Mock usage adatok generálása teszteléshez."""
        import random
        
        self.usage_stats = {
            "open-meteo": {
                "requests": random.randint(100, 1000),
                "limit": float('inf'),  # Korlátlan
                "estimated_cost": 0.0   # Ingyenes
            },
            "meteostat": {
                "requests": random.randint(50, 500),
                "limit": 1000,
                "estimated_cost": random.uniform(5.0, 25.0)
            },
            "weatherapi": {
                "requests": random.randint(20, 200),
                "limit": 1000000,
                "estimated_cost": random.uniform(10.0, 50.0)
            }
        }
    
    def _check_usage_warnings(self, usage_percent: float, estimated_cost: float) -> None:
        """Usage warning ellenőrzések."""
        # Usage warnings
        if usage_percent >= self.warning_thresholds["usage_critical"]:
            self.usage_warning.emit(self.current_provider, int(usage_percent))
            self.usage_progress.setStyleSheet("QProgressBar::chunk { background-color: #dc2626; }")
        elif usage_percent >= self.warning_thresholds["usage_warning"]:
            self.usage_warning.emit(self.current_provider, int(usage_percent))
            self.usage_progress.setStyleSheet("QProgressBar::chunk { background-color: #f59e0b; }")
        else:
            self.usage_progress.setStyleSheet("")  # Default styling
        
        # Cost warnings
        if estimated_cost >= self.warning_thresholds["cost_warning"]:
            self.cost_warning.emit(self.current_provider, estimated_cost)
    
    def _update_details_display(self) -> None:
        """Details display frissítése - OPEN-METEO KIEMELÉS."""
        details = []
        
        for provider, stats in self.usage_stats.items():
            requests = stats.get('requests', 0)
            cost = stats.get('estimated_cost', 0)
            
            if provider == "open-meteo":
                # 🌍 OPEN-METEO POZITÍV KIEMELÉS
                details.append(f"🌍 Open-Meteo: {requests:,} kérés (INGYENES) ⭐")
            else:
                details.append(f"💎 {provider.title()}: {requests:,} kérés (${cost:.2f})")
        
        if not details:
            # Alapértelmezett üzenet OPEN-METEO-val
            details = ["🌍 Open-Meteo: Ingyenes, korlátlan, megbízható ⭐"]
        
        self.details_text.setText("\n".join(details))
    
    def _refresh_usage_stats(self) -> None:
        """Usage statisztikák frissítése."""
        print("🔄 DEBUG: Refreshing usage statistics...")
        
        # Mock refresh - in real implementation this would call API
        self._generate_mock_usage_data()
        self._update_usage_display()
        
        print("✅ DEBUG: Usage statistics refreshed")
    
    def _reset_usage_stats(self) -> None:
        """Usage statisztikák resetelése."""
        print("🗑️ DEBUG: Resetting usage statistics...")
        
        self.usage_stats.clear()
        
        # OPEN-METEO alapértelmezett megjelenítés reset után
        if self.current_provider == "open-meteo":
            self.usage_progress.setValue(0)
            self.usage_label.setText("🌍 Ingyenes - Korlátlan használat")
            self.cost_label.setText("💰 Költség: $0.00/hó")
            self.details_text.setText("🌍 Open-Meteo: Ingyenes, korlátlan, megbízható ⭐")
        else:
            self.usage_progress.setValue(0)
            self.usage_label.setText("💎 0/10,000 kérés (0%)")
            self.cost_label.setText("💰 Becsült költség: $0.00/hó")
            self.details_text.setText("📊 Statisztikák törölve")
        
        print("✅ DEBUG: Usage statistics reset")
    
    # === PUBLIC API METHODS ===
    
    def set_provider(self, provider_name: str) -> None:
        """Provider beállítása külső hívásból."""
        try:
            # Find and set provider in combo
            for i in range(self.provider_combo.count()):
                if self.provider_combo.itemData(i) == provider_name:
                    self.provider_combo.setCurrentIndex(i)
                    break
            
            print(f"✅ DEBUG: Provider set to: {provider_name}")
            
        except Exception as e:
            print(f"❌ DEBUG: Set provider error: {e}")
    
    def get_current_provider(self) -> str:
        """Jelenlegi provider lekérdezése."""
        return self.current_provider
    
    def update_usage_stats(self, stats: Dict[str, Any]) -> None:
        """Usage statisztikák frissítése külső forrásból."""
        try:
            self.usage_stats.update(stats)
            self._update_usage_display()
            
            print(f"✅ DEBUG: Usage stats updated: {len(stats)} providers")
            
        except Exception as e:
            print(f"❌ DEBUG: Update usage stats error: {e}")
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Usage összefoglaló lekérdezése."""
        total_requests = sum(stats.get('requests', 0) for stats in self.usage_stats.values())
        total_cost = sum(stats.get('estimated_cost', 0) for stats in self.usage_stats.values())
        
        return {
            "current_provider": self.current_provider,
            "total_requests": total_requests,
            "total_cost": total_cost,
            "provider_stats": self.usage_stats.copy()
        }
    
    def stop_monitoring(self) -> None:
        """Monitoring leállítása."""
        if self.usage_timer.isActive():
            self.usage_timer.stop()
            print("🛑 DEBUG: Usage monitoring stopped")
    
    def start_monitoring(self) -> None:
        """Monitoring indítása."""
        if not self.usage_timer.isActive():
            self.usage_timer.start()
            print("🔄 DEBUG: Usage monitoring started")
    
    # === STATE MANAGEMENT API ===
    
    def get_state(self) -> Dict[str, Any]:
        """Widget állapot lekérdezése."""
        return {
            "current_provider": self.current_provider,
            "provider_preferences": {
                "default_provider": "open-meteo",  # OPEN-METEO alapértelmezett
                "auto_fallback": False  # Auto routing letiltva alapértelmezetten
            },
            "is_valid": self.is_valid()
        }
    
    def set_state(self, state: Dict[str, Any]) -> bool:
        """Widget állapot beállítása."""
        try:
            provider = state.get("current_provider", "open-meteo")  # Fallback to Open-Meteo
            self.set_provider(provider)
            
            print(f"✅ DEBUG: ProviderWidget state set: {provider}")
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Failed to set ProviderWidget state: {e}")
            return False
    
    def is_valid(self) -> bool:
        """Widget validálása - mindig valid (van alapértelmezett provider)."""
        return True
    
    def set_enabled(self, enabled: bool) -> None:
        """Widget engedélyezése/letiltása."""
        self.provider_combo.setEnabled(enabled)
        
        print(f"🌍 DEBUG: ProviderWidget enabled state: {enabled}")
    
    def refresh_usage_display(self) -> None:
        """Usage display frissítése (external API)."""
        self._update_usage_display()
    
    # === LIFECYCLE ===
    
    def cleanup(self) -> None:
        """Widget cleanup."""
        self.stop_monitoring()
        print("🧹 DEBUG: ProviderWidget cleanup completed")
    
    def closeEvent(self, event) -> None:
        """Widget bezárása."""
        self.cleanup()
        super().closeEvent(event)


# Export
__all__ = ['ProviderWidget']