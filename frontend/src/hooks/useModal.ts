/**
 * useModal Hook
 * Manages modal state with accessibility features.
 *
 * Features:
 * - Open/close state management
 * - Focus trap preparation
 * - ESC key handling support
 * - Body scroll lock when open
 */

import { useCallback, useEffect, useRef } from 'react';

export interface UseModalReturn {
  isOpen: boolean;
  open: () => void;
  close: () => void;
  toggle: () => void;
  modalRef: React.RefObject<HTMLDivElement | null>;
}

export interface UseModalOptions {
  /**
   * Whether to close modal on ESC key press
   * @default true
   */
  closeOnEsc?: boolean;

  /**
   * Whether to close modal on backdrop click
   * @default true
   */
  closeOnBackdropClick?: boolean;

  /**
   * Callback when modal closes
   */
  onClose?: () => void;

  /**
   * Callback when modal opens
   */
  onOpen?: () => void;
}

/**
 * Hook for managing modal state with accessibility
 */
export function useModal(options: UseModalOptions = {}): UseModalReturn {
  const {
    closeOnEsc = true,
    closeOnBackdropClick = true,
    onClose,
    onOpen,
  } = options;

  const [isOpen, setIsOpen] = React.useState(false);
  const modalRef = useRef<HTMLDivElement>(null);
  const previousActiveElementRef = useRef<HTMLElement | null>(null);

  /**
   * Open modal
   */
  const open = useCallback(() => {
    setIsOpen(true);
    onOpen?.();
  }, [onOpen]);

  /**
   * Close modal
   */
  const close = useCallback(() => {
    setIsOpen(false);
    onClose?.();
  }, [onClose]);

  /**
   * Toggle modal state
   */
  const toggle = useCallback(() => {
    setIsOpen((prev) => {
      const newState = !prev;
      if (newState) {
        onOpen?.();
      } else {
        onClose?.();
      }
      return newState;
    });
  }, [onOpen, onClose]);

  /**
   * Handle ESC key press
   */
  useEffect(() => {
    if (!isOpen || !closeOnEsc) return;

    const handleEsc = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') {
        close();
      }
    };

    document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, [isOpen, closeOnEsc, close]);

  /**
   * Focus management
   * - Store previous active element when opening
   * - Restore focus when closing
   */
  useEffect(() => {
    if (isOpen) {
      // Store the currently focused element
      previousActiveElementRef.current = document.activeElement as HTMLElement;

      // Focus the modal after a brief delay to allow render
      const focusTimer = setTimeout(() => {
        if (modalRef.current) {
          // Try to find the first focusable element
          const focusableSelector =
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
          const firstFocusable = modalRef.current.querySelector(
            focusableSelector
          ) as HTMLElement;

          if (firstFocusable) {
            firstFocusable.focus();
          } else {
            modalRef.current.focus();
          }
        }
      }, 50);

      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';

      return () => {
        clearTimeout(focusTimer);
        document.body.style.overflow = '';

        // Restore focus to previous element
        if (previousActiveElementRef.current) {
          previousActiveElementRef.current.focus();
        }
      };
    }
  }, [isOpen]);

  return {
    isOpen,
    open,
    close,
    toggle,
    modalRef,
  };
}

import React from 'react';
