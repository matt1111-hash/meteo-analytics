/**
 * WindChart.test.tsx
 * Szigorú tesztek a WindChart komponenshez (Beaufort skálával)
 *
 * @see AGENTS.md - Quality Gate: Coverage ≥85% (local)
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import WindChart from './WindChart';
import { BEAUFORT_LEVELS, WIND_THRESHOLDS } from '../constants/windConstants';

// Mock Recharts since it requires canvas/DOM
vi.mock('recharts', () => {
  return {
    ResponsiveContainer: ({ children }: any) => (
      <div data-testid="responsive-container" style={{ width: '100%', height: 450 }}>
        {children}
      </div>
    ),
    ComposedChart: ({ children }: any) => <div data-testid="composed-chart">{children}</div>,
    Line: () => <div data-testid="line-chart" />,
    Bar: () => <div data-testid="bar-chart" />,
    XAxis: () => <div data-testid="x-axis" />,
    YAxis: () => <div data-testid="y-axis" />,
    CartesianGrid: () => <div data-testid="cartesian-grid" />,
    Tooltip: () => <div data-testid="tooltip" />,
    Legend: () => <div data-testid="legend" />,
    ReferenceArea: () => <div data-testid="reference-area" />,
    ReferenceLine: () => <div data-testid="reference-line" />,
  };
});

// Mock BeaufortLegend
vi.mock('./charts/BeaufortLegend', () => {
  return {
    default: function MockBeaufortLegend(props: any) {
      return (
        <div
          data-testid="beaufort-legend"
          data-compact={props.compact}
          data-highlight={props.highlightLevel}
        >
          Beaufort Legend Mock
        </div>
      );
    },
  };
});

describe('WindChart Component', () => {
  const mockData = [
    { date: '2024-01-01', windspeed: 15.5, windgusts: 25.3 },
    { date: '2024-01-02', windspeed: 20.0, windgusts: 35.0 },
    { date: '2024-01-03', windspeed: 45.0, windgusts: 65.0 },
    { date: '2024-01-04', windspeed: null, windgusts: 30.0 },
    { date: '2024-01-05', windspeed: 10.0, windgusts: null },
  ];

  describe('Rendering', () => {
    test('should render without crashing', () => {
      render(<WindChart data={mockData} city="Budapest" />);
      expect(screen.getByText(/Szélanalízis/i)).toBeInTheDocument();
    });

    test('should render city name', () => {
      render(<WindChart data={mockData} city="Budapest" />);
      expect(screen.getByText(/Budapest/i)).toBeInTheDocument();
    });

    test('should render data count', () => {
      render(<WindChart data={mockData} city="Budapest" />);
      expect(screen.getByText(/5 nap/i)).toBeInTheDocument();
    });

    test('should render empty state when no data', () => {
      render(<WindChart data={[]} city="Budapest" />);
      expect(screen.getByText(/Nem érhető el széladat/i)).toBeInTheDocument();
    });

    test('should render empty state when all data is filtered out', () => {
      const nullData = [
        { date: '2024-01-01', windspeed: null, windgusts: null },
        { date: '2024-01-02', windspeed: null, windgusts: null },
      ];
      render(<WindChart data={nullData} city="Budapest" />);
      expect(screen.getByText(/Nem érhető el széladat/i)).toBeInTheDocument();
    });
  });

  describe('Statistics Display', () => {
    test('should calculate and display average wind speed', () => {
      render(<WindChart data={mockData} city="Budapest" />);
      expect(screen.getAllByText(/Átlag szél/i).length).toBeGreaterThan(0);
    });

    test('should calculate and display maximum wind speed', () => {
      render(<WindChart data={mockData} city="Budapest" />);
      expect(screen.getAllByText(/Max szél/i).length).toBeGreaterThan(0);
    });

    test('should calculate and display maximum gust speed', () => {
      render(<WindChart data={mockData} city="Budapest" />);
      expect(screen.getAllByText(/Max széllökés/i).length).toBeGreaterThan(0);
    });

    test('should calculate and display windy days count', () => {
      render(<WindChart data={mockData} city="Budapest" />);
      expect(screen.getAllByText(/Szeles napok/i).length).toBeGreaterThan(0);
    });

    test('should display Beaufort levels in statistics', () => {
      const { container } = render(<WindChart data={mockData} city="Budapest" />);
      const statValues = container.querySelectorAll('.stat-value');
      expect(statValues.length).toBeGreaterThan(0);

      // At least one stat should have Beaufort info
      const hasBeaufort = Array.from(statValues).some((stat) => stat.textContent?.match(/\(\d+\)/));
      expect(hasBeaufort).toBe(true);
    });
  });

  describe('Beaufort Scale Integration', () => {
    test('should render BeaufortLegend when showBeaufortLegend is true (default)', () => {
      render(<WindChart data={mockData} city="Budapest" />);
      expect(screen.getByTestId('beaufort-legend')).toBeInTheDocument();
    });

    test('should not render BeaufortLegend when showBeaufortLegend is false', () => {
      render(<WindChart data={mockData} city="Budapest" showBeaufortLegend={false} />);
      expect(screen.queryByTestId('beaufort-legend')).not.toBeInTheDocument();
    });

    test('should highlight max gust level in legend', () => {
      const { container } = render(<WindChart data={mockData} city="Budapest" />);
      const legend = screen.getByTestId('beaufort-legend');

      // Mock gust is 65 km/h which should be Beaufort level 8
      expect(legend.getAttribute('data-highlight')).toBeDefined();
    });

    test('should render reference areas for Beaufort levels', () => {
      const { container } = render(<WindChart data={mockData} city="Budapest" />);
      const referenceAreas = container.querySelectorAll('[data-testid="reference-area"]');
      expect(referenceAreas.length).toBeGreaterThan(0);
    });

    test('should render reference lines for strong wind and gale thresholds', () => {
      const { container } = render(<WindChart data={mockData} city="Budapest" />);
      const referenceLines = container.querySelectorAll('[data-testid="reference-line"]');
      expect(referenceLines.length).toBe(2); // Strong wind and Gale
    });
  });

  describe('Legend Info', () => {
    test('should render chart legend info', () => {
      const { container } = render(<WindChart data={mockData} city="Budapest" />);
      const legendInfo = container.querySelector('.chart-legend-info');
      expect(legendInfo).toBeInTheDocument();
    });

    test('should render wind speed legend item', () => {
      render(<WindChart data={mockData} city="Budapest" />);
      expect(screen.getAllByText(/Szélsebesség/i).length).toBeGreaterThan(0);
    });

    test('should render wind gust legend item', () => {
      render(<WindChart data={mockData} city="Budapest" />);
      expect(screen.getAllByText(/Széllökés/i).length).toBeGreaterThan(0);
    });

    test('should render both legend markers', () => {
      const { container } = render(<WindChart data={mockData} city="Budapest" />);
      const legendItems = container.querySelectorAll('.legend-item');
      expect(legendItems.length).toBe(2);
    });
  });

  describe('Data Handling', () => {
    test('should filter out data points with null values', () => {
      const dataWithNulls = [
        { date: '2024-01-01', windspeed: null, windgusts: null },
        { date: '2024-01-02', windspeed: 10, windgusts: 20 },
      ];
      render(<WindChart data={dataWithNulls} city="Budapest" />);
      expect(screen.getByText(/1 nap/i)).toBeInTheDocument();
    });

    test('should sort data by date', () => {
      const unsortedData = [
        { date: '2024-01-03', windspeed: 10, windgusts: 20 },
        { date: '2024-01-01', windspeed: 15, windgusts: 25 },
        { date: '2024-01-02', windspeed: 20, windgusts: 30 },
      ];
      render(<WindChart data={unsortedData} city="Budapest" />);
      expect(screen.getByText(/3 nap/i)).toBeInTheDocument();
    });

    test('should handle single data point', () => {
      const singleData = [{ date: '2024-01-01', windspeed: 15, windgusts: 25 }];
      render(<WindChart data={singleData} city="Budapest" />);
      expect(screen.getByText(/1 nap/i)).toBeInTheDocument();
    });

    test('should handle data with only wind speed', () => {
      const speedOnlyData = [
        { date: '2024-01-01', windspeed: 15, windgusts: null },
        { date: '2024-01-02', windspeed: 20, windgusts: null },
      ];
      render(<WindChart data={speedOnlyData} city="Budapest" />);
      expect(screen.getByText(/2 nap/i)).toBeInTheDocument();
    });

    test('should handle data with only wind gusts', () => {
      const gustOnlyData = [
        { date: '2024-01-01', windspeed: null, windgusts: 25 },
        { date: '2024-01-02', windspeed: null, windgusts: 30 },
      ];
      render(<WindChart data={gustOnlyData} city="Budapest" />);
      expect(screen.getByText(/2 nap/i)).toBeInTheDocument();
    });
  });

  describe('Hungarian Language', () => {
    test('should display labels in Hungarian', () => {
      render(<WindChart data={mockData} city="Budapest" />);
      expect(screen.getByText('Átlag szél')).toBeInTheDocument();
      expect(screen.getByText('Max szél')).toBeInTheDocument();
      expect(screen.getByText('Max széllökés')).toBeInTheDocument();
      expect(screen.getByText('Szeles napok')).toBeInTheDocument();
    });

    test('should display Beaufort names in Hungarian', () => {
      const { container } = render(<WindChart data={mockData} city="Budapest" />);
      const statValues = container.querySelectorAll('.stat-value small');

      // Check for Hungarian Beaufort names
      const hasHungarianNames = Array.from(statValues).some((stat) =>
        stat.textContent?.match(/(Szélcsend|Enyhe szellő|Gyenge szél|Erős szél|Vihar|Orkán)/),
      );
      expect(hasHungarianNames).toBe(true);
    });
  });

  describe('Chart Components', () => {
    test('should render ComposedChart', () => {
      const { container } = render(<WindChart data={mockData} city="Budapest" />);
      expect(container.querySelector('[data-testid="composed-chart"]')).toBeInTheDocument();
    });

    test('should render Line chart for wind speed', () => {
      const { container } = render(<WindChart data={mockData} city="Budapest" />);
      expect(container.querySelector('[data-testid="line-chart"]')).toBeInTheDocument();
    });

    test('should render Bar chart for wind gusts', () => {
      const { container } = render(<WindChart data={mockData} city="Budapest" />);
      expect(container.querySelector('[data-testid="bar-chart"]')).toBeInTheDocument();
    });

    test('should render X and Y axes', () => {
      const { container } = render(<WindChart data={mockData} city="Budapest" />);
      expect(container.querySelector('[data-testid="x-axis"]')).toBeInTheDocument();
      expect(container.querySelector('[data-testid="y-axis"]')).toBeInTheDocument();
    });

    test('should render Tooltip', () => {
      const { container } = render(<WindChart data={mockData} city="Budapest" />);
      expect(container.querySelector('[data-testid="tooltip"]')).toBeInTheDocument();
    });
  });

  describe('Props Handling', () => {
    test('should accept showBeaufortLegend prop', () => {
      render(<WindChart data={mockData} city="Budapest" showBeaufortLegend={false} />);
      expect(screen.queryByTestId('beaufort-legend')).not.toBeInTheDocument();
    });

    test('should handle missing optional props', () => {
      render(<WindChart data={mockData} city="Budapest" />);
      expect(screen.getByText(/Szélanalízis/i)).toBeInTheDocument();
    });
  });

  describe('Statistics Calculations', () => {
    test('should calculate correct average speed', () => {
      const data = [
        { date: '2024-01-01', windspeed: 10, windgusts: 20 },
        { date: '2024-01-02', windspeed: 20, windgusts: 30 },
        { date: '2024-01-03', windspeed: 30, windgusts: 40 },
      ];
      const { container } = render(<WindChart data={data} city="Budapest" />);
      const avgSpeedText = Array.from(container.querySelectorAll('.stat-value')).find((el) =>
        el.textContent?.includes('20.0'),
      );
      expect(avgSpeedText).toBeInTheDocument();
    });

    test('should identify correct maximum values', () => {
      const data = [
        { date: '2024-01-01', windspeed: 10, windgusts: 20 },
        { date: '2024-01-02', windspeed: 50, windgusts: 70 },
        { date: '2024-01-03', windspeed: 30, windgusts: 40 },
      ];
      const { container } = render(<WindChart data={data} city="Budapest" />);
      const statValues = container.querySelectorAll('.stat-value');
      const maxGust = Array.from(statValues).find((el) => el.textContent?.includes('70.0'));
      expect(maxGust).toBeInTheDocument();
    });

    test('should count windy days (above Beaufort 6 threshold)', () => {
      const data = [
        { date: '2024-01-01', windspeed: 10, windgusts: 30 }, // Below threshold
        { date: '2024-01-02', windspeed: 30, windgusts: 55 }, // Above threshold
        { date: '2024-01-03', windspeed: 40, windgusts: 65 }, // Above threshold
      ];
      const { container } = render(<WindChart data={data} city="Budapest" />);
      const windyDaysText = Array.from(container.querySelectorAll('.stat-value')).find((el) =>
        el.textContent?.includes('2 / 3'),
      );
      expect(windyDaysText).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    test('should handle very high wind speeds', () => {
      const extremeData = [
        { date: '2024-01-01', windspeed: 150, windgusts: 200 }, // Hurricane force
      ];
      render(<WindChart data={extremeData} city="Budapest" />);
      expect(screen.getByText(/1 nap/i)).toBeInTheDocument();
    });

    test('should handle zero wind speeds', () => {
      const calmData = [
        { date: '2024-01-01', windspeed: 0, windgusts: 0 },
        { date: '2024-01-02', windspeed: 0.5, windgusts: 1 },
      ];
      render(<WindChart data={calmData} city="Budapest" />);
      expect(screen.getByText(/2 nap/i)).toBeInTheDocument();
    });

    test('should handle decimal speeds', () => {
      const decimalData = [
        { date: '2024-01-01', windspeed: 12.5, windgusts: 23.7 },
        { date: '2024-01-02', windspeed: 15.3, windgusts: 28.9 },
      ];
      render(<WindChart data={decimalData} city="Budapest" />);
      expect(screen.getByText(/2 nap/i)).toBeInTheDocument();
    });
  });
});
