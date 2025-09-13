'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

interface InviteCodeCardProps {
  inviteCode: string;
  className: string;
  onClose: () => void;
}

export function InviteCodeCard({ inviteCode, className, onClose }: InviteCodeCardProps) {
  const [copied, setCopied] = useState(false);

  const handleCopyCode = async () => {
    try {
      await navigator.clipboard.writeText(inviteCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy invite code:', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = inviteCode;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center">🎉 Class Created Successfully!</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Your class <strong>&ldquo;{className}&rdquo;</strong> has been created.
            </p>
            
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Invite Code:</p>
              <div className="flex items-center justify-center space-x-2">
                <code className="text-2xl font-mono font-bold text-primary-600 dark:text-primary-400 bg-white dark:bg-gray-700 px-3 py-2 rounded border">
                  {inviteCode}
                </code>
                <Button
                  onClick={handleCopyCode}
                  size="sm"
                  variant="outline"
                  className="shrink-0"
                >
                  {copied ? '✅' : '📋'}
                </Button>
              </div>
            </div>
            
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
              <p className="text-sm text-blue-700 dark:text-blue-300">
                💡 <strong>Share this code with students</strong> so they can join your class!
              </p>
            </div>
          </div>
          
          <Button onClick={onClose} className="w-full">
            Got it!
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
