import React, { useState } from 'react';
import { FormData, WeatherAnalysisRequest, DateRange } from '../types/weather';
import { HUNGARIAN_CITIES, EUROPEAN_CITIES } from '../constants/cities';
import './WeatherForm.css';

interface WeatherFormProps {
  onSubmit: (request: WeatherAnalysisRequest) => Promise<void>;
  loading?: boolean;
}

const WeatherForm: React.FC<WeatherFormProps> = ({ onSubmit, loading = false }) => {
  const [formData, setFormData] = useState<FormData>({
    cities: '',
    dateType: 'single',
    singleDate: new Date().toISOString().split('T')[0],
    startDate: '',
    endDate: '',
  });

  const [error, setError] = useState<string | null>(null);

  const handleChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setError(null);
  };

  const validateForm = (): string | null => {
    if (!formData.cities.trim()) {
      return 'Please enter at least one city';
    }

    const cityList = formData.cities.split(',').map((c) => c.trim()).filter((c) => c);
    if (cityList.length === 0) {
      return 'Please enter valid city names';
    }

    if (formData.dateType === 'single') {
      if (!formData.singleDate) {
        return 'Please select a date';
      }
    } else {
      if (!formData.startDate || !formData.endDate) {
        return 'Please select both start and end dates';
      }
      if (new Date(formData.startDate) > new Date(formData.endDate)) {
        return 'Start date must be before end date';
      }
    }

    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    const cityList = formData.cities
      .split(',')
      .map((c) => c.trim())
      .filter((c) => c);

    const dateRange: DateRange = formData.dateType === 'single'
      ? { date: formData.singleDate }
      : { start: formData.startDate, end: formData.endDate };

    const request: WeatherAnalysisRequest = {
      cities: cityList,
      date_range: dateRange,
    };

    try {
      await onSubmit(request);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  return (
    <form className="weather-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="cities">Városok</label>
        <div className="preset-buttons">
          <button
            type="button"
            onClick={() => handleChange('cities', HUNGARIAN_CITIES.map(c => c.name).join(', '))}
            disabled={loading}
            className="preset-btn"
          >
            Magyar városok
          </button>
          <button
            type="button"
            onClick={() => handleChange('cities', EUROPEAN_CITIES.map(c => c.name).join(', '))}
            disabled={loading}
            className="preset-btn"
          >
            Európai városok
          </button>
          <button
            type="button"
            onClick={() => handleChange('cities', [...HUNGARIAN_CITIES, ...EUROPEAN_CITIES].map(c => c.name).join(', '))}
            disabled={loading}
            className="preset-btn"
          >
            Mind
          </button>
        </div>
        <textarea
          id="cities"
          value={formData.cities}
          onChange={(e) => handleChange('cities', e.target.value)}
          placeholder="Budapest, Vienna, Prague"
          rows={3}
          disabled={loading}
          style={{ color: '#000000', backgroundColor: '#ffffff' }}
        />
        <span className="form-hint">Vesszővel elválasztott városnevek</span>
      </div>

      <div className="form-group">
        <label>Date Selection</label>
        <div className="date-type-selector">
          <label className="radio-label">
            <input
              type="radio"
              name="dateType"
              value="single"
              checked={formData.dateType === 'single'}
              onChange={(e) => handleChange('dateType', e.target.value)}
              disabled={loading}
            />
            <span>Single Date</span>
          </label>
          <label className="radio-label">
            <input
              type="radio"
              name="dateType"
              value="range"
              checked={formData.dateType === 'range'}
              onChange={(e) => handleChange('dateType', e.target.value)}
              disabled={loading}
            />
            <span>Date Range</span>
          </label>
        </div>
      </div>

      {formData.dateType === 'single' ? (
        <div className="form-group">
          <label htmlFor="singleDate">Date</label>
          <input
            type="date"
            id="singleDate"
            value={formData.singleDate}
            onChange={(e) => handleChange('singleDate', e.target.value)}
            disabled={loading}
            style={{ color: '#1f2937' }}
          />
        </div>
      ) : (
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="startDate">Start Date</label>
            <input
              type="date"
              id="startDate"
              value={formData.startDate}
              onChange={(e) => handleChange('startDate', e.target.value)}
              disabled={loading}
              style={{ color: '#1f2937' }}
            />
          </div>
          <div className="form-group">
            <label htmlFor="endDate">End Date</label>
            <input
              type="date"
              id="endDate"
              value={formData.endDate}
              onChange={(e) => handleChange('endDate', e.target.value)}
              disabled={loading}
              style={{ color: '#1f2937' }}
            />
          </div>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      <button type="submit" disabled={loading} className="submit-button">
        {loading ? 'Analyzing...' : 'Analyze Weather'}
      </button>
    </form>
  );
};

export default WeatherForm;
