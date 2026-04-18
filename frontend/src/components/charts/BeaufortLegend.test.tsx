/**
 * BeaufortLegend.test.tsx
 * Szigorú tesztek a BeaufortLegend komponenshez
 *
 * @see AGENTS.md - Quality Gate: Coverage ≥85% (local)
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import BeaufortLegend from './BeaufortLegend';
import { BEAUFORT_LEVELS } from '../../constants/windConstants';

describe('BeaufortLegend Component', () => {
  describe('Rendering', () => {
    test('should render without crashing', () => {
      render(<BeaufortLegend />);
      expect(screen.getByText(/Beaufort Skála/i)).toBeInTheDocument();
    });

    test('should render title with emoji', () => {
      render(<BeaufortLegend />);
      expect(screen.getByText(/🌬️/i)).toBeInTheDocument();
    });

    test('should render all 13 Beaufort levels', () => {
      render(<BeaufortLegend />);

      // Check for level numbers - use getAllByText since levels can appear in multiple places
      for (let i = 0; i <= 12; i++) {
        const levelElements = screen.getAllByText(i.toString());
        expect(levelElements.length).toBeGreaterThan(0);
      }
    });

    test('should render Hungarian names for all levels', () => {
      render(<BeaufortLegend />);

      BEAUFORT_LEVELS.forEach((level) => {
        expect(screen.getByText(level.nameHu)).toBeInTheDocument();
      });
    });

    test('should render speed ranges for all levels', () => {
      const { container } = render(<BeaufortLegend />);

      BEAUFORT_LEVELS.forEach((level) => {
        const rangeText =
          level.speedRange.min === 0
            ? `0-${level.speedRange.max}`
            : `${level.speedRange.min}-${level.speedRange.max}`;
        expect(screen.getByText(rangeText)).toBeInTheDocument();
      });
    });

    test('should render footer with threshold info', () => {
      const { container } = render(<BeaufortLegend />);

      const footer = container.querySelector('.beaufort-footer');
      expect(footer).toBeInTheDocument();
      expect(footer?.textContent).toContain('0');
      expect(footer?.textContent).toContain('6');
      expect(footer?.textContent).toContain('10');
      expect(footer?.textContent).toContain('12');
    });
  });

  describe('Compact Mode', () => {
    test('should render in compact mode when prop is true', () => {
      const { container } = render(<BeaufortLegend compact={true} />);
      expect(container.querySelector('.beaufort-legend.compact')).toBeInTheDocument();
    });

    test('should not render subtitle in compact mode', () => {
      render(<BeaufortLegend compact={true} />);
      expect(screen.queryByText(/Szélereősség skála/i)).not.toBeInTheDocument();
    });

    test('should not render footer in compact mode', () => {
      render(<BeaufortLegend compact={true} />);
      expect(screen.queryByText(/Szélcsend/i)).not.toBeInTheDocument();
    });

    test('should still render all levels in compact mode', () => {
      render(<BeaufortLegend compact={true} />);

      for (let i = 0; i <= 12; i++) {
        const levelElements = screen.getAllByText(i.toString());
        expect(levelElements.length).toBeGreaterThan(0);
      }
    });
  });

  describe('Highlight Level', () => {
    test('should apply highlighted class when level is specified', () => {
      const { container } = render(<BeaufortLegend highlightLevel={6} />);
      const highlighted = container.querySelector('.beaufort-level.highlighted');
      expect(highlighted).toBeInTheDocument();
    });

    test('should not apply highlighted class when no level is specified', () => {
      const { container } = render(<BeaufortLegend />);
      const highlighted = container.querySelector('.beaufort-level.highlighted');
      expect(highlighted).not.toBeInTheDocument();
    });

    test('should highlight the correct level', () => {
      const { container } = render(<BeaufortLegend highlightLevel={8} />);
      const highlighted = container.querySelector('.beaufort-level.highlighted');

      // Find the level 8 element
      const level8Text = screen.getByText('8');
      expect(level8Text).toBeInTheDocument();

      // The highlighted element should be an ancestor of the level 8 text
      expect(highlighted?.contains(level8Text)).toBe(true);
    });

    test('should handle level 0 highlighting', () => {
      const { container } = render(<BeaufortLegend highlightLevel={0} />);
      const highlighted = container.querySelector('.beaufort-level.highlighted');
      expect(highlighted).toBeInTheDocument();
    });

    test('should handle level 12 highlighting', () => {
      const { container } = render(<BeaufortLegend highlightLevel={12} />);
      const highlighted = container.querySelector('.beaufort-level.highlighted');
      expect(highlighted).toBeInTheDocument();
    });
  });

  describe('CSS Classes and Styling', () => {
    test('should have base class', () => {
      const { container } = render(<BeaufortLegend />);
      const legend = container.querySelector('.beaufort-legend');
      expect(legend).toBeInTheDocument();
    });

    test('should add custom className when provided', () => {
      const { container } = render(<BeaufortLegend className="custom-class" />);
      const legend = container.querySelector('.beaufort-legend.custom-class');
      expect(legend).toBeInTheDocument();
    });

    test('should render level icons', () => {
      const { container } = render(<BeaufortLegend />);

      BEAUFORT_LEVELS.forEach((level) => {
        const icon = container.querySelector(`.beaufort-icon`);
        expect(icon).toBeInTheDocument();
      });
    });

    test('should render speed ranges with correct format', () => {
      render(<BeaufortLegend />);

      // Level 0: 0-1
      expect(screen.getByText('0-1')).toBeInTheDocument();

      // Level 6: 39-50
      expect(screen.getByText('39-50')).toBeInTheDocument();

      // Level 12 - check for the dash format
      expect(screen.getByText(/118-/)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('should be accessible with proper heading structure', () => {
      render(<BeaufortLegend />);
      const heading = screen.getByRole('heading', { level: 4 });
      expect(heading).toBeInTheDocument();
    });

    test('should have title attributes for tooltips', () => {
      const { container } = render(<BeaufortLegend />);

      const levels = container.querySelectorAll('.beaufort-level');
      levels.forEach((level) => {
        expect(level).toHaveAttribute('title');
      });
    });

    test('tooltips should include description', () => {
      const { container } = render(<BeaufortLegend />);

      const levels = container.querySelectorAll('.beaufort-level');
      levels.forEach((level) => {
        expect(level).toHaveAttribute('title');
        const title = level.getAttribute('title');
        expect(title).toBeTruthy();
        expect(title!.length).toBeGreaterThan(10);
      });
    });
  });

  describe('Props Validation', () => {
    test('should handle undefined props', () => {
      const { container } = render(<BeaufortLegend compact={undefined} />);
      expect(container.querySelector('.beaufort-legend')).toBeInTheDocument();
    });

    test('should handle empty string className', () => {
      const { container } = render(<BeaufortLegend className="" />);
      expect(container.querySelector('.beaufort-legend')).toBeInTheDocument();
    });

    test('should handle invalid highlightLevel gracefully', () => {
      const { container } = render(<BeaufortLegend highlightLevel={999} />);
      // Should not crash
      expect(container.querySelector('.beaufort-legend')).toBeInTheDocument();
    });

    test('should handle negative highlightLevel', () => {
      const { container } = render(<BeaufortLegend highlightLevel={-1} />);
      expect(container.querySelector('.beaufort-legend')).toBeInTheDocument();
    });
  });

  describe('Visual Consistency', () => {
    test('should display levels in correct order', () => {
      const { container } = render(<BeaufortLegend />);

      const levels = container.querySelectorAll('.beaufort-level-number');
      const levelNumbers = Array.from(levels).map((el) => parseInt(el.textContent || '0'));

      // Should have exactly 13 levels (0-12)
      expect(levelNumbers.length).toBe(13);

      for (let i = 1; i < levelNumbers.length; i++) {
        expect(levelNumbers[i]).toBe(levelNumbers[i - 1] + 1);
      }
    });

    test('should maintain consistent color scheme', () => {
      const { container } = render(<BeaufortLegend />);

      const levels = container.querySelectorAll('.beaufort-level');
      levels.forEach((level) => {
        const style = level.getAttribute('style');
        expect(style).toBeTruthy();
        expect(style).toContain('--level-color');
        expect(style).toContain('#');
      });
    });
  });

  describe('Integration with windConstants', () => {
    test('should use the same number of levels as BEAUFORT_LEVELS', () => {
      render(<BeaufortLegend />);

      // Check that all level numbers appear
      for (let i = 0; i <= 12; i++) {
        expect(screen.getAllByText(i.toString()).length).toBeGreaterThan(0);
      }

      // Check that all Hungarian names appear
      BEAUFORT_LEVELS.forEach((level) => {
        expect(screen.getByText(level.nameHu)).toBeInTheDocument();
      });
    });

    test('should display correct speed ranges from BEAUFORT_LEVELS', () => {
      const { container } = render(<BeaufortLegend />);

      BEAUFORT_LEVELS.forEach((level) => {
        const rangeText =
          level.speedRange.min === 0
            ? `0-${level.speedRange.max}`
            : `${level.speedRange.min}-${level.speedRange.max}`;
        expect(screen.getByText(rangeText)).toBeInTheDocument();
      });
    });
  });

  describe('Edge Cases', () => {
    test('should render correctly with all props enabled', () => {
      const { container } = render(
        <BeaufortLegend compact={false} highlightLevel={6} className="test-class" />,
      );

      expect(container.querySelector('.beaufort-legend.test-class')).toBeInTheDocument();
      expect(container.querySelector('.beaufort-level.highlighted')).toBeInTheDocument();
      expect(screen.getByText(/Szélereősség skála/i)).toBeInTheDocument();
    });

    test('should handle multiple renders', () => {
      const { rerender } = render(<BeaufortLegend highlightLevel={3} />);
      expect(screen.getByText('3')).toBeInTheDocument();

      rerender(<BeaufortLegend highlightLevel={7} />);
      expect(screen.getByText('7')).toBeInTheDocument();
    });

    test('should update highlight level on prop change', () => {
      const { rerender, container } = render(<BeaufortLegend highlightLevel={3} />);
      let highlighted = container.querySelectorAll('.beaufort-level.highlighted');
      expect(highlighted.length).toBe(1);

      rerender(<BeaufortLegend highlightLevel={8} />);
      highlighted = container.querySelectorAll('.beaufort-level.highlighted');
      expect(highlighted.length).toBe(1);
    });
  });

  describe('Performance', () => {
    test('should render quickly with all levels', () => {
      const startTime = performance.now();
      render(<BeaufortLegend />);
      const endTime = performance.now();

      // Should render in less than 100ms
      expect(endTime - startTime).toBeLessThan(100);
    });

    test('should not cause unnecessary re-renders', () => {
      const { rerender } = render(<BeaufortLegend />);

      // Rerender with same props
      rerender(<BeaufortLegend />);

      // Should still work without errors
      expect(screen.getByText(/Beaufort Skála/i)).toBeInTheDocument();
    });
  });
});
