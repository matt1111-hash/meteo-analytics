/**
 * ConnectionStatus banner — shows when the backend server is unreachable.
 *
 * Subscribes to apiClient's connection events and renders a dismissible
 * warning bar at the top of the page.
 */

import React, { useEffect, useState } from 'react';

import { isBackendConnected, onConnectionChange } from '../../services/apiClient';

const ConnectionStatus: React.FC = () => {
  const [visible, setVisible] = useState(!isBackendConnected());

  useEffect(() => {
    const unsubscribe = onConnectionChange((connected) => {
      setVisible(!connected);
    });
    return unsubscribe;
  }, []);

  if (!visible) {
    return null;
  }

  return (
    <div
      role="alert"
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.75rem',
        padding: '0.6rem 1rem',
        background: '#e74c3c',
        color: '#fff',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        fontSize: '0.9rem',
        fontWeight: 500,
      }}
    >
      <span>Backend server is not reachable.</span>
      <code
        style={{
          background: 'rgba(0,0,0,0.2)',
          padding: '0.15rem 0.4rem',
          borderRadius: '3px',
          fontSize: '0.82rem',
        }}
      >
        python -m uvicorn src.api.main:app --port 8003
      </code>
    </div>
  );
};

export default ConnectionStatus;
