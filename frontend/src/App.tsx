import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import MultiCityView from './pages/MultiCityView';
import SingleCityView from './pages/SingleCityView';
import AnomalyView from './pages/AnomalyView';
import './App.css';

function Navigation() {
  const location = useLocation();

  return (
    <nav className="app-nav">
      <Link
        to="/"
        className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
      >
        🌍 Multi-City Analysis
      </Link>
      <Link
        to="/single-city"
        className={`nav-link ${location.pathname === '/single-city' ? 'active' : ''}`}
      >
        📍 Single City Time Series
      </Link>
      <Link
        to="/anomalies"
        className={`nav-link ${location.pathname === '/anomalies' ? 'active' : ''}`}
      >
        🔍 Anomaly Detection
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
            <Route path="/" element={<MultiCityView />} />
            <Route path="/single-city" element={<SingleCityView />} />
            <Route path="/anomalies" element={<AnomalyView />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
