# 🗺️ HungarianMapTab God Class Analysis - Pre Split

## 📊 FÁJL STATISZTIKA
- **Sorok száma:** ~1968 sor
- **Metódusok száma:** 69 metódus
- **Hely/relation:** `src/gui/hungarian_map_tab/_map_tab.py`
- **JAVASLAT:** Clean Architecture szerinti 4 modulos szétbontás

## 🏛️ OSZTÁLY STRUKTÚRA

```python
class HungarianMapTab(QWidget):
    # Osztályadatok (16 adattag)
    # Signal-ok (6 signal)
    # 69 metódus
```

---

## 🗂️ FELELŐSSÉGI KÖRÖK KATEGORIZÁLÁSA

### 1️⃣ **UI ÉS LAYOUT** *(~Metódusok: elő inicializálás)*
```python
# Layout és UI komponensek
_setup_ui()
_setup_theme()
_initialize_weather_components()
_show_folium_installation_message()

# UI getter metódusok
get_weather_bridge()
get_location_selector()
get_map_visualizer()
get_multi_city_engine()
```

### 2️⃣ **INIT ÉS STEP-INITIALIZATION** (~10 metódus)
```python
_init_()  # __init__ (115 sor)
_initialize_components()
_initialize_step_1()  # Folium init
_initialize_step_2()  # Visualizations
_initialize_step_3()  # Weather overlays
_initialize_step_4()  # Final setup
_initialization_complete()
_hide_loading_indicators()
```

### 3️⃣ **SIGNAL/SLOT EVENT HANDLING** (~8 metódus)
```python
_connect_signals()  # Main signal connections

# Event handler metódusok
_on_county_selected()
_on_map_update_requested()
_on_location_selected()
_on_selection_changed()
_on_folium_map_ready()
_on_export_completed()
_on_error_occurred()
```

### 4️⃣ **MAP INTERACTION EVENTS** (~6 metódus)
```python
# Folium specifikus interakciók
_on_folium_county_clicked()
_on_folium_coordinates_clicked()
_on_folium_map_moved()
_on_folium_county_hovered()

# Rendszeres refresh
_refresh_folium_map()
```

### 5️⃣ **ANALYTICS SYNC ENGINE** (~12 metódus) **⭐ CRITICAL**
```python
# Analytics paramétertovábbítás
set_analytics_parameter()        # Új parameter memória
set_analytics_result()          # Analytics result tárolás

# Fő sync metódusok → NEVEZETES KIEMELÉS
update_analysis_parameters()    # ⭐ Analysis típus sync
update_weather_parameters()     # ⭐ Weather provider sync
update_date_range()            # ⭐ Date range sync
refresh_with_new_parameters()   # ⭐ Complex bundle sync

# Helper sync metódusok
_update_map_for_single_location()
_update_map_for_region()
_update_map_for_county()
_refresh_weather_overlays()
_refresh_temporal_data()
_refresh_weather_overlay_with_new_dates()
```

### 6️⃣ **WEATHER OVERLAY ENGINE** (~6 metódus)
```python
# Weather data management
_on_auto_weather_refresh_toggled()
_refresh_weather_overlay()
_refresh_weather_overlay_from_analytics()
_generate_weather_overlay_from_analytics()  # Data → Overlay

# Weather data loading
load_weather_data_from_analytics()
```

### 7️⃣ **DATUMKEZELÉS & PARAMETER BUNDLE** (~4 metódus)
```python
# State management
_current_analytics_parameter
_current_analytics_result
last_analysis_parameters
last_weather_parameters
last_date_parameters

# Utility sync helper
_full_map_refresh(),
```

### 8️⃣ **UI INTERACTION & TOGGLE** (~4 metódus)
```python
_reset_map_view()
_export_map()
_on_auto_sync_toggled()
```

### 9️⃣ **SIGNAL FORWARDING** (~8 metódus)
```python
# Internal → external signal forwarding
_forward_location_selected()
_forward_county_selected()
_forward_map_interaction()
_forward_weather_updated()
_forward_analytics_sync_completed()
```

---

## 🎯 FELELŐSSÉGI KÖR MATRIX

| **Kategória** | **Metódusok** | **Kapcsolat** | **ÚJ MODUL** |
|---------------|---------------|---------------|--------------|
| **Map Rendering** | 🗺️ Folium, HTTP Server, Visualizer | External Dependencies | `MapWidget.py` |
| **Events/Signals** | Signal/Slot bridge, JS Bridge | QWidget Signal System | `MapEvents.py` |
| **Analytics Sync** | 12+ sync metódus + parameter handling | Analytics engine | `MapAnalyticsBridge.py` |
| **Layout/Container** | UI Layout + Widget Container | QWidget Layout + Styling | `MapTab.py` |

---

## 🏗️ PROPOSED SPLIT ARCHITECTURE

```
src/gui/map_tab/
├── \_\_init\_\_.py                    # Ecportok controll
├── MapTab.py                        # Slim container (200 LOC)
│   ├── HungarianMapTab(QWidget)
│   ├── Factory methods (widget_create)
│   └── Layout management (50%)
│
├── MapWidget.py                     # Rendering engine (300 LOC)
│   ├── WeatherOverlayPlanager
│   ├── FoliumManager
│   └── Visualization helpers
│
├── MapEvents.py                     # Event bridge (250 LOC)
│   ├── SignalSlotBridge
│   ├── JSBridge
│   └── Event handlers
│
└── MapAnalyticsBridge.py            # Analytics sync (300 LOC)
    ├── AnalyticsParameterSync
    ├── WeatherDataSync
    └── Sync orchestration
```

---

## 🔧 TECHNICAL MIGRATION STRATEGY

### **STEP 1: Interface Definition**
- Create 4 abstract interfaces for module communication
- Define dependency contract

### **STEP 2: Extract MapWidget**
- Move Folium rendering to dedicated class
- Extract weather overlay generation

### **STEP 3: Extract MapEvents**
- Create bridge pattern for signal handling
- Extract JS interaction handling

### **STEP 4: Extract MapAnalyticsBridge**
- Extract all sync logic + parameter management
- Dependency injection pattern (like previous circular fix)

### **STEP 5: Simplify MapTab**
- Leave only coordination + dependency passthrough
- Widget factory methods + layout logic

---

## 🎪 NEXT: DETAILED METHOD MAPPING

Let me check the exact method names and cosenintelocations to create the precise migration plan.