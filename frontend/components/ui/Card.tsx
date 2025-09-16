import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface CardProps {
  children: ReactNode;
  className?: string;
  padding?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'outlined' | 'elevated';
}

export function Card({ children, className, padding = 'md', variant = 'default' }: CardProps) {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const variantClasses = {
    default: 'bg-white dark:bg-muted-800 rounded-2xl shadow-soft border border-muted-200 dark:border-muted-700',
    outlined: 'bg-white dark:bg-muted-800 rounded-2xl border-2 border-muted-300 dark:border-muted-600',
    elevated: 'bg-white dark:bg-muted-800 rounded-2xl shadow-medium border border-muted-200 dark:border-muted-700',
  };

  return (
    <div className={cn(variantClasses[variant], paddingClasses[padding], className)}>
      {children}
    </div>
  );
}

interface CardHeaderProps {
  children: ReactNode;
  className?: string;
}

export function CardHeader({ children, className }: CardHeaderProps) {
  return (
    <div className={cn('mb-4', className)}>
      {children}
    </div>
  );
}

interface CardTitleProps {
  children: ReactNode;
  className?: string;
}

export function CardTitle({ children, className }: CardTitleProps) {
  return (
    <h3 className={cn('text-lg font-semibold text-muted-900 dark:text-muted-100', className)}>
      {children}
    </h3>
  );
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function CardContent({ children, className }: CardContentProps) {
  return (
    <div className={cn('text-muted-600 dark:text-muted-300', className)}>
      {children}
    </div>
  );
}
