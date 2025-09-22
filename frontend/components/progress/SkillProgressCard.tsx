'use client';

import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { SkillProgressChart } from './SkillProgressChart';
import { SkillBadge } from './Badge';
import InfoTooltip from '@/components/ui/InfoTooltip';
import { ProgressLoadingSkeleton } from '@/components/ui/LoadingSkeleton';

interface SkillData {
  tag: string;
  mastery: number;
  samples: number;
}

interface SkillProgressCardProps {
  data: SkillData[];
  overallMastery: number;
  totalResponses: number;
  onPracticeClick?: () => void;
  className?: string;
  loading?: boolean;
}

export function SkillProgressCard({ 
  data, 
  overallMastery, 
  totalResponses, 
  onPracticeClick,
  className = '',
  loading = false
}: SkillProgressCardProps) {
  if (loading) {
    return <ProgressLoadingSkeleton />;
  }
  const formatTag = (tag: string) => {
    return tag.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getOverallBadgeInfo = (mastery: number) => {
    if (mastery >= 0.8) {
      return { label: 'Excellent', color: 'text-green-600' };
    } else if (mastery >= 0.6) {
      return { label: 'Good', color: 'text-yellow-600' };
    } else {
      return { label: 'Needs Improvement', color: 'text-red-600' };
    }
  };

  const overallBadge = getOverallBadgeInfo(overallMastery);
  const overallPercentage = Math.round(overallMastery * 100);

  return (
    <Card className={`p-6 ${className}`}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold">Skill Progress</h3>
            <InfoTooltip content="Computed from your recent answers and rubric-aligned scores." />
          </div>
          {onPracticeClick && (
            <Button onClick={onPracticeClick} size="sm" variant="outline">
              Practice Next
            </Button>
          )}
        </div>

        {/* Overall Progress */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Overall Mastery</span>
            <span className={`text-sm font-semibold ${overallBadge.color}`}>
              {overallBadge.label}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${overallPercentage}%` }}
              />
            </div>
            <span className="text-sm font-bold text-gray-700">
              {overallPercentage}%
            </span>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Based on {totalResponses} responses across {data.length} skills
          </div>
        </div>

        {/* Chart */}
        {data.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-3">Mastery by Skill</h4>
            <SkillProgressChart data={data} />
          </div>
        )}

        {/* Skill List with Badges */}
        {data.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-3">Individual Skills</h4>
            <div className="space-y-3">
              {data.map((skill) => (
                <div key={skill.tag} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">
                      {formatTag(skill.tag)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {skill.samples} response{skill.samples !== 1 ? 's' : ''}
                    </div>
                  </div>
                  <SkillBadge mastery={skill.mastery} />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {data.length === 0 && (
          <div className="text-center py-4">
            <div className="text-sm mb-2"></div>
            <p className="text-sm text-gray-500 mb-1">No skill data available yet</p>
            <p className="text-xs text-gray-400">
              Complete some assignments to see your skill progress
            </p>
          </div>
        )}
      </div>
    </Card>
  );
}
