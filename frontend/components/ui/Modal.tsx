'use client';

import React, { useEffect } from 'react';
import { FocusTrap } from '@/components/a11y/FocusTrap';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

export function Modal({
  isOpen,
  onClose,
  title,
  description,
  children,
  size = 'md',
  className = ''
}: ModalProps) {
  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      aria-describedby={description ? "modal-description" : undefined}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />
      
      {/* Modal Content */}
      <FocusTrap active={isOpen}>
        <div
          className={cn(
            "relative bg-white rounded-lg shadow-xl w-full",
            sizeClasses[size],
            className
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div>
              <h2 id="modal-title" className="text-lg font-semibold text-gray-900">
                {title}
              </h2>
              {description && (
                <p id="modal-description" className="mt-1 text-sm text-gray-600">
                  {description}
                </p>
              )}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={onClose}
              className="ml-4"
              aria-label="Close modal"
            >
              <span className="sr-only">Close</span>
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </Button>
          </div>
          
          {/* Body */}
          <div className="p-6">
            {children}
          </div>
        </div>
      </FocusTrap>
    </div>
  );
}
