'use client';

interface GradingBadgeProps {
  status: 'ai-graded' | 'awaiting-override' | 'overridden' | 'pending';
  className?: string;
  showIcon?: boolean;
}

export default function GradingBadge({ 
  status, 
  className = '', 
  showIcon = true 
}: GradingBadgeProps) {
  const getBadgeConfig = () => {
    switch (status) {
      case 'ai-graded':
        return {
          label: 'AI Graded',
          bgColor: 'bg-blue-100',
          textColor: 'text-blue-800',
          borderColor: 'border-blue-200',
          icon: null
        };
      case 'awaiting-override':
        return {
          label: 'Awaiting Override',
          bgColor: 'bg-yellow-100',
          textColor: 'text-yellow-800',
          borderColor: 'border-yellow-200',
          icon: (
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          )
        };
      case 'overridden':
        return {
          label: 'Overridden',
          bgColor: 'bg-purple-100',
          textColor: 'text-purple-800',
          borderColor: 'border-purple-200',
          icon: (
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          )
        };
      case 'pending':
        return {
          label: 'Pending',
          bgColor: 'bg-gray-100',
          textColor: 'text-gray-800',
          borderColor: 'border-gray-200',
          icon: (
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          )
        };
      default:
        return {
          label: 'Unknown',
          bgColor: 'bg-gray-100',
          textColor: 'text-gray-800',
          borderColor: 'border-gray-200',
          icon: null
        };
    }
  };

  const config = getBadgeConfig();

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${config.bgColor} ${config.textColor} ${config.borderColor} ${className}`}
    >
      {showIcon && config.icon && (
        <span className="mr-1">
          {config.icon}
        </span>
      )}
      {config.label}
    </span>
  );
}

// Helper function to determine grading status
export function getGradingStatus(
  aiScore: number | null,
  teacherScore: number | null,
  hasTeacherFeedback: boolean = false
): 'ai-graded' | 'awaiting-override' | 'overridden' | 'pending' {
  if (teacherScore !== null || hasTeacherFeedback) {
    return 'overridden';
  }
  
  if (aiScore !== null) {
    return 'awaiting-override';
  }
  
  return 'pending';
}

// Component for displaying grading status with tooltip
interface GradingStatusWithTooltipProps {
  aiScore: number | null;
  teacherScore: number | null;
  hasTeacherFeedback?: boolean;
  className?: string;
}

export function GradingStatusWithTooltip({ 
  aiScore, 
  teacherScore, 
  hasTeacherFeedback = false,
  className = ''
}: GradingStatusWithTooltipProps) {
  const status = getGradingStatus(aiScore, teacherScore, hasTeacherFeedback);
  
  const getTooltipContent = () => {
    switch (status) {
      case 'ai-graded':
        return 'This response has been automatically graded by AI. Teachers can review and override if needed.';
      case 'awaiting-override':
        return 'AI has graded this response. Teachers can review and override the score.';
      case 'overridden':
        return 'This score has been manually adjusted by a teacher.';
      case 'pending':
        return 'This response is awaiting AI grading.';
      default:
        return 'Grading status unknown.';
    }
  };

  return (
    <div className={`inline-flex items-center ${className}`}>
      <GradingBadge status={status} />
      <span className="ml-2 text-xs text-gray-500">
        {getTooltipContent()}
      </span>
    </div>
  );
}
