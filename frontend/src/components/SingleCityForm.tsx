import React from 'react';
import CityAutocomplete from './common/CityAutocomplete';
import MetricSelector from './MetricSelector';

interface SingleCityFormData {
  city: string;
  startDate: string;
  endDate: string;
  metric: string;
}

interface SingleCityFormProps {
  formData: SingleCityFormData;
  viewMode: 'simple' | 'detailed';
  loading: boolean;
  onFieldChange: (field: keyof SingleCityFormData, value: string) => void;
  onViewModeChange: (mode: 'simple' | 'detailed') => void;
  onMetricChange: (metric: string) => void;
  onSubmit: (e: React.FormEvent) => void;
}

const SingleCityForm: React.FC<SingleCityFormProps> = ({
  formData,
  viewMode,
  loading,
  onFieldChange,
  onViewModeChange,
  onMetricChange,
  onSubmit,
}) => {
  return (
    <form className="single-city-form" onSubmit={onSubmit}>
      <div className="view-mode-toggle">
        <button
          type="button"
          onClick={() => onViewModeChange('simple')}
          className={`toggle-btn ${viewMode === 'simple' ? 'active' : ''}`}
          disabled={loading}
        >
          📊 Simple View
        </button>
        <button
          type="button"
          onClick={() => onViewModeChange('detailed')}
          className={`toggle-btn ${viewMode === 'detailed' ? 'active' : ''}`}
          disabled={loading}
        >
          📈 Detailed Analysis
        </button>
      </div>

      <div className="form-grid">
        <div className="form-group">
          <CityAutocomplete
            value={formData.city}
            onChange={(city) => onFieldChange('city', city)}
            disabled={loading}
            placeholder="Város neve..."
          />
        </div>

        <div className="form-group">
          <label htmlFor="start-date">Start Date</label>
          <input
            id="start-date"
            type="date"
            value={formData.startDate}
            onChange={(e) => onFieldChange('startDate', e.target.value)}
            disabled={loading}
            className="form-input bg-white text-gray-900"
            style={{ color: '#1f2937' }}
          />
        </div>

        <div className="form-group">
          <label htmlFor="end-date">End Date</label>
          <input
            id="end-date"
            type="date"
            value={formData.endDate}
            onChange={(e) => onFieldChange('endDate', e.target.value)}
            disabled={loading}
            className="form-input bg-white text-gray-900"
            style={{ color: '#1f2937' }}
          />
        </div>
      </div>

      {viewMode === 'simple' && (
        <MetricSelector
          selectedMetric={formData.metric}
          onMetricChange={onMetricChange}
          disabled={loading}
        />
      )}

      {viewMode === 'detailed' && (
        <div className="detailed-info">
          <p className="info-text">
            Detailed analysis includes temperature, wind (speed & gusts), and precipitation charts
          </p>
        </div>
      )}

      <button type="submit" disabled={loading} className="submit-button">
        {loading
          ? '⏳ Loading...'
          : viewMode === 'simple'
            ? '🔍 Analyze Weather Data'
            : '📊 Run Detailed Analysis'}
      </button>
    </form>
  );
};

export default SingleCityForm;
