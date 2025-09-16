'use client';

import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function Error({ error, reset }: ErrorProps) {
  React.useEffect(() => {
    // Log the error to an error reporting service
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <Card className="max-w-md w-full text-center">
        <div className="p-8">
          {/* Error Icon */}
          <div className="text-6xl mb-4">⚠️</div>
          
          {/* Error Message */}
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Something went wrong
          </h1>
          
          <p className="text-gray-600 mb-6">
            We encountered an unexpected error. Don&apos;t worry, our team has been notified.
          </p>
          
          {/* Error Details (Development only) */}
          {process.env.NODE_ENV === 'development' && (
            <details className="mb-6 text-left">
              <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
                Error Details
              </summary>
              <pre className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded overflow-auto">
                {error.message}
                {error.digest && `\nDigest: ${error.digest}`}
              </pre>
            </details>
          )}
          
          {/* Action Buttons */}
          <div className="space-y-3">
            <Button 
              onClick={reset}
              className="w-full"
            >
              Try Again
            </Button>
            
            <Link href="/">
              <Button 
                variant="outline" 
                className="w-full"
              >
                Go Home
              </Button>
            </Link>
          </div>
          
          {/* Support Link */}
          <p className="text-xs text-gray-500 mt-6">
            If this problem persists, please{' '}
            <a 
              href="mailto:support@k12lms.com" 
              className="text-blue-600 hover:text-blue-800 underline"
            >
              contact support
            </a>
          </p>
        </div>
      </Card>
    </div>
  );
}
