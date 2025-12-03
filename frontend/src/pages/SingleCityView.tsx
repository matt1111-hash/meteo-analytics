import React, { useState } from 'react';
import SingleCityForm from '../components/SingleCityForm';
import SingleCityResults from '../components/SingleCityResults';
import DetailedResults from '../components/DetailedResults';
import { useCityWeather } from '../hooks/useCityWeather';
import './SingleCityView.css';

interface SingleCityFormData {
  city: string;
  startDate: string;
  endDate: string;
  metric: string;
}

const SingleCityView: React.FC = () => {
  const [formData, setFormData] = useState<SingleCityFormData>({
    city: '',
    startDate: '',
    endDate: '',
    metric: 'temperature_2m_max',
  });

  const [viewMode, setViewMode] = useState<'simple' | 'detailed'>('simple');
  const [metricInfo, setMetricInfo] = useState<{ name: string; unit: string }>({
    name: 'Temperature',
    unit: '°C',
  });

  const { results, detailedData, loading, error, fetchWeatherData } = useCityWeather();

  const handleChange = (field: keyof SingleCityFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleMetricChange = (metric: string) => {
    handleChange('metric', metric);

    // Update metric info for chart (simplified mapping)
    const metricMap: Record<string, { name: string; unit: string }> = {
      temperature_2m_max: { name: 'Maximum Temperature', unit: '°C' },
      temperature_2m_min: { name: 'Minimum Temperature', unit: '°C' },
      temperature_2m_mean: { name: 'Mean Temperature', unit: '°C' },
      precipitation_sum: { name: 'Precipitation', unit: 'mm' },
      windspeed_10m_max: { name: 'Wind Speed', unit: 'km/h' },
      windgusts_10m_max: { name: 'Wind Gusts', unit: 'km/h' },
      temperature_range: { name: 'Temperature Range', unit: '°C' },
    };

    setMetricInfo(metricMap[metric] || { name: metric, unit: '' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Basic validation
    if (!formData.city.trim() || !formData.startDate || !formData.endDate) {
      return;
    }

    if (formData.startDate > formData.endDate) {
      return;
    }

    await fetchWeatherData({
      city: formData.city,
      startDate: formData.startDate,
      endDate: formData.endDate,
      metric: formData.metric,
      viewMode,
    });
  };

  return (
    <div className="single-city-view">
      <div className="view-header">
        <h1>📍 Single City Time Series</h1>
        <p className="view-subtitle">Analyze weather trends for a specific city over time</p>
      </div>

      <div className="view-content">
        <SingleCityForm
          formData={formData}
          viewMode={viewMode}
          loading={loading}
          onFieldChange={handleChange}
          onViewModeChange={setViewMode}
          onMetricChange={handleMetricChange}
          onSubmit={handleSubmit}
        />

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {results.length > 0 && viewMode === 'simple' && (
          <SingleCityResults
            data={results}
            metric={formData.metric}
            metricName={metricInfo.name}
            metricUnit={metricInfo.unit}
            city={formData.city}
            startDate={formData.startDate}
            endDate={formData.endDate}
          />
        )}

        {detailedData && viewMode === 'detailed' && (
          <>
            <div style={{ color: 'red', fontWeight: 'bold' }}>
              DEBUG: Detailed view branch REACHED
            </div>
            <DetailedResults
              temperatureData={detailedData?.temperature_data || []}
              windData={detailedData?.wind_data || []}
              windGustsData={detailedData?.wind_gusts_data || []}
              precipitationData={detailedData?.precipitation_data || []}
              city={formData.city}
              startDate={formData.startDate}
              endDate={formData.endDate}
            />
          </>
        )}
      </div>
    </div>
  );
};

export default SingleCityView;