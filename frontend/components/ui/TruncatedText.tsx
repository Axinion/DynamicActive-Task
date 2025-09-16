'use client';

import { useState } from 'react';

interface TruncatedTextProps {
  text: string;
  maxLength?: number;
  className?: string;
  showMoreText?: string;
  showLessText?: string;
}

export function TruncatedText({ 
  text, 
  maxLength = 100, 
  className = '',
  showMoreText = 'Show more',
  showLessText = 'Show less'
}: TruncatedTextProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (text.length <= maxLength) {
    return <span className={className}>{text}</span>;
  }

  const displayText = isExpanded ? text : text.substring(0, maxLength) + '...';

  return (
    <span className={className}>
      {displayText}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="ml-1 text-blue-600 hover:text-blue-800 underline text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 rounded"
        aria-label={isExpanded ? showLessText : showMoreText}
      >
        {isExpanded ? showLessText : showMoreText}
      </button>
    </span>
  );
}
