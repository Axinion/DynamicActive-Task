'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Spinner({ size = 'md', className = '' }: SpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  return (
    <div
      className={cn(
        'animate-spin rounded-full border-2 border-gray-300 border-t-blue-600',
        sizeClasses[size],
        className
      )}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
}

interface CenteredSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  className?: string;
}

export function CenteredSpinner({ 
  size = 'md', 
  message = 'Loading...', 
  className = '' 
}: CenteredSpinnerProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center p-8', className)}>
      <Spinner size={size} className="mb-4" />
      <p className="text-sm text-gray-600">{message}</p>
    </div>
  );
}
