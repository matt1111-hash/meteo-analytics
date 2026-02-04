/**
 * HierarchicalSelector.test.tsx
 * Szigorú tesztek a HierarchicalSelector komponenshez
 *
 * @see AGENTS.md - Quality Gate: Coverage ≥85% (local)
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import HierarchicalSelector from './HierarchicalSelector';
import { SelectedLocation } from './HierarchicalSelector';

// Mock the HungaryService module
jest.mock('../../services/hungaryService', () => ({
  getHungarianRegions: jest.fn(),
  getHungarianCounties: jest.fn(),
  getHungarianSettlements: jest.fn(),
}));

import {
  getHungarianRegions,
  getHungarianCounties,
  getHungarianSettlements,
} from '../../services/hungaryService';

const mockGetHungarianRegions = getHungarianRegions as jest.MockedFunction<
  typeof getHungarianRegions
>;
const mockGetHungarianCounties = getHungarianCounties as jest.MockedFunction<
  typeof getHungarianCounties
>;
const mockGetHungarianSettlements = getHungarianSettlements as jest.MockedFunction<
  typeof getHungarianSettlements
>;

// Mock API responses
const MOCK_REGIONS = {
  count: 7,
  regions: [
    'Közép-Magyarország',
    'Észak-Magyarország',
    'Észak-Alföld',
    'Dél-Alföld',
    'Dél-Dunántúl',
    'Nyugat-Dunántúl',
    'Közép-Dunántúl',
  ],
};

const MOCK_COUNTIES = {
  count: 20,
  counties: [
    'Budapest',
    'Pest',
    'Fejér',
    'Komárom-Esztergom',
    'Veszprém',
    'Győr-Moson-Sopron',
    'Vas',
    'Zala',
    'Baranya',
    'Somogy',
    'Tolna',
    'Borsod-Abaúj-Zemplén',
    'Heves',
    'Nógrád',
    'Hajdú-Bihar',
    'Jász-Nagykun-Szolnok',
    'Szabolcs-Szatmár-Bereg',
    'Bács-Kiskun',
    'Békés',
    'Csongrád-Csanád',
  ],
};

const MOCK_SETTLEMENTS = {
  count: 2,
  filter: { county: 'Pest', settlement_type: null },
  settlements: [
    {
      name: 'Budakalász',
      county: 'Pest',
      settlement_type: 'város',
      coordinates: { lat: 47.55, lon: 19.05 },
      population: 12000,
      region_priority: 1,
    },
    {
      name: 'Érd',
      county: 'Pest',
      settlement_type: 'város',
      coordinates: { lat: 47.38, lon: 18.91 },
      population: 75000,
      region_priority: 1,
    },
  ],
};

describe('HierarchicalSelector Component', () => {
  let mockOnLocationSelect: jest.MockedFunction<(location: SelectedLocation) => void>;

  beforeEach(() => {
    mockOnLocationSelect = jest.fn();
    jest.clearAllMocks();

    mockGetHungarianRegions.mockResolvedValue(MOCK_REGIONS);
    mockGetHungarianCounties.mockResolvedValue(MOCK_COUNTIES);
    mockGetHungarianSettlements.mockResolvedValue(MOCK_SETTLEMENTS);
  });

  describe('Rendering', () => {
    test('should render without crashing', async () => {
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      expect(await screen.findByText(/Magyarországi településválasztó/i)).toBeInTheDocument();
    });

    test('should render title and subtitle', async () => {
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      expect(await screen.findByText('Magyarországi településválasztó')).toBeInTheDocument();
      expect(screen.getByText(/Válassz régiót, majd megyét és végül települést/i)).toBeInTheDocument();
    });

    test('should render all three select dropdowns', async () => {
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      expect(await screen.findByLabelText('Régió')).toBeInTheDocument();
      expect(screen.getByLabelText('Megye')).toBeInTheDocument();
      expect(screen.getByLabelText('Település')).toBeInTheDocument();
    });

    test('should have base CSS class', () => {
      const { container } = render(
        <HierarchicalSelector onLocationSelect={mockOnLocationSelect} />
      );
      expect(container.querySelector('.hierarchical-selector')).toBeInTheDocument();
    });

    test('should add custom className when provided', () => {
      const { container } = render(
        <HierarchicalSelector onLocationSelect={mockOnLocationSelect} className="custom-class" />
      );
      const selector = container.querySelector('.hierarchical-selector');
      expect(selector?.classList.contains('custom-class')).toBe(true);
    });
  });

  describe('Region Selection', () => {
    test('should load regions on mount', async () => {
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      await waitFor(() => {
        expect(mockGetHungarianRegions).toHaveBeenCalledTimes(1);
      });
    });

    test('should display all 7 Hungarian regions', async () => {
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      await screen.findByLabelText('Régió');
      MOCK_REGIONS.regions.forEach((region) => {
        expect(screen.getByText(region)).toBeInTheDocument();
      });
    });
  });

  describe('County Selection', () => {
    test('should be disabled until region is selected', async () => {
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      await screen.findByLabelText('Régió');
      const countySelect = screen.getByLabelText('Megye');
      expect(countySelect).toBeDisabled();
    });

    test('should load counties when region is selected', async () => {
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      const regionSelect = await screen.findByLabelText('Régió');
      fireEvent.change(regionSelect, { target: { value: 'Közép-Magyarország' } });
      await waitFor(() => {
        expect(mockGetHungarianCounties).toHaveBeenCalled();
      });
    });
  });

  describe('Settlement Selection', () => {
    test('should be disabled until county is selected', async () => {
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      await screen.findByLabelText('Régió');
      const settlementSelect = screen.getByLabelText('Település');
      expect(settlementSelect).toBeDisabled();
    });

    test('should load settlements when county is selected', async () => {
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      const regionSelect = await screen.findByLabelText('Régió');
      fireEvent.change(regionSelect, { target: { value: 'Közép-Magyarország' } });
      await screen.findByText('Pest');
      const countySelect = screen.getByLabelText('Megye');
      fireEvent.change(countySelect, { target: { value: 'Pest' } });
      await waitFor(() => {
        expect(mockGetHungarianSettlements).toHaveBeenCalledWith({
          county: 'Pest',
          limit: 500,
        });
      });
    });
  });

  describe('Location Selection Callback', () => {
    test('should call onLocationSelect with correct data', async () => {
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      const regionSelect = await screen.findByLabelText('Régió');
      fireEvent.change(regionSelect, { target: { value: 'Közép-Magyarország' } });
      await screen.findByText('Pest');
      const countySelect = screen.getByLabelText('Megye');
      fireEvent.change(countySelect, { target: { value: 'Pest' } });
      await screen.findByText('Érd');
      const settlementSelect = screen.getByLabelText('Település');
      fireEvent.change(settlementSelect, { target: { value: 'Érd' } });
      await waitFor(() => {
        expect(mockOnLocationSelect).toHaveBeenCalledWith({
          region: 'Közép-Magyarország',
          county: 'Pest',
          settlement: 'Érd',
          coordinates: { lat: 47.38, lon: 18.91 },
          population: 75000,
        });
      });
    });

    test('should include coordinates when available', async () => {
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      const regionSelect = await screen.findByLabelText('Régió');
      fireEvent.change(regionSelect, { target: { value: 'Közép-Magyarország' } });
      await screen.findByText('Pest');
      const countySelect = screen.getByLabelText('Megye');
      fireEvent.change(countySelect, { target: { value: 'Pest' } });
      await screen.findByText('Budakalász');
      const settlementSelect = screen.getByLabelText('Település');
      fireEvent.change(settlementSelect, { target: { value: 'Budakalász' } });
      await waitFor(() => {
        expect(mockOnLocationSelect).toHaveBeenCalled();
        const callArgs = mockOnLocationSelect.mock.calls[0][0];
        expect(callArgs.coordinates).toEqual({ lat: 47.55, lon: 19.05 });
      });
    });

    test('should include population when available', async () => {
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      const regionSelect = await screen.findByLabelText('Régió');
      fireEvent.change(regionSelect, { target: { value: 'Közép-Magyarország' } });
      await screen.findByText('Pest');
      const countySelect = screen.getByLabelText('Megye');
      fireEvent.change(countySelect, { target: { value: 'Pest' } });
      await screen.findByText('Érd');
      const settlementSelect = screen.getByLabelText('Település');
      fireEvent.change(settlementSelect, { target: { value: 'Érd' } });
      await waitFor(() => {
        expect(mockOnLocationSelect).toHaveBeenCalled();
        const callArgs = mockOnLocationSelect.mock.calls[0][0];
        expect(callArgs.population).toBe(75000);
      });
    });
  });

  describe('Disabled State', () => {
    test('should disable all selects when disabled prop is true', () => {
      const { container } = render(
        <HierarchicalSelector onLocationSelect={mockOnLocationSelect} disabled={true} />
      );
      const regionSelect = screen.getByLabelText('Régió');
      expect(regionSelect).toBeDisabled();
    });

    test('should not disable when disabled prop is false', async () => {
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} disabled={false} />);
      const regionSelect = await screen.findByLabelText('Régió');
      expect(regionSelect).not.toBeDisabled();
    });
  });

  describe('Error Handling', () => {
    test('should display error when region API fails', async () => {
      mockGetHungarianRegions.mockRejectedValue(new Error('API Error'));
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      expect(await screen.findByText(/Nem sikerült betölteni a régiókat/i)).toBeInTheDocument();
    });

    test('should display error when county API fails', async () => {
      mockGetHungarianCounties.mockRejectedValue(new Error('API Error'));
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      const regionSelect = await screen.findByLabelText('Régió');
      fireEvent.change(regionSelect, { target: { value: 'Közép-Magyarország' } });
      expect(await screen.findByText(/Nem sikerült betölteni a megyéket/i)).toBeInTheDocument();
    });

    test('should display error when settlement API fails', async () => {
      mockGetHungarianSettlements.mockRejectedValue(new Error('API Error'));
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      const regionSelect = await screen.findByLabelText('Régió');
      fireEvent.change(regionSelect, { target: { value: 'Közép-Magyarország' } });
      await screen.findByText('Pest');
      const countySelect = screen.getByLabelText('Megye');
      fireEvent.change(countySelect, { target: { value: 'Pest' } });
      expect(await screen.findByText(/Nem sikerült betölteni a településeket/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('should have proper labels for all selects', async () => {
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      expect(await screen.findByLabelText('Régió')).toBeInTheDocument();
      expect(screen.getByLabelText('Megye')).toBeInTheDocument();
      expect(screen.getByLabelText('Település')).toBeInTheDocument();
    });

    test('should have disabled attribute on disabled selects', async () => {
      render(<HierarchicalSelector onLocationSelect={mockOnLocationSelect} />);
      await screen.findByLabelText('Régió');
      const countySelect = screen.getByLabelText('Megye');
      expect(countySelect).toBeDisabled();
      const settlementSelect = screen.getByLabelText('Település');
      expect(settlementSelect).toBeDisabled();
    });
  });
});
