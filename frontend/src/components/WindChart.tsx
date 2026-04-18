/**
 * WindChart - Wind speed and gust chart with Beaufort scale
 * Shows sustained wind speed and gusts with Beaufort level indicators
 */
import React, { useMemo } from 'react';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceArea,
  ReferenceLine,
} from 'recharts';
import {
  getBeaufortLevel,
  BEAUFORT_LEVELS,
  WIND_THRESHOLDS,
  type BeaufortLevel,
} from '../constants/windConstants';
import BeaufortLegend from './charts/BeaufortLegend';
import './WindChart.css';

interface WindDataPoint {
  date: string;
  windspeed: number | null;
  windgusts: number | null;
}

interface WindChartProps {
  data: WindDataPoint[];
  city: string;
  showBeaufortLegend?: boolean;
}

// Custom Tooltip with Beaufort information
const CustomTooltip: React.FC<any> = ({ active, payload, label }) => {
  if (!active || !payload || !payload.length) return null;

  const data = payload[0].payload;
  const windSpeed = data.windspeed;
  const windGust = data.windgusts;

  const getBeaufortInfo = (speed: number | null) => {
    if (speed === null) return null;
    const level = getBeaufortLevel(speed);
    return { level, color: level.color };
  };

  const speedInfo = getBeaufortInfo(windSpeed);
  const gustInfo = getBeaufortInfo(windGust);

  return (
    <div
      className="custom-tooltip"
      style={{
        backgroundColor: '#ffffff',
        border: '2px solid #3b82f6',
        borderRadius: '8px',
        padding: '12px',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        minWidth: '200px',
      }}
    >
      <p style={{ margin: '0 0 8px 0', fontWeight: 600, color: '#1e293b' }}>{label}</p>

      {windSpeed !== null && speedInfo && (
        <div style={{ marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div
              style={{
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                backgroundColor: speedInfo.color,
              }}
            />
            <span style={{ fontWeight: 500, color: '#374151' }}>
              Szeles: {windSpeed.toFixed(1)} km/h
            </span>
          </div>
          <span
            style={{
              fontSize: '12px',
              color: speedInfo.color,
              marginLeft: '20px',
              fontWeight: 600,
            }}
          >
            {speedInfo.level.icon} {speedInfo.level.nameHu} ({speedInfo.level.level})
          </span>
        </div>
      )}

      {windGust !== null && gustInfo && (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div
              style={{
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                backgroundColor: gustInfo.color,
              }}
            />
            <span style={{ fontWeight: 500, color: '#374151' }}>
              Széllökés: {windGust.toFixed(1)} km/h
            </span>
          </div>
          <span
            style={{
              fontSize: '12px',
              color: gustInfo.color,
              marginLeft: '20px',
              fontWeight: 600,
            }}
          >
            {gustInfo.level.icon} {gustInfo.level.nameHu} ({gustInfo.level.level})
          </span>
        </div>
      )}
    </div>
  );
};

// Beaufort Reference Area Component
const BeaufortReferenceArea: React.FC<{ level: BeaufortLevel }> = ({ level }) => {
  if (level.level === 0) return null;

  return (
    <ReferenceArea
      y1={level.speedRange.min}
      y2={level.speedRange.max}
      stroke="none"
      fill={level.color}
      fillOpacity={0.05}
      key={`beaufort-${level.level}`}
    />
  );
};

const WindChart: React.FC<WindChartProps> = ({ data, city, showBeaufortLegend = true }) => {
  // Filter and sort data
  const chartData = useMemo(() => {
    return data
      .filter((point) => point.windspeed !== null || point.windgusts !== null)
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [data]);

  // Calculate statistics with Beaufort levels
  const stats = useMemo(() => {
    if (chartData.length === 0) return null;

    const validSpeeds = chartData.filter((d) => d.windspeed !== null).map((d) => d.windspeed!);
    const validGusts = chartData.filter((d) => d.windgusts !== null).map((d) => d.windgusts!);

    if (validSpeeds.length === 0) return null;

    const avgSpeed = validSpeeds.reduce((sum, s) => sum + s, 0) / validSpeeds.length;
    const maxSpeed = Math.max(...validSpeeds);
    const maxGust = validGusts.length > 0 ? Math.max(...validGusts) : 0;

    const avgSpeedLevel = getBeaufortLevel(avgSpeed);
    const maxSpeedLevel = getBeaufortLevel(maxSpeed);
    const maxGustLevel = getBeaufortLevel(maxGust);

    // Count days above Beaufort 6 (Strong Breeze)
    const windyDays = chartData.filter(
      (d) => d.windgusts !== null && d.windgusts >= WIND_THRESHOLDS.STRONG,
    ).length;

    return {
      avgSpeed,
      maxSpeed,
      maxGust,
      windyDays,
      avgSpeedLevel,
      maxSpeedLevel,
      maxGustLevel,
      totalDays: chartData.length,
    };
  }, [chartData]);

  if (chartData.length === 0) {
    return (
      <div className="wind-chart-empty">
        <p>Nem érhető el széladat a megjelenítéshez</p>
      </div>
    );
  }

  return (
    <div className="wind-chart">
      <div className="chart-header">
        <h3>💨 Szélanalízis</h3>
        <p className="chart-subtitle">
          Szélsebesség és széllökés adatai: {city} • {chartData.length} nap
        </p>

        {stats && (
          <div className="chart-stats">
            <div className="stat-item">
              <span className="stat-label">Átlag szél</span>
              <span className="stat-value" style={{ color: stats.avgSpeedLevel.color }}>
                {stats.avgSpeed.toFixed(1)} km/h
                <small style={{ display: 'block', fontSize: '0.75rem', fontWeight: 500 }}>
                  {stats.avgSpeedLevel.icon} {stats.avgSpeedLevel.nameHu} (
                  {stats.avgSpeedLevel.level})
                </small>
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Max szél</span>
              <span className="stat-value" style={{ color: stats.maxSpeedLevel.color }}>
                {stats.maxSpeed.toFixed(1)} km/h
                <small style={{ display: 'block', fontSize: '0.75rem', fontWeight: 500 }}>
                  {stats.maxSpeedLevel.icon} {stats.maxSpeedLevel.nameHu} (
                  {stats.maxSpeedLevel.level})
                </small>
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Max széllökés</span>
              <span className="stat-value" style={{ color: stats.maxGustLevel.color }}>
                {stats.maxGust.toFixed(1)} km/h
                <small style={{ display: 'block', fontSize: '0.75rem', fontWeight: 500 }}>
                  {stats.maxGustLevel.icon} {stats.maxGustLevel.nameHu} ({stats.maxGustLevel.level})
                </small>
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Szeles napok</span>
              <span className="stat-value">
                {stats.windyDays} / {stats.totalDays}
                <small style={{ display: 'block', fontSize: '0.75rem', fontWeight: 500 }}>
                  ({((stats.windyDays / stats.totalDays) * 100).toFixed(0)}%)
                </small>
              </span>
            </div>
          </div>
        )}
      </div>

      <ResponsiveContainer width="100%" height={450}>
        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />

          {/* Beaufort Reference Areas */}
          {BEAUFORT_LEVELS.filter((l) => l.level >= 3 && l.level <= 10).map((level) => (
            <BeaufortReferenceArea key={level.level} level={level} />
          ))}

          <XAxis
            dataKey="date"
            angle={-45}
            textAnchor="end"
            height={80}
            tick={{ fill: '#374151', fontSize: 11 }}
          />
          <YAxis
            label={{
              value: 'Szélsebesség (km/h)',
              angle: -90,
              position: 'insideLeft',
              style: { fill: '#374151', fontWeight: 600 },
            }}
            tick={{ fill: '#374151', fontSize: 12 }}
            domain={[0, 'auto']}
          />

          {/* Reference lines for Beaufort thresholds */}
          <ReferenceLine
            y={WIND_THRESHOLDS.STRONG}
            label="Erős szél (6)"
            stroke="#f97316"
            strokeDasharray="5 5"
            strokeOpacity={0.5}
          />
          <ReferenceLine
            y={WIND_THRESHOLDS.GALE}
            label="Vihar (8)"
            stroke="#dc2626"
            strokeDasharray="5 5"
            strokeOpacity={0.5}
          />

          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ paddingTop: '20px' }} iconType="line" />

          <Bar
            dataKey="windgusts"
            fill="#93c5fd"
            fillOpacity={0.5}
            radius={[4, 4, 0, 0]}
            name="Széllökés"
          />
          <Line
            type="monotone"
            dataKey="windspeed"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={(props) => {
              const { cx, cy, payload } = props;
              if (payload.windspeed === null) return null;
              const level = getBeaufortLevel(payload.windspeed);
              return (
                <circle cx={cx} cy={cy} r={5} fill={level.color} stroke="#2563eb" strokeWidth={2} />
              );
            }}
            activeDot={{ r: 7 }}
            name="Szélsebesség"
          />
        </ComposedChart>
      </ResponsiveContainer>

      <div className="chart-legend-info">
        <div className="legend-item">
          <span className="legend-marker legend-line"></span>
          <span className="legend-text">Szélsebesség (folyamatos átlag)</span>
        </div>
        <div className="legend-item">
          <span className="legend-marker legend-bar"></span>
          <span className="legend-text">Széllökés (csúcssebesség)</span>
        </div>
      </div>

      {showBeaufortLegend && (
        <div style={{ marginTop: '20px' }}>
          <BeaufortLegend
            compact={false}
            highlightLevel={stats ? stats.maxGustLevel.level : undefined}
          />
        </div>
      )}
    </div>
  );
};

export default WindChart;
