# MASTER PLAN - React Frontend Migration
**Comprehensive Parity Audit + 5-Week Implementation Schedule**

---

## DOCUMENT METADATA

| Attribute | Value |
|-----------|-------|
| **Version** | 1.4 |
| **Updated** | 2026-02-02 |
| **Timeline** | 5 weeks (25 working days) |
| **Current Coverage** | **~69%** (+11% total) |
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

### 📈 COVERAGE TRACKING

| Category | Start | After W1 | After W2 | Target | Delta |
|----------|-------|----------|----------|--------|-------|
| Location Selectors | 50% | **100%** | **100%** | 100% | **+50%** ✅ |
| Theming System | 0% | **100%** | **100%** | 100% | **+100%** ✅ |
| Main Application | 67% | **100%** | **100%** | 100% | **+33%** ✅ |
| Chart Components | 43% | 43% | **71%** | 100% | **+28%** ✅ |
| **OVERALL** | **58%** | **~63%** | **~69%** | **95%** | **+11%** ✅ |

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

### 🔴 Week 3: Maps + Hierarchical Selector
- Hungary GeoJSON data
- County-level map with layers
- Country→Region→County→City selector

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

### Week 3 - PENDING
- [ ] Hungary map with counties
- [ ] Map layers functional
- [ ] Hierarchical selector

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

### ✅ NEW ENDPOINTS (Week 2)

```python
# Wind Rose data
POST /api/weather/wind-rose
→ {"directions": [{"direction": int, "speed_buckets": [float*8]}], "calms": float}
```

### 🔴 NEEDED ENDPOINTS

```python
# Trend Analytics (Week 4)
POST /api/analytics/trend

# Hungary regions (Week 3)
GET /api/hungary/regions
GET /api/hungary/stations

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
| 3 | Maps | Hungary County Map | 85% (+7%) | 🔴 Pending |
| 4 | Analytics | Trend View, Exports | 92% (+7%) | 🔴 Pending |
| 5 | Polish | Providers, Modals, Status Bar | 95% (+3%) | 🔴 Pending |

---

**Status**: 🔄 **IN PROGRESS** (Week 2 Complete)
**Coverage Gap to Close**: 26 percentage points
**Target**: 95% feature parity

*Updated: 2026-02-02*
