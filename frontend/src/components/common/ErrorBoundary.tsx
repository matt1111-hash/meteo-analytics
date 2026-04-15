/**
 * React Error Boundary — catches unhandled render errors and shows a fallback UI.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { logger } from '../../utils/logger';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    logger.error('ErrorBoundary caught:', error.message);
  }

  private handleReload = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div
          style={{
            padding: '2rem',
            margin: '2rem auto',
            maxWidth: '600px',
            border: '1px solid #e74c3c',
            borderRadius: '8px',
            backgroundColor: 'var(--error-bg, #fff5f5)',
            color: 'var(--text-primary, #333)',
          }}
        >
          <h2 style={{ color: '#e74c3c', marginTop: 0 }}>
            Something went wrong
          </h2>
          <p>
            An unexpected error occurred in the application.
          </p>
          <details style={{ marginBottom: '1rem' }}>
            <summary style={{ cursor: 'pointer', fontWeight: 500 }}>
              Error details
            </summary>
            <pre
              style={{
                whiteSpace: 'pre-wrap',
                fontSize: '0.85rem',
                background: 'var(--code-bg, #f5f5f5)',
                padding: '0.75rem',
                borderRadius: '4px',
                overflow: 'auto',
              }}
            >
              {this.state.error?.message}
            </pre>
          </details>
          <button
            type="button"
            onClick={this.handleReload}
            style={{
              padding: '0.5rem 1.25rem',
              border: '1px solid #3498db',
              borderRadius: '4px',
              background: '#3498db',
              color: '#fff',
              cursor: 'pointer',
              fontSize: '0.95rem',
            }}
          >
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
