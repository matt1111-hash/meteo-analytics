/**
 * AnomalySettingsModal Component Tests
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AnomalySettingsModal, AnomalyThresholds, DetectionMethod } from './AnomalySettingsModal';

// Mock the Modal component
jest.mock('../common/Modal', () => ({
  Modal: ({ isOpen, onClose, title, children, footer }: any) => {
    if (!isOpen) return null;
    return (
      <div className="modal-mock" data-testid="modal">
        <h2>{title}</h2>
        <div className="modal-content">{children}</div>
        <div className="modal-footer">{footer}</div>
        <button onClick={onClose} aria-label="Close modal">
          Close
        </button>
      </div>
    );
  },
}));

describe('AnomalySettingsModal', () => {
  const defaultProps = {
    isOpen: true,
    onClose: jest.fn(),
    onSave: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render modal when isOpen is true', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('⚙️ Anomália detektálás beállítások')).toBeInTheDocument();
    });

    it('should not render modal when isOpen is false', () => {
      render(<AnomalySettingsModal {...defaultProps} isOpen={false} />);

      expect(screen.queryByTestId('modal')).not.toBeInTheDocument();
    });

    it('should render preset buttons', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      expect(screen.getByText('Alapértelmezett')).toBeInTheDocument();
      expect(screen.getByText('Érzékeny')).toBeInTheDocument();
      expect(screen.getByText('Szigorú')).toBeInTheDocument();
    });

    it('should render detection method select', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      expect(screen.getByDisplayValue('Z-score (Statisztikai)')).toBeInTheDocument();
    });

    it('should render temperature threshold fields', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      expect(screen.getByLabelText('Forró (°C)')).toBeInTheDocument();
      expect(screen.getByLabelText('Hideg (°C)')).toBeInTheDocument();
    });

    it('should render precipitation threshold fields', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      expect(screen.getByLabelText('Magas (mm)')).toBeInTheDocument();
      expect(screen.getByLabelText('Alacsony (mm)')).toBeInTheDocument();
    });

    it('should render wind threshold fields', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      expect(screen.getByLabelText('Normál (km/h)')).toBeInTheDocument();
      expect(screen.getByLabelText('Erős (km/h)')).toBeInTheDocument();
      expect(screen.getByLabelText('Extrém (km/h)')).toBeInTheDocument();
      expect(screen.getByLabelText('Hurrikán (km/h)')).toBeInTheDocument();
    });

    it('should render footer buttons', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      expect(screen.getByText('Alaphelyzet')).toBeInTheDocument();
      expect(screen.getByText('Mégse')).toBeInTheDocument();
      expect(screen.getByText('Mentés')).toBeInTheDocument();
    });
  });

  describe('Initial values', () => {
    it('should use default thresholds when no initial values provided', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      expect(screen.getByDisplayValue('35')).toBeInTheDocument(); // temp_hot
      expect(screen.getByDisplayValue('-10')).toBeInTheDocument(); // temp_cold
    });

    it('should use provided initial thresholds', () => {
      const customThresholds: AnomalyThresholds = {
        temp_hot: 40,
        temp_cold: -15,
        precip_high: 80,
      };

      render(
        <AnomalySettingsModal
          {...defaultProps}
          initialThresholds={customThresholds}
        />
      );

      expect(screen.getByDisplayValue('40')).toBeInTheDocument();
      expect(screen.getByDisplayValue('-15')).toBeInTheDocument();
      expect(screen.getByDisplayValue('80')).toBeInTheDocument();
    });

    it('should use provided initial method', () => {
      render(
        <AnomalySettingsModal
          {...defaultProps}
          initialMethod="iqr"
        />
      );

      expect(screen.getByDisplayValue('IQR (Interquartile Range)')).toBeInTheDocument();
    });
  });

  describe('Preset selection', () => {
    it('should apply default preset values', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const defaultButton = screen.getByText('Alapértelmezett');
      fireEvent.click(defaultButton);

      expect(screen.getByDisplayValue('35')).toBeInTheDocument();
    });

    it('should apply sensitive preset values', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const sensitiveButton = screen.getByText('Érzékeny');
      fireEvent.click(sensitiveButton);

      const tempHotInput = screen.getByLabelText('Forró (°C)') as HTMLInputElement;
      const tempColdInput = screen.getByLabelText('Hideg (°C)') as HTMLInputElement;
      expect(tempHotInput.value).toBe('30'); // Lower temp_hot
      expect(tempColdInput.value).toBe('-5'); // Higher temp_cold
    });

    it('should apply strict preset values', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const strictButton = screen.getByText('Szigorú');
      fireEvent.click(strictButton);

      expect(screen.getByDisplayValue('40')).toBeInTheDocument(); // Higher temp_hot
      expect(screen.getByDisplayValue('-15')).toBeInTheDocument(); // Lower temp_cold
    });

    it('should mark selected preset as active', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      expect(screen.getByText('Alapértelmezett')).toHaveClass('active');
    });
  });

  describe('Detection method selection', () => {
    it('should update method when changing select', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const select = screen.getByDisplayValue('Z-score (Statisztikai)') as HTMLSelectElement;
      fireEvent.change(select, { target: { value: 'iqr' } });

      expect(select.value).toBe('iqr');
    });

    it('should display method hint for zscore', () => {
      render(<AnomalySettingsModal {...defaultProps} initialMethod="zscore" />);

      expect(screen.getByText('Statisztikai eltérés a szórás alapján')).toBeInTheDocument();
    });

    it('should display method hint for iqr', () => {
      render(<AnomalySettingsModal {...defaultProps} initialMethod="iqr" />);

      expect(screen.getByText('Negyedérték-tartományon alapuló detektálás')).toBeInTheDocument();
    });

    it('should display method hint for isolation_forest', () => {
      render(<AnomalySettingsModal {...defaultProps} initialMethod="isolation_forest" />);

      expect(screen.getByText('Gépi tanulás alapú anomália detektálás')).toBeInTheDocument();
    });
  });

  describe('Threshold value changes', () => {
    it('should update temperature hot threshold', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const input = screen.getByLabelText('Forró (°C)') as HTMLInputElement;
      fireEvent.change(input, { target: { value: '40' } });

      expect(input.value).toBe('40');
    });

    it('should update precipitation high threshold', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const input = screen.getByLabelText('Magas (mm)') as HTMLInputElement;
      fireEvent.change(input, { target: { value: '100' } });

      expect(input.value).toBe('100');
    });

    it('should allow empty values', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const input = screen.getByLabelText('Forró (°C)') as HTMLInputElement;
      fireEvent.change(input, { target: { value: '' } });

      expect(input.value).toBe('');
    });
  });

  describe('Validation', () => {
    it('should show error for invalid temp_hot range', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const input = screen.getByLabelText('Forró (°C)');
      fireEvent.change(input, { target: { value: '100' } });

      expect(screen.getByText('Érvénytelen tartomány (-50 to 60°C)')).toBeInTheDocument();
    });

    it('should show error for invalid temp_cold range', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const input = screen.getByLabelText('Hideg (°C)');
      fireEvent.change(input, { target: { value: '-100' } });

      expect(screen.getByText('Érvénytelen tartomány (-50 to 40°C)')).toBeInTheDocument();
    });

    it('should show error for invalid precip_high range', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const input = screen.getByLabelText('Magas (mm)');
      fireEvent.change(input, { target: { value: '600' } });

      expect(screen.getByText('Érvénytelen tartomány (0 to 500mm)')).toBeInTheDocument();
    });

    it('should show error for invalid wind_hurricane range', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const input = screen.getByLabelText('Hurrikán (km/h)');
      fireEvent.change(input, { target: { value: '50' } });

      expect(screen.getByText('Érvénytelen tartomány (100 to 200km/h)')).toBeInTheDocument();
    });

    it('should clear error when value becomes valid', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const input = screen.getByLabelText('Forró (°C)');
      fireEvent.change(input, { target: { value: '100' } });

      expect(screen.queryByText('Érvénytelen tartomány (-50 to 60°C)')).toBeInTheDocument();

      fireEvent.change(input, { target: { value: '35' } });

      expect(screen.queryByText('Érvénytelen tartomány (-50 to 60°C)')).not.toBeInTheDocument();
    });

    it('should disable save button when there are errors', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const saveButton = screen.getByText('Mentés');
      expect(saveButton).not.toBeDisabled();

      const input = screen.getByLabelText('Forró (°C)');
      fireEvent.change(input, { target: { value: '100' } });

      expect(saveButton).toBeDisabled();
    });
  });

  describe('Save functionality', () => {
    it('should call onSave with thresholds and method when clicking save', () => {
      const onSave = jest.fn();
      render(<AnomalySettingsModal {...defaultProps} onSave={onSave} />);

      const saveButton = screen.getByText('Mentés');
      fireEvent.click(saveButton);

      expect(onSave).toHaveBeenCalledWith(
        expect.objectContaining({
          temp_hot: 35,
          temp_cold: -10,
        }),
        'zscore'
      );
    });

    it('should close modal after save', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const saveButton = screen.getByText('Mentés');
      fireEvent.click(saveButton);

      expect(defaultProps.onClose).toHaveBeenCalled();
    });

    it('should include custom threshold values in save', () => {
      const onSave = jest.fn();
      render(<AnomalySettingsModal {...defaultProps} onSave={onSave} />);

      const tempInput = screen.getByLabelText('Forró (°C)');
      fireEvent.change(tempInput, { target: { value: '38' } });

      const methodSelect = screen.getByDisplayValue('Z-score (Statisztikai)') as HTMLSelectElement;
      fireEvent.change(methodSelect, { target: { value: 'iqr' } });

      const saveButton = screen.getByText('Mentés');
      fireEvent.click(saveButton);

      expect(onSave).toHaveBeenCalledWith(
        expect.objectContaining({
          temp_hot: 38,
        }),
        'iqr'
      );
    });
  });

  describe('Reset functionality', () => {
    it('should reset to default values when clicking reset', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      // Change a value
      const tempInput = screen.getByLabelText('Forró (°C)');
      fireEvent.change(tempInput, { target: { value: '50' } });

      // Click reset
      const resetButton = screen.getByText('Alaphelyzet');
      fireEvent.click(resetButton);

      // Should be back to default
      expect(screen.getByDisplayValue('35')).toBeInTheDocument();
    });

    it('should reset method to zscore', () => {
      render(<AnomalySettingsModal {...defaultProps} initialMethod="iqr" />);

      const methodSelect = screen.getByDisplayValue('IQR (Interquartile Range)') as HTMLSelectElement;
      expect(methodSelect.value).toBe('iqr');

      const resetButton = screen.getByText('Alaphelyzet');
      fireEvent.click(resetButton);

      expect(methodSelect.value).toBe('zscore');
    });
  });

  describe('Cancel functionality', () => {
    it('should call onClose when clicking cancel', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const cancelButton = screen.getByText('Mégse');
      fireEvent.click(cancelButton);

      expect(defaultProps.onClose).toHaveBeenCalled();
    });

    it('should call onClose when clicking close button in modal', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const closeButton = screen.getByLabelText('Close modal');
      fireEvent.click(closeButton);

      expect(defaultProps.onClose).toHaveBeenCalled();
    });
  });

  describe('Form state on modal open', () => {
    it('should reset form when modal reopens with new initial values', () => {
      const { rerender } = render(<AnomalySettingsModal {...defaultProps} />);

      // Change a value
      const tempInput = screen.getByLabelText('Forró (°C)');
      fireEvent.change(tempInput, { target: { value: '45' } });
      expect(screen.getByDisplayValue('45')).toBeInTheDocument();

      // Reopen with new initial values
      rerender(
        <AnomalySettingsModal
          {...defaultProps}
          initialThresholds={{ temp_hot: 38 }}
          isOpen={false}
        />
      );
      rerender(
        <AnomalySettingsModal
          {...defaultProps}
          initialThresholds={{ temp_hot: 38 }}
          isOpen={true}
        />
      );

      // Should have new initial value, not the previously edited value
      expect(screen.getByDisplayValue('38')).toBeInTheDocument();
      expect(screen.queryByDisplayValue('45')).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper labels for all inputs', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      expect(screen.getByLabelText('Forró (°C)')).toBeInTheDocument();
      expect(screen.getByLabelText('Hideg (°C)')).toBeInTheDocument();
      expect(screen.getByLabelText('Magas (mm)')).toBeInTheDocument();
      expect(screen.getByLabelText('Alacsony (mm)')).toBeInTheDocument();
      expect(screen.getByLabelText('Normál (km/h)')).toBeInTheDocument();
      expect(screen.getByLabelText('Erős (km/h)')).toBeInTheDocument();
      expect(screen.getByLabelText('Extrém (km/h)')).toBeInTheDocument();
      expect(screen.getByLabelText('Hurrikán (km/h)')).toBeInTheDocument();
    });

    it('should have accessible select element', () => {
      render(<AnomalySettingsModal {...defaultProps} />);

      const select = screen.getByDisplayValue('Z-score (Statisztikai)');
      expect(select).toBeVisible();
    });
  });
});
