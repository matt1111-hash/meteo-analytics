# Temperature Heatmap - Kalendárium Nézet Frissítés

## Változtatások

### 1. Elrendezés Módosítása
- **Régi**: Négyzetes elrendezés (`Math.ceil(Math.sqrt(365))` oszlop)
- **Új**: Kalendárium nézet 12 oszloppal (hónapok szerint)

### 2. Mátrix Struktúra
- **Oszlopok**: 12 (hónapok)
- **Sorok**: 31 (max napok/hónap)
- **Cellák**: 365 (konstans, Qt kompatibilis)

### 3. Koordináta Számítás
```typescript
// Hónap és nap kiszámítása
const month = date.getMonth(); // 0-11
const day = date.getDate() - 1; // 0-30

// Pozíciók
x: month * cellWidth
y: day * cellHeight + 30 // +30px hónap címkéknek
```

### 4. UI Változtatások
- Hónap nevek címkéi a tetején (Jan-Dec)
- Bővített szélesség: 800px → 1000px
- Frissített magyarázat: "12 months" a "columns" helyett

### 5. Qt Kompatibilitás
- 12 oszlop a Qt implementációval megegyezően
- 365 cella konstans maradt
- Kalendárium-szerű elrendezés

## Fájlok Módosítva
- `frontend/src/components/analytics/TemperatureHeatmap.tsx`
- `frontend/src/components/analytics/TemperatureHeatmap.css`

## Build Status
✅ Sikeres build, nincs TypeScript vagy React hiba