import { ReactNode, ButtonHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'link';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Button({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  className,
  ...props 
}: ButtonProps) {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-xl transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none';
  
  const variantClasses = {
    primary: 'bg-primary-600 hover:bg-primary-700 text-white focus-visible:ring-primary-500',
    secondary: 'bg-muted-100 hover:bg-muted-200 dark:bg-muted-700 dark:hover:bg-muted-600 text-muted-900 dark:text-muted-100 focus-visible:ring-muted-500',
    outline: 'border border-muted-300 dark:border-muted-600 bg-transparent hover:bg-muted-50 dark:hover:bg-muted-800 text-muted-700 dark:text-muted-300 focus-visible:ring-muted-500',
    ghost: 'bg-transparent hover:bg-muted-100 dark:hover:bg-muted-800 text-muted-700 dark:text-muted-300 focus-visible:ring-muted-500',
    link: 'bg-transparent hover:bg-transparent text-primary-600 hover:text-primary-700 underline-offset-4 hover:underline focus-visible:ring-primary-500',
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  return (
    <button
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
