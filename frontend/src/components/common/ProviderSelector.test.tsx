/**
 * ProviderSelector Component Tests
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ProviderSelector } from './ProviderSelector';
import * as providerService from '../../services/providerService';

// Mock the providerService
jest.mock('../../services/providerService');
jest.mock('../../hooks/useProviderManagement', () => ({
  useProviderManagement: () => ({
    providers: mockProviders,
    providerStatuses: mockStatuses,
    selectedProvider: mockProviders[0],
    selectProvider: mockSelectProvider,
    isLoadingProviders: false,
    isSelecting: false,
    error: null,
    clearError: jest.fn(),
    fetchProviders: jest.fn(),
    fetchStatus: jest.fn(),
    fetchUsage: jest.fn(),
    refreshAll: jest.fn(),
  }),
}));

const mockSelectProvider = jest.fn().mockResolvedValue(true);

const mockProviders = [
  {
    provider_id: 'auto',
    name: 'Automatikus',
    description: 'Intelligens útválasztás',
    icon: '🔄',
    cost: 'Ingyenes',
    limitations: [],
    features: ['Smart routing', 'Cost optimization'],
    routing_logic: {},
  },
  {
    provider_id: 'open-meteo',
    name: 'Open-Meteo',
    description: 'Ingyenes időjárás API',
    icon: '🌤️',
    cost: 'Ingyenes',
    limitations: ['Nincs történelmi adat'],
    features: ['Free tier', 'No API key'],
    routing_logic: {},
  },
  {
    provider_id: 'meteostat',
    name: 'Meteostat',
    description: 'Prémium időjárás adatok',
    icon: '📊',
    cost: '$10 USD/hónap',
    limitations: [],
    features: ['Historical data', 'High accuracy'],
    routing_logic: {},
  },
];

const mockStatuses = [
  {
    provider_id: 'auto',
    name: 'Automatikus',
    status: 'healthy' as const,
    is_selected: true,
    usage_percentage: 0.0,
    requests_this_month: 0,
    monthly_limit: null,
    estimated_cost_usd: 0.0,
    last_used: null,
  },
  {
    provider_id: 'open-meteo',
    name: 'Open-Meteo',
    status: 'healthy' as const,
    is_selected: false,
    usage_percentage: 0.15,
    requests_this_month: 1500,
    monthly_limit: 10000,
    estimated_cost_usd: 0.0,
    last_used: '2024-01-15T10:30:00Z',
  },
  {
    provider_id: 'meteostat',
    name: 'Meteostat',
    status: 'warning' as const,
    is_selected: false,
    usage_percentage: 0.85,
    requests_this_month: 8500,
    monthly_limit: 10000,
    estimated_cost_usd: 8.5,
    last_used: '2024-01-15T09:45:00Z',
  },
];

describe('ProviderSelector', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the trigger button with current provider', () => {
      render(<ProviderSelector />);

      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Adatszolgáltató: Automatikus');
    });

    it('should render custom label when provided', () => {
      render(<ProviderSelector label="Válasszon szolgáltatót" />);

      expect(screen.getByText('Válasszon szolgáltatót')).toBeInTheDocument();
    });

    it('should display provider icon in trigger', () => {
      render(<ProviderSelector />);

      expect(screen.getByText('🔄')).toBeInTheDocument();
    });

    it('should display status indicator when showStatus is true', () => {
      render(<ProviderSelector showStatus={true} />);

      const statusIndicator = screen.getByText('✓');
      expect(statusIndicator).toBeInTheDocument();
      expect(statusIndicator).toHaveStyle({ color: '#22c55e' });
    });

    it('should not display status indicator when showStatus is false', () => {
      render(<ProviderSelector showStatus={false} />);

      expect(screen.queryByText('✓')).not.toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(<ProviderSelector className="custom-class" />);

      expect(container.querySelector('.custom-class')).toBeInTheDocument();
    });

    it('should be disabled when disabled prop is true', () => {
      render(<ProviderSelector disabled={true} />);

      expect(screen.getByRole('button')).toBeDisabled();
    });
  });

  describe('Dropdown interaction', () => {
    it('should open dropdown on click', () => {
      render(<ProviderSelector />);

      const trigger = screen.getByRole('button');
      fireEvent.click(trigger);

      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    it('should close dropdown when clicking trigger again', () => {
      render(<ProviderSelector />);

      const trigger = screen.getByRole('button');
      fireEvent.click(trigger);
      fireEvent.click(trigger);

      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
    });

    it('should display all providers in dropdown', () => {
      render(<ProviderSelector />);

      fireEvent.click(screen.getByRole('button'));

      expect(screen.getByText('Automatikus')).toBeInTheDocument();
      expect(screen.getByText('Open-Meteo')).toBeInTheDocument();
      expect(screen.getByText('Meteostat')).toBeInTheDocument();
    });

    it('should display provider description', () => {
      render(<ProviderSelector />);

      fireEvent.click(screen.getByRole('button'));

      expect(screen.getByText('Intelligens útválasztás')).toBeInTheDocument();
    });

    it('should display cost when showCost is true', () => {
      render(<ProviderSelector showCost={true} />);

      fireEvent.click(screen.getByRole('button'));

      expect(screen.getByText('Ingyenes')).toBeInTheDocument();
      expect(screen.getByText('$10 USD/hónap')).toBeInTheDocument();
    });

    it('should display usage for providers with limits', () => {
      render(<ProviderSelector />);

      fireEvent.click(screen.getByRole('button'));

      expect(screen.getByText(/85% használva/)).toBeInTheDocument();
    });

    it('should display checkmark for selected provider', () => {
      render(<ProviderSelector />);

      fireEvent.click(screen.getByRole('button'));

      const checkmarks = screen.getAllByText('✓');
      expect(checkmarks.length).toBeGreaterThan(0);
    });

    it('should highlight provider on mouse enter', () => {
      render(<ProviderSelector />);

      fireEvent.click(screen.getByRole('button'));

      const options = screen.getAllByRole('option');
      fireEvent.mouseEnter(options[1]);

      expect(options[1]).toHaveClass('highlighted');
    });
  });

  describe('Provider selection', () => {
    it('should call selectProvider when clicking an option', async () => {
      render(<ProviderSelector />);

      fireEvent.click(screen.getByRole('button'));

      const meteostatOption = screen.getByText('Meteostat').closest('[role="option"]');
      fireEvent.click(meteostatOption!);

      await waitFor(() => {
        expect(mockSelectProvider).toHaveBeenCalledWith('meteostat');
      });
    });

    it('should call onChange callback when provider is selected', async () => {
      const onChange = jest.fn();
      render(<ProviderSelector onChange={onChange} />);

      fireEvent.click(screen.getByRole('button'));

      const openMeteoOption = screen.getAllByText('Open-Meteo')[0].closest('[role="option"]');
      fireEvent.click(openMeteoOption!);

      await waitFor(() => {
        expect(onChange).toHaveBeenCalledWith('open-meteo');
      });
    });

    it('should close dropdown after selection', async () => {
      render(<ProviderSelector />);

      fireEvent.click(screen.getByRole('button'));
      expect(screen.getByRole('listbox')).toBeInTheDocument();

      const option = screen.getByText('Open-Meteo').closest('[role="option"]');
      fireEvent.click(option!);

      await waitFor(() => {
        expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
      });
    });

    it('should not allow selection when disabled', () => {
      render(<ProviderSelector disabled={true} />);

      fireEvent.click(screen.getByRole('button'));
      const option = screen.getByText('Open-Meteo').closest('[role="option"]');
      fireEvent.click(option!);

      expect(mockSelectProvider).not.toHaveBeenCalled();
    });
  });

  describe('Keyboard navigation', () => {
    it('should open dropdown on Arrow Down when closed', () => {
      render(<ProviderSelector />);

      const trigger = screen.getByRole('button');
      fireEvent.keyDown(trigger, { key: 'ArrowDown' });

      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    it('should navigate down on Arrow Down when open', () => {
      render(<ProviderSelector />);

      fireEvent.click(screen.getByRole('button'));

      const trigger = screen.getByRole('button');
      fireEvent.keyDown(trigger, { key: 'ArrowDown' });
      fireEvent.keyDown(trigger, { key: 'ArrowDown' });

      const options = screen.getAllByRole('option');
      expect(options[1]).toHaveClass('highlighted');
    });

    it('should navigate up on Arrow Up', () => {
      render(<ProviderSelector />);

      fireEvent.click(screen.getByRole('button'));

      const trigger = screen.getByRole('button');
      fireEvent.keyDown(trigger, { key: 'ArrowDown' });
      fireEvent.keyDown(trigger, { key: 'ArrowDown' });
      fireEvent.keyDown(trigger, { key: 'ArrowUp' });

      const options = screen.getAllByRole('option');
      expect(options[0]).toHaveClass('highlighted');
    });

    it('should select provider on Enter when highlighted', async () => {
      render(<ProviderSelector />);

      fireEvent.click(screen.getByRole('button'));

      const trigger = screen.getByRole('button');
      fireEvent.keyDown(trigger, { key: 'ArrowDown' });
      fireEvent.keyDown(trigger, { key: 'Enter' });

      await waitFor(() => {
        expect(mockSelectProvider).toHaveBeenCalled();
      });
    });

    it('should close dropdown on Escape', () => {
      render(<ProviderSelector />);

      fireEvent.click(screen.getByRole('button'));

      const trigger = screen.getByRole('button');
      fireEvent.keyDown(trigger, { key: 'Escape' });

      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
    });

    it('should close dropdown on Tab', () => {
      render(<ProviderSelector />);

      fireEvent.click(screen.getByRole('button'));

      const trigger = screen.getByRole('button');
      fireEvent.keyDown(trigger, { key: 'Tab' });

      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes on trigger', () => {
      render(<ProviderSelector />);

      const trigger = screen.getByRole('button');
      expect(trigger).toHaveAttribute('aria-haspopup', 'listbox');
      expect(trigger).toHaveAttribute('aria-expanded', 'false');
    });

    it('should update aria-expanded when dropdown opens', () => {
      render(<ProviderSelector />);

      const trigger = screen.getByRole('button');
      fireEvent.click(trigger);

      expect(trigger).toHaveAttribute('aria-expanded', 'true');
    });

    it('should have aria-label on listbox', () => {
      render(<ProviderSelector />);

      fireEvent.click(screen.getByRole('button'));

      expect(screen.getByRole('listbox')).toHaveAttribute('aria-label', 'Adatszolgáltató lehetőségek');
    });

    it('should have aria-selected on options', () => {
      render(<ProviderSelector />);

      fireEvent.click(screen.getByRole('button'));

      const options = screen.getAllByRole('option');
      const selectedOption = options.find(opt => opt.getAttribute('aria-selected') === 'true');
      expect(selectedOption).toBeInTheDocument();
    });
  });

  describe('Controlled mode', () => {
    it('should use controlled value when provided', () => {
      render(<ProviderSelector value="meteostat" />);

      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Adatszolgáltató: Meteostat');
    });

    it('should display controlled provider in trigger', () => {
      render(<ProviderSelector value="open-meteo" />);

      expect(screen.getByText('Open-Meteo')).toBeInTheDocument();
    });
  });
});
