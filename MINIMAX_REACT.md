# Meteo-Analytics React Frontend Migration Plan

## Overview

This document details the migration from PySide6 desktop GUI to React frontend, ensuring full feature parity between the two implementations.

**Created:** 2026-02-01
**Source:** `src/presentation/gui/` (388 Python files)
**Target:** `frontend/src/` (TypeScript/React)

---

## 1. PARITY AUDIT: PySide vs React

### Summary Table

| Category | PySide Files | React Files | Missing | Coverage |
|----------|-------------|-------------|---------|----------|
| **Main Views/Pages** | ~100 | ~15 | - | 100% |
| **Charts & Visualizations** | ~40 | ~12 | Wind Rose, Trend | 60% |
| **Maps** | ~35 | ~1 | Hungary Map, Layers | 30% |
| **Theme/Styling** | ~26 | ~2 | Full system | 10% |
| **Data Export** | ~5 | ~1 | Excel, JSON | 40% |
| **Background Workers** | ~20 | ~2 | Full system | 20% |
| **Validation** | ~10 | ~2 | Advanced | 30% |
| **Dialogs/Modals** | ~15 | ~1 | Settings, Config | 20% |

### Detailed Feature Comparison

#### Main Pages

| Feature | PySide | React | Status |
|---------|--------|-------|--------|
| Home/Dashboard | main_window.py + menus | HomePage.tsx | ✅ Complete |
| Analytics Dashboard | analytics_view/ (10 files) | AnalyticsView.tsx | ✅ Complete |
| Multi-City View | multi_city_widget/ (15 files) | MultiCityView.tsx | ✅ Complete |
| Single-City View | various controllers | SingleCityView.tsx | ✅ Complete |
| Multi-Year View | trend_analytics/ (12 files) | MultiYearView.tsx | ✅ Complete |
| Anomaly Detection | anomaly_settings_dialog/ | AnomalyView.tsx | ⚠️ Partial |
| Heatmap View | heatmap_chart/ (6 files) | HeatmapView.tsx | ✅ Complete |
| Extreme Events | extreme_events_tab/ (7 files) | ExtremeEventsView.tsx | ⚠️ Partial |
| Windy Days | windy_days_chart/ (3 files) | WindyDaysView.tsx | ✅ Complete |
| Data Table | data_widgets/ (10 files) | DataTableView.tsx | ✅ Complete |
| **Trend Analytics** | trend_analytics/ (12 files) | **MISSING** | ❌ Missing |
| **Hungary Map** | hungarian_map_tab/ (10 files) | **MISSING** | ❌ Missing |

#### Charts

| Chart Type | PySide | React | Status |
|------------|--------|-------|--------|
| Temperature (Line) | temperature_chart/ (5 files) | TemperatureHeatmap | ⚠️ Line chart missing |
| Temperature (Zones) | temperature_chart/core.py | **MISSING** | ❌ Missing |
| Precipitation (Bar) | precipitation_chart/ (3 files) | PrecipitationChart.tsx | ✅ Complete |
| Wind Speed | wind_chart/ (4 files) | WindChart.tsx | ⚠️ Categories missing |
| **Wind Rose** | wind_rose_chart/ (3 files) | **MISSING** | ❌ Missing |
| Calendar Heatmap | heatmap_chart/ (6 files) | HeatmapChart.tsx | ✅ Complete |
| Windy Days Bar | windy_days_chart/ (3 files) | WindyDaysView.tsx | ✅ Complete |
| **Trend Chart (Interactive)** | trend_widgets/trend_chart.py | **MISSING** | ❌ Missing |
| **Multi-City Comparison** | analytics_view/ | MultiCityChart.tsx | ✅ Complete |

#### Maps

| Feature | PySide | React | Status |
|---------|--------|-------|--------|
| Interactive Map (Leaflet) | map_visualizer/ (25 files) | MapView.tsx | ⚠️ Basic only |
| **Hungary County Map** | hungarian_map_tab/ (10 files) | **MISSING** | ❌ Missing |
| Map Overlays | layer_builder.py | **MISSING** | ❌ Missing |
| Map Interactivity | map_interactions.py | Partial | ⚠️ Partial |

#### Theme & Styling

| Feature | PySide | React | Status |
|---------|--------|-------|--------|
| **Theme Manager** | theme_manager/ (20 files) | **MISSING** | ❌ Missing |
| **Dark/Light Mode** | theme_manager/ | **MISSING** | ❌ Missing |
| **Color Palette** | color_palette/ (6 files) | **MISSING** | ❌ Missing |
| **Accessibility Colors** | accessibility.py | **MISSING** | ❌ Missing |

#### Data Export

| Feature | PySide | React | Status |
|---------|--------|-------|--------|
| CSV Export | export_mixin.py | ExportCSVButton.tsx | ✅ Complete |
| **Excel Export** | export_mixin.py | **MISSING** | ❌ Missing |
| **JSON Export** | export_mixin.py | **MISSING** | ❌ Missing |

#### Background Processing

| Feature | PySide | React | Status |
|---------|--------|-------|--------|
| Analysis Worker | analysis_worker/ (5 files) | **MISSING** | ❌ Missing |
| Weather Data Worker | weather_data_worker/ (4 files) | useCityWeather hook | ⚠️ Partial |
| Geocoding Worker | geocoding_worker.py | CityAutocomplete | ⚠️ Partial |
| Worker Manager | worker_manager/ (4 files) | **MISSING** | ❌ Missing |

---

## 2. MISSING FEATURES BY PRIORITY

### 🔴 Critical Priority (Required for Parity)

| # | Feature | PySide Source | Implementation | Effort |
|---|---------|---------------|----------------|--------|
| 1 | **Trend Analytics Tab** | trend_analytics/ (12 files) | New component + API | 3-4 days |
| 2 | **Wind Rose Chart** | wind_rose_chart/ (3 files) | Plotly component | 1-2 days |
| 3 | **Theme System** | theme_manager/ (20 files) | Tailwind + Context | 2-3 days |
| 4 | **Provider Routing** | controller/provider_routing.py | API endpoints | 1 day |

### 🟠 High Priority

| # | Feature | PySide Source | Implementation | Effort |
|---|---------|---------------|----------------|--------|
| 5 | **Hungary County Map** | hungarian_map_tab/ (10 files) | GeoJSON + Leaflet | 2-3 days |
| 6 | **Dark/Light Mode** | theme_manager/ | Tailwind dark mode | 1 day |
| 7 | **Color Palette System** | color_palette/ (6 files) | Tailwind config | 1 day |
| 8 | **Interactive Trend Chart** | trend_widgets/trend_chart.py | Recharts/Plotly | 1 day |
| 9 | **Excel Export** | export_mixin.py | xlsx library | 0.5 day |
| 10 | **JSON Export** | export_mixin.py | Native JS | 0.5 day |

### 🟡 Medium Priority

| # | Feature | PySide Source | Implementation | Effort |
|---|---------|---------------|----------------|--------|
| 11 | Provider Selector Widget | provider_widget/ (2 files) | UI component | 0.5 day |
| 12 | Anomaly Settings Modal | anomaly_settings_dialog/ | Modal + Form | 1 day |
| 13 | Advanced Validation | utils/validation/ (10 files) | Zod + React Hook Form | 1 day |
| 14 | Enhanced Geocoding | geocoding_handler + worker | API endpoint | 1 day |
| 15 | Map Overlays | layer_builder.py | Leaflet layers | 1 day |

### 🟢 Low Priority

| # | Feature | PySide Source | Implementation | Effort |
|---|---------|---------------|----------------|--------|
| 16 | API Usage Tracking | provider_tracker.py | Dashboard stat | 0.5 day |
| 17 | Accessibility Colors | accessibility.py | Tailwind colors | 0.5 day |
| 18 | Enhanced Tooltips | tooltip_mixin/ (4 files) | Recharts tooltips | 1 day |
| 19 | Temperature Zones | temperature_chart/core.py | SVG zones | 0.5 day |
| 20 | Wind Categories | wind_chart/wind_categories.py | Legend component | 0.5 day |

---

## 3. FILE STRUCTURE

### Current React Structure

```
frontend/src/
├── components/
│   ├── TimeSeriesChart.tsx
│   ├── MultiCityChart.tsx
│   ├── MultiYearChart.tsx
│   ├── HeatmapChart.tsx
│   ├── MapView.tsx
│   ├── WindChart.tsx
│   ├── PrecipitationChart.tsx
│   ├── WeatherForm.tsx
│   ├── SingleCityForm.tsx
│   ├── CitySelector.tsx
│   ├── MetricSelector.tsx
│   ├── YearSelector.tsx
│   ├── CityAutocomplete.tsx
│   ├── WeatherResults.tsx
│   ├── SingleCityResults.tsx
│   ├── DetailedResults.tsx
│   ├── ExtremeRecordsTable.tsx
│   ├── ExportCSVButton.tsx
│   ├── panels/
│   │   ├── AnomalyPanel.tsx
│   │   └── DataTablePanel.tsx
│   └── analytics/
│       ├── TemperatureTab.tsx
│       ├── PrecipitationTab.tsx
│       ├── WindTab.tsx
│       ├── WindGustTab.tsx
│       ├── RecordCard.tsx
│       ├── TemperatureHeatmap.tsx
│       ├── PrecipitationHeatmap.tsx
│       ├── WindHeatmap.tsx
│       └── WindGustHeatmap.tsx
├── pages/
│   ├── HomePage.tsx
│   ├── AnalyticsView.tsx
│   ├── MultiCityView.tsx
│   ├── SingleCityView.tsx
│   ├── MultiYearView.tsx
│   ├── AnomalyView.tsx
│   ├── HeatmapView.tsx
│   ├── ExtremeEventsView.tsx
│   ├── WindyDaysView.tsx
│   └── DataTableView.tsx
├── hooks/
│   ├── useCityWeather.ts
│   └── useMultiYearWeather.ts
├── utils/
│   └── extremeCalculator/
│       ├── index.ts
│       ├── dailyRecords.ts
│       ├── monthlyRecords.ts
│       ├── yearlyRecords.ts
│       └── types.ts
├── types/
│   └── weather.ts
├── constants/
│   └── cities.ts
├── App.tsx
└── index.tsx
```

### Target Structure

```
frontend/src/
├── components/
│   ├── charts/
│   │   ├── TimeSeriesChart.tsx
│   │   ├── MultiCityChart.tsx
│   │   ├── MultiYearChart.tsx
│   │   ├── HeatmapChart.tsx
│   │   ├── MapView.tsx
│   │   ├── WindChart.tsx
│   │   ├── PrecipitationChart.tsx
│   │   ├── TemperatureChart.tsx          [NEW]
│   │   ├── WindRoseChart.tsx             [NEW]
│   │   └── TrendChart.tsx                [NEW]
│   ├── analytics/
│   │   ├── TemperatureTab.tsx
│   │   ├── PrecipitationTab.tsx
│   │   ├── WindTab.tsx
│   │   ├── WindGustTab.tsx
│   │   ├── RecordCard.tsx
│   │   ├── TemperatureHeatmap.tsx
│   │   ├── PrecipitationHeatmap.tsx
│   │   ├── WindHeatmap.tsx
│   │   ├── WindGustHeatmap.tsx
│   │   └── TrendAnalyticsTab.tsx         [NEW]
│   ├── maps/
│   │   ├── MapView.tsx
│   │   ├── HungaryMap.tsx                [NEW]
│   │   └── HungaryMapLayers.tsx          [NEW]
│   ├── common/
│   │   ├── WeatherForm.tsx
│   │   ├── SingleCityForm.tsx
│   │   ├── CitySelector.tsx
│   │   ├── MetricSelector.tsx
│   │   ├── YearSelector.tsx
│   │   ├── CityAutocomplete.tsx
│   │   ├── ExportCSVButton.tsx
│   │   ├── ExportMenu.tsx                [NEW]
│   │   ├── ThemeToggle.tsx               [NEW]
│   │   ├── ProviderSelector.tsx          [NEW]
│   │   ├── SettingsModal.tsx             [NEW]
│   │   └── AnomalyConfigForm.tsx         [NEW]
│   ├── results/
│   │   ├── WeatherResults.tsx
│   │   ├── SingleCityResults.tsx
│   │   ├── DetailedResults.tsx
│   │   ├── ExtremeRecordsTable.tsx
│   │   ├── QuickOverview.tsx             [NEW]
│   │   └── DataTable.tsx                 [NEW]
│   └── panels/
│       ├── AnomalyPanel.tsx
│       ├── DataTablePanel.tsx
│       └── WindyDaysPanel.tsx            [NEW]
├── pages/
│   ├── HomePage.tsx
│   ├── AnalyticsView.tsx
│   ├── MultiCityView.tsx
│   ├── SingleCityView.tsx
│   ├── MultiYearView.tsx
│   ├── AnomalyView.tsx
│   ├── HeatmapView.tsx
│   ├── ExtremeEventsView.tsx
│   ├── WindyDaysView.tsx
│   ├── DataTableView.tsx
│   └── TrendAnalyticsView.tsx           [NEW]
├── hooks/
│   ├── useCityWeather.ts
│   ├── useMultiYearWeather.ts
│   ├── useTheme.ts                       [NEW]
│   ├── useTrendData.ts                   [NEW]
│   ├── useExport.ts                      [NEW]
│   └── useAnomalyConfig.ts               [NEW]
├── contexts/
│   ├── ThemeContext.tsx                  [NEW]
│   └── AppContext.tsx                    [NEW]
├── services/
│   ├── api.ts
│   ├── providerService.ts                [NEW]
│   └── exportService.ts                  [NEW]
├── utils/
│   ├── extremeCalculator/
│   │   ├── index.ts
│   │   ├── dailyRecords.ts
│   │   ├── monthlyRecords.ts
│   │   ├── yearlyRecords.ts
│   │   └── types.ts
│   ├── colorPalette.ts                   [NEW]
│   ├── formatters.ts                     [NEW]
│   └── validators.ts                     [NEW]
├── types/
│   ├── weather.ts
│   ├── theme.ts                          [NEW]
│   └── api.ts                            [NEW]
├── constants/
│   ├── cities.ts
│   ├── colors.ts                         [NEW]
│   └── windConstants.ts                  [NEW]
├── styles/
│   └── theme.css                         [NEW]
├── App.tsx
└── index.tsx
```

---

## 4. BACKEND API ENDPOINTS

### Required New Endpoints

#### Trend Analytics
```python
# POST /api/analytics/trend
Request:
{
    "city": str,
    "metric": str,
    "start_year": int,
    "end_year": int,
    "aggregation": "daily" | "monthly" | "yearly"
}

Response:
{
    "data": [{"date": str, "value": float, "trend": float, "slope": float}],
    "statistics": {
        "mean": float,
        "std": float,
        "trend_slope": float,
        "p_value": float
    }
}
```

#### Wind Rose Data
```python
# GET /api/weather/wind-rose
Request:
{
    "city": str,
    "start_date": str,
    "end_date": str
}

Response:
{
    "directions": [
        {"direction": 0, "speed_buckets": [0.5, 1.5, 3.0, 5.5, 8.0, 10.5, 13.5, 16.5]},
        ...
    ],
    "calms": float,
    "total_observations": int
}
```

#### Provider Management
```python
# GET /api/weather/providers
Response:
{
    "providers": [
        {"id": str, "name": str, "available": bool, "quota_remaining": int}
    ],
    "recommended": str
}

# GET /api/providers/status
Response:
{
    "status": "healthy" | "degraded" | "down",
    "latency_ms": int,
    "last_check": str
}
```

#### Data Export
```python
# POST /api/export/csv
# POST /api/export/excel
# POST /api/export/json
Request:
{
    "data": dict,
    "filename": str,
    "options": dict
}
```

#### Hungary Map Data
```python
# GET /api/hungary/regions
Response:
{
    "counties": [
        {"id": str, "name": str, "geometry": GeoJSON}
    ]
}

# GET /api/hungary/stations
Response:
{
    "stations": [
        {"id": str, "name": str, "county": str, "lat": float, "lon": float}
    ]
}
```

---

## 5. NPM DEPENDENCIES

### Required New Packages

```json
{
  "dependencies": {
    "plotly.js": "^2.27.0",
    "react-plotly.js": "^2.6.0",
    "xlsx": "^0.18.5",
    "file-saver": "^2.0.5",
    "react-colorful": "^5.6.1",
    "react-toggle-dark-mode": "^1.1.1",
    "zustand": "^4.5.0"
  },
  "devDependencies": {
    "@types/file-saver": "^2.0.7"
  }
}
```

### Justification

| Package | Purpose | Alternative |
|---------|---------|-------------|
| `plotly.js` | Wind Rose, interactive charts | Recharts (limited polar) |
| `react-plotly.js` | React wrapper for Plotly | - |
| `xlsx` | Excel export | exceljs, export-to-csv |
| `file-saver` | Cross-browser file download | Native Blob |
| `react-colorful` | Color picker component | HTML5 color input |
| `react-toggle-dark-mode` | Dark mode toggle | Custom hook |
| `zustand` | State management | Context API (sufficient) |

---

## 6. PHASE-BY-PHASE SCHEDULE

### Phase 1: Core Infrastructure (Week 1)

**Goal:** Theme system, provider routing, data export

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| 1 | ThemeContext, Tailwind dark mode | Dark/Light toggle works |
| 2 | Color palette system | Tailwind config extended |
| 3 | Export service (CSV/Excel/JSON) | ExportMenu component |
| 4 | Provider service API integration | Provider selector UI |
| 5 | Integration testing | All Phase 1 features working |

**Files to Create/Modify:**
```
New: contexts/ThemeContext.tsx
New: components/common/ThemeToggle.tsx
New: components/common/ExportMenu.tsx
New: services/exportService.ts
New: services/providerService.ts
New: types/theme.ts
Modified: tailwind.config.js
Modified: constants/colors.ts
```

### Phase 2: Advanced Charts (Week 2)

**Goal:** Wind Rose, Trend Chart, Temperature Zones

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| 1 | Wind Rose Chart component | WindRoseChart.tsx (Plotly) |
| 2 | Trend Chart component | TrendChart.tsx (Plotly) |
| 3 | Temperature zones overlay | TemperatureChart.tsx |
| 4 | Wind categories legend | wind_constants.ts + UI |
| 5 | Integration with views | All charts working |

**Files to Create/Modify:**
```
New: components/charts/WindRoseChart.tsx
New: components/charts/TrendChart.tsx
New: components/charts/TemperatureChart.tsx
New: constants/windConstants.ts
Modified: components/analytics/WindTab.tsx
```

### Phase 3: Hungary Map (Week 3)

**Goal:** Interactive county map with weather overlays

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| 1 | Hungary GeoJSON data | constants/hungary.ts |
| 2 | HungaryMap component | Leaflet county map |
| 3 | Map layer management | Overlays, legends |
| 4 | Weather data integration | County-level display |
| 5 | Polish and testing | Interactive map |

**Files to Create/Modify:**
```
New: constants/hungary.ts (GeoJSON)
New: components/maps/HungaryMap.tsx
New: components/maps/HungaryMapLayers.tsx
New: services/hungaryService.ts
Modified: components/maps/MapView.tsx
```

### Phase 4: Trend Analytics View (Week 4)

**Goal:** Full multi-year trend analysis

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| 1 | Backend API endpoint | /api/analytics/trend |
| 2 | useTrendData hook | Data fetching + caching |
| 3 | TrendAnalyticsView page | Full page component |
| 4 | Trend analytics tab | Integration in analytics |
| 5 | Statistics panel | KPI cards, trend indicators |

**Files to Create/Modify:**
```
New: pages/TrendAnalyticsView.tsx
New: components/analytics/TrendAnalyticsTab.tsx
New: components/analytics/StatsPanel.tsx
New: components/analytics/TrendCard.tsx
New: hooks/useTrendData.ts
Modified: App.tsx (new route)
```

### Phase 5: Polish & Testing (Week 5)

**Goal:** Accessibility, mobile responsive, bug fixes

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| 1 | Accessibility audit | WCAG compliance |
| 2 | Mobile responsiveness | All views responsive |
| 3 | Error handling | Graceful failures |
| 4 | Loading states | Skeleton screens |
| 5 | Final testing | All features working |

---

## 7. RISKS AND MITIGATIONS

| Risk | Impact | Mitigation |
|------|--------|------------|
| Plotly bundle size | High (3MB+) | Use react-plotly.js with dynamic import |
| API endpoint availability | Critical | Create mock services for development |
| Complex state management | Medium | Use Zustand instead of Context |
| Mobile performance | Medium | Lazy load heavy components |
| Browser compatibility | Low | Modern browsers only (ES2020+) |

---

## 8. SUCCESS CRITERIA

### Functional Requirements

- [ ] All 10 PySide views have React equivalents
- [ ] Wind Rose chart renders correctly
- [ ] Trend analytics show linear regression + statistics
- [ ] Hungary map displays county boundaries
- [ ] Dark/Light mode toggles without page reload
- [ ] CSV, Excel, JSON exports work correctly
- [ ] All API endpoints respond within 2 seconds
- [ ] Mobile responsive (breakpoints at 768px, 1024px)

### Non-Functional Requirements

- [ ] Lighthouse performance score > 80
- [ ] Lighthouse accessibility score > 90
- [ ] TypeScript strict mode enabled
- [ ] ESLint + Prettier formatting
- [ ] Jest tests for utils (80% coverage)

---

## 9. POST-MIGRATION TASKS

1. **Deprecation of PySide GUI**
   - Archive `src/presentation/gui/` directory
   - Update documentation
   - Create migration guide for contributors

2. **Monitoring & Analytics**
   - Implement Sentry error tracking
   - Add Google Analytics for usage
   - Monitor API latency

3. **Continuous Improvement**
   - Regular dependency updates
   - Performance profiling
   - User feedback collection

---

## 10. SUMMARY

### Effort Estimate

| Phase | Duration | Total Days |
|-------|----------|------------|
| Phase 1: Infrastructure | 1 week | 5 days |
| Phase 2: Advanced Charts | 1 week | 5 days |
| Phase 3: Hungary Map | 1 week | 5 days |
| Phase 4: Trend Analytics | 1 week | 5 days |
| Phase 5: Polish & Testing | 1 week | 5 days |
| **Total** | **5 weeks** | **~25 days** |

### Final Coverage Target

| Category | Target Coverage |
|----------|-----------------|
| Main Views | 100% |
| Charts & Visualizations | 95% |
| Maps | 90% |
| Theme/Styling | 100% |
| Data Export | 100% |
| **Overall** | **~95-100%** |

---

*Document generated: 2026-02-01*
