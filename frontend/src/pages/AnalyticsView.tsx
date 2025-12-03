import React, { useState } from 'react';
import TemperatureTab from '../components/analytics/TemperatureTab';
import PrecipitationTab from '../components/analytics/PrecipitationTab';
import WindTab from '../components/analytics/WindTab';
import WindGustTab from '../components/analytics/WindGustTab';
import CityAutocomplete from '../components/common/CityAutocomplete';
import './AnalyticsView.css';

interface TabConfig {
  id: string;
  label: string;
  icon: string;
}

const AnalyticsView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('temperature');

  // Calculate default date range (last 30 days)
  const getDateString = (daysBack: number): string => {
    const date = new Date();
    date.setDate(date.getDate() - daysBack);
    return date.toISOString().split('T')[0];
  };

  const [city, setCity] = useState<string>('Budapest');
  const [startDate, setStartDate] = useState<string>(getDateString(30));
  const [endDate, setEndDate] = useState<string>(getDateString(0));
  const [isCustomMode, setIsCustomMode] = useState<boolean>(false);

  const handleDatePreset = (days: number) => {
    setIsCustomMode(false);
    setStartDate(getDateString(days));
    setEndDate(getDateString(0));
  };

  const handleCustomMode = () => {
    setIsCustomMode(true);
  };

  const handleDateChange = (field: 'start' | 'end', value: string) => {
    if (field === 'start') {
      setStartDate(value);
      setIsCustomMode(true);
    } else {
      setEndDate(value);
      setIsCustomMode(true);
    }
  };

  const tabs: TabConfig[] = [
    { id: 'temperature', label: 'Temperature', icon: '🌡️' },
    { id: 'precipitation', label: 'Precipitation', icon: '🌧️' },
    { id: 'wind', label: 'Wind', icon: '💨' },
    { id: 'wind-gust', label: 'Wind Gust', icon: '🌪️' }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'temperature':
        return (
          <TemperatureTab
            city={city}
            startDate={startDate}
            endDate={endDate}
          />
        );
      case 'precipitation':
        return (
          <PrecipitationTab
            city={city}
            startDate={startDate}
            endDate={endDate}
          />
        );
      case 'wind':
        return (
          <WindTab
            city={city}
            startDate={startDate}
            endDate={endDate}
          />
        );
      case 'wind-gust':
        return (
          <WindGustTab
            city={city}
            startDate={startDate}
            endDate={endDate}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="analytics-view">
      <div className="analytics-header">
        <h1>📊 Analytics View</h1>
        <p>Multi-city weather analysis with detailed meteorological visualizations</p>
      </div>

      <div className="analytics-controls">
        <div className="control-group">
          <label className="control-label">City:</label>
          <CityAutocomplete
            value={city}
            onChange={setCity}
            placeholder="Search for any city..."
            className="analytics-city-selector"
          />
        </div>

        <div className="control-group">
          <label className="control-label">Date Range:</label>
          <div className="date-presets">
            <button
              className={`preset-btn ${!isCustomMode && startDate === getDateString(30) ? 'active' : ''}`}
              onClick={() => handleDatePreset(30)}
            >
              30 Days
            </button>
            <button
              className={`preset-btn ${!isCustomMode && startDate === getDateString(90) ? 'active' : ''}`}
              onClick={() => handleDatePreset(90)}
            >
              90 Days
            </button>
            <button
              className={`preset-btn ${!isCustomMode && startDate === getDateString(365) ? 'active' : ''}`}
              onClick={() => handleDatePreset(365)}
            >
              1 Year
            </button>
            <button
              className={`preset-btn ${isCustomMode ? 'active' : ''}`}
              onClick={handleCustomMode}
            >
              Custom
            </button>
          </div>
        </div>

        {isCustomMode && (
          <div className="control-group custom-date-inputs">
            <label className="control-label">Custom Dates:</label>
            <div className="date-inputs">
              <div className="date-input-group">
                <label htmlFor="start-date" className="date-input-label">Start:</label>
                <input
                  id="start-date"
                  type="date"
                  value={startDate}
                  onChange={(e) => handleDateChange('start', e.target.value)}
                  className="date-input"
                  max={endDate}
                />
              </div>
              <div className="date-input-group">
                <label htmlFor="end-date" className="date-input-label">End:</label>
                <input
                  id="end-date"
                  type="date"
                  value={endDate}
                  onChange={(e) => handleDateChange('end', e.target.value)}
                  className="date-input"
                  min={startDate}
                />
              </div>
            </div>
          </div>
        )}

        <div className="control-group">
          <label className="control-label">Period:</label>
          <span className="period-display">
            {city} • {startDate} to {endDate}
          </span>
        </div>
      </div>

      <div className="analytics-content">
        <div className="tab-navigation">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="tab-content">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsView;