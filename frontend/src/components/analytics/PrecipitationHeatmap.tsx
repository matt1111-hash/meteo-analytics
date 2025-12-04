import React, { useMemo } from 'react';

interface PrecipitationData {
  date: string;
  value: number;
  location?: string;
}

interface PrecipitationHeatmapProps {
  data: PrecipitationData[];
  width?: number;
  height?: number;
}

// 🌧️ Csapadék színskála - Qt get_precipitation_colormap() alapján
// 0mm = FEHÉR, progresszív kék átmenet
const getPrecipitationColor = (precipitation: number): string => {
  // Qt szintűk: [0, 1, 5, 10, 20, 30, 40, 50, 80, 100] mm
  if (precipitation === 0) return '#FFFFFF'; // 0 mm - FEHÉR (száraz nap!)
  if (precipitation <= 1) return '#E6F3FF'; // 1 mm - nagyon világoskék
  if (precipitation <= 5) return '#CCE7FF'; // 5 mm - világoskék
  if (precipitation <= 10) return '#99D6FF'; // 10 mm - kék
  if (precipitation <= 20) return '#66C2FF'; // 20 mm - sötétkék
  if (precipitation <= 30) return '#3399FF'; // 30 mm - erős kék
  if (precipitation <= 40) return '#0066CC'; // 40 mm - sötét kék
  if (precipitation <= 50) return '#004499'; // 50 mm - nagyon sötét kék
  if (precipitation <= 80) return '#002266'; // 80 mm - sötétbordó
  return '#001133'; // 100+ mm - fekete-kék
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
const buildCalendarMatrix = (data: PrecipitationData[]): number[][] => {
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

// 🎯 Csapadék formázás
const formatPrecipitation = (precip: number): string => {
  return `${precip.toFixed(1)}mm`;
};

const PrecipitationHeatmap: React.FC<PrecipitationHeatmapProps> = ({
  data,
  width = 1000,
  height = 400
}) => {
  const heatmapData = useMemo(() => {
    if (!data || data.length === 0) return null;

    // Rendezés dátum szerint
    const sortedData = [...data].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    
    // Csapadék határok
    const precipitations = sortedData.map(d => d.value);
    const minPrecip = Math.min(...precipitations);
    const maxPrecip = Math.max(...precipitations);
    
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
        const precipValue = calendarMatrix[day][week];
        if (!isNaN(precipValue)) {
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
            color: getPrecipitationColor(precipValue),
            precipitation: precipValue,
            date: cellDate.toISOString().split('T')[0],
            formattedDate: formatDate(cellDate.toISOString().split('T')[0]),
            formattedPrecip: formatPrecipitation(precipValue),
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
      minPrecip,
      maxPrecip,
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
      <div className="precipitation-heatmap empty">
        <div className="empty-message">No precipitation data available</div>
      </div>
    );
  }

  return (
    <div className="precipitation-heatmap">
      <div className="heatmap-header">
        <h4>🌧️ Precipitation Heatmap</h4>
        <div className="precip-range">
          Range: {heatmapData.minPrecip.toFixed(1)}mm - {heatmapData.maxPrecip.toFixed(1)}mm
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
          <pattern id="precip-grid" width={heatmapData.cellWidth} height={heatmapData.cellHeight} patternUnits="userSpaceOnUse">
            <path d={`M ${heatmapData.cellWidth} 0 L ${heatmapData.cellWidth} ${heatmapData.cellHeight} L 0 ${heatmapData.cellHeight}`} 
                  fill="none" stroke="#e0e0e0" strokeWidth="0.5"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#precip-grid)" />
        
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
            
            {/* Tooltip megjelenítés hover esetén */}
            <title>{`${cell.formattedDate}: ${cell.formattedPrecip}`}</title>
          </g>
        ))}
      </svg>
      
      {/* Szín skála magyarázat - Qt színskála szerint */}
      <div className="color-scale precip-scale">
        <span className="scale-label">🏜️ Dry (0mm)</span>
        <div className="scale-gradient precip-gradient"></div>
        <span className="scale-label">🌧️ Wet (100mm+)</span>
      </div>
      
      <div className="heatmap-stats">
        <small>📊 {heatmapData.cells.length} days visualized • 7×53 calendar matrix • Qt compatible</small>
      </div>
    </div>
  );
};

export default PrecipitationHeatmap;