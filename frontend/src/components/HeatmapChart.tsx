/**
 * CalendarHeatmap - Python stílusú calendar heatmap
 * Rectangle cells, month labels below, Sunday at top, vertical color scale
 */
import React, { useState, useMemo } from 'react';
import { CityWeatherResult } from '../types/weather';
import './HeatmapChart.css';

interface HeatmapChartProps {
  data: CityWeatherResult[];
  metric: string;
  unit: string;
}

interface DayCell {
  date: string;
  value: number | null;
  dayOfWeek: number; // 0=Mon, 6=Sun
  weekIndex: number;
}

interface TooltipData {
  x: number;
  y: number;
  date: string;
  value: number | null;
  visible: boolean;
}

// Hungarian day labels - Sunday at TOP (index 0), Monday at BOTTOM (index 6)
const DAYS_HU = ['V', 'Szo', 'P', 'Cs', 'Sze', 'K', 'H'];

// Hungarian month names (index 0 unused, 1-12 = Jan-Dec)
const MONTHS_HU = ['', 'Jan', 'Feb', 'Már', 'Ápr', 'Máj', 'Jún', 'Júl', 'Aug', 'Sze', 'Okt', 'Nov', 'Dec'];

// Color stops: blue → cyan → green → yellow → orange → red
const COLOR_STOPS = [
  { pos: 0.0, r: 59, g: 130, b: 246 },
  { pos: 0.2, r: 34, g: 211, b: 238 },
  { pos: 0.4, r: 34, g: 197, b: 94 },
  { pos: 0.6, r: 250, g: 204, b: 21 },
  { pos: 0.8, r: 249, g: 115, b: 22 },
  { pos: 1.0, r: 239, g: 68, b: 68 },
];

const interpolateColor = (norm: number): string => {
  const clamped = Math.max(0, Math.min(1, norm));
  for (let i = 0; i < COLOR_STOPS.length - 1; i++) {
    const c1 = COLOR_STOPS[i], c2 = COLOR_STOPS[i + 1];
    if (clamped >= c1.pos && clamped <= c2.pos) {
      const t = (clamped - c1.pos) / (c2.pos - c1.pos);
      return `rgb(${Math.round(c1.r + t * (c2.r - c1.r))}, ${Math.round(c1.g + t * (c2.g - c1.g))}, ${Math.round(c1.b + t * (c2.b - c1.b))})`;
    }
  }
  return `rgb(${COLOR_STOPS[5].r}, ${COLOR_STOPS[5].g}, ${COLOR_STOPS[5].b})`;
};

const HeatmapChart: React.FC<HeatmapChartProps> = ({ data, metric, unit }) => {
  const [tooltip, setTooltip] = useState<TooltipData>({ x: 0, y: 0, date: '', value: null, visible: false });

  const { minValue, maxValue } = useMemo(() => {
    const values = data.map(d => d.value).filter(v => v !== null && !isNaN(v));
    return { minValue: values.length ? Math.min(...values) : 0, maxValue: values.length ? Math.max(...values) : 100 };
  }, [data]);

  const cityCalendars = useMemo(() => {
    const cities = Array.from(new Set(data.map(d => d.city_name)));
    return cities.map(cityName => {
      const cityData = data.filter(d => d.city_name === cityName);
      const dateMap = new Map(cityData.map(d => [d.date, d.value]));
      const dates = cityData.map(d => new Date(d.date)).sort((a, b) => a.getTime() - b.getTime());
      if (dates.length === 0) return { cityName, cells: [], weeks: 0, months: [] };

      const firstDate = new Date(dates[0]);
      const dayOffset = (firstDate.getDay() + 6) % 7;
      firstDate.setDate(firstDate.getDate() - dayOffset);

      const lastDate = dates[dates.length - 1];
      const totalDays = Math.ceil((lastDate.getTime() - firstDate.getTime()) / (1000 * 60 * 60 * 24)) + 7;
      const weeks = Math.ceil(totalDays / 7);

      const cells: DayCell[] = [];
      const monthPositions: Map<string, { start: number; end: number; month: number; year: number }> = new Map();

      for (let w = 0; w < weeks; w++) {
        for (let d = 0; d < 7; d++) {
          const cellDate = new Date(firstDate);
          cellDate.setDate(firstDate.getDate() + w * 7 + d);
          const dateStr = cellDate.toISOString().split('T')[0];
          const year = cellDate.getFullYear();
          const month = cellDate.getMonth() + 1; // 1-12
          const monthKey = `${year}-${month}`;

          // Track month positions for centered labels
          if (!monthPositions.has(monthKey)) {
            monthPositions.set(monthKey, { start: w, end: w, month, year });
          } else {
            monthPositions.get(monthKey)!.end = w;
          }

          cells.push({ date: dateStr, value: dateMap.get(dateStr) ?? null, dayOfWeek: d, weekIndex: w });
        }
      }

      // Calculate centered month labels using Hungarian month names
      const firstYear = dates[0].getFullYear();
      const months = Array.from(monthPositions.entries()).map(([, pos]) => ({
        label: pos.year !== firstYear ? `${MONTHS_HU[pos.month]}\n${pos.year}` : MONTHS_HU[pos.month],
        weekIndex: Math.floor((pos.start + pos.end) / 2)
      }));

      return { cityName, cells, weeks, months };
    });
  }, [data]);

  const getColor = (value: number | null): string => {
    if (value === null) return '#ebedf0';
    const range = maxValue - minValue;
    if (range === 0) return interpolateColor(0.5);
    return interpolateColor((value - minValue) / range);
  };

  const formatValue = (v: number | null): string => v === null ? 'N/A' : `${v.toFixed(1)}${unit}`;
  const formatDate = (dateStr: string): string => new Date(dateStr).toLocaleDateString('hu-HU', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

  const handleMouseEnter = (e: React.MouseEvent, cell: DayCell) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setTooltip({ x: rect.left + rect.width / 2, y: rect.top - 10, date: cell.date, value: cell.value, visible: true });
  };

  if (data.length === 0) return <div className="calendar-empty">No data available</div>;

  // Calculate dynamic cell size based on available width with fallback
  const maxWeeks = cityCalendars.length > 0 ? Math.max(...cityCalendars.map(c => c.weeks)) : 52;
  const cellSize = Math.max(12, Math.min(20, Math.floor(800 / maxWeeks)));

  return (
    <div className="calendar-container">
      <div className="calendar-header">
        <h3>{metric.replace(/_/g, ' ')}</h3>
      </div>

      <div className="calendar-scroll-wrapper">
        {cityCalendars.map(({ cityName, cells, weeks, months }) => (
          <div key={cityName} className="city-calendar">
            <div className="city-label">{cityName}</div>
            <div className="calendar-main">
              <div className="day-labels">
                {DAYS_HU.map((day, i) => <div key={i} className="day-label">{day}</div>)}
              </div>
              <div className="calendar-grid-area">
                <div className="calendar-grid" style={{ gridTemplateColumns: `repeat(${weeks}, ${cellSize}px)` }}>
                  {cells.map((cell, i) => (
                    <div
                      key={i}
                      className="calendar-cell"
                      style={{
                        backgroundColor: getColor(cell.value),
                        gridRow: 7 - cell.dayOfWeek, // Sunday(6)→row1, Monday(0)→row7
                        gridColumn: cell.weekIndex + 1,
                        width: `${cellSize}px`,
                        height: `${Math.max(10, cellSize - 6)}px`
                      }}
                      onMouseEnter={(e) => handleMouseEnter(e, cell)}
                      onMouseLeave={() => setTooltip(prev => ({ ...prev, visible: false }))}
                    />
                  ))}
                </div>
                <div className="month-labels" style={{ gridTemplateColumns: `repeat(${weeks}, ${cellSize}px)` }}>
                  {months.map(({ label, weekIndex }, i) => (
                    <div key={i} className="month-label" style={{ gridColumn: weekIndex + 1 }}>{label}</div>
                  ))}
                </div>
              </div>
              <div className="color-scale">
                <span className="scale-label">{maxValue.toFixed(0)}{unit}</span>
                <div className="scale-bar" />
                <span className="scale-label">{minValue.toFixed(0)}{unit}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {tooltip.visible && (
        <div className="calendar-tooltip" style={{ left: tooltip.x, top: tooltip.y }}>
          <div className="tooltip-date">{formatDate(tooltip.date)}</div>
          <div className="tooltip-value">{formatValue(tooltip.value)}</div>
        </div>
      )}
    </div>
  );
};

export default HeatmapChart;
