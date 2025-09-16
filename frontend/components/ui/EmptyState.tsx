'use client';

import React from 'react';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: string;
  action?: React.ReactNode;
}

export function EmptyState({ title, description, icon = '📭', action }: EmptyStateProps) {
  return (
    <div className="text-center py-12">
      <div className="text-6xl mb-4">{icon}</div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-500 mb-6">{description}</p>
      {action && <div>{action}</div>}
    </div>
  );
}
