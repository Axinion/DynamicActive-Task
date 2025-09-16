import React from 'react';
import { CenteredSpinner } from '@/components/ui/Spinner';

export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <CenteredSpinner 
        size="lg" 
        message="Loading your dashboard..." 
      />
    </div>
  );
}
