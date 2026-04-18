import React, { useMemo } from 'react';

// 🌡️ Temperature Heatmap Component - Bővített színskála -20°C és +40°C között
// Frissítve: 2025-12-04 - Részletesebb színárnyalatokkal

interface TemperatureData {
  date: string;
  value: number;
  location?: string;
}

interface TemperatureHeatmapProps {
  data: TemperatureData[];
  width?: number;
  height?: number;
}

// 🎨 Hőmérséklet színskála - RdYlBu_r inspirált, -20°C és +40°C között
const getTemperatureColor = (temp: number, minTemp: number, maxTemp: number): string => {
  if (minTemp === maxTemp) return '#808080'; // Szürke ha nincs különbség

  // Tartomány számítása -20°C és +40°C között
  const absoluteMin = Math.max(-20, Math.min(...[minTemp, -20]));
  const absoluteMax = Math.min(40, Math.max(...[maxTemp, 40]));
  const normalized = (temp - absoluteMin) / (absoluteMax - absoluteMin);

  // RdYlBu_r színskála: 14+ szín a részletesebb megjelenítésért
  if (normalized < 0.08) return '#08519c'; // -20°C: Nagyon hideg, sötét kék
  if (normalized < 0.15) return '#2171b5'; // -15°C: Hideg kék
  if (normalized < 0.23) return '#4292c6'; // -10°C: Mérsékelt hideg kék
  if (normalized < 0.31) return '#6baed6'; // -5°C: Enyhe hideg kék
  if (normalized < 0.38) return '#9ecae1'; // 0°C: Fagyhatár világoskék
  if (normalized < 0.46) return '#c6dbef'; // 5°C: Hideg világoskék
  if (normalized < 0.54) return '#fee0d2'; // 10°C: Semleges világosrózsaszín
  if (normalized < 0.62) return '#fcbba1'; // 15°C: Enyhe meleg rózsaszín
  if (normalized < 0.69) return '#fc9272'; // 20°C: Mérsékelt meleg narancs
  if (normalized < 0.77) return '#fb6a4a'; // 25°C: Meleg narancs
  if (normalized < 0.85) return '#ef3b2c'; // 30°C: Forró vörös
  if (normalized < 0.92) return '#cb181d'; // 35°C: Nagyon forró sötétvörös
  return '#99000d'; // 40°C: Extrém forró bordó
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
const buildCalendarMatrix = (data: TemperatureData[]): number[][] => {
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

// 🎯 Hőmérséklet formázás
const formatTemperature = (temp: number): string => {
  return `${Math.round(temp)}°C`;
};

const TemperatureHeatmap: React.FC<TemperatureHeatmapProps> = ({
  data,
  width = 1000,
  height = 400,
}) => {
  const heatmapData = useMemo(() => {
    if (!data || data.length === 0) return null;

    // Rendezés dátum szerint
    const sortedData = [...data].sort(
      (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
    );

    // Hőmérséklet határok - kibővített tartomány -20°C és +40°C között
    const temperatures = sortedData.map((d) => d.value);
    const minTemp = Math.max(-20, Math.min(...temperatures)); // Minimum -20°C
    const maxTemp = Math.min(40, Math.max(...temperatures)); // Maximum +40°C

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
        const tempValue = calendarMatrix[day][week];
        if (!isNaN(tempValue)) {
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
            color: getTemperatureColor(tempValue, minTemp, maxTemp),
            temperature: tempValue,
            date: cellDate.toISOString().split('T')[0],
            formattedDate: formatDate(cellDate.toISOString().split('T')[0]),
            formattedTemp: formatTemperature(tempValue),
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
      minTemp,
      maxTemp,
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
      <div className="temperature-heatmap empty">
        <div className="empty-message">No temperature data available</div>
      </div>
    );
  }

  return (
    <div className="temperature-heatmap">
      <div className="heatmap-header">
        <h4>🌡️ Temperature Heatmap</h4>
        <div className="temp-range">
          Range: {Math.round(heatmapData.minTemp)}°C - {Math.round(heatmapData.maxTemp)}°C
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
            id="grid"
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
        <rect width="100%" height="100%" fill="url(#grid)" />

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

            {/* Tooltip megjelenítés hover esetén */}
            <title>{`${cell.formattedDate}: ${cell.formattedTemp}`}</title>
          </g>
        ))}
      </svg>

      {/* Szín skála magyarázat */}
      <div className="color-scale">
        <span className="scale-label">🥶 -20°C</span>
        <div className="scale-gradient"></div>
        <span className="scale-label">🥵 +40°C</span>
      </div>

      {/* Részletes hőmérsékleti tartományok */}
      <div className="temperature-ranges">
        <div className="range-item">
          <span className="color-box temp-very-cold"></span>
          <span>Extrém hideg (-20°C - -15°C)</span>
        </div>
        <div className="range-item">
          <span className="color-box temp-cold"></span>
          <span>Nagyon hideg (-15°C - -10°C)</span>
        </div>
        <div className="range-item">
          <span className="color-box temp-cool"></span>
          <span>Hideg (-10°C - -5°C)</span>
        </div>
        <div className="range-item">
          <span className="color-box temp-mild-cold"></span>
          <span>Mérsékelten hideg (-5°C - 0°C)</span>
        </div>
        <div className="range-item">
          <span className="color-box temp-freezing"></span>
          <span>Fagyhatár (0°C - 5°C)</span>
        </div>
        <div className="range-item">
          <span className="color-box temp-cool-light"></span>
          <span>Hűvös (5°C - 10°C)</span>
        </div>
        <div className="range-item">
          <span className="color-box temp-neutral"></span>
          <span>Semleges (10°C - 15°C)</span>
        </div>
        <div className="range-item">
          <span className="color-box temp-mild-warm"></span>
          <span>Mérsékelten meleg (15°C - 20°C)</span>
        </div>
        <div className="range-item">
          <span className="color-box temp-warm"></span>
          <span>Meleg (20°C - 25°C)</span>
        </div>
        <div className="range-item">
          <span className="color-box temp-hot"></span>
          <span>Forró (25°C - 30°C)</span>
        </div>
        <div className="range-item">
          <span className="color-box temp-very-hot"></span>
          <span>Nagyon forró (30°C - 35°C)</span>
        </div>
        <div className="range-item">
          <span className="color-box temp-extreme-hot"></span>
          <span>Extrém forró (35°C - 40°C)</span>
        </div>
      </div>

      <div className="heatmap-stats">
        <small>
          📊 {heatmapData.cells.length} days visualized • 7×53 calendar matrix • Qt compatible
        </small>
      </div>
    </div>
  );
};

export default TemperatureHeatmap;
