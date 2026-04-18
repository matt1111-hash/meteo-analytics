/**
 * Modal Component
 * Accessible modal dialog with backdrop, focus trap, and keyboard support.
 *
 * Features:
 * - Portal rendering (renders outside DOM hierarchy)
 * - Backdrop with click-to-close
 * - Focus trap (keyboard tab cycles within modal)
 * - ESC key to close
 * - ARIA attributes for screen readers
 * - Fade-in/out animations
 * - Body scroll lock when open
 *
 * WCAG 2.1 AA Compliant
 */

import React, { useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import './Modal.css';

// =============================================================================
// TYPES
// =============================================================================

export interface ModalProps {
  /** Whether the modal is currently open */
  isOpen: boolean;

  /** Callback when modal closes */
  onClose: () => void;

  /** Modal title (required for accessibility) */
  title: string;

  /** Modal content */
  children: React.ReactNode;

  /** Optional footer content */
  footer?: React.ReactNode;

  /** Custom CSS class name */
  className?: string;

  /** Modal size variant */
  size?: 'small' | 'medium' | 'large' | 'full';

  /** Whether to show close button in header */
  showCloseButton?: boolean;

  /** Whether clicking backdrop closes modal */
  closeOnBackdropClick?: boolean;

  /** Whether pressing ESC closes modal */
  closeOnEsc?: boolean;

  /** ARIA describedby for additional description */
  ariaDescribedby?: string;

  /** ARIA labelledby for custom label (overrides title) */
  ariaLabelledby?: string;
}

// =============================================================================
// FOCUS TRAP UTILITY
// =============================================================================

/**
 * Trap focus within a container element
 * Ensures keyboard tab cycles through focusable elements within the modal
 */
function useFocusTrap(isActive: boolean, containerRef: React.RefObject<HTMLElement | null>): void {
  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    const container = containerRef.current;
    const focusableSelector =
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
    const focusableElements = Array.from(
      container.querySelectorAll<HTMLElement>(focusableSelector),
    );

    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTab = (event: KeyboardEvent): void => {
      if (event.key !== 'Tab') return;

      // Shift + Tab
      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
      }
      // Tab only
      else {
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        }
      }
    };

    container.addEventListener('keydown', handleTab);
    return () => container.removeEventListener('keydown', handleTab);
  }, [isActive, containerRef]);
}

// =============================================================================
// MODAL COMPONENT
// =============================================================================

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  className = '',
  size = 'medium',
  showCloseButton = true,
  closeOnBackdropClick = true,
  closeOnEsc = true,
  ariaDescribedby,
  ariaLabelledby,
}) => {
  const contentRef = React.useRef<HTMLDivElement>(null);

  // Apply focus trap when modal is open
  useFocusTrap(isOpen, contentRef);

  /**
   * Handle backdrop click
   * Only close if clicking directly on backdrop (not on modal content)
   */
  const handleBackdropClick = useCallback(
    (event: React.MouseEvent<HTMLDivElement>) => {
      if (!closeOnBackdropClick) return;

      if (event.target === event.currentTarget) {
        onClose();
      }
    },
    [closeOnBackdropClick, onClose],
  );

  /**
   * Handle ESC key press
   */
  useEffect(() => {
    if (!isOpen || !closeOnEsc) return;

    const handleEsc = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, [isOpen, closeOnEsc, onClose]);

  /**
   * Prevent body scroll when modal is open
   */
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = '';
      };
    }
  }, [isOpen]);

  /**
   * Store and restore focus
   */
  useEffect(() => {
    if (!isOpen) return;

    // Store current focused element
    const previouslyFocused = document.activeElement as HTMLElement;

    // Focus the modal after render
    const focusTimer = setTimeout(() => {
      if (contentRef.current) {
        // Find first focusable element or focus container
        const focusableSelector =
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
        const firstFocusable = contentRef.current.querySelector<HTMLElement>(focusableSelector);

        // Focus the first focusable element, or the modal container if none exists
        if (firstFocusable) {
          firstFocusable.focus();
        } else {
          contentRef.current.focus();
        }
      }
    }, 50);

    return () => {
      clearTimeout(focusTimer);
      // Restore focus when modal closes
      previouslyFocused?.focus();
    };
  }, [isOpen]);

  const modalId = React.useId();
  const titleId = ariaLabelledby || `${modalId}-title`;
  const descId = ariaDescribedby || `${modalId}-description`;

  // Don't render if not open (optional - can also use CSS for animations)
  if (!isOpen) return null;

  return createPortal(
    <div
      className={`modal-backdrop ${isOpen ? 'modal-backdrop-open' : ''}`}
      onClick={handleBackdropClick}
      role="presentation"
    >
      <div
        ref={contentRef}
        className={`modal modal-${size} ${className}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={descId}
        tabIndex={-1}
      >
        {/* Header */}
        <div className="modal-header">
          <h2 id={titleId} className="modal-title">
            {title}
          </h2>
          {showCloseButton && (
            <button
              type="button"
              className="modal-close-button"
              onClick={onClose}
              aria-label="Bezárás"
            >
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          )}
        </div>

        {/* Content */}
        <div id={descId} className="modal-content">
          {children}
        </div>

        {/* Footer */}
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </div>,
    document.body,
  );
};

export default Modal;
