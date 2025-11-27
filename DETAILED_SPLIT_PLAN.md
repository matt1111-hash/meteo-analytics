# 🔧 DETAILED SPLIT PLAN - HungarianMapTab Refactoring

## 🎯 GOAL: 1968 lines → 4 Clean Architecture modules

## 📋 METÓDUSOK PONTOS HOVÁ RENDELÉSE

---

## 1️⃣ **MapTab.py** *(~200 LOC - Thin Container)*
**Primary Role:** Layout management + Dependency injection coordination

### **Core Constructor & Layout** ∎
```python
# KEEPS IN MAINTAB:
__init__(self, parent=None)                    # Constructor - dependency setup
_setup_ui()                                    # Widget layout orchestration
_setup_theme()                                 # Theme application
_initialize_weather_components()               # ComponentFactory pattern
_connect_signals()                             # External signal coordination
```

### **Event Coordination Interfaces** ∎
```python
# KEEPS - Coordination only:
_on_location_selected(location)               # Forward to MapEvents
_on_county_selected(county_name, geometry)    # Forward to MapEvents
_on_map_update_requested(bounds)             # Forward to MapEvents
_on_selection_changed()                      # Forward to MapEvents
```

### **External Signal Forwarding** ∎
```python
# KEEPS - Public interface maintenance:
set_region_and_county()                       # Trigger MapWidget action
focus_on_county()                            # Trigger MapWidget action
get_available_counties()                     # Forward to MapWidget
get_counties_geodataframe()                  # Forward to MapWidget
get_current_location()                       # Aggregate from submodules
get_current_analytics_parameter()           # Forward to AnalyticsBridge
get_current_analytics_result()              # Forward to AnalyticsBridge
get_current_weather_overlay()               # Forward to MapWidget
has_weather_data()                          # Forward to MapWidget
```

### **Factory Pattern Methods** ∎
```python
# KEEPS - Factory coordination:
get_location_selector()                      # Factory getter
get_map_visualizer()                         # Factory getter
get_weather_bridge()                         # Factory getter
get_multi_city_engine()                      # Factory getter
```

---

## 2️⃣ **MapWidget.py** *(~300 LOC - Rendering Engine)*
**Primary Role:** Folium rendering + Weather overlay generation

### **Folium Rendering Core** 📍
```python
# MOVE - Pure rendering logic:
_initialize_step_1()                          # Folium initialization
_initialize_step_2()                          # Visualization setup
_initialize_step_3()                          # Layer configuration
_initialize_step_4()                          # Final rendering
_initialization_complete()                   # Render verification
_hide_loading_indicators()                   # UI state management
_show_folium_installation_message()         # Error handling
_on_folium_map_ready()                       # Render completion callback
```

### **Map Interaction Handling** 📍
```python
# MOVE - Folium specific interactions:
_on_folium_county_clicked(county_name)       # JS → Python bridge
_on_folium_coordinates_clicked(lat, lon)     # Coordinate handling
_on_folium_map_moved(lat, lon, zoom)         # Map state handling
_on_folium_county_hovered(county_name)      # Hover interaction
_reset_map_view()                           # Map state reset
_clear_selection()                          # Selection management
```

### **Weather Overlay Generation** 📍
```python
# MOVE - Weather visualization logic:
_generate_weather_overlay_from_analytics()   # Data → Visual overlay
_refresh_weather_overlay_with_new_dates()  # Temporal overlay update
_on_auto_weather_refresh_toggled()          # Auto refresh logic
set_weather_data(weather_data)              # External weather data injection
```

### **Export & Persistence** 📍
```python
# MOVE - Map export functionality:
_export_map()                               # Map export to HTML
_get_map_status()                           # Status reporting
is_ready()                                  # Readiness check
is_folium_ready_status()                    # Component readiness
toggle_auto_weather_refresh()               # Mode switching
```

---

## 3️⃣ **MapEvents.py** *(~250 LOC - Event Bridge)*
**Primary Role:** Signal/Slot + JS interaction bridge

### **Signal Management** ⚡
```python
# MOVE - Event coordination:
_on_export_completed()                        # Export event handling
_on_error_occurred()                          # Error event propagation
```

### **Auto-synchronization Control** ⚡
```python
# MOVE - Sync toggles:
_on_auto_sync_toggled()                       # Sync mode switching
get_analytics_sync_status()                   # Sync status reporting
get_integration_status()                      # Integration health check
```

### **Refresh Management** ⚡
```python
# MOVE - Refresh orchestration:
_refresh_folium_map()                         # Map refresh
_refresh_weather_overlay()                    # Weather refresh
_refresh_all_components()                     # Complete refresh
```

### **Forward Signal Bridges** ⚡
```python
# MOVE - External signal forwarding patterns:
_emit_location_selected()                     # External signal wrapper
_emit_county_selected()                       # External signal wrapper
_emit_map_interaction()                       # External signal wrapper
_emit_weather_updated()                       # External signal wrapper
_emit_analytics_sync_completed()              # External signal wrapper
```

---

## 4️⃣ **MapAnalyticsBridge.py** *(~300 LOC - Analytics Sync)*
**Primary Role:** Analytics parameter coordination + Weather data sync

### **Parameter Memory Management** 🔗
```python
# MOVE - Parameter state management:
set_analytics_parameter()
set_analytics_result()
_current_analytics_parameter
_current_analytics_result
last_analysis_parameters
last_weather_parameters
last_date_parameters
```

### **Analytics Sync Engine** 🔗 ⭐ (PRIORITY EXTRACTION)
```python
# MOVE - Main sync orchestration:
update_analysis_parameters(params)           # ⭐ Analysis type sync
update_weather_parameters(params)            # ⭐ Weather provider sync
update_date_range(start_date, end_date)      # ⭐ Date range sync
refresh_with_new_parameters(bundle)          # ⭐ Complex bundle sync
```

### **Location & Region Updates** 🔗
```python
# MOVE - Map content sync:
_update_map_for_single_location()            # Single city handling
_update_map_for_region()                     # Regional handling
_update_map_for_county()                     # County specific handling
```

### **Weather Data Synchronization** 🔗
```python
# MOVE - Weather data management:
_refresh_weather_overlays()                  # Overlay refresh orchestration
_refresh_temporal_data()                     # Time-based refresh
_on_county_selected()                        # County-specific weather
load_weather_data_from_analytics()           # Data loading pipeline
_on_map_update_requested()                   # Reactive weather update
```

### **Utility Helper Methods** 🔗
```python
# MOVE - Sync helpers and validation:
_full_map_refresh()                          # Complete refresh coordination
theme_switcher(map_instances)               # Visual coordination
set_theme(theme)                             # Styling coordination
_clear_selection()                           # Cleanup helper
```

---

## 🎛️ DEPENDENCY INJECTION ARCHITECTURE

### **Interface Definition Pattern:**
```python
# src/gui/map_tab/interfaces.py
class IMapWidget(ABC):
    @abstractmethod
    def render_map(self, configuration: MapConfig) -> None: ...
    @abstractmethod
    def add_weather_overlay(self, data: WeatherData) -> None: ...

class IMapEvents(ABC):
    @abstractmethod
    def setup_signal_bridges(self, target_widget: QWidget) -> None: ...
    @abstractmethod
    def handle_map_interaction(self, event: MapEvent) -> None: ...

class IMapAnalyticsBridge(ABC):
    @abstractmethod
    def sync_analysis_parameters(self, params: AnalysisParams) -> None: ...
    @abstractmethod
    def sync_weather_parameters(self, params: WeatherParams) -> None: ...
```

### **Factory Registration Pattern:**
```python
# MapTab.py - Dependency coordination
class HungarianMapTab(QWidget):
    def __init__(self):
        self.map_widget = MapWidgetFactory.create()
        self.event_bridge = MapEventsFactory.create()
        self.analytics_bridge = AnalyticsBridgeFactory.create()

        # Dependency injection setup
        self.event_bridge.setup_signal_bridges(self)
        self.analytics_bridge.set_map_widget(self.map_widget)
```

---

## ⚙️ IMPLEMENTATION SEQUENCE

### **Phase 1:** Interface Creation
- `interfaces.py` - Abstract contracts creation
- Define clear dependency boundaries

### **Phase 2:** MapAnalyticsBridge Extraction
- **FIRST PRIORITY** (largest functional cluster)
- Move 12+ sync methods out of main class
- Maintain backward compatibility via delegates

### **Phase 3:** MapWidget Extraction
- Folium rendering centralization
- Weather overlay generation centralization

### **Phase 4:** MapEvents Extraction
- Signal/Slot bridge pattern
- Event forwarding coordination

### **Phase 5:** MapTab Simplification
- Remove all complex logic → coordination only
- Ensure proper dependency injection setup

---

## ✅ VALIDATION CRITERIA

- **[ ]** All methods categorized with clear responsibility
- **[ ]** 0 methods > 250 lines (God Class rule)
- **[ ]** Clean interfaces between modules
- **[ ]** Dependency injection pattern applied
- **[ ]** Backward compatibility maintained
- **[ ]** < 250 lines per new module
- **[ ]** Complete file reconstruction (not snippets)

---

## 📋 Ready for Implementation Review

This detailed split plan provides:
1. **Exact method assignments** to each new module
2. **Clear interfaces** with dependency injection
3. **Clean Architecture** principles application
4. **Backward compatibility** maintenance strategy
5. **Implementation sequence** with validation checkpoints

**Confirm this split strategy before proceeding to implementation!**