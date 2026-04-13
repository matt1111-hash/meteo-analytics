import React, { useMemo } from 'react';

interface WindData {
  date: string;
  value: number;
  location?: string;
}

interface WindHeatmapProps {
  data: WindData[];
  width?: number;
  height?: number;
}

// 💨 BEAUFORT-ALAPÚ szél színskála - 13 FOKOZAT (Qt get_wind_colormap() szerint)
// Progresszív átmenet: Fehér → Kék → Zöld → Sárga → Narancs → Piros → Bíbor → Ibolya
const getWindColor = (windspeed: number): string => {
  // 🎯 BEAUFORT SZINTŰ HATÁROK (km/h) - 13 FOKOZAT
  if (windspeed === 0) return '#FFFFFF'; // 0: Szélcsend - Tiszta fehér
  if (windspeed <= 1) return '#F0F8FF'; // 1: Gyenge szellő - Alice blue
  if (windspeed <= 6) return '#E6F3FF'; // 2: Enyhe szél - Világos égkék
  if (windspeed <= 11) return '#CCE7FF'; // 3: Gyenge szél - Világosabb kék
  if (windspeed <= 19) return '#90EE90'; // 4: Mérsékelt szél - Világos zöld (természet)
  if (windspeed <= 29) return '#32CD32'; // 5: Élénk szél - Lime zöld (aktív, de biztonságos)

  // === ELSŐFOK ZÓNA (6-7): FIGYELMEZTETŐ SZÍNEK ===
  if (windspeed <= 39) return '#FFD700'; // 6: Erős szél - Arany sárga (FIGYELEM!)
  if (windspeed <= 49) return '#FFA500'; // 7: Viharos szél - Narancs (FOKOZOTT FIGYELEM!)

  // === MÁSODFOK ZÓNA (8-12): VESZÉLY SZÍNEK ===
  if (windspeed <= 60) return '#FF6347'; // 8: Élénk viharos - Paradicsom piros (VESZÉLY!)
  if (windspeed <= 72) return '#FF4500'; // 9: Heves vihar - Narancs-piros (NAGY VESZÉLY!)
  if (windspeed <= 85) return '#DC143C'; // 10: Dühöngő vihar - Crimson piros (SZÉLSŐSÉGES!)
  if (windspeed <= 100) return '#8B008B'; // 11: Heves szélvész - Sötét magenta (KRITIKUS!)
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
const buildCalendarMatrix = (data: WindData[]): number[][] => {
  if (!data || data.length === 0) return Array(7).fill(null).map(() => Array(53).fill(NaN));

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

// 🎯 Szélsebesség formázás
const formatWindSpeed = (speed: number): string => {
  return `${Math.round(speed)} km/h`;
};

// 🌪️ Beaufort fokozat meghatározása
const getBeaufortScale = (windspeed: number): string => {
  if (windspeed === 0) return '0 - Szélcsend';
  if (windspeed <= 1) return '1 - Gyenge szellő';
  if (windspeed <= 6) return '2 - Enyhe szél';
  if (windspeed <= 11) return '3 - Gyenge szél';
  if (windspeed <= 19) return '4 - Mérsékelt szél';
  if (windspeed <= 29) return '5 - Élénk szél';
  if (windspeed <= 39) return '6 - Erős szél';
  if (windspeed <= 49) return '7 - Viharos szél';
  if (windspeed <= 60) return '8 - Élénk viharos szél';
  if (windspeed <= 72) return '9 - Heves vihar';
  if (windspeed <= 85) return '10 - Dühöngő vihar';
  if (windspeed <= 100) return '11 - Heves szélvész';
  return '12 - Orkán';
};

const WindHeatmap: React.FC<WindHeatmapProps> = ({
  data,
  width = 1000,
  height = 400
}) => {
  const heatmapData = useMemo(() => {
    if (!data || data.length === 0) return null;

    // Rendezés dátum szerint
    const sortedData = [...data].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

    // Szélsebesség határok
    const windSpeeds = sortedData.map(d => d.value);
    const minWind = Math.min(...windSpeeds);
    const maxWind = Math.max(...windSpeeds);

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
        const windValue = calendarMatrix[day][week];
        if (!isNaN(windValue)) {
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
            color: getWindColor(windValue),
            windSpeed: windValue,
            date: cellDate.toISOString().split('T')[0],
            formattedDate: formatDate(cellDate.toISOString().split('T')[0]),
            formattedWind: formatWindSpeed(windValue),
            beaufortScale: getBeaufortScale(windValue),
            week: week,
            day: day
          });
        }
      }
    }

    // Hét napjai címkék - ISO szabvány szerint (Hétfőtől Vasárnapig)
    const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

    return {
      cells,
      minWind,
      maxWind,
      cellWidth,
      cellHeight,
      rows,
      cols,
      dayNames,
      calendarMatrix
    };
  }, [data, width, height]);

  if (!heatmapData) {
    return (
      <div className="wind-heatmap empty">
        <div className="empty-message">No wind data available</div>
      </div>
    );
  }

  return (
    <div className="wind-heatmap">
      <div className="heatmap-header">
        <h4>💨 Wind Speed Heatmap (Beaufort Scale)</h4>
        <div className="wind-range">
          Range: {Math.round(heatmapData.minWind)}-{Math.round(heatmapData.maxWind)} km/h
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
          <pattern id="wind-grid" width={heatmapData.cellWidth} height={heatmapData.cellHeight} patternUnits="userSpaceOnUse">
            <path d={`M ${heatmapData.cellWidth} 0 L ${heatmapData.cellWidth} ${heatmapData.cellHeight} L 0 ${heatmapData.cellHeight}`}
                  fill="none" stroke="#e0e0e0" strokeWidth="0.5"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#wind-grid)" />

        {/* Hét napjai címkék - Minden 7. nap címkézése vertikálisan */}
        {heatmapData.dayNames.map((dayName, index) => (
          <text
            key={index}
            x={10}
            y={(index * heatmapData.cellHeight) + 20 + (heatmapData.cellHeight / 2)}
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
            const cell = heatmapData.cells.find(c => c.week === week && c.day === 0); // Hétfői cella
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
                    x={(week * heatmapData.cellWidth) + (heatmapData.cellWidth / 2)}
                    y={25}
                    textAnchor="middle"
                    fontSize="10"
                    fill="#666"
                    fontWeight="500"
                  >
                    {monthName}
                  </text>
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
            <title>{`${cell.formattedDate}: ${cell.formattedWind} (${cell.beaufortScale})`}</title>
          </g>
        ))}
      </svg>

      {/* Szín skála magyarázat - Beaufort 13 fokozat szerint */}
      <div className="color-scale wind-scale">
        <span className="scale-label">🍃 Calm (0 km/h)</span>
        <div className="scale-gradient wind-gradient"></div>
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
        <small>📊 {heatmapData.cells.length} days visualized • 7×53 calendar matrix • Beaufort 13 fokozat • Qt compatible</small>
      </div>
    </div>
  );
};

export default WindHeatmap;
