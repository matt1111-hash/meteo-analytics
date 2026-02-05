# MASTER PLAN - React Frontend Migration
**Comprehensive Parity Audit + 5-Week Implementation Schedule**

---

## DOCUMENT METADATA

| Attribute | Value |
|-----------|-------|
| **Version** | 2.2 |
| **Updated** | 2026-02-05 |
| **Timeline** | 5 weeks (25 working days) |
| **Frontend Coverage** | **~87%** (+29% total) |
| **Backend Coverage** | **15%** (Python src/) |
| **Target Coverage** | 95% |

---

## 🐍 PYTHON BACKEND TESTING (Config + Data Layer)

### ✅ CONFIG LAYER - COMPLETED (2026-02-04)

### ✅ CONFIG LAYER - COMPLETED (2026-02-04)

| File | Lines | Coverage | Tests | Status |
|------|-------|----------|-------|--------|
| `src/config/api_config.py` | 206 | 100% | 35 | ✅ DONE |
| `src/config/config_settings.py` | 103 | 100% | 28 | ✅ DONE |
| `src/config/config_validation.py` | 192 | 97.18% | 35 | ✅ DONE |
| `src/config/paths_config.py` | 113 | 100% | 35 | ✅ DONE |
| `src/config/provider_config.py` | 254 | 100% | 51 | ✅ DONE |
| `src/config/usage_config.py` | 291 | 97.16% | 34 | ✅ DONE |

**Config Layer Summary**: 183 tests added, ~99% average coverage ✅

---

### ✅ DATA LAYER - IN PROGRESS (2026-02-05)

| File | Lines | Coverage | Tests | Status |
|------|-------|----------|-------|--------|
| `src/data/geo_types.py` | 167 | 98% | 41 | ✅ DONE |
| `src/data/anomaly_types.py` | 103 | 100% | 33 | ✅ DONE |
| `src/data/weather_provider_base.py` | 85 | 100% | 27 | ✅ DONE |
| `src/data/anomaly_storage.py` | 174 | 90% | 36 | ✅ DONE |

**Data Layer Priority Files Summary**: 137 tests added, ~97% average coverage ✅

**Remaining Data Layer files** (30 files, 0% coverage):
- `city_manager_*.py` (5 files: db, demo, hungarian, search, stats)
- `weather_client*.py` (4 files: core, extensions, providers)
- `geo_utils*.py` (4 files: core, region, analytics)
- `anomaly_profile/` (3 files: manager, profile_actions, default_profiles)
- `distance_calculator.py` (215 lines)
- `models.py`, `enums.py`, `weather_types.py`
- ... and more

---

### 🔴 PYTHON BACKEND REMAINING GAPS

| Layer | Coverage | Gap | Priority |
|-------|----------|-----|----------|
| **Presentation/GUI** | 5.75% | ~94% | Low (hard to test) |
| **Data** | 32% | ~63% | **High** |
| **Analytics** | 47.8% | ~52% | **High** |
| API | 96.77% | ~3% | ✅ Complete |
| Application | 100% | 0% | ✅ Complete |
| Domain | 100% | 0% | ✅ Complete |
| Infrastructure | 100% | 0% | ✅ Complete |

**Backend Overall**: ~15% coverage (target: 95%) - ~80% gap remaining

---

## 📅 PROGRESS LOG

### ✅ WEEK 1 - COMPLETED (2026-02-01)

| Task | Files Created/Modified |
|------|------------------------|
| Theme system (ThemeContext + useTheme hook) | `contexts/ThemeContext.tsx`, `types/theme.ts`, `styles/theme.css` |
| ThemeToggle component (sun/moon icon) | `components/common/ThemeToggle.tsx` |
| CityAutocomplete migration (6 files) | All views: CitySelector → CityAutocomplete |
| Backend import fixes (5 API files) | `MultiCityEngine.QUERY_TYPES` import |
| Deleted hardcoded files | `CitySelector.tsx`, `constants/cities.ts` |

**Week 1 Summary**: +5% coverage (Theme: 0%→100%, Location: 50%→100%)

### ✅ WEEK 2 - COMPLETED (2026-02-02)

| Task | Files Created/Modified |
|------|------------------------|
| Wind Rose Chart (Plotly polar) | `components/charts/WindRoseChart.tsx` |
| Wind Rose API endpoint | `POST /api/weather/wind-rose` |
| Beaufort Scale (0-12 levels) | `constants/windConstants.ts`, `BeaufortLegend.tsx` |
| Beaufort integration | `WindChart.tsx`, `WindyDaysView.tsx` |
| Beaufort tests | 125/125 tests passing ✅ |

**Week 2 Summary**: +6% coverage (Charts: 43%→71%)

### ✅ WEEK 3 - COMPLETED (2026-02-04)

| Task | Files Created/Modified | Status |
|------|------------------------|--------|
| Hungary API endpoints (4 db) | `src/api/routes/hungary.py` (215 sor) | ✅ DONE |
| Backend port implementation | `src/data/city_manager_stats.py` | ✅ DONE |
| Router registration | `src/api/main.py` | ✅ DONE |
| Frontend HungaryService | `frontend/src/services/hungaryService.ts` | ✅ DONE |
| Backend server running | `http://127.0.0.1:8003` | ✅ RUNNING |
| Frontend server running | `http://localhost:3000` | ✅ RUNNING |
| Hungary GeoJSON data | `constants/hungary.ts` | ✅ DONE (73 tests) |
| HungaryMap component | `components/maps/HungaryMap.tsx` (+CSS +GeoJSON) | ✅ DONE |
| HierarchicalSelector | `components/common/HierarchicalSelector.tsx` (+CSS +test) | ✅ DONE (21/21 tests passing) |
| API port fixes (8001→8003) | 9 TS/TSX files + package.json | ✅ DONE |
| DataTable validation fix | `pages/DataTableView.tsx` | ✅ DONE |

**Week 3 Summary**: +6% coverage (Maps: 0%→~85%, HierarchicalSelector: 100% stmts, 88% branches)

### ✅ WEEK 4 - COMPLETED (2026-02-04)

| Task | Files Created/Modified | Status |
|------|------------------------|--------|
| Backend: TrendAnalysisRequest DTO | `src/api/dto/trend_request.py` (55 sor) | ✅ DONE |
| Backend: TrendAnalysisResult entity | `src/domain/entities/trend_result.py` (158 sor) | ✅ DONE |
| Backend: TrendCalculator service | `src/domain/analytics/services/trend_calculator.py` (201 sor) | ✅ DONE |
| Backend: TrendDataProcessor | `src/domain/analytics/services/trend_data_processor.py` (74 sor) | ✅ DONE |
| Backend: TrendStatisticsCalculator | `src/domain/analytics/services/trend_statistics.py` (73 sor) | ✅ DONE |
| Backend: CalculateTrendUseCase | `src/application/use_cases/calculate_trend.py` (163 sor) | ✅ DONE |
| Backend: Analytics API route | `src/api/routes/analytics.py` (79 sor) | ✅ DONE |
| Backend: Router registration | `src/api/main.py` | ✅ DONE |
| Frontend: trendService.ts | `frontend/src/services/trendService.ts` | ✅ DONE |
| Frontend: useTrendAnalytics hook | `frontend/src/hooks/useTrendAnalytics.ts` | ✅ DONE |
| Frontend: TrendChart component | `frontend/src/components/charts/TrendChart.tsx` + CSS | ✅ DONE |
| Frontend: TrendAnalyticsView page | `frontend/src/pages/TrendAnalyticsView.tsx` + CSS | ✅ DONE |
| Frontend: Route + Navigation | `frontend/src/App.tsx` | ✅ DONE |

**Week 4 Summary**: +7% coverage (TrendAnalytics: 0%→100%, Analytics API: new)

### ✅ WEEK 5 - COMPLETED (2026-02-04)

| Task | Files Created/Modified | Status |
|------|------------------------|--------|
| Modal Infrastructure | `frontend/src/components/common/Modal.tsx` + CSS + test | ✅ DONE (37/37 tests) |
| useModal Hook | `frontend/src/hooks/useModal.ts` | ✅ DONE |
| Provider DTOs | `src/api/dto/provider_dto.py` (280 sor) | ✅ DONE |
| Provider API Routes | `src/api/routes/providers.py` (290 sor) | ✅ DONE (19/19 tests) |
| ProviderService frontend | `frontend/src/services/providerService.ts` | ✅ DONE |
| useProviderManagement hook | `frontend/src/hooks/useProviderManagement.ts` | ✅ DONE |
| ProviderSelector component | `frontend/src/components/common/ProviderSelector.tsx` + CSS + test | ✅ DONE |
| StatusBar component | `frontend/src/components/common/StatusBar.tsx` + CSS + test | ✅ DONE |
| AnomalySettingsModal component | `frontend/src/components/analytics/AnomalySettingsModal.tsx` + CSS + test | ✅ DONE |
| Router registration | `src/api/main.py` | ✅ DONE |
| Backend server running | `http://127.0.0.1:8003` | ✅ RUNNING |
| Frontend server running | `http://localhost:3000` | ✅ RUNNING |

**Week 5 Summary**: +6% coverage (Modals: 100%, Provider Management: 100%, StatusBar: 100%)

---

## 📈 COVERAGE TRACKING

### Frontend (React/TypeScript)

| Category | Start | After W1 | After W2 | After W3 | After W4 | After W5 | Target | Delta |
|----------|-------|----------|----------|---------|---------|---------|--------|-------|
| Location Selectors | 50% | **100%** | **100%** | **100%** | **100%** | **100%** | 100% | **+50%** ✅ |
| Theming System | 0% | **100%** | **100%** | **100%** | **100%** | **100%** | 100% | **+100%** ✅ |
| Main Application | 67% | **100%** | **100%** | **100%** | **100%** | **100%** | 100% | **+33%** ✅ |
| Chart Components | 43% | 43% | **71%** | **73%** | **~85%** | **~85%** | 100% | **+42%** ✅ |
| Maps & Selectors | 0% | 0% | 0% | **~90%** | **~90%** | **~90%** | 100% | **+90%** ✅ |
| Trend Analytics | 0% | 0% | 0% | 0% | **100%** | **100%** | 100% | **+100%** ✅ |
| Modals & Providers | 0% | 0% | 0% | 0% | 0% | **100%** | 100% | **+100%** ✅ |
| **FRONTEND** | **58%** | **~63%** | **~69%** | **~78%** | **~85%** | **~87%** | **95%** | **+29%** ✅ |

### Backend (Python)

| Layer | Coverage | Target | Gap | Status |
|-------|----------|--------|-----|--------|
| Config | **~99%** | 95% | -4% | ✅ Complete |
| API | 96.77% | 95% | -1.77% | ✅ Excellent |
| Application | 100% | 95% | -5% | ✅ Complete |
| Domain | 100% | 95% | -5% | ✅ Complete |
| Infrastructure | 100% | 95% | -5% | ✅ Complete |
| Analytics | 47.8% | 95% | +47.2% | 🔴 Poor |
| Data | 25.47% | 95% | +69.53% | 🔴 Poor |
| Presentation/GUI | 5.75% | 95% | +89.25% | 🔴 Very Poor |
| **BACKEND** | **~14%** | **95%** | **+81%** | 🔴 Gap |

---

---

## 🎯 WEEKLY PLAN

### ✅ Week 1: Core Infrastructure - DONE
- Theme system (dark/light toggle)
- CityAutocomplete API migration
- Backend import fixes

### ✅ Week 2: Advanced Charts - DONE
- Wind Rose Chart (Plotly polar)
- Beaufort Scale (0-12 levels, Hungarian)
- Enhanced wind charts

### ✅ Week 3: Maps + Hierarchical Selector - DONE
- ✅ Hungary API endpoints (counties, regions, settlements, stations)
- ✅ Frontend HungaryService
- ✅ Hungary GeoJSON data preparation
- ✅ HungaryMap component with county boundaries
- ✅ HierarchicalSelector component (Region→County→Settlement) - 21/21 tests passing

### ✅ Week 4: Trend Analytics + Exports - DONE
- ✅ TrendAnalyticsView with KPI dashboard
- ✅ Time range selector (5/10/25/55 years)
- ✅ Linear regression trend calculation (slope, R², p-value)
- ✅ CSV/JSON export functionality
- ✅ Trend chart with confidence intervals
- ✅ Backend API: POST /api/analytics/trend

### 🔴 Week 5: Provider Management + Polish - IN PROGRESS
- ✅ Modal Infrastructure (base Modal component) - 37/37 tests
- ✅ Provider Management API - 19/19 tests
- [ ] Provider Selector UI
- [ ] Status Bar component
- [ ] Anomaly Settings Modal

---

## ✅ EXECUTION CHECKLIST

### Week 1 - COMPLETED
- [x] Theme system implemented
- [x] Theme toggle component
- [x] CityAutocomplete migration (6 files)
- [x] Backend import fixes (5 files)
- [x] Coverage +5%

### Week 2 - COMPLETED
- [x] Wind Rose chart rendering
- [x] Beaufort scales implemented
- [x] 125/125 tests passing
- [x] Coverage +6%

### Week 3 - COMPLETED
- [x] Hungary API endpoints (4 db)
- [x] Backend port implementation
- [x] Frontend HungaryService
- [x] Backend server running
- [x] Frontend server running
- [x] Hungary GeoJSON data (20 counties + 7 regions)
- [x] HungaryMap component (Leaflet + CSS + GeoJSON)
- [x] HierarchicalSelector component (21/21 tests passing, 100% stmts, 88% branches)
- [x] Coverage +6% (achieved: ~78%)

### Week 4 - COMPLETED
- [x] Trend analytics view
- [x] Backend trend API (POST /api/analytics/trend)
- [x] Export formats (CSV, JSON)
- [x] KPI dashboard (slope, R², p-value, direction, significance)
- [x] Time period selector (5/10/25/55 years)
- [x] Metric selector (temperature, precipitation, wind)
- [x] Linear regression calculation service
- [x] Coverage +7% (achieved: ~85%)

### Week 5 - COMPLETED
- [x] Modal Infrastructure (base Modal + useModal hook)
- [x] Provider Management API (DTO + Routes + Tests)
- [x] Provider Selector component (with tests)
- [x] ProviderService frontend (providerService.ts)
- [x] useProviderManagement hook
- [x] Status Bar component (with tests)
- [x] Anomaly Settings Modal (with tests)
- [x] Backend + Frontend servers running

### Final Goals
- [ ] Coverage ≥95%
- [ ] All features working
- [ ] Production ready

**Week 5 Summary**: +6% coverage (Modals: 100%, Provider Management: 100%, StatusBar: 100%)

---

### 🔴 PYTHON BACKEND TESTING - IN PROGRESS (2026-02-04)

| Task | Files Created/Modified | Status |
|------|------------------------|--------|
| Config Layer Tests (6 files) | `tests/test_api_config.py` (35 tests) | ✅ 100% |
| | `tests/test_config_settings.py` (28 tests) | ✅ 100% |
| | `tests/test_config_validation.py` (35 tests) | ✅ 97.18% |
| | `tests/test_paths_config.py` (35 tests) | ✅ 100% |
| | `tests/test_provider_config.py` (51 tests) | ✅ 100% |
| | `tests/test_usage_config.py` (34 tests) | ✅ 97.16% |
| conftest fixture update | `tests/conftest.py` (added FakePath.unlink) | ✅ DONE |

**Config Layer Summary**: 183 tests added, ~99% coverage, all 6 config files tested

### 🔴 PYTHON BACKEND - NEXT STEPS

**Priority 1: Data Layer** (34 files, 2 tested)
- `weather_provider_base.py` (85 lines) - Base provider interface
- `geo_types.py` (167 lines) - Geographic domain types
- `anomaly_types.py` (103 lines) - Anomaly domain types
- `anomaly_storage.py` (174 lines) - Critical I/O operations
- `city_manager_stats.py` (199 lines) - Main city manager
- ... (28 more files)

**Priority 2: Analytics Layer** (47.8% → 95%)
- `multi_city_engine.py` - Core analytics engine
- `wind_analysis.py` - Wind analysis functionality
- Trend calculator services

---

### ✅ EXISTING ENDPOINTS

```python
# Health check
GET /health

# City search (CityAutocomplete uses this)
GET /api/cities/search?query={name}&limit={number}

# Metrics metadata
GET /api/weather/metrics

# Single city analysis
POST /api/weather/single-city

# Detailed single city
POST /api/weather/single-city-detailed

# Multi-city analysis
POST /api/weather/multi-city?aggregate={bool}

# Anomaly detection
POST /api/weather/detect-anomalies
```

### ✅ WEEK 2 - WIND ROSE

```python
# Wind Rose data
POST /api/weather/wind-rose
→ {"directions": [{"direction": int, "speed_buckets": [float*8]}], "calms": float}
```

### ✅ WEEK 3 - HUNGARY API

```python
# Hungarian counties (20 db: Budapest + 19 megye)
GET /api/hungary/counties
→ {"count": 20, "counties": ["Baranya", "Budapest", "Pest", ...]}

# Hungarian statistical regions (7 db)
GET /api/hungary/regions
→ {"count": 7, "regions": ["Közép-Magyarország", "Észak-Magyarország", ...]}

# Hungarian settlements with filters
GET /api/hungary/settlements?county={name}&limit={number}
→ {"count": N, "settlements": [{"name": "Érd", "county": "Pest", ...}]}

# Hungarian weather stations (settlements)
GET /api/hungary/stations?limit={number}
→ {"count": N, "stations": [{"id": "HU-2151", "name": "Pécs", ...}]}
```

### ✅ WEEK 4 - TREND ANALYTICS (NEW!)

```python
# Trend analysis with linear regression
POST /api/analytics/trend
→ {
    "location_name": "Budapest",
    "metric": "temperature_2m_max",
    "periods": [
      {
        "time_period": 10,
        "slope_per_decade": 0.234,
        "r_squared": 0.678,
        "p_value": 0.001,
        "trend_direction": "increasing",
        "significance": "highly_significant",
        ...
      }
    ]
  }
```

### ✅ WEEK 5 - PROVIDER MANAGEMENT (NEW!)

```python
# Provider Management
GET /api/providers/list
→ {"count": 3, "providers": [...], "default_provider": "auto"}

GET /api/providers/status
→ [{"provider_id": "auto", "name": "Automatikus", "status": "healthy", ...}, ...]

GET /api/providers/{provider_id}/status
→ {"provider_id": "meteostat", "name": "Meteostat (Prémium)", "status": "healthy", ...}

GET /api/providers/{provider_id}/usage
→ {"provider_id": "meteostat", "requests_total": 0, "estimated_cost_usd": 0.0, ...}

POST /api/providers/{provider_id}/select
→ {"success": true, "provider_id": "meteostat", "previous_provider_id": "auto", ...}

GET /api/providers/selected
→ {"provider_id": "auto", "name": "Automatikus (Smart Routing)", ...}
```

---

## 📊 WEEKLY SUMMARY

| Week | Focus | Deliverables | Coverage | Status |
|------|-------|--------------|----------|--------|
| 1 | Infrastructure | Theme, City Autocomplete | ~63% (+5%) | ✅ DONE |
| 2 | Charts | Wind Rose, Beaufort Scale | ~69% (+6%) | ✅ DONE |
| 3 | Maps | Hungary API + Map components | ~78% (+6%) | ✅ DONE |
| 4 | Analytics | Trend View, Exports, KPI Dashboard | ~85% (+7%) | ✅ DONE |
| 5 | Polish | Providers, Modals, Status Bar | ~87% (+2%) | ✅ DONE |
| 6 | Backend Testing | Config (183 tests) + Data Layer (137 tests) | Config: ~99%, Data Priority: ~97% | 🔴 IN PROGRESS |

---

**Status**: ✅ **WEEK 5 COMPLETED** (Modal Infrastructure ✅, Provider API ✅, Selector UI ✅, StatusBar ✅, AnomalySettingsModal ✅)
**Frontend Coverage**: ~87% overall (target: 95%)
**Backend Coverage**: ~15% overall (target: 95%)
**Backend Progress**: Config Layer ~99% ✅ | Data Layer Priority Files ~97% ✅ | Analytics 48%
**Coverage Gap**: Frontend 8pp | Backend ~80pp
**Servers**: Backend `:8003` ✅ | Frontend `:3000` ✅

*Updated: 2026-02-05 (Data Layer testing: 137 tests added - geo_types, anomaly_types, weather_provider_base, anomaly_storage. 30 data files remaining)*
