import React, { useMemo } from 'react';

interface WindGustData {
  date: string;
  value: number;
  location?: string;
}

interface WindGustHeatmapProps {
  data: WindGustData[];
  width?: number;
  height?: number;
}

// 🌪️ BEAUFORT-ALAPÚ széllökés színskála - 13 FOKOZAT (Qt get_wind_colormap() szerint)
// Ugyanaz a skála mint a WindHeatmap-nél, mert mindkettő Beaufort alapú
// Progresszív átmenet: Fehér → Kék → Zöld → Sárga → Narancs → Piros → Bíbor → Ibolya
const getWindGustColor = (windgust: number): string => {
  // 🎯 BEAUFORT SZINTŰ HATÁROK (km/h) - 13 FOKOZAT
  if (windgust === 0) return '#FFFFFF'; // 0: Szélcsend - Tiszta fehér
  if (windgust <= 1) return '#F0F8FF'; // 1: Gyenge szellő - Alice blue
  if (windgust <= 6) return '#E6F3FF'; // 2: Enyhe szél - Világos égkék
  if (windgust <= 11) return '#CCE7FF'; // 3: Gyenge szél - Világosabb kék
  if (windgust <= 19) return '#90EE90'; // 4: Mérsékelt szél - Világos zöld (természet)
  if (windgust <= 29) return '#32CD32'; // 5: Élénk szél - Lime zöld (aktív, de biztonságos)

  // === ELSŐFOK ZÓNA (6-7): FIGYELMEZTETŐ SZÍNEK ===
  if (windgust <= 39) return '#FFD700'; // 6: Erős szél - Arany sárga (FIGYELEM!)
  if (windgust <= 49) return '#FFA500'; // 7: Viharos szél - Narancs (FOKOZOTT FIGYELEM!)

  // === MÁSODFOK ZÓNA (8-12): VESZÉLY SZÍNEK ===
  if (windgust <= 60) return '#FF6347'; // 8: Élénk viharos - Paradicsom piros (VESZÉLY!)
  if (windgust <= 72) return '#FF4500'; // 9: Heves vihar - Narancs-piros (NAGY VESZÉLY!)
  if (windgust <= 85) return '#DC143C'; // 10: Dühöngő vihar - Crimson piros (SZÉLSŐSÉGES!)
  if (windgust <= 100) return '#8B008B'; // 11: Heves szélvész - Sötét magenta (KRITIKUS!)
  return '#4B0082'; // 12+: Orkán - Indigo ibolya (KATASZTROFÁLIS!)
};

// 📅 Dátum formázás hónap/nap formátumba
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr);
  return `${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
};

// 📆 Hét számának meghatározása az évben
const getWeekNumber = (dateStr: string): number => {
  const date = new Date(dateStr);
  const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
  const pastDaysOfYear = (date.getTime() - firstDayOfYear.getTime()) / 86400000;
  return Math.floor((pastDaysOfYear + firstDayOfYear.getDay()) / 7);
};

// 🎯 Kalendárium mátrix építése (7×53) - Qt kompatibilis
const buildCalendarMatrix = (data: WindGustData[]): number[][] => {
  if (!data || data.length === 0)
    return Array(7)
      .fill(null)
      .map(() => Array(53).fill(NaN));

  const calendarMatrix = Array(7)
    .fill(null)
    .map(() => Array(53).fill(NaN));

  data.forEach((item) => {
    const date = new Date(item.date);
    const dayOfWeek = date.getDay(); // 0=Vasárnap, 1=Hétfő, ..., 6=Vasárnap
    const weekNumber = getWeekNumber(item.date);

    if (weekNumber >= 0 && weekNumber < 53 && dayOfWeek >= 0 && dayOfWeek < 7) {
      calendarMatrix[dayOfWeek][weekNumber] = item.value;
    }
  });

  return calendarMatrix;
};

// 🎯 Széllökés formázás
const formatWindGust = (gust: number): string => {
  return `${Math.round(gust)} km/h`;
};

// 🌪️ Beaufort fokozat meghatározása széllökésekhez
const getBeaufortScaleGust = (windgust: number): string => {
  if (windgust === 0) return '0 - Szélcsend';
  if (windgust <= 1) return '1 - Gyenge szellő';
  if (windgust <= 6) return '2 - Enyhe szél';
  if (windgust <= 11) return '3 - Gyenge szél';
  if (windgust <= 19) return '4 - Mérsékelt szél';
  if (windgust <= 29) return '5 - Élénk szél';
  if (windgust <= 39) return '6 - Erős szél';
  if (windgust <= 49) return '7 - Viharos szél';
  if (windgust <= 60) return '8 - Élénk viharos szél';
  if (windgust <= 72) return '9 - Heves vihar';
  if (windgust <= 85) return '10 - Dühöngő vihar';
  if (windgust <= 100) return '11 - Heves szélvész';
  return '12 - Orkán';
};

const WindGustHeatmap: React.FC<WindGustHeatmapProps> = ({ data, width = 1000, height = 400 }) => {
  const heatmapData = useMemo(() => {
    if (!data || data.length === 0) return null;

    // Rendezés dátum szerint
    const sortedData = [...data].sort(
      (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
    );

    // Széllökés határok
    const windGusts = sortedData.map((d) => d.value);
    const minGust = Math.min(...windGusts);
    const maxGust = Math.max(...windGusts);

    // 🗓️ Qt kompatibilis 7×53-as kalendárium mátrix
    const rows = 7; // 7 nap (Hétfőtől Vasárnapig)
    const cols = 53; // 53 hét egy évben

    // Cellák méretezése - Qt kompatibilis (15-16px per cella)
    const cellWidth = Math.floor(width / cols);
    const cellHeight = Math.max(15, Math.floor((height - 40) / rows)); // -40px a hét napjai címkéknek

    // 🗓️ Kalendárium mátrix építése
    const calendarMatrix = buildCalendarMatrix(sortedData);

    // 🎯 Cellák létrehozása 7×53-as elrendezésben
    const cells: any[] = [];
    for (let week = 0; week < cols; week++) {
      for (let day = 0; day < rows; day++) {
        const gustValue = calendarMatrix[day][week];
        if (!isNaN(gustValue)) {
          // Valós dátum kiszámítása a hét és nap alapján
          const year = new Date(sortedData[0].date).getFullYear();
          const firstDayOfYear = new Date(year, 0, 1);
          const firstWeekday = firstDayOfYear.getDay();
          const daysFromStart = week * 7 + day - firstWeekday;
          const cellDate = new Date(year, 0, 1 + daysFromStart);

          cells.push({
            x: week * cellWidth,
            y: day * cellHeight + 20, // +20px a hét napjai címkéknek
            width: cellWidth - 1, // -1 a rács vonalakhoz
            height: cellHeight - 1, // -1 a rács vonalakhoz
            color: getWindGustColor(gustValue),
            windGust: gustValue,
            date: cellDate.toISOString().split('T')[0],
            formattedDate: formatDate(cellDate.toISOString().split('T')[0]),
            formattedGust: formatWindGust(gustValue),
            beaufortScale: getBeaufortScaleGust(gustValue),
            week: week,
            day: day,
          });
        }
      }
    }

    // Hét napjai címkék - ISO szabvány szerint (Hétfőtől Vasárnapig)
    const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

    return {
      cells,
      minGust,
      maxGust,
      cellWidth,
      cellHeight,
      rows,
      cols,
      dayNames,
      calendarMatrix,
    };
  }, [data, width, height]);

  if (!heatmapData) {
    return (
      <div className="windgust-heatmap empty">
        <div className="empty-message">No wind gust data available</div>
      </div>
    );
  }

  return (
    <div className="windgust-heatmap">
      <div className="heatmap-header">
        <h4>🌪️ Wind Gust Heatmap (Beaufort Scale)</h4>
        <div className="windgust-range">
          Range: {Math.round(heatmapData.minGust)}-{Math.round(heatmapData.maxGust)} km/h
        </div>
      </div>

      <svg
        width={width}
        height={height}
        className="heatmap-svg"
        viewBox={`0 -20 ${width} ${height + 20}`}
      >
        {/* Rács vonalak - 7×53 Qt kalendárium elrendezés */}
        <defs>
          <pattern
            id="windgust-grid"
            width={heatmapData.cellWidth}
            height={heatmapData.cellHeight}
            patternUnits="userSpaceOnUse"
          >
            <path
              d={`M ${heatmapData.cellWidth} 0 L ${heatmapData.cellWidth} ${heatmapData.cellHeight} L 0 ${heatmapData.cellHeight}`}
              fill="none"
              stroke="#e0e0e0"
              strokeWidth="0.5"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#windgust-grid)" />

        {/* Hét napjai címkék - Minden 7. nap címkézése vertikálisan */}
        {heatmapData.dayNames.map((dayName, index) => (
          <text
            key={index}
            x={10}
            y={index * heatmapData.cellHeight + 20 + heatmapData.cellHeight / 2}
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize="10"
            fill="#666"
            fontWeight="500"
          >
            {dayName}
          </text>
        ))}

        {/* Hónap címkék - Csak új hónap kezdeténél */}
        {(() => {
          const monthLabels = [];
          let prevMonth = -1;

          for (let week = 0; week < heatmapData.cols; week++) {
            const cell = heatmapData.cells.find((c) => c.week === week && c.day === 0); // Hétfői cella
            if (cell) {
              const cellDate = new Date(cell.date);
              const currentMonth = cellDate.getMonth();

              // Csak akkor jelenítjük meg, ha új hónap kezdődik
              if (currentMonth !== prevMonth) {
                prevMonth = currentMonth;
                const monthName = cellDate.toLocaleString('default', { month: 'short' });
                monthLabels.push(
                  <text
                    key={week}
                    x={week * heatmapData.cellWidth + heatmapData.cellWidth / 2}
                    y={25}
                    textAnchor="middle"
                    fontSize="10"
                    fill="#666"
                    fontWeight="500"
                  >
                    {monthName}
                  </text>,
                );
              }
            }
          }
          return monthLabels;
        })()}

        {/* 7×53 kalendárium cellák - Qt kompatibilis */}
        {heatmapData.cells.map((cell, index) => (
          <g key={index}>
            <rect
              x={cell.x}
              y={cell.y}
              width={cell.width}
              height={cell.height}
              fill={cell.color}
              stroke="#ffffff"
              strokeWidth="0.5"
              className="heatmap-cell"
            />

            {/* Tooltip megjelenítés hover esetén - Beaufort skálával */}
            <title>{`${cell.formattedDate}: ${cell.formattedGust} (${cell.beaufortScale})`}</title>
          </g>
        ))}
      </svg>

      {/* Szín skála magyarázat - Beaufort 13 fokozat szerint */}
      <div className="color-scale windgust-scale">
        <span className="scale-label">🍃 Calm (0 km/h)</span>
        <div className="scale-gradient windgust-gradient"></div>
        <span className="scale-label">🌪️ Hurricane (115+ km/h)</span>
      </div>

      {/* Beaufort skála magyarázat */}
      <div className="beaufort-legend">
        <div className="legend-row">
          <span className="legend-item calm">0-1: 🟢 Nyugodt</span>
          <span className="legend-item light">2-5: 🔵 Enyhe</span>
          <span className="legend-item moderate">6-11: 🟢 Mérsékelt</span>
          <span className="legend-item fresh">12-19: 🟡 Élénk</span>
        </div>
        <div className="legend-row">
          <span className="legend-item strong">20-29: 🟢 Erős</span>
          <span className="legend-item gale">30-39: 🟡 Viharos</span>
          <span className="legend-item storm">40-49: 🟠 Heves</span>
          <span className="legend-item violent">50+: 🔴 Szélsőséges</span>
        </div>
      </div>

      <div className="heatmap-stats">
        <small>
          📊 {heatmapData.cells.length} days visualized • 7×53 calendar matrix • Beaufort 13 fokozat
          • Qt compatible
        </small>
      </div>
    </div>
  );
};

export default WindGustHeatmap;
