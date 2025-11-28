/**
 * CalendarHeatmap - GitHub contribution graph style heatmap
 * Dynamic cell size, continuous color scale, Hungarian day labels
 */
import React, { useState, useMemo, useRef, useEffect } from 'react';
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
  dayOfWeek: number;
  weekIndex: number;
}

interface TooltipData {
  x: number;
  y: number;
  date: string;
  value: number | null;
  visible: boolean;
}

// Hungarian day labels
const DAYS_HU = ['H', 'K', 'Sze', 'Cs', 'P', 'Szo', 'V'];

// Color stops for interpolation: blue → cyan → green → yellow → orange → red
const COLOR_STOPS = [
  { pos: 0.0, r: 59, g: 130, b: 246 },  // Blue
  { pos: 0.2, r: 34, g: 211, b: 238 },  // Cyan
  { pos: 0.4, r: 34, g: 197, b: 94 },   // Green
  { pos: 0.6, r: 250, g: 204, b: 21 },  // Yellow
  { pos: 0.8, r: 249, g: 115, b: 22 },  // Orange
  { pos: 1.0, r: 239, g: 68, b: 68 },   // Red
];

/** Interpolate between color stops */
const interpolateColor = (norm: number): string => {
  const clamped = Math.max(0, Math.min(1, norm));
  for (let i = 0; i < COLOR_STOPS.length - 1; i++) {
    const c1 = COLOR_STOPS[i];
    const c2 = COLOR_STOPS[i + 1];
    if (clamped >= c1.pos && clamped <= c2.pos) {
      const t = (clamped - c1.pos) / (c2.pos - c1.pos);
      const r = Math.round(c1.r + t * (c2.r - c1.r));
      const g = Math.round(c1.g + t * (c2.g - c1.g));
      const b = Math.round(c1.b + t * (c2.b - c1.b));
      return `rgb(${r}, ${g}, ${b})`;
    }
  }
  return `rgb(${COLOR_STOPS[5].r}, ${COLOR_STOPS[5].g}, ${COLOR_STOPS[5].b})`;
};

const HeatmapChart: React.FC<HeatmapChartProps> = ({ data, metric, unit }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [cellSize, setCellSize] = useState(16);
  const [tooltip, setTooltip] = useState<TooltipData>({
    x: 0, y: 0, date: '', value: null, visible: false
  });

  // Calculate min/max for color scale
  const { minValue, maxValue } = useMemo(() => {
    const values = data.map(d => d.value).filter(v => v !== null && !isNaN(v));
    return {
      minValue: values.length > 0 ? Math.min(...values) : 0,
      maxValue: values.length > 0 ? Math.max(...values) : 100
    };
  }, [data]);

  // Group data by city and organize into calendar grid
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
      const months: { label: string; weekIndex: number }[] = [];
      let lastMonth = -1;

      for (let w = 0; w < weeks; w++) {
        for (let d = 0; d < 7; d++) {
          const cellDate = new Date(firstDate);
          cellDate.setDate(firstDate.getDate() + w * 7 + d);
          const dateStr = cellDate.toISOString().split('T')[0];
          const currentMonth = cellDate.getMonth();

          // Track month change on ANY day, place label at that week
          if (currentMonth !== lastMonth) {
            lastMonth = currentMonth;
            months.push({
              label: cellDate.toLocaleDateString('hu-HU', { month: 'short' }),
              weekIndex: w
            });
          }

          cells.push({ date: dateStr, value: dateMap.get(dateStr) ?? null, dayOfWeek: d, weekIndex: w });
        }
      }
      return { cityName, cells, weeks, months };
    });
  }, [data]);

  // Dynamic cell size calculation
  useEffect(() => {
    const updateCellSize = () => {
      if (!containerRef.current || cityCalendars.length === 0) return;
      const containerWidth = containerRef.current.offsetWidth - 80; // minus day labels + padding
      const maxWeeks = Math.max(...cityCalendars.map(c => c.weeks), 1);
      const gap = 2;
      const calculated = Math.floor((containerWidth - (maxWeeks - 1) * gap) / maxWeeks);
      setCellSize(Math.max(12, Math.min(24, calculated)));
    };
    updateCellSize();
    window.addEventListener('resize', updateCellSize);
    return () => window.removeEventListener('resize', updateCellSize);
  }, [cityCalendars]);

  const getColor = (value: number | null): string => {
    if (value === null) return '#ebedf0';
    const range = maxValue - minValue;
    if (range === 0) return interpolateColor(0.5);
    return interpolateColor((value - minValue) / range);
  };

  const formatValue = (v: number | null): string => v === null ? 'N/A' : `${v.toFixed(1)}${unit}`;

  const formatDate = (dateStr: string): string => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('hu-HU', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  };

  const handleMouseEnter = (e: React.MouseEvent, cell: DayCell) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setTooltip({ x: rect.left + rect.width / 2, y: rect.top - 10, date: cell.date, value: cell.value, visible: true });
  };

  const handleMouseLeave = () => setTooltip(prev => ({ ...prev, visible: false }));

  if (data.length === 0) return <div className="calendar-empty">No data available</div>;

  return (
    <div className="calendar-container" ref={containerRef}>
      <div className="calendar-header">
        <h3>{metric.replace(/_/g, ' ')}</h3>
      </div>

      {cityCalendars.map(({ cityName, cells, weeks, months }) => (
        <div key={cityName} className="city-calendar">
          <div className="city-label">{cityName}</div>
          <div className="calendar-wrapper">
            <div className="day-labels" style={{ gap: `${cellSize > 16 ? 2 : 1}px` }}>
              {DAYS_HU.map((day, i) => (
                <div key={i} className="day-label" style={{ height: cellSize }}>{day}</div>
              ))}
            </div>
            <div className="calendar-grid-wrapper">
              <div className="month-labels" style={{ gridTemplateColumns: `repeat(${weeks}, ${cellSize}px)` }}>
                {months.map(({ label, weekIndex }, i) => (
                  <div key={i} className="month-label" style={{ gridColumn: weekIndex + 1 }}>{label}</div>
                ))}
              </div>
              <div className="calendar-grid" style={{
                gridTemplateColumns: `repeat(${weeks}, ${cellSize}px)`,
                gridTemplateRows: `repeat(7, ${cellSize}px)`,
                gap: '2px'
              }}>
                {cells.map((cell, i) => (
                  <div
                    key={i}
                    className="calendar-cell"
                    style={{
                      backgroundColor: getColor(cell.value),
                      gridRow: cell.dayOfWeek + 1,
                      gridColumn: cell.weekIndex + 1,
                      width: cellSize,
                      height: cellSize
                    }}
                    onMouseEnter={(e) => handleMouseEnter(e, cell)}
                    onMouseLeave={handleMouseLeave}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      ))}

      <div className="calendar-legend">
        <span className="legend-label">{minValue.toFixed(1)}{unit}</span>
        <div className="legend-gradient" />
        <span className="legend-label">{maxValue.toFixed(1)}{unit}</span>
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
