'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

interface CopyFieldProps {
  value: string;
  label?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export function CopyField({ 
  value, 
  label, 
  className = '', 
  size = 'md',
  showLabel = true 
}: CopyFieldProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      toast.success('Copied to clipboard!');
      
      // Reset copied state after 2 seconds
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error('Failed to copy to clipboard');
    }
  };

  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  const inputSizeClasses = {
    sm: 'px-3 py-2',
    md: 'px-4 py-2',
    lg: 'px-4 py-3'
  };

  return (
    <div className={cn('space-y-2', className)}>
      {showLabel && label && (
        <label className="block text-sm font-medium text-muted-700 dark:text-muted-300">
          {label}
        </label>
      )}
      
      <div className="flex items-center space-x-2">
        <div className="flex-1 relative">
          <input
            type="text"
            value={value}
            readOnly
            className={cn(
              'w-full bg-muted-50 dark:bg-muted-800 border border-muted-300 dark:border-muted-600 rounded-lg',
              'text-muted-900 dark:text-muted-100',
              'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
              sizeClasses[size],
              inputSizeClasses[size]
            )}
            aria-label={label || 'Copy field'}
          />
        </div>
        
        <Button
          onClick={handleCopy}
          variant="outline"
          size={size}
          className="flex-shrink-0"
          aria-label={copied ? 'Copied!' : 'Copy to clipboard'}
        >
          {copied ? (
            <svg
              className="w-4 h-4 text-success-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          ) : (
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
                d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
          )}
        </Button>
      </div>
    </div>
  );
}
