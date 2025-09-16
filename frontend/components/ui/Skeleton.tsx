'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface SkeletonProps {
  className?: string;
  lines?: number;
  height?: string;
}

export function Skeleton({ className, lines = 1, height = 'h-4' }: SkeletonProps) {
  return (
    <div className={cn("animate-pulse bg-gray-200 dark:bg-gray-700 rounded", className, height)}>
      {lines > 1 && (
        <div className="space-y-2">
          {Array.from({ length: lines }).map((_, i) => (
            <div key={i} className={cn("bg-gray-200 dark:bg-gray-700 rounded", height)}></div>
          ))}
        </div>
      )}
    </div>
  );
}

export function CardSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={cn("bg-white rounded-lg shadow-sm border border-gray-200 p-6", className)}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Skeleton className="w-48 h-6" />
          <Skeleton className="w-20 h-8" />
        </div>
        
        {/* Content lines */}
        <div className="space-y-2">
          <Skeleton className="w-full h-4" />
          <Skeleton className="w-3/4 h-4" />
          <Skeleton className="w-1/2 h-4" />
        </div>
        
        {/* Footer */}
        <div className="flex items-center justify-between pt-4">
          <Skeleton className="w-24 h-4" />
          <Skeleton className="w-16 h-8" />
        </div>
      </div>
    </div>
  );
}

export function LineSkeleton({ lines = 3, className = '' }: { lines?: number; className?: string }) {
  return (
    <div className={cn("space-y-3", className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="flex items-center space-x-3">
          <Skeleton className="w-8 h-8 rounded-full" />
          <div className="flex-1 space-y-2">
            <Skeleton className="w-3/4 h-4" />
            <Skeleton className="w-1/2 h-3" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function TableSkeleton({ rows = 5, columns = 4, className = '' }: { 
  rows?: number; 
  columns?: number; 
  className?: string; 
}) {
  return (
    <div className={cn("space-y-3", className)}>
      {/* Header */}
      <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} className="w-full h-6" />
        ))}
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} className="w-full h-4" />
          ))}
        </div>
      ))}
    </div>
  );
}
