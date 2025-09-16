'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { config } from '@/lib/config';

interface DemoTip {
  id: string;
  title: string;
  content: string;
  position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center';
  screen: string;
  order: number;
}

const DEMO_TIPS: DemoTip[] = [
  {
    id: 'create-class',
    title: 'Create Your First Class',
    content: 'Click "Create Class" to set up a new classroom. You\'ll get an invite code to share with students.',
    position: 'top-right',
    screen: 'teacher-dashboard',
    order: 1
  },
  {
    id: 'build-assignment',
    title: 'Build an Assignment',
    content: 'Create quizzes and assignments with multiple choice and short answer questions. The AI will automatically grade responses.',
    position: 'top-right',
    screen: 'teacher-assignments',
    order: 2
  },
  {
    id: 'take-quiz',
    title: 'Take a Quiz',
    content: 'Students can take quizzes and get immediate feedback. AI grading provides instant results and helpful explanations.',
    position: 'center',
    screen: 'student-assignment',
    order: 3
  },
  {
    id: 'insights',
    title: 'View Insights',
    content: 'The Insights tab shows common misconceptions and suggests mini-lessons to help students improve.',
    position: 'top-right',
    screen: 'teacher-insights',
    order: 4
  },
  {
    id: 'progress',
    title: 'Track Progress',
    content: 'Students can see their skill progress with visual charts and get personalized recommendations.',
    position: 'center',
    screen: 'student-dashboard',
    order: 5
  }
];

interface DemoTipsProps {
  currentScreen: string;
}

export function DemoTips({ currentScreen }: DemoTipsProps) {
  const [currentTip, setCurrentTip] = useState<DemoTip | null>(null);
  const [isVisible, setIsVisible] = useState(false);
  const [dismissedTips, setDismissedTips] = useState<Set<string>>(new Set());

  useEffect(() => {
    // Only show tips in demo mode
    if (!config.IS_DEVELOPMENT && !process.env.NEXT_PUBLIC_DEMO) {
      return;
    }

    // Load dismissed tips from localStorage
    const savedDismissed = localStorage.getItem('demo-dismissed-tips');
    if (savedDismissed) {
      setDismissedTips(new Set(JSON.parse(savedDismissed)));
    }

    // Find the next tip to show for current screen
    const availableTips = DEMO_TIPS.filter(tip => 
      tip.screen === currentScreen && !dismissedTips.has(tip.id)
    ).sort((a, b) => a.order - b.order);

    if (availableTips.length > 0) {
      setCurrentTip(availableTips[0]);
      setIsVisible(true);
    }
  }, [currentScreen, dismissedTips]);

  const handleDismiss = () => {
    if (currentTip) {
      const newDismissed = new Set(dismissedTips);
      newDismissed.add(currentTip.id);
      setDismissedTips(newDismissed);
      localStorage.setItem('demo-dismissed-tips', JSON.stringify([...newDismissed]));
    }
    setIsVisible(false);
    setCurrentTip(null);
  };

  const handleNext = () => {
    if (currentTip) {
      const newDismissed = new Set(dismissedTips);
      newDismissed.add(currentTip.id);
      setDismissedTips(newDismissed);
      localStorage.setItem('demo-dismissed-tips', JSON.stringify([...newDismissed]));
    }
    
    // Find next tip for current screen
    const availableTips = DEMO_TIPS.filter(tip => 
      tip.screen === currentScreen && !dismissedTips.has(tip.id)
    ).sort((a, b) => a.order - b.order);

    if (availableTips.length > 1) {
      setCurrentTip(availableTips[1]);
    } else {
      setIsVisible(false);
      setCurrentTip(null);
    }
  };

  const getPositionClasses = (position: string) => {
    switch (position) {
      case 'top-left':
        return 'top-4 left-4';
      case 'top-right':
        return 'top-4 right-4';
      case 'bottom-left':
        return 'bottom-4 left-4';
      case 'bottom-right':
        return 'bottom-4 right-4';
      case 'center':
        return 'top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2';
      default:
        return 'top-4 right-4';
    }
  };

  if (!isVisible || !currentTip) {
    return null;
  }

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black bg-opacity-20 pointer-events-auto" />
      
      {/* Tip Card */}
      <div className={`absolute ${getPositionClasses(currentTip.position)} pointer-events-auto`}>
        <Card className="max-w-sm shadow-lg border-2 border-primary-500">
          <div className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" />
                <h3 className="font-semibold text-primary-700">Demo Tip</h3>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleDismiss}
                className="h-6 w-6 p-0"
                aria-label="Dismiss tip"
              >
                ×
              </Button>
            </div>
            
            <h4 className="font-medium text-gray-900 mb-2">
              {currentTip.title}
            </h4>
            
            <p className="text-sm text-gray-600 mb-4">
              {currentTip.content}
            </p>
            
            <div className="flex gap-2">
              <Button
                variant="primary"
                size="sm"
                onClick={handleNext}
                className="text-xs"
              >
                Next Tip
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleDismiss}
                className="text-xs"
              >
                Dismiss
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
