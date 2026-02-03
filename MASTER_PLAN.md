# MASTER PLAN - React Frontend Migration
**Comprehensive Parity Audit + 5-Week Implementation Schedule**

---

## DOCUMENT METADATA

| Attribute | Value |
|-----------|-------|
| **Version** | 1.6 |
| **Updated** | 2026-02-03 |
| **Timeline** | 5 weeks (25 working days) |
| **Current Coverage** | **~72%** (+14% total) |
| **Target Coverage** | 95% |

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

### 🔄 WEEK 3 - IN PROGRESS (2026-02-03)

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
| HierarchicalSelector | `components/common/HierarchicalSelector.tsx` | 🔴 PENDING |
| API port fixes (8001→8003) | 9 TS/TSX files + package.json | ✅ DONE |
| DataTable validation fix | `pages/DataTableView.tsx` | ✅ DONE |

**Week 3 Progress**: HungaryMap kész, API portok javítva, HierarchicalSelector hátravan

---

## 📈 COVERAGE TRACKING

| Category | Start | After W1 | After W2 | After W3 (partial) | Target | Delta |
|----------|-------|----------|----------|-------------------|--------|-------|
| Location Selectors | 50% | **100%** | **100%** | **100%** | 100% | **+50%** ✅ |
| Theming System | 0% | **100%** | **100%** | **100%** | 100% | **+100%** ✅ |
| Main Application | 67% | **100%** | **100%** | **100%** | 100% | **+33%** ✅ |
| Chart Components | 43% | 43% | **71%** | **73%** | 100% | **+30%** ✅ |
| **OVERALL** | **58%** | **~63%** | **~69%** | **~72%** | **95%** | **+14%** ✅ |

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

### 🔄 Week 3: Maps + Hierarchical Selector - IN PROGRESS
- ✅ Hungary API endpoints (counties, regions, settlements, stations)
- ✅ Frontend HungaryService
- 🔴 Hungary GeoJSON data preparation
- 🔴 HungaryMap component with county boundaries
- 🔴 HierarchicalSelector component (Country→Region→County→City)

### 🔴 Week 4: Trend Analytics + Exports
- TrendAnalyticsView with KPI dashboard
- Time range selector (5/10/25/55 years)
- Excel/JSON export, chart image export

### 🔴 Week 5: Provider Management + Polish
- Provider Management API
- Provider Selector UI
- Status Bar component
- Anomaly Settings Modal

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

### Week 3 - IN PROGRESS
- [x] Hungary API endpoints (4 db)
- [x] Backend port implementation
- [x] Frontend HungaryService
- [x] Backend server running
- [x] Frontend server running
- [x] Hungary GeoJSON data (20 counties + 7 regions)
- [x] HungaryMap component (Leaflet + CSS + GeoJSON)
- [ ] HierarchicalSelector component
- [ ] Coverage +3% (target: ~72%)

### Week 4 - PENDING
- [ ] Trend analytics view
- [ ] Export formats (Excel, JSON, PNG)
- [ ] Backend trend API

### Week 5 - PENDING
- [ ] Provider Management API
- [ ] Provider Selector component
- [ ] Status Bar component
- [ ] All modals implemented

### Final Goals
- [ ] Coverage ≥95%
- [ ] All features working
- [ ] Production ready

---

## 🔌 BACKEND API ENDPOINTS

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

### ✅ WEEK 3 - HUNGARY API (NEW!)

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

### 🔴 NEEDED ENDPOINTS

```python
# Trend Analytics (Week 4)
POST /api/analytics/trend

# Providers (Week 5)
GET /api/weather/providers
GET /api/providers/status

# Export (Week 4)
POST /api/export/excel
POST /api/export/json
```

---

## 📊 WEEKLY SUMMARY

| Week | Focus | Deliverables | Coverage | Status |
|------|-------|--------------|----------|--------|
| 1 | Infrastructure | Theme, City Autocomplete | ~63% (+5%) | ✅ DONE |
| 2 | Charts | Wind Rose, Beaufort Scale | ~69% (+6%) | ✅ DONE |
| 3 | Maps | Hungary API + Map components | ~72% (+3%) | 🔄 IN PROGRESS |
| 4 | Analytics | Trend View, Exports | 92% (+7%) | 🔴 Pending |
| 5 | Polish | Providers, Modals, Status Bar | 95% (+3%) | 🔴 Pending |

---

**Status**: 🔄 **WEEK 3 IN PROGRESS** (HungaryMap done, HierarchicalSelector pending)
**Coverage Gap to Close**: 23 percentage points
**Target**: 95% feature parity
**Servers**: Backend `:8003` ✅ | Frontend `:3000` ✅

*Updated: 2026-02-03 (Week 3 progress - HungaryMap done, port fixes applied)*
