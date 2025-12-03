import React, { useState } from 'react';
import CitySelector from '../components/CitySelector';
import YearSelector from '../components/YearSelector';
import MetricSelector from '../components/MetricSelector';
import MultiYearChart from '../components/MultiYearChart';
import { useMultiYearWeather } from '../hooks/useMultiYearWeather';
import './MultiYearView.css';

interface MultiYearFormData {
  city: string;
  years: number[];
  metric: string;
}

const MultiYearView: React.FC = () => {
  const [formData, setFormData] = useState<MultiYearFormData>({
    city: '',
    years: [2023, 2024, 2025], // Default to recent 3 years
    metric: 'temperature_2m_max',
  });

  const [metricInfo, setMetricInfo] = useState<{ name: string; unit: string }>({
    name: 'Maximum Temperature',
    unit: '°C',
  });

  const { data, loading, error, fetchMultiYearData, resetData } = useMultiYearWeather();

  // Multi-year CSV export handler
  const handleExportCSV = (): void => {
    if (data.length === 0) return;

    // Build CSV content
    const headers = ['month', 'year', 'metric', 'value', 'city'];
    const rows = data.flatMap(item =>
      Object.entries(item)
        .filter(([key]) => key !== 'month')
        .map(([year, value]) => [
          item.month,
          year,
          formData.metric,
          value?.toString() ?? '',
          formData.city,
        ])
    );

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.join(',')),
    ].join('\n');

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    // Filename: {city}_{metric}_{years}.csv
    const sanitizedCity = formData.city.replace(/[^a-zA-Z0-9]/g, '_');
    const yearsStr = formData.years.join('-');
    const filename = `${sanitizedCity}_${formData.metric}_${yearsStr}_multiyear.csv`;

    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleCityChange = (city: string) => {
    setFormData((prev) => ({ ...prev, city }));
  };

  const handleYearsChange = (years: number[]) => {
    setFormData((prev) => ({ ...prev, years }));
  };

  const handleMetricChange = (metric: string) => {
    setFormData((prev) => ({ ...prev, metric }));

    // Update metric info for chart
    const metricMap: Record<string, { name: string; unit: string }> = {
      temperature_2m_max: { name: 'Maximum Temperature', unit: '°C' },
      temperature_2m_min: { name: 'Minimum Temperature', unit: '°C' },
      temperature_2m_mean: { name: 'Mean Temperature', unit: '°C' },
      precipitation_sum: { name: 'Precipitation', unit: 'mm' },
      windspeed_10m_max: { name: 'Wind Speed', unit: 'km/h' },
      windgusts_10m_max: { name: 'Wind Gusts', unit: 'km/h' },
    };

    setMetricInfo(metricMap[metric] || { name: metric, unit: '' });
  };

  const validateForm = (): string | null => {
    if (!formData.city.trim()) {
      return 'Please enter a city name';
    }
    if (formData.years.length === 0) {
      return 'Please select at least one year';
    }
    if (!formData.metric) {
      return 'Please select a metric';
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    console.log('Debug: Form submit with data:', formData);

    const validationError = validateForm();
    if (validationError) {
      console.log('Debug: Validation failed:', validationError);
      return;
    }

    console.log('Debug: Validation passed, calling fetchMultiYearData');
    resetData(); // Clear previous data
    await fetchMultiYearData({
      city: formData.city,
      years: formData.years,
      metric: formData.metric,
    });
    console.log('Debug: fetchMultiYearData completed');
  };

  
  return (
    <div className="multi-year-view">
      <div className="view-header">
        <h1>📊 Multi-Year Comparison</h1>
        <p className="view-subtitle">Compare weather patterns across different years</p>
      </div>

      <div className="view-content">
        <form className="multi-year-form" onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <CitySelector
                id="city-input"
                value={formData.city}
                onChange={handleCityChange}
                disabled={loading}
                label="Város"
              />
            </div>
          </div>

          <YearSelector
            selectedYears={formData.years}
            onYearsChange={handleYearsChange}
            disabled={loading}
            minYear={2018}
            maxYear={2025}
          />

          <div className="form-group">
            <MetricSelector
              selectedMetric={formData.metric}
              onMetricChange={handleMetricChange}
              disabled={loading}
            />
          </div>

          <button type="submit" disabled={loading} className="submit-button">
            {loading ? '⏳ Loading...' : '📊 Compare Years'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {data.length > 0 && (
          <div className="results-section">
            <div className="results-header">
              <h3>
                {formData.city} - {metricInfo.name} ({formData.years.join(', ')})
              </h3>
              <button
                className="export-csv-btn"
                onClick={handleExportCSV}
                title={`Export ${formData.years.length} years of data`}
                disabled={data.length === 0}
              >
                ⬇️ Export CSV
              </button>
            </div>

            <MultiYearChart
              data={data}
              years={formData.years}
              metricName={metricInfo.name}
              metricUnit={metricInfo.unit}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default MultiYearView;