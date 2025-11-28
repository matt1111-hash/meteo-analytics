/** WindyDaysView - Szeles napok analízis (táblázat + oszlopdiagram) */
import React, { useState, useMemo } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import './WindyDaysView.css';

interface WindDataPoint {
  city_name: string;
  date: string;
  value: number;
  metric: string;
}

interface MonthlyWindyStats {
  month: string;
  monthNum: number;
  windyDays: number;
  totalDays: number;
  percentage: number;
  maxWind: number;
}

const MONTHS_HU = ['Jan', 'Feb', 'Már', 'Ápr', 'Máj', 'Jún', 'Júl', 'Aug', 'Sze', 'Okt', 'Nov', 'Dec'];
const DEFAULT_THRESHOLD = 43; // km/h

const getDefaultDates = () => {
  const today = new Date();
  const yearAgo = new Date(today);
  yearAgo.setFullYear(today.getFullYear() - 1);
  return {
    start: yearAgo.toISOString().split('T')[0],
    end: today.toISOString().split('T')[0],
  };
};

const WindyDaysView: React.FC = () => {
  const defaultDates = getDefaultDates();
  const [city, setCity] = useState<string>('Budapest');
  const [startDate, setStartDate] = useState<string>(defaultDates.start);
  const [endDate, setEndDate] = useState<string>(defaultDates.end);
  const [threshold, setThreshold] = useState<number>(DEFAULT_THRESHOLD);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [windData, setWindData] = useState<WindDataPoint[]>([]);

  // Havi statisztikák számítása
  const monthlyStats = useMemo((): MonthlyWindyStats[] => {
    if (windData.length === 0) return [];

    const monthMap = new Map<string, { winds: number[]; dates: Set<string> }>();

    windData.forEach((d) => {
      const date = new Date(d.date);
      const key = `${date.getFullYear()}-${date.getMonth()}`;
      if (!monthMap.has(key)) {
        monthMap.set(key, { winds: [], dates: new Set() });
      }
      const entry = monthMap.get(key)!;
      entry.winds.push(d.value);
      entry.dates.add(d.date);
    });

    const stats: MonthlyWindyStats[] = [];
    monthMap.forEach((data, key) => {
      const [year, monthIdx] = key.split('-').map(Number);
      const windyDays = data.winds.filter((w) => w >= threshold).length;
      const totalDays = data.dates.size;
      const maxWind = Math.max(...data.winds);

      stats.push({
        month: `${MONTHS_HU[monthIdx]} ${year}`,
        monthNum: year * 12 + monthIdx,
        windyDays,
        totalDays,
        percentage: totalDays > 0 ? (windyDays / totalDays) * 100 : 0,
        maxWind,
      });
    });

    return stats.sort((a, b) => a.monthNum - b.monthNum);
  }, [windData, threshold]);

  // Összesítő statisztikák
  const summary = useMemo(() => {
    if (monthlyStats.length === 0) return null;
    const totalWindy = monthlyStats.reduce((sum, m) => sum + m.windyDays, 0);
    const totalDays = monthlyStats.reduce((sum, m) => sum + m.totalDays, 0);
    const maxWind = Math.max(...monthlyStats.map((m) => m.maxWind));
    const windiest = monthlyStats.reduce((max, m) => (m.windyDays > max.windyDays ? m : max), monthlyStats[0]);
    return { totalWindy, totalDays, maxWind, windiest, percentage: (totalWindy / totalDays) * 100 };
  }, [monthlyStats]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setWindData([]);

    try {
      const response = await axios.post('http://localhost:8001/api/weather/single-city-detailed', {
        city,
        start: startDate,
        end: endDate,
      });

      if (response.data?.wind_gusts_data) {
        setWindData(response.data.wind_gusts_data);
      } else {
        setError('Nincs széllökés adat a válaszban');
      }
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(axiosErr.response?.data?.detail || axiosErr.message || 'API hiba');
    } finally {
      setLoading(false);
    }
  };

  const getBarColor = (windyDays: number): string => {
    if (windyDays >= 15) return '#ef4444';
    if (windyDays >= 10) return '#f97316';
    if (windyDays >= 5) return '#eab308';
    return '#22c55e';
  };

  return (
    <div className="windy-days-view">
      <h1>🌪️ Szeles Napok Analízis</h1>
      <p className="view-description">
        Havi szeles napok eloszlása széllökés (gust) alapján (küszöb: {DEFAULT_THRESHOLD} km/h)
      </p>

      <form onSubmit={handleSubmit} className="windy-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="city">Város</label>
            <input
              type="text"
              id="city"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              placeholder="Budapest"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="threshold">Küszöb (km/h)</label>
            <input
              type="number"
              id="threshold"
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              min={10}
              max={100}
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="startDate">Kezdő dátum</label>
            <input type="date" id="startDate" value={startDate} onChange={(e) => setStartDate(e.target.value)} required />
          </div>
          <div className="form-group">
            <label htmlFor="endDate">Záró dátum</label>
            <input type="date" id="endDate" value={endDate} onChange={(e) => setEndDate(e.target.value)} required />
          </div>
        </div>

        <button type="submit" disabled={loading} className="submit-button">
          {loading ? 'Betöltés...' : 'Analízis indítása'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {summary && (
        <div className="summary-cards">
          {[
            { value: summary.totalWindy, label: 'Szeles nap összesen' },
            { value: `${summary.percentage.toFixed(1)}%`, label: 'Szeles napok aránya' },
            { value: `${summary.maxWind.toFixed(1)} km/h`, label: 'Max szélsebesség' },
            { value: summary.windiest.month, label: 'Legszélesebb hónap' },
          ].map((card, i) => (
            <div key={i} className="summary-card">
              <span className="card-value">{card.value}</span>
              <span className="card-label">{card.label}</span>
            </div>
          ))}
        </div>
      )}

      {monthlyStats.length > 0 && (
        <div className="results-container">
          <div className="chart-section">
            <h3>📊 Havi Szeles Napok</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={monthlyStats} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" angle={-45} textAnchor="end" height={80} tick={{ fontSize: 11 }} />
                <YAxis label={{ value: 'Napok', angle: -90, position: 'insideLeft' }} />
                <Tooltip
                  formatter={(value: number, name: string) => [
                    name === 'windyDays' ? `${value} nap` : `${value.toFixed(1)}%`,
                    name === 'windyDays' ? 'Szeles napok' : 'Arány',
                  ]}
                />
                <Bar dataKey="windyDays" name="Szeles napok">
                  {monthlyStats.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={getBarColor(entry.windyDays)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="table-section">
            <h3>📋 Részletes Táblázat</h3>
            <table className="windy-table">
              <thead>
                <tr>{['Hónap', 'Szeles', 'Összes', 'Arány', 'Max'].map((h) => <th key={h}>{h}</th>)}</tr>
              </thead>
              <tbody>
                {monthlyStats.map((r) => (
                  <tr key={r.month}>
                    <td>{r.month}</td>
                    <td className="numeric">{r.windyDays}</td>
                    <td className="numeric">{r.totalDays}</td>
                    <td className="numeric">{r.percentage.toFixed(1)}%</td>
                    <td className="numeric">{r.maxWind.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {!loading && !error && windData.length === 0 && (
        <div className="empty-state">
          <p>Add meg a várost és az időtartamot, majd kattints az "Analízis indítása" gombra.</p>
        </div>
      )}
    </div>
  );
};

export default WindyDaysView;
