import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AnalyticsView from './pages/AnalyticsView';
import MultiCityView from './pages/MultiCityView';
import SingleCityView from './pages/SingleCityView';
import MultiYearView from './pages/MultiYearView';
import AnomalyView from './pages/AnomalyView';
import HeatmapView from './pages/HeatmapView';
import ExtremeEventsView from './pages/ExtremeEventsView';
import WindyDaysView from './pages/WindyDaysView';
import './App.css';

function Navigation() {
  const location = useLocation();

  // Don't show navigation on home page
  if (location.pathname === '/') {
    return null;
  }

  return (
    <nav className="app-nav">
      <Link
        to="/"
        className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
      >
        🏠 Home
      </Link>
      <Link
        to="/analytics"
        className={`nav-link ${location.pathname === '/analytics' ? 'active' : ''}`}
      >
        📊 Analytics
      </Link>
      <Link
        to="/single-city"
        className={`nav-link ${location.pathname === '/single-city' ? 'active' : ''}`}
      >
        📍 Single City Time Series
      </Link>
      <Link
        to="/multi-year"
        className={`nav-link ${location.pathname === '/multi-year' ? 'active' : ''}`}
      >
        📊 Multi-Year Comparison
      </Link>
      <Link
        to="/anomalies"
        className={`nav-link ${location.pathname === '/anomalies' ? 'active' : ''}`}
      >
        🔍 Anomaly Detection
      </Link>
      <Link
        to="/heatmap"
        className={`nav-link ${location.pathname === '/heatmap' ? 'active' : ''}`}
      >
        🗺️ Heatmap View
      </Link>
      <Link
        to="/extreme-events"
        className={`nav-link ${location.pathname === '/extreme-events' ? 'active' : ''}`}
      >
        ⚡ Extreme Events
      </Link>
      <Link
        to="/windy-days"
        className={`nav-link ${location.pathname === '/windy-days' ? 'active' : ''}`}
      >
        🌪️ Windy Days
      </Link>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="app">
        <header className="app-header">
          <div className="header-content">
            <h1 className="app-title">Global Weather Analyzer</h1>
            <p className="app-subtitle">Multi-city weather analysis powered by Clean Architecture</p>
          </div>
          <Navigation />
        </header>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/analytics" element={<AnalyticsView />} />
            <Route path="/multi-city" element={<MultiCityView />} />
            <Route path="/single-city" element={<SingleCityView />} />
            <Route path="/multi-year" element={<MultiYearView />} />
            <Route path="/anomalies" element={<AnomalyView />} />
            <Route path="/heatmap" element={<HeatmapView />} />
            <Route path="/extreme-events" element={<ExtremeEventsView />} />
            <Route path="/windy-days" element={<WindyDaysView />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
