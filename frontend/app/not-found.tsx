import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <Card className="max-w-md w-full text-center">
        <div className="p-8">
          {/* 404 Icon */}
          <div className="text-6xl mb-4">🔍</div>
          
          {/* 404 Message */}
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            404
          </h1>
          
          <h2 className="text-xl font-semibold text-gray-700 mb-2">
            Page Not Found
          </h2>
          
          <p className="text-gray-600 mb-6">
            The page you&apos;re looking for doesn&apos;t exist or has been moved.
          </p>
          
          {/* Action Buttons */}
          <div className="space-y-3">
            <Link href="/">
              <Button className="w-full">
                Go Home
              </Button>
            </Link>
            
            <Link href="/teacher">
              <Button variant="outline" className="w-full">
                Teacher Dashboard
              </Button>
            </Link>
            
            <Link href="/student">
              <Button variant="outline" className="w-full">
                Student Dashboard
              </Button>
            </Link>
          </div>
          
          {/* Help Text */}
          <p className="text-xs text-gray-500 mt-6">
            Need help? Check our{' '}
            <a 
              href="/help" 
              className="text-blue-600 hover:text-blue-800 underline"
            >
              help center
            </a>
          </p>
        </div>
      </Card>
    </div>
  );
}
