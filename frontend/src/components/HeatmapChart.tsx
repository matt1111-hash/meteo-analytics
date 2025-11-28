/**
 * CalendarHeatmap - GitHub contribution graph style heatmap
 * Y-axis: Days of week (Mon-Sun), X-axis: Weeks, Cells: colored by value
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

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

const HeatmapChart: React.FC<HeatmapChartProps> = ({ data, metric, unit }) => {
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

      // Find first Monday before/on the earliest date
      const firstDate = new Date(dates[0]);
      const dayOffset = (firstDate.getDay() + 6) % 7; // Convert Sun=0 to Mon=0
      firstDate.setDate(firstDate.getDate() - dayOffset);

      // Find last date and calculate weeks
      const lastDate = dates[dates.length - 1];
      const totalDays = Math.ceil((lastDate.getTime() - firstDate.getTime()) / (1000 * 60 * 60 * 24)) + 7;
      const weeks = Math.ceil(totalDays / 7);

      // Build cells grid
      const cells: DayCell[] = [];
      const months: { label: string; weekIndex: number }[] = [];
      let lastMonth = -1;

      for (let w = 0; w < weeks; w++) {
        for (let d = 0; d < 7; d++) {
          const cellDate = new Date(firstDate);
          cellDate.setDate(firstDate.getDate() + w * 7 + d);
          const dateStr = cellDate.toISOString().split('T')[0];

          // Track month changes for labels
          if (d === 0 && cellDate.getMonth() !== lastMonth) {
            lastMonth = cellDate.getMonth();
            months.push({
              label: cellDate.toLocaleDateString('en-US', { month: 'short' }),
              weekIndex: w
            });
          }

          cells.push({
            date: dateStr,
            value: dateMap.get(dateStr) ?? null,
            dayOfWeek: d,
            weekIndex: w
          });
        }
      }
      return { cityName, cells, weeks, months };
    });
  }, [data]);

  // Color scale: blue → cyan → yellow → orange → red
  const getColor = (value: number | null): string => {
    if (value === null) return '#ebedf0';
    const range = maxValue - minValue;
    if (range === 0) return '#3b82f6';
    const norm = (value - minValue) / range;

    if (norm < 0.25) return '#3b82f6'; // Blue
    if (norm < 0.5) return '#22d3ee';  // Cyan
    if (norm < 0.75) return '#facc15'; // Yellow
    return '#ef4444';                   // Red
  };

  const formatValue = (v: number | null): string =>
    v === null ? 'N/A' : `${v.toFixed(1)}${unit}`;

  const formatDate = (dateStr: string): string => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  };

  const handleMouseEnter = (e: React.MouseEvent, cell: DayCell) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setTooltip({
      x: rect.left + rect.width / 2,
      y: rect.top - 10,
      date: cell.date,
      value: cell.value,
      visible: true
    });
  };

  const handleMouseLeave = () => {
    setTooltip(prev => ({ ...prev, visible: false }));
  };

  if (data.length === 0) {
    return <div className="calendar-empty">No data available for heatmap</div>;
  }

  return (
    <div className="calendar-container">
      <div className="calendar-header">
        <h3>{metric.replace(/_/g, ' ')}</h3>
      </div>

      {cityCalendars.map(({ cityName, cells, weeks, months }) => (
        <div key={cityName} className="city-calendar">
          <div className="city-label">{cityName}</div>
          <div className="calendar-wrapper">
            <div className="day-labels">
              {DAYS.map((day, i) => (
                <div key={day} className="day-label">{i % 2 === 0 ? day : ''}</div>
              ))}
            </div>
            <div className="calendar-grid-wrapper">
              <div className="month-labels">
                {months.map(({ label, weekIndex }, i) => (
                  <div key={i} className="month-label" style={{ gridColumn: weekIndex + 1 }}>
                    {label}
                  </div>
                ))}
              </div>
              <div className="calendar-grid" style={{ gridTemplateColumns: `repeat(${weeks}, 12px)` }}>
                {cells.map((cell, i) => (
                  <div
                    key={i}
                    className="calendar-cell"
                    style={{
                      backgroundColor: getColor(cell.value),
                      gridRow: cell.dayOfWeek + 1,
                      gridColumn: cell.weekIndex + 1
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
        <span className="legend-label">Low</span>
        <div className="legend-scale">
          <div className="legend-color" style={{ backgroundColor: '#3b82f6' }} />
          <div className="legend-color" style={{ backgroundColor: '#22d3ee' }} />
          <div className="legend-color" style={{ backgroundColor: '#facc15' }} />
          <div className="legend-color" style={{ backgroundColor: '#ef4444' }} />
        </div>
        <span className="legend-label">High</span>
        <span className="legend-range">({minValue.toFixed(1)} - {maxValue.toFixed(1)}{unit})</span>
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
