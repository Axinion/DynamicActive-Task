'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'secondary' | 'outline' | 'destructive' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Badge({ 
  children, 
  variant = 'default', 
  size = 'md',
  className = '' 
}: BadgeProps) {
  const baseClasses = 'inline-flex items-center rounded-full font-medium';
  
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-0.5 text-xs',
    lg: 'px-3 py-1 text-sm'
  };
  
  const variantClasses = {
    default: 'bg-primary-100 text-primary-800',
    secondary: 'bg-muted-100 text-muted-800',
    outline: 'border border-muted-300 text-muted-700 bg-transparent',
    destructive: 'bg-danger-100 text-danger-800',
    success: 'bg-success-100 text-success-800',
    warning: 'bg-warning-100 text-warning-800',
    danger: 'bg-danger-100 text-danger-800',
    info: 'bg-info-100 text-info-800'
  };

  return (
    <span className={cn(
      baseClasses,
      sizeClasses[size],
      variantClasses[variant],
      className
    )}>
      {children}
    </span>
  );
}
