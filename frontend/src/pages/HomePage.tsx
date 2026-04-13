import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

interface FeatureCard {
  id: string;
  title: string;
  description: string;
  icon: string;
  path: string;
}

const HomePage: React.FC = () => {
  const features: FeatureCard[] = [
    {
      id: 'analytics',
      title: 'Analytics',
      description: 'Detailed Analysis',
      icon: '📊',
      path: '/analytics'
    },
    {
      id: 'multi-city',
      title: 'Multi-City',
      description: 'Analysis',
      icon: '🌍',
      path: '/multi-city'
    },
    {
      id: 'single-city',
      title: 'Single City',
      description: 'Time Series',
      icon: '📍',
      path: '/single-city'
    },
    {
      id: 'multi-year',
      title: 'Multi-Year',
      description: 'Comparison',
      icon: '📈',
      path: '/multi-year'
    },
    {
      id: 'anomalies',
      title: 'Anomaly',
      description: 'Detection',
      icon: '🔍',
      path: '/anomalies'
    },
    {
      id: 'heatmap',
      title: 'Heatmap',
      description: 'View',
      icon: '🗺️',
      path: '/heatmap'
    },
    {
      id: 'extreme-events',
      title: 'Extreme',
      description: 'Events',
      icon: '⚡',
      path: '/extreme-events'
    },
    {
      id: 'windy-days',
      title: 'Windy Days',
      description: 'Wind Analysis',
      icon: '🌬️',
      path: '/windy-days'
    },
    {
      id: 'data-table',
      title: 'Data Table',
      description: 'Raw Weather Data',
      icon: '📋',
      path: '/data-table'
    }
  ];

  return (
    <div className="home-page">
      <div className="hero-section">
        <h1 className="hero-title">Global Weather Analyzer</h1>
        <p className="hero-subtitle">Choose your analysis type to get started</p>
      </div>

      <div className="dashboard-grid">
        {features.map((feature) => (
          <Link
            key={feature.id}
            to={feature.path}
            className="feature-card"
          >
            <div className="card-content">
              <div className="card-icon">{feature.icon}</div>
              <div className="card-text">
                <h3 className="card-title">{feature.title}</h3>
                <p className="card-description">{feature.description}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default HomePage;
