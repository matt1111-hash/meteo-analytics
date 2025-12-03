import React, { useState } from 'react';
import TemperatureTab from '../components/analytics/TemperatureTab';
import './AnalyticsView.css';

interface TabConfig {
  id: string;
  label: string;
  icon: string;
}

const AnalyticsView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('temperature');

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
            city="Budapest"
            startDate="2023-01-01"
            endDate="2023-12-31"
          />
        );
      case 'precipitation':
        return (
          <div className="tab-placeholder">
            <h3>🌧️ Precipitation Analysis</h3>
            <p>Precipitation heatmap with meteorological color scale (0mm = white)</p>
            <div className="placeholder-grid">
              <div className="placeholder-item">Loading precipitation heatmap...</div>
            </div>
          </div>
        );
      case 'wind':
        return (
          <div className="tab-placeholder">
            <h3>💨 Wind Analysis</h3>
            <p>Wind speed heatmap with BEAUFORT scale visualization</p>
            <div className="placeholder-grid">
              <div className="placeholder-item">Loading wind heatmap...</div>
            </div>
          </div>
        );
      case 'wind-gust':
        return (
          <div className="tab-placeholder">
            <h3>🌪️ Wind Gust Analysis</h3>
            <p>Maximum wind gusts with BEAUFORT 13-level scale</p>
            <div className="placeholder-grid">
              <div className="placeholder-item">Loading wind gust heatmap...</div>
            </div>
          </div>
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