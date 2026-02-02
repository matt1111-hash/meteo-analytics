import React, { useState } from 'react';
import AnomalyPanel from '../components/panels/AnomalyPanel';
import CityAutocomplete from '../components/common/CityAutocomplete';
import './AnomalyView.css';

interface FormData {
  city: string;
  startDate: string;
  endDate: string;
}

interface AnomalyThresholds {
  temp_hot: number;
  temp_cold: number;
  precip_high: number;
  precip_low: number;
  wind_normal: number;
  wind_strong: number;
  wind_extreme: number;
  wind_hurricane: number;
}

const AnomalyView: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    city: '',
    startDate: '',
    endDate: '',
  });

  const [thresholds, setThresholds] = useState<AnomalyThresholds>({
    temp_hot: 30.0,
    temp_cold: 0.0,
    precip_high: 50.0,
    precip_low: 1.0,
    wind_normal: 20.0,
    wind_strong: 40.0,
    wind_extreme: 60.0,
    wind_hurricane: 100.0,
  });

  const [showThresholds, setShowThresholds] = useState<boolean>(false);
  const [submitted, setSubmitted] = useState<boolean>(false);

  const handleChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleThresholdChange = (field: keyof AnomalyThresholds, value: string) => {
    const numValue = parseFloat(value);
    if (!isNaN(numValue)) {
      setThresholds((prev) => ({ ...prev, [field]: numValue }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  const isFormValid = formData.city.trim() && formData.startDate && formData.endDate;

  return (
    <div className="anomaly-view">
      <div className="view-header">
        <h1>🔍 Anomaly Detection</h1>
        <p className="view-subtitle">
          Detect unusual weather patterns and extreme events
        </p>
      </div>

      <div className="view-content">
        <form className="anomaly-form" onSubmit={handleSubmit}>
          <div className="form-section">
            <h3>Location & Date Range</h3>

            <div className="form-group">
              <CityAutocomplete
                value={formData.city}
                onChange={(city) => handleChange('city', city)}
                placeholder="Város neve..."
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="startDate">Start Date</label>
                <input
                  id="startDate"
                  type="date"
                  value={formData.startDate}
                  onChange={(e) => handleChange('startDate', e.target.value)}
                  style={{ color: '#000000', backgroundColor: '#ffffff' }}
                />
              </div>

              <div className="form-group">
                <label htmlFor="endDate">End Date</label>
                <input
                  id="endDate"
                  type="date"
                  value={formData.endDate}
                  onChange={(e) => handleChange('endDate', e.target.value)}
                  style={{ color: '#000000', backgroundColor: '#ffffff' }}
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <div className="threshold-header">
              <h3>Anomaly Thresholds</h3>
              <button
                type="button"
                onClick={() => setShowThresholds(!showThresholds)}
                className="toggle-button"
              >
                {showThresholds ? '▲ Hide' : '▼ Show'} Advanced Settings
              </button>
            </div>

            {showThresholds && (
              <div className="threshold-grid">
                <div className="threshold-group">
                  <h4>Temperature (°C)</h4>
                  <div className="threshold-input">
                    <label>Hot Threshold:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={thresholds.temp_hot}
                      onChange={(e) => handleThresholdChange('temp_hot', e.target.value)}
                      style={{ color: '#000000' }}
                    />
                  </div>
                  <div className="threshold-input">
                    <label>Cold Threshold:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={thresholds.temp_cold}
                      onChange={(e) => handleThresholdChange('temp_cold', e.target.value)}
                      style={{ color: '#000000' }}
                    />
                  </div>
                </div>

                <div className="threshold-group">
                  <h4>Precipitation (mm)</h4>
                  <div className="threshold-input">
                    <label>High Threshold:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={thresholds.precip_high}
                      onChange={(e) => handleThresholdChange('precip_high', e.target.value)}
                      style={{ color: '#000000' }}
                    />
                  </div>
                  <div className="threshold-input">
                    <label>Low Threshold:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={thresholds.precip_low}
                      onChange={(e) => handleThresholdChange('precip_low', e.target.value)}
                      style={{ color: '#000000' }}
                    />
                  </div>
                </div>

                <div className="threshold-group">
                  <h4>Wind (km/h)</h4>
                  <div className="threshold-input">
                    <label>Normal:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={thresholds.wind_normal}
                      onChange={(e) => handleThresholdChange('wind_normal', e.target.value)}
                      style={{ color: '#000000' }}
                    />
                  </div>
                  <div className="threshold-input">
                    <label>Strong:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={thresholds.wind_strong}
                      onChange={(e) => handleThresholdChange('wind_strong', e.target.value)}
                      style={{ color: '#000000' }}
                    />
                  </div>
                  <div className="threshold-input">
                    <label>Extreme:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={thresholds.wind_extreme}
                      onChange={(e) => handleThresholdChange('wind_extreme', e.target.value)}
                      style={{ color: '#000000' }}
                    />
                  </div>
                  <div className="threshold-input">
                    <label>Hurricane:</label>
                    <input
                      type="number"
                      step="0.1"
                      value={thresholds.wind_hurricane}
                      onChange={(e) => handleThresholdChange('wind_hurricane', e.target.value)}
                      style={{ color: '#000000' }}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={!isFormValid}
            className="submit-button"
          >
            🔍 Detect Anomalies
          </button>
        </form>

        {submitted && isFormValid && (
          <AnomalyPanel
            city={formData.city}
            startDate={formData.startDate}
            endDate={formData.endDate}
            thresholds={thresholds}
          />
        )}
      </div>
    </div>
  );
};

export default AnomalyView;
