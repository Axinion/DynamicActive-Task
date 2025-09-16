'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { config } from '@/lib/config';

export function DemoModeToggle() {
  const [isDemoMode, setIsDemoMode] = useState(false);

  useEffect(() => {
    // Check if demo mode is enabled
    const demoMode = localStorage.getItem('demo-mode') === 'true';
    setIsDemoMode(demoMode);
  }, []);

  const toggleDemoMode = () => {
    const newDemoMode = !isDemoMode;
    setIsDemoMode(newDemoMode);
    localStorage.setItem('demo-mode', newDemoMode.toString());
    
    // Clear dismissed tips when enabling demo mode
    if (newDemoMode) {
      localStorage.removeItem('demo-dismissed-tips');
    }
    
    // Reload page to apply demo mode changes
    window.location.reload();
  };

  // Only show in development or when explicitly enabled
  if (!config.IS_DEVELOPMENT && !process.env.NEXT_PUBLIC_DEMO) {
    return null;
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-600">Demo Mode:</span>
      <Button
        variant={isDemoMode ? "primary" : "outline"}
        size="sm"
        onClick={toggleDemoMode}
        className="text-xs"
      >
        {isDemoMode ? 'ON' : 'OFF'}
      </Button>
    </div>
  );
}
