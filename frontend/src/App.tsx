import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import ErrorBoundary from './components/common/ErrorBoundary';
import ConnectionStatus from './components/common/ConnectionStatus';
import ThemeToggle from './components/common/ThemeToggle';

const HomePage = React.lazy(() => import('./pages/HomePage'));
const AnalyticsView = React.lazy(() => import('./pages/AnalyticsView'));
const MultiCityView = React.lazy(() => import('./pages/MultiCityView'));
const SingleCityView = React.lazy(() => import('./pages/SingleCityView'));
const MultiYearView = React.lazy(() => import('./pages/MultiYearView'));
const AnomalyView = React.lazy(() => import('./pages/AnomalyView'));
const HeatmapView = React.lazy(() => import('./pages/HeatmapView'));
const ExtremeEventsView = React.lazy(() => import('./pages/ExtremeEventsView'));
const WindyDaysView = React.lazy(() => import('./pages/WindyDaysView'));
const DataTableView = React.lazy(() => import('./pages/DataTableView'));
const TrendAnalyticsView = React.lazy(() => import('./pages/TrendAnalyticsView'));

import './styles/theme.css';
import './App.css';

function LoadingFallback() {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '50vh',
        fontSize: '1.2rem',
        color: 'var(--text-secondary, #666)',
      }}
    >
      Loading...
    </div>
  );
}

function Navigation() {
  const location = useLocation();

  // Don't show navigation on home page
  if (location.pathname === '/') {
    return null;
  }

  return (
    <nav className="app-nav">
      <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>
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
        📈 Multi-Year Comparison
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
      <Link
        to="/data-table"
        className={`nav-link ${location.pathname === '/data-table' ? 'active' : ''}`}
      >
        📋 Data Table
      </Link>
      <Link
        to="/trend-analytics"
        className={`nav-link ${location.pathname === '/trend-analytics' ? 'active' : ''}`}
      >
        📈 Trend Analytics
      </Link>
    </nav>
  );
}

function AppHeader() {
  return (
    <header className="app-header">
      <div className="header-content">
        <h1 className="app-title">Global Weather Analyzer</h1>
        <p className="app-subtitle">Multi-city weather analysis powered by Clean Architecture</p>
      </div>
      <div className="header-actions">
        <ThemeToggle className="theme-toggle-header" />
      </div>
      <Navigation />
    </header>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <ThemeProvider>
          <ConnectionStatus />
          <div className="app">
            <AppHeader />

            <main className="app-main">
              <Suspense fallback={<LoadingFallback />}>
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
                  <Route path="/data-table" element={<DataTableView />} />
                  <Route path="/trend-analytics" element={<TrendAnalyticsView />} />
                </Routes>
              </Suspense>
            </main>
          </div>
        </ThemeProvider>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
