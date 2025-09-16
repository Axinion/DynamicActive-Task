'use client';

import { Badge as UIBadge } from '@/components/ui/badge';

interface SkillBadgeProps {
  mastery: number;
  className?: string;
}

export function SkillBadge({ mastery, className = '' }: SkillBadgeProps) {
  const getBadgeInfo = (mastery: number) => {
    if (mastery >= 0.8) {
      return {
        label: 'STRONG',
        variant: 'default' as const,
        color: 'bg-green-100 text-green-800 border-green-200',
        icon: '💪'
      };
    } else if (mastery >= 0.5) {
      return {
        label: 'GROWING',
        variant: 'secondary' as const,
        color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
        icon: '📈'
      };
    } else {
      return {
        label: 'NEEDS PRACTICE',
        variant: 'destructive' as const,
        color: 'bg-red-100 text-red-800 border-red-200',
        icon: '🎯'
      };
    }
  };

  const badgeInfo = getBadgeInfo(mastery);
  const percentage = Math.round(mastery * 100);

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <UIBadge 
        variant={badgeInfo.variant}
        className={`${badgeInfo.color} font-medium`}
      >
        <span className="mr-1">{badgeInfo.icon}</span>
        {badgeInfo.label}
      </UIBadge>
      <span className="text-sm text-gray-600 font-medium">
        {percentage}%
      </span>
    </div>
  );
}
