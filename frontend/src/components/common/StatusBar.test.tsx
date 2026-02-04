/**
 * StatusBar Component Tests
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { StatusBar } from './StatusBar';

// Mock the providerService
jest.mock('../../services/providerService', () => ({
  STATUS_LABELS: { healthy: 'Egészséges', warning: 'Figyelmeztetés', critical: 'Kritikus' },
  STATUS_COLORS: { healthy: '#22c55e', warning: '#f59e0b', critical: '#ef4444' },
  STATUS_BG_COLORS: {
    healthy: 'rgba(34, 197, 94, 0.1)',
    warning: 'rgba(245, 158, 11, 0.1)',
    critical: 'rgba(239, 68, 68, 0.1)',
  },
  formatUsagePercentage: (p: number) => `${(p * 100).toFixed(1)}%`,
  formatCost: (c: number) => (c === 0 ? 'Ingyenes' : `$${c.toFixed(4)}`),
  formatRequestCount: (c: number) => new Intl.NumberFormat('hu-HU').format(c),
  getStatusIcon: (s: string) => (s === 'healthy' ? '✓' : s === 'warning' ? '⚠' : '✕'),
}));

// Mock the useProviderManagement hook
const mockRefreshAll = jest.fn().mockResolvedValue(undefined);

const mockSelectedProvider = {
  provider_id: 'auto',
  name: 'Automatikus',
  description: 'Smart routing',
  icon: '🔄',
  cost: 'Ingyenes',
  limitations: [],
  features: [],
  routing_logic: {},
};

const mockStatuses = [
  {
    provider_id: 'auto',
    name: 'Automatikus',
    status: 'healthy' as const,
    is_selected: true,
    usage_percentage: 0.35,
    requests_this_month: 3500,
    monthly_limit: 10000,
    estimated_cost_usd: 3.5,
    last_used: '2024-01-15T10:30:00Z',
  },
];

const mockUsage = {
  provider_id: 'auto',
  requests_total: 50000,
  requests_this_month: 3500,
  requests_today: 150,
  errors_total: 125,
  errors_this_month: 5,
  average_response_time_ms: 125.5,
  estimated_cost_usd: 3.5,
  budget_remaining_usd: 46.5,
  last_used: '2024-01-15T10:30:00Z',
  first_used: '2024-01-01T00:00:00Z',
  monthly_reset_date: '2024-02-01T00:00:00Z',
};

jest.mock('../../hooks/useProviderManagement', () => ({
  useProviderManagement: () => ({
    providerStatuses: mockStatuses,
    selectedProvider: mockSelectedProvider,
    selectedProviderUsage: mockUsage,
    isLoadingStatus: false,
    isLoadingUsage: false,
    error: null,
    refreshAll: mockRefreshAll,
    fetchProviders: jest.fn(),
    fetchStatus: jest.fn(),
    fetchUsage: jest.fn(),
    clearError: jest.fn(),
  }),
}));

describe('StatusBar', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('Rendering', () => {
    it('should render provider information', () => {
      render(<StatusBar />);

      expect(screen.getByText('Automatikus')).toBeInTheDocument();
      expect(screen.getByText('🔄')).toBeInTheDocument();
    });

    it('should render status indicator', () => {
      render(<StatusBar />);

      expect(screen.getByText('✓')).toBeInTheDocument();
      expect(screen.getByText('Egészséges')).toBeInTheDocument();
    });

    it('should render request statistics', () => {
      render(<StatusBar />);

      expect(screen.getByText('Kérések:')).toBeInTheDocument();
    });

    it('should render usage percentage', () => {
      render(<StatusBar />);

      expect(screen.getByText('Használat:')).toBeInTheDocument();
    });

    it('should render cost when showCost is true', () => {
      render(<StatusBar showCost={true} />);

      expect(screen.getByText('Költség:')).toBeInTheDocument();
    });

    it('should not render cost when showCost is false', () => {
      render(<StatusBar showCost={false} />);

      expect(screen.queryByText('Költség:')).not.toBeInTheDocument();
    });

    it('should render last used timestamp', () => {
      render(<StatusBar />);

      expect(screen.getByText('Utolsó használat:')).toBeInTheDocument();
    });

    it('should render detailed usage stats when available', () => {
      render(<StatusBar />);

      expect(screen.getByText('Válaszidő:')).toBeInTheDocument();
      expect(screen.getByText('Hibaráta:')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(<StatusBar className="custom-class" />);

      expect(container.querySelector('.custom-class')).toBeInTheDocument();
    });
  });

  describe('Progress bar', () => {
    it('should render progress bar with correct width', () => {
      render(<StatusBar />);

      const progressBar = document.querySelector('[role="progressbar"]');
      expect(progressBar).toBeInTheDocument();
      expect(progressBar).toHaveAttribute('aria-valuenow', '35');
    });

    it('should have proper ARIA attributes', () => {
      render(<StatusBar />);

      const progressBar = document.querySelector('[role="progressbar"]');
      expect(progressBar).toHaveAttribute('aria-valuemin', '0');
      expect(progressBar).toHaveAttribute('aria-valuemax', '100');
    });
  });

  describe('Refresh functionality', () => {
    it('should render refresh button', () => {
      render(<StatusBar />);

      expect(screen.getByLabelText('Frissítés')).toBeInTheDocument();
    });

    it('should call refreshAll when clicking refresh button', () => {
      render(<StatusBar />);

      const refreshButton = screen.getByLabelText('Frissítés');
      fireEvent.click(refreshButton);

      expect(mockRefreshAll).toHaveBeenCalled();
    });

    it('should auto-refresh at specified interval', () => {
      render(<StatusBar refreshInterval={10000} />);

      expect(mockRefreshAll).not.toHaveBeenCalled();

      jest.advanceTimersByTime(10000);

      expect(mockRefreshAll).toHaveBeenCalled();
    });

    it('should not auto-refresh when interval is 0', () => {
      render(<StatusBar refreshInterval={0} />);

      jest.advanceTimersByTime(10000);

      expect(mockRefreshAll).not.toHaveBeenCalled();
    });
  });

  describe('Conditional rendering', () => {
    it('should not show provider name when showProviderName is false', () => {
      render(<StatusBar showProviderName={false} />);

      expect(screen.queryByText('Automatikus')).not.toBeInTheDocument();
    });

    it('should not show status when showStatus is false', () => {
      render(<StatusBar showStatus={false} />);

      expect(screen.queryByText('Egészséges')).not.toBeInTheDocument();
    });

    it('should not show details when showDetails is false', () => {
      render(<StatusBar showDetails={false} />);

      expect(screen.queryByText('Kérések:')).not.toBeInTheDocument();
      expect(screen.queryByText('Használat:')).not.toBeInTheDocument();
    });
  });
});
