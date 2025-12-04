# 🗓️ Heatmap Komponensek Átalakítása - Qt 7×53 Kalendárium Mátrix

## 📋 Változtatások Összefoglalója

Mind a 4 heatmap komponenst átalakítottam a Qt implementációval kompatibilis 7×53-as kalendárium mátrixra:

### ✅ Frissített Komponensek:
1. **TemperatureHeatmap.tsx** - Teljesen átalakítva
2. **PrecipitationHeatmap.tsx** - Teljesen átalakítva  
3. **WindHeatmap.tsx** - Teljesen átalakítva
4. **WindGustHeatmap.tsx** - Teljesen átalakítva

### 🔧 Technikai Változtatások:

#### Új Függvények:
```typescript
// Hét számának meghatározása az évben
const getWeekNumber = (dateStr: string): number => {
  const date = new Date(dateStr);
  const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
  const pastDaysOfYear = (date.getTime() - firstDayOfYear.getTime()) / 86400000;
  return Math.floor((pastDaysOfYear + firstDayOfYear.getDay()) / 7);
};

// Kalendárium mátrix építése (7×53) - Qt kompatibilis
const buildCalendarMatrix = (data: DataType[]): number[][] => {
  const calendarMatrix = Array(7).fill(null).map(() => Array(53).fill(NaN));
  
  data.forEach(item => {
    const date = new Date(item.date);
    const dayOfWeek = date.getDay(); // 0=Vasárnap, 1=Hétfő, ..., 6=Vasárnap
    const weekNumber = getWeekNumber(item.date);
    
    if (weekNumber >= 0 && weekNumber < 53 && dayOfWeek >= 0 && dayOfWeek < 7) {
      calendarMatrix[dayOfWeek][weekNumber] = item.value;
    }
  });
  
  return calendarMatrix;
};
```

#### Mátrix Struktúra Változás:
- **Régi**: 12×31 mátrix (hónapok × napok)
- **Új**: 7×53 mátrix (napok × hetek) - Qt kompatibilis

#### Elrendezés Változás:
- **Régi**: Hónapok oszlopokban, napok sorokban
- **Új**: Hét napjai sorokban (Sun-Sat), hetek oszlopokban (0-52)

#### Koordináta Számítás:
```typescript
// Új Qt kompatibilis koordináták
x = week * cellWidth
y = day * cellHeight + 40  // +40px a hét napjai címkéknek
```

### 🎨 UI Változtatások:

#### SVG Renderelés:
- **Hét napjai címkék**: Bal oldalon, 7 darab (Sun, Mon, Tue, Wed, Thu, Fri, Sat)
- **Hónap címkék**: Minden 4. héten felül, dinamikus dátum alapján
- **Rács**: 7×53 cella Qt kompatibilis elrendezésben

#### CSS Frissítések:
- Minden 4 komponens CSS fájlja frissítve az új elrendezéshez
- Kommentek frissítve: "Qt 7×53 Calendar Matrix"

### 📊 Statisztika Változás:
- Régi: "📊 X days visualized • 12 months"
- Új: "📊 X days visualized • 7×53 calendar matrix • Qt compatible"

### 🔍 Qt Kompatibilitás:
- **Mátrix méret**: 7×53 (mint a Qt `calendar_matrix = np.full((7, 53), np.nan)`)
- **NaN kezelés**: Nem létező napok átlátszóak maradnak
- **Valódi dátumok**: Helyettesítő dátum számítás a hét és nap alapján
- **Hónap címkék**: Valódi hónapnevek a megfelelő pozíciókban

### ⚡ Teljesítmény:
- Build méret: +299 B (minimalis növekedés)
- Nincs aggregációs logika - közvetlen dátum->mátrix mapping
- Optimált cella generálás - csak valós adatokkal rendelkező cellák

### 🧪 Tesztelés:
- Build sikeres: ✅
- TypeScript figyelmeztetések javítva: ✅
- CSS kompatibilitás: ✅
- Responsive design megőrizve: ✅

## 🎯 Eredmény:
Mind a 4 heatmap komponens most már Qt-val kompatibilis 7×53-as kalendárium mátrixot használ, ahelyett hogy a régi 12×31-es hónap-nap elrendezést használná. Az új elrendezés valódi kalendárium nézetet biztosít, ahol a hét napjai vannak függőlegesen és a hetek vannak vízszintesen, pont mint a Qt implementációban.