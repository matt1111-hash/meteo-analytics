import React, { useState, useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface MultiYearChartProps {
  data: Array<{
    month: string;
    [key: string]: string | number | null;
  }>;
  years: number[];
  metricName: string;
  metricUnit: string;
}

const MultiYearChart: React.FC<MultiYearChartProps> = ({
  data,
  years,
  metricName,
  metricUnit,
}) => {
  const [hiddenYears, setHiddenYears] = useState<Set<number>>(new Set());

  const yearColors = useMemo(() => {
    const colors = [
      '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316',
      '#eab308', '#84cc16', '#10b981', '#14b8a6', '#06b6d4',
    ];
    const colorMap: Record<number, string> = {};
    years.forEach((year, index) => {
      colorMap[year] = colors[index % colors.length];
    });
    return colorMap;
  }, [years]);

  const toggleYear = (year: number) => {
    const newHiddenYears = new Set(hiddenYears);
    if (newHiddenYears.has(year)) {
      newHiddenYears.delete(year);
    } else {
      newHiddenYears.add(year);
    }
    setHiddenYears(newHiddenYears);
  };

  const CustomLegend: React.FC<any> = (props) => {
    return (
      <div className="multi-year-legend">
        {years.map((year) => {
          const isHidden = hiddenYears.has(year);
          const color = yearColors[year];
          return (
            <button
              key={year}
              className={`legend-item ${isHidden ? 'hidden' : ''}`}
              onClick={() => toggleYear(year)}
              style={{ color: isHidden ? '#94a3b8' : color }}
            >
              <span
                className="legend-color"
                style={{ backgroundColor: color }}
              />
              {year}
            </button>
          );
        })}
      </div>
    );
  };

  const CustomTooltip: React.FC<any> = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="multi-year-tooltip">
          <div className="tooltip-header">{label}</div>
          {payload.map((entry: any, index: number) => {
            const year = Number(entry.dataKey);
            if (hiddenYears.has(year)) return null;
            return (
              <div
                key={entry.dataKey}
                className="tooltip-item"
                style={{ color: yearColors[year] }}
              >
                <span className="tooltip-label">{entry.dataKey}:</span>
                <span className="tooltip-value">
                  {entry.value !== null ? `${entry.value.toFixed(1)} ${metricUnit}` : 'N/A'}
                </span>
              </div>
            );
          })}
        </div>
      );
    }
    return null;
  };

  // Filter out hidden years from the data
  const visibleData = useMemo(() => {
    const filtered = data.map(item => {
      const filteredItem: any = { month: item.month };
      years.forEach(year => {
        if (!hiddenYears.has(year)) {
          filteredItem[year.toString()] = item[year.toString()];
        }
      });
      return filteredItem;
    });
    console.log('Debug: Final data for LineChart:', filtered);
    return filtered;
  }, [data, years, hiddenYears]);

  return (
    <div className="multi-year-chart">
      <div className="chart-header">
        <h3 className="chart-title">
          {metricName} Comparison ({years.join(', ')})
        </h3>
      </div>

      <div style={{ width: '100%', height: 400, border: '2px solid #e2e8f0', padding: '20px' }}>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={visibleData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis
              dataKey="month"
              tick={{ fill: '#64748b' }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis
              tick={{ fill: '#64748b' }}
              label={{
                value: metricName,
                angle: -90,
                position: 'insideLeft',
                style: { fill: '#64748b' }
              }}
              domain={['auto', 'auto']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend content={<CustomLegend />} />

          {(() => {
        const visibleYears = years.filter(year => !hiddenYears.has(year));
        console.log('Debug: Visible years for Line rendering:', visibleYears);
        console.log('Debug: Year colors:', yearColors);

        return visibleYears.map(year => {
          // Check if year has any data
          const hasData = data.some(item => item[year.toString()] !== null);
          const yearData = data.map(item => item[year.toString()]);
          console.log(`Debug: Year ${year} has data: ${hasData}, values:`, yearData);

          return (
            <Line
              key={year}
              type="monotone"
              dataKey={year.toString()}
              stroke={yearColors[year]}
              strokeWidth={hasData ? 2 : 1}
              strokeDasharray={hasData ? undefined : "5 5"}
              dot={{ r: hasData ? 3 : 2 }}
              activeDot={{ r: 5 }}
              connectNulls={false}
              opacity={1}
            />
          );
        });
      })()}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {(() => {
        const yearsWithoutData = years.filter(year =>
          !data.some(item => item[year.toString()] !== null)
        );
        const currentYear = new Date().getFullYear();

        // Find the latest month with actual data for current year
        const latestMonth = data.length > 0 && years.includes(currentYear)
          ? data[data.length - 1]?.month
          : null;

        return (hiddenYears.size > 0 || yearsWithoutData.length > 0 || (latestMonth && years.includes(currentYear))) && (
          <div className="chart-info">
            <p>
              {hiddenYears.size > 0 && (
                <span>{hiddenYears.size} year{hiddenYears.size > 1 ? 's' : ''} hidden. </span>
              )}
              {yearsWithoutData.length > 0 && (
                <span>
                  {yearsWithoutData.join(', ')}: no data available.{' '}
                </span>
              )}
              {latestMonth && years.includes(currentYear) && (
                <span>
                  {currentYear}: data available up to {latestMonth}.
                </span>
              )}
              Click legend items to show/hide years.
            </p>
          </div>
        );
      })()}
    </div>
  );
};

export default MultiYearChart;