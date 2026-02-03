import React, { useState } from 'react';
import axios from 'axios';
import CityAutocomplete from '../components/common/CityAutocomplete';
import DataTablePanel, { WeatherTableRow } from '../components/panels/DataTablePanel';
import { CityWeatherResult } from '../types/weather';
import './DataTableView.css';

const API_BASE_URL = 'http://localhost:8003';

interface FormData {
  city: string;
  startDate: string;
  endDate: string;
}

const DataTableView: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    city: '',
    startDate: '',
    endDate: '',
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [tableData, setTableData] = useState<WeatherTableRow[]>([]);
  const [hasSearched, setHasSearched] = useState<boolean>(false);

  const handleChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setError(null);
  };

  const validateForm = (): string | null => {
    if (!formData.city.trim()) {
      return 'Please enter a city name';
    }
    const startDate = formData.startDate || defaultDates.start;
    const endDate = formData.endDate || defaultDates.end;
    if (startDate > endDate) {
      return 'Start date must be before end date';
    }
    return null;
  };

  const transformToTableData = (results: CityWeatherResult[]): WeatherTableRow[] => {
    const dataMap = new Map<string, WeatherTableRow>();

    for (const result of results) {
      const existing = dataMap.get(result.date) || {
        date: result.date,
        temperature_max: null,
        temperature_min: null,
        temperature_mean: null,
        precipitation: null,
        windspeed: null,
        windgusts: null,
        humidity: null,
      };

      switch (result.metric) {
        case 'temperature_2m_max':
          existing.temperature_max = result.value;
          break;
        case 'temperature_2m_min':
          existing.temperature_min = result.value;
          break;
        case 'temperature_2m_mean':
          existing.temperature_mean = result.value;
          break;
        case 'precipitation_sum':
          existing.precipitation = result.value;
          break;
        case 'windspeed_10m_max':
          existing.windspeed = result.value;
          break;
        case 'windgusts_10m_max':
          existing.windgusts = result.value;
          break;
      }

      dataMap.set(result.date, existing);
    }

    return Array.from(dataMap.values()).sort((a, b) => a.date.localeCompare(b.date));
  };

  const fetchAllMetrics = async (): Promise<WeatherTableRow[]> => {
    const metrics = [
      'temperature_2m_max',
      'temperature_2m_min',
      'temperature_2m_mean',
      'precipitation_sum',
      'windspeed_10m_max',
      'windgusts_10m_max',
    ];

    const startDate = formData.startDate || defaultDates.start;
    const endDate = formData.endDate || defaultDates.end;

    const results: CityWeatherResult[] = [];

    for (const metric of metrics) {
      try {
        const response = await axios.post<{
          city_results: CityWeatherResult[];
        }>(`${API_BASE_URL}/api/weather/single-city`, {
          city: formData.city.trim(),
          start: startDate,
          end: endDate,
          metric,
        });
        results.push(...response.data.city_results);
      } catch (err) {
        console.warn(`Failed to fetch ${metric}:`, err);
      }
    }

    return transformToTableData(results);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const data = await fetchAllMetrics();

      if (data.length === 0) {
        setError('No data returned from API');
        setTableData([]);
        return;
      }

      setTableData(data);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const errorMessage = err.response?.data?.detail || err.message;
        setError(`API Error: ${errorMessage}`);
      } else {
        setError('An unexpected error occurred');
      }
      setTableData([]);
    } finally {
      setLoading(false);
    }
  };

  const getDefaultDates = (): { start: string; end: string } => {
    const end = new Date();
    const start = new Date();
    start.setFullYear(start.getFullYear() - 1);

    const formatDate = (d: Date): string => d.toISOString().split('T')[0];

    return {
      start: formatDate(start),
      end: formatDate(end),
    };
  };

  const defaultDates = getDefaultDates();

  return (
    <div className="data-table-view">
      <div className="view-header">
        <h1>Weather Data Table</h1>
        <p className="view-subtitle">View raw weather data in a paginated, sortable table</p>
      </div>

      <div className="view-content">
        <form className="data-table-form" onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <CityAutocomplete
                value={formData.city}
                onChange={(city) => handleChange('city', city)}
                disabled={loading}
                placeholder="City name..."
              />
            </div>

            <div className="form-group">
              <label htmlFor="start-date">Start Date</label>
              <input
                id="start-date"
                type="date"
                value={formData.startDate || defaultDates.start}
                onChange={(e) => handleChange('startDate', e.target.value)}
                disabled={loading}
                className="form-input"
                style={{ color: '#1f2937', backgroundColor: '#ffffff' }}
              />
            </div>

            <div className="form-group">
              <label htmlFor="end-date">End Date</label>
              <input
                id="end-date"
                type="date"
                value={formData.endDate || defaultDates.end}
                onChange={(e) => handleChange('endDate', e.target.value)}
                disabled={loading}
                className="form-input"
                style={{ color: '#1f2937', backgroundColor: '#ffffff' }}
              />
            </div>
          </div>

          <button type="submit" disabled={loading} className="submit-button">
            {loading ? 'Loading...' : 'Load Data'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {hasSearched && !loading && tableData.length === 0 && !error && (
          <div className="no-data-message">
            <span className="no-data-icon">📋</span>
            <span>No data available for the selected criteria</span>
          </div>
        )}

        {tableData.length > 0 && (
          <div className="results-section">
            <div className="section-header">
              <h3>Weather Data ({tableData.length} days)</h3>
            </div>
            <DataTablePanel data={tableData} loading={loading} />
          </div>
        )}
      </div>
    </div>
  );
};

export default DataTableView;
