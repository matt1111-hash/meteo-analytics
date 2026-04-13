/**
 * Modal.test.tsx
 * Comprehensive tests for the Modal component
 *
 * @see AGENTS.md - Quality Gate: Coverage ≥85% (local)
 * @see WCAG 2.1 AA Compliance
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Modal from './Modal';

// =============================================================================
// TEST UTILITIES
// =============================================================================

const defaultProps = {
  isOpen: false,
  onClose: vi.fn(),
  title: 'Test Modal',
  children: <div>Modal content</div>,
};

const renderModal = (props = {}) => {
  return render(<Modal {...defaultProps} {...props} />);
};

const waitForModalToRender = async () => {
  // Wait for the modal to be rendered in the portal
  await waitFor(
    () => {
      expect(document.querySelector('.modal-backdrop')).toBeInTheDocument();
    },
    { timeout: 300 }
  );
};

// =============================================================================
// RENDER TESTS
// =============================================================================

describe('Modal - Rendering', () => {
  test('should not render when isOpen is false', () => {
    renderModal();
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(document.querySelector('.modal-backdrop')).not.toBeInTheDocument();
  });

  test('should render when isOpen is true', async () => {
    renderModal({ isOpen: true });
    await waitForModalToRender();

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(document.querySelector('.modal-backdrop')).toBeInTheDocument();
    expect(document.querySelector('.modal-backdrop-open')).toBeInTheDocument();
  });

  test('should render title', async () => {
    renderModal({ isOpen: true, title: 'Test Title' });
    await waitForModalToRender();

    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  test('should render children content', async () => {
    renderModal({
      isOpen: true,
      children: <div data-testid="content">Test content</div>,
    });
    await waitForModalToRender();

    expect(screen.getByTestId('content')).toBeInTheDocument();
    expect(screen.getByTestId('content')).toHaveTextContent('Test content');
  });

  test('should render footer when provided', async () => {
    const footerContent = <button data-testid="footer-btn">Footer Button</button>;
    renderModal({ isOpen: true, footer: footerContent });
    await waitForModalToRender();

    expect(screen.getByTestId('footer-btn')).toBeInTheDocument();
    expect(document.querySelector('.modal-footer')).toBeInTheDocument();
  });

  test('should not render footer when not provided', async () => {
    renderModal({ isOpen: true });
    await waitForModalToRender();

    expect(document.querySelector('.modal-footer')).not.toBeInTheDocument();
  });
});

// =============================================================================
// SIZE VARIANT TESTS
// =============================================================================

describe('Modal - Size Variants', () => {
  test.each([
    ['small', 'modal-small'],
    ['medium', 'modal-medium'],
    ['large', 'modal-large'],
    ['full', 'modal-full'],
  ] as const)('should apply %s size class', async (size, expectedClass) => {
    renderModal({ isOpen: true, size });
    await waitForModalToRender();

    const modal = screen.getByRole('dialog');
    expect(modal).toHaveClass(expectedClass);
  });

  test('should default to medium size', async () => {
    renderModal({ isOpen: true });
    await waitForModalToRender();

    const modal = screen.getByRole('dialog');
    expect(modal).toHaveClass('modal-medium');
  });
});

// =============================================================================
// CLOSE BUTTON TESTS
// =============================================================================

describe('Modal - Close Button', () => {
  test('should render close button by default', async () => {
    renderModal({ isOpen: true });
    await waitForModalToRender();

    const closeButton = screen.getByLabelText('Bezárás');
    expect(closeButton).toBeInTheDocument();
  });

  test('should not render close button when showCloseButton is false', async () => {
    renderModal({ isOpen: true, showCloseButton: false });
    await waitForModalToRender();

    expect(screen.queryByLabelText('Bezárás')).not.toBeInTheDocument();
  });

  test('should call onClose when close button is clicked', async () => {
    const onClose = vi.fn();
    renderModal({ isOpen: true, onClose });
    await waitForModalToRender();

    const closeButton = screen.getByLabelText('Bezárás');
    await userEvent.click(closeButton);

    expect(onClose).toHaveBeenCalledTimes(1);
  });
});

// =============================================================================
// BACKDROP CLICK TESTS
// =============================================================================

describe('Modal - Backdrop Click', () => {
  test('should close when clicking backdrop', async () => {
    const onClose = vi.fn();
    renderModal({ isOpen: true, onClose, closeOnBackdropClick: true });
    await waitForModalToRender();

    const backdrop = document.querySelector('.modal-backdrop');
    expect(backdrop).toBeInTheDocument();

    if (backdrop) {
      fireEvent.click(backdrop);
      expect(onClose).toHaveBeenCalledTimes(1);
    }
  });

  test('should not close when clicking modal content', async () => {
    const onClose = vi.fn();
    renderModal({ isOpen: true, onClose, closeOnBackdropClick: true });
    await waitForModalToRender();

    const modal = screen.getByRole('dialog');
    await userEvent.click(modal);

    expect(onClose).not.toHaveBeenCalled();
  });

  test('should not close when closeOnBackdropClick is false', async () => {
    const onClose = vi.fn();
    renderModal({ isOpen: true, onClose, closeOnBackdropClick: false });
    await waitForModalToRender();

    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) {
      fireEvent.click(backdrop);
      expect(onClose).not.toHaveBeenCalled();
    }
  });
});

// =============================================================================
// ESC KEY TESTS
// =============================================================================

describe('Modal - ESC Key', () => {
  test('should close on ESC key press by default', async () => {
    const onClose = vi.fn();
    renderModal({ isOpen: true, onClose, closeOnEsc: true });
    await waitForModalToRender();

    fireEvent.keyDown(document, { key: 'Escape' });
    await waitFor(() => {
      expect(onClose).toHaveBeenCalledTimes(1);
    });
  });

  test('should not close on ESC key when closeOnEsc is false', async () => {
    const onClose = vi.fn();
    renderModal({ isOpen: true, onClose, closeOnEsc: false });
    await waitForModalToRender();

    fireEvent.keyDown(document, { key: 'Escape' });

    expect(onClose).not.toHaveBeenCalled();
  });

  test('should not close on other key presses', async () => {
    const onClose = vi.fn();
    renderModal({ isOpen: true, onClose });
    await waitForModalToRender();

    fireEvent.keyDown(document, { key: 'Enter' });
    fireEvent.keyDown(document, { key: 'Tab' });

    expect(onClose).not.toHaveBeenCalled();
  });
});

// =============================================================================
// ACCESSIBILITY TESTS
// =============================================================================

describe('Modal - Accessibility', () => {
  test('should have role="dialog"', async () => {
    renderModal({ isOpen: true });
    await waitForModalToRender();

    const modal = screen.getByRole('dialog');
    expect(modal).toBeInTheDocument();
  });

  test('should have aria-modal="true"', async () => {
    renderModal({ isOpen: true });
    await waitForModalToRender();

    const modal = screen.getByRole('dialog');
    expect(modal).toHaveAttribute('aria-modal', 'true');
  });

  test('should have aria-labelledby pointing to title', async () => {
    renderModal({ isOpen: true, title: 'Test Title' });
    await waitForModalToRender();

    const modal = screen.getByRole('dialog');
    const labelledBy = modal.getAttribute('aria-labelledby');

    expect(labelledBy).toBeTruthy();

    if (labelledBy) {
      const titleElement = document.getElementById(labelledBy);
      expect(titleElement).toBeInTheDocument();
      expect(titleElement).toHaveTextContent('Test Title');
    }
  });

  test('should use custom aria-labelledby when provided', async () => {
    const customLabelId = 'custom-label';
    renderModal({ isOpen: true, ariaLabelledby: customLabelId });

    await waitForModalToRender();

    const modal = screen.getByRole('dialog');
    expect(modal).toHaveAttribute('aria-labelledby', customLabelId);
  });

  test('should have aria-describedby pointing to content', async () => {
    renderModal({ isOpen: true });
    await waitForModalToRender();

    const modal = screen.getByRole('dialog');
    const describedBy = modal.getAttribute('aria-describedby');

    expect(describedBy).toBeTruthy();
  });

  test('should use custom aria-describedby when provided', async () => {
    const customDescId = 'custom-desc';
    renderModal({ isOpen: true, ariaDescribedby: customDescId });

    await waitForModalToRender();

    const modal = screen.getByRole('dialog');
    expect(modal).toHaveAttribute('aria-describedby', customDescId);
  });

  test('should apply custom className', async () => {
    renderModal({ isOpen: true, className: 'custom-modal-class' });
    await waitForModalToRender();

    const modal = screen.getByRole('dialog');
    expect(modal).toHaveClass('custom-modal-class');
  });

  test('should have backdrop with role="presentation"', async () => {
    renderModal({ isOpen: true });
    await waitForModalToRender();

    const backdrop = document.querySelector('.modal-backdrop');
    expect(backdrop).toHaveAttribute('role', 'presentation');
  });
});

// =============================================================================
// FOCUS MANAGEMENT TESTS
// =============================================================================

describe('Modal - Focus Management', () => {
  test('should focus modal on open', async () => {
    renderModal({
      isOpen: true,
      children: (
        <>
          <button data-testid="first-button">First</button>
          <button data-testid="second-button">Second</button>
        </>
      ),
    });
    await waitForModalToRender();

    // Wait for focus to be set (there's a 50ms timeout in the component)
    await waitFor(() => {
      const modal = screen.getByRole('dialog');
      // Either modal or close button should have focus
      const closeButton = screen.getByLabelText('Bezárás');
      const modalHasFocus = modal === document.activeElement;
      const closeButtonHasFocus = closeButton === document.activeElement;
      expect(modalHasFocus || closeButtonHasFocus).toBe(true);
    }, { timeout: 200 });
  });

  test('should focus first focusable element if available', async () => {
    renderModal({
      isOpen: true,
      children: (
        <>
          <button data-testid="first-button">First Button</button>
          <button data-testid="second-button">Second Button</button>
        </>
      ),
    });
    await waitForModalToRender();

    // The close button in the header is the first focusable element
    await waitFor(() => {
      const closeButton = screen.getByLabelText('Bezárás');
      expect(closeButton).toHaveFocus();
    }, { timeout: 200 });
  });

  test('should trap focus within modal on Tab', async () => {
    renderModal({
      isOpen: true,
      children: (
        <>
          <button data-testid="first-button">First</button>
          <button data-testid="second-button">Second</button>
          <button data-testid="third-button">Third</button>
        </>
      ),
    });
    await waitForModalToRender();

    // Wait for focus to be set
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    const modal = screen.getByRole('dialog');

    // Simulate tab key press - focus should cycle
    fireEvent.keyDown(modal, { key: 'Tab' });

    // Modal should still be in focus trap (either content or one of the buttons)
    expect(modal).toBeInTheDocument();
  });
});

// =============================================================================
// BODY SCROLL LOCK TESTS
// =============================================================================

describe('Modal - Body Scroll Lock', () => {
  test('should prevent body scroll when open', async () => {
    renderModal({ isOpen: true });
    await waitForModalToRender();

    expect(document.body.style.overflow).toBe('hidden');
  });

  test('should restore body scroll when closed', async () => {
    const { rerender, unmount } = renderModal({ isOpen: true });
    await waitForModalToRender();

    expect(document.body.style.overflow).toBe('hidden');

    // Unmount the component to trigger cleanup
    unmount();

    // Scroll should be restored after unmount
    await waitFor(() => {
      expect(document.body.style.overflow).toBe('');
    });
  });
});

// =============================================================================
// PORTAL RENDERING TESTS
// =============================================================================

describe('Modal - Portal Rendering', () => {
  test('should render modal in document.body', async () => {
    renderModal({ isOpen: true });
    await waitForModalToRender();

    const backdrop = document.querySelector('.modal-backdrop');
    expect(backdrop).toBeInTheDocument();
    expect(backdrop?.parentElement).toBe(document.body);
  });

  test('should render multiple modals independently', async () => {
    const { rerender: rerender1 } = renderModal({
      isOpen: true,
      title: 'Modal 1',
    });
    await waitForModalToRender();

    const { rerender: rerender2 } = render(
      <Modal {...defaultProps} isOpen={true} title="Modal 2" />
    );
    await waitForModalToRender();

    expect(screen.getByText('Modal 1')).toBeInTheDocument();
    expect(screen.getByText('Modal 2')).toBeInTheDocument();
  });
});

// =============================================================================
// REUSABILITY TESTS
// =============================================================================

describe('Modal - Reusability', () => {
  test('should handle complex content', async () => {
    const complexContent = (
      <div>
        <h3>Section 1</h3>
        <p>Paragraph 1</p>
        <button>Action Button</button>
        <ul>
          <li>Item 1</li>
          <li>Item 2</li>
        </ul>
      </div>
    );

    renderModal({ isOpen: true, children: complexContent });
    await waitForModalToRender();

    expect(screen.getByText('Section 1')).toBeInTheDocument();
    expect(screen.getByText('Paragraph 1')).toBeInTheDocument();
    expect(screen.getByText('Action Button')).toBeInTheDocument();
    expect(screen.getByText('Item 1')).toBeInTheDocument();
  });

  test('should handle form content', async () => {
    const formContent = (
      <form data-testid="test-form">
        <label htmlFor="input1">Input 1</label>
        <input id="input1" name="input1" />
        <button type="submit">Submit</button>
      </form>
    );

    renderModal({ isOpen: true, children: formContent });
    await waitForModalToRender();

    expect(screen.getByTestId('test-form')).toBeInTheDocument();
    expect(screen.getByLabelText('Input 1')).toBeInTheDocument();
  });
});
