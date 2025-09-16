'use client';

import { useState } from 'react';

interface PrivacyNoteProps {
  className?: string;
  variant?: 'compact' | 'full';
}

export default function PrivacyNote({ 
  className = '', 
  variant = 'compact' 
}: PrivacyNoteProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const compactContent = (
    <div className="flex items-center text-xs text-gray-600">
      <svg className="w-3 h-3 mr-1 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>AI feedback assists learning; teachers may adjust final scores.</span>
    </div>
  );

  const fullContent = (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div className="flex items-start">
        <svg className="w-5 h-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div className="flex-1">
          <h4 className="text-sm font-medium text-blue-900 mb-1">
            About AI Feedback
          </h4>
          <p className="text-sm text-blue-800">
            AI feedback is designed to assist your learning by providing immediate insights on your responses. 
            Your teachers may review and adjust final scores based on their professional judgment. 
            This helps ensure fair and accurate assessment of your work.
          </p>
        </div>
      </div>
    </div>
  );

  const expandableContent = (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center w-full text-left focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset rounded"
      >
        <svg className="w-4 h-4 text-blue-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span className="text-sm font-medium text-blue-900">
          About AI Feedback
        </span>
        <svg
          className={`w-4 h-4 ml-auto text-blue-500 transition-transform duration-200 ${
            isExpanded ? 'transform rotate-180' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      {isExpanded && (
        <div className="mt-3 pt-3 border-t border-blue-200">
          <p className="text-sm text-blue-800">
            AI feedback is designed to assist your learning by providing immediate insights on your responses. 
            Your teachers may review and adjust final scores based on their professional judgment. 
            This helps ensure fair and accurate assessment of your work.
          </p>
          <div className="mt-3 space-y-2">
            <div className="flex items-start">
              <svg className="w-4 h-4 text-blue-600 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-xs text-blue-700">
                AI scores are based on content analysis and keyword matching
              </span>
            </div>
            <div className="flex items-start">
              <svg className="w-4 h-4 text-blue-600 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-xs text-blue-700">
                Teachers can override scores to ensure fairness
              </span>
            </div>
            <div className="flex items-start">
              <svg className="w-4 h-4 text-blue-600 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-xs text-blue-700">
                Your privacy is protected - only your teachers see your responses
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  if (variant === 'compact') {
    return <div className={className}>{compactContent}</div>;
  }

  if (variant === 'full') {
    return <div className={className}>{fullContent}</div>;
  }

  return <div className={className}>{expandableContent}</div>;
}

// Specialized component for assignment result pages
export function AssignmentPrivacyNote({ className = '' }: { className?: string }) {
  return (
    <div className={`bg-blue-50 border border-blue-200 rounded-lg p-4 ${className}`}>
      <div className="flex items-start">
        <svg className="w-5 h-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div className="flex-1">
          <h4 className="text-sm font-medium text-blue-900 mb-1">
            About Your Results
          </h4>
          <p className="text-sm text-blue-800">
            Your scores and feedback are generated by AI to help you learn. 
            Your teacher may review and adjust these scores to ensure they accurately reflect your understanding.
          </p>
        </div>
      </div>
    </div>
  );
}

// Specialized component for recommendations
export function RecommendationPrivacyNote({ className = '' }: { className?: string }) {
  return (
    <div className={`bg-purple-50 border border-purple-200 rounded-lg p-3 ${className}`}>
      <div className="flex items-start">
        <svg className="w-4 h-4 text-purple-500 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div className="flex-1">
          <p className="text-xs text-purple-800">
            Recommendations are personalized based on your performance and learning patterns. 
            Your teacher can see these recommendations to better support your learning.
          </p>
        </div>
      </div>
    </div>
  );
}
