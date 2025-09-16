'use client';

import { useState, useRef, useEffect } from 'react';

interface InfoTooltipProps {
  content: string;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  maxWidth?: string;
  className?: string;
}

export default function InfoTooltip({ 
  content, 
  children, 
  position = 'top',
  maxWidth = '300px',
  className = ''
}: InfoTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isVisible && triggerRef.current && tooltipRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect();
      const tooltipRect = tooltipRef.current.getBoundingClientRect();
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

      let top = 0;
      let left = 0;

      switch (position) {
        case 'top':
          top = triggerRect.top + scrollTop - tooltipRect.height - 8;
          left = triggerRect.left + scrollLeft + (triggerRect.width - tooltipRect.width) / 2;
          break;
        case 'bottom':
          top = triggerRect.bottom + scrollTop + 8;
          left = triggerRect.left + scrollLeft + (triggerRect.width - tooltipRect.width) / 2;
          break;
        case 'left':
          top = triggerRect.top + scrollTop + (triggerRect.height - tooltipRect.height) / 2;
          left = triggerRect.left + scrollLeft - tooltipRect.width - 8;
          break;
        case 'right':
          top = triggerRect.top + scrollTop + (triggerRect.height - tooltipRect.height) / 2;
          left = triggerRect.right + scrollLeft + 8;
          break;
      }

      // Ensure tooltip stays within viewport
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      if (left < 8) left = 8;
      if (left + tooltipRect.width > viewportWidth - 8) {
        left = viewportWidth - tooltipRect.width - 8;
      }
      if (top < 8) top = 8;
      if (top + tooltipRect.height > viewportHeight + scrollTop - 8) {
        top = viewportHeight + scrollTop - tooltipRect.height - 8;
      }

      setTooltipPosition({ top, left });
    }
  }, [isVisible, position]);

  const handleMouseEnter = () => {
    setIsVisible(true);
  };

  const handleMouseLeave = () => {
    setIsVisible(false);
  };

  const handleClick = () => {
    setIsVisible(!isVisible);
  };

  return (
    <>
      <div
        ref={triggerRef}
        className={`inline-block cursor-help ${className}`}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
        role="button"
        tabIndex={0}
        aria-describedby="tooltip"
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleClick();
          }
        }}
      >
        {children}
      </div>

      {isVisible && (
        <div
          ref={tooltipRef}
          id="tooltip"
          className="fixed z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg pointer-events-none"
          style={{
            top: tooltipPosition.top,
            left: tooltipPosition.left,
            maxWidth: maxWidth,
          }}
          role="tooltip"
        >
          <div className="whitespace-pre-wrap">{content}</div>
          
          {/* Arrow */}
          <div
            className={`absolute w-2 h-2 bg-gray-900 transform rotate-45 ${
              position === 'top' ? 'top-full left-1/2 -translate-x-1/2 -translate-y-1/2' :
              position === 'bottom' ? 'bottom-full left-1/2 -translate-x-1/2 translate-y-1/2' :
              position === 'left' ? 'left-full top-1/2 -translate-y-1/2 -translate-x-1/2' :
              'right-full top-1/2 -translate-y-1/2 translate-x-1/2'
            }`}
          />
        </div>
      )}
    </>
  );
}

// Specialized tooltip for AI explanations
interface AITooltipProps {
  title: string;
  explanation: string;
  children: React.ReactNode;
  className?: string;
}

export function AITooltip({ title, explanation, children, className = '' }: AITooltipProps) {
  const content = `${title}\n\n${explanation}`;
  
  return (
    <InfoTooltip 
      content={content} 
      position="top" 
      maxWidth="350px"
      className={className}
    >
      {children}
    </InfoTooltip>
  );
}

// Specialized tooltip for recommendations
interface RecommendationTooltipProps {
  reason: string;
  children: React.ReactNode;
  className?: string;
}

export function RecommendationTooltip({ reason, children, className = '' }: RecommendationTooltipProps) {
  const content = `Why this recommendation?\n\n${reason}`;
  
  return (
    <InfoTooltip 
      content={content} 
      position="top" 
      maxWidth="400px"
      className={className}
    >
      {children}
    </InfoTooltip>
  );
}
