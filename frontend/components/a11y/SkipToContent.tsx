'use client';

import React from 'react';
import Link from 'next/link';

export function SkipToContent() {
  return (
    <Link
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium z-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
    >
      Skip to main content
    </Link>
  );
}
