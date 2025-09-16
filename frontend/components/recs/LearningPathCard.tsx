'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getMyRecommendations, Recommendation } from '@/lib/api/recommendations';
import { useAuthStore } from '@/lib/auth';
import { RecommendationTooltip } from '@/components/ui/InfoTooltip';
import { RecommendationPrivacyNote } from '@/components/ui/PrivacyNote';

interface LearningPathCardProps {
  classId: number;
  className?: string;
  showTitle?: boolean;
}


export default function LearningPathCard({ classId, className = '', showTitle = true }: LearningPathCardProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const { token, user } = useAuthStore();

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!token || !user || user.role !== 'student') {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        const response = await getMyRecommendations(classId, token);
        setRecommendations(response.recommendations || []);
      } catch (err) {
        console.error('Failed to fetch recommendations:', err);
        setError(err instanceof Error ? err.message : 'Failed to load recommendations');
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecommendations();
  }, [token, user, classId]);


  // Don't render if user is not a student
  if (!user || user.role !== 'student') {
    return null;
  }

  // Show loading state
  if (isLoading) {
    return (
      <div className={`bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6 ${className}`}>
        {showTitle && (
          <div className="flex items-center mb-4">
            <h3 className="text-lg font-semibold text-purple-900">My Learning Path</h3>
          </div>
        )}
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-purple-600"></div>
          <span className="ml-3 text-purple-700">Loading your personalized recommendations...</span>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className={`bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6 ${className}`}>
        {showTitle && (
          <div className="flex items-center mb-4">
            <h3 className="text-lg font-semibold text-purple-900">My Learning Path</h3>
          </div>
        )}
        <div className="text-center py-3">
          <div className="text-red-600 mb-2">
            <p className="text-xs text-red-700">Unable to load recommendations</p>
            <p className="text-xs text-red-600 mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  // Show empty state
  if (recommendations.length === 0) {
    return (
      <div className={`bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6 ${className}`}>
        {showTitle && (
          <div className="flex items-center mb-4">
            <h3 className="text-lg font-semibold text-purple-900">My Learning Path</h3>
          </div>
        )}
        <div className="text-center py-4">
          <div className="text-purple-600 mb-2">
            <h4 className="font-medium text-purple-800 mb-1 text-sm">No recommendations yet</h4>
            <p className="text-xs text-purple-600">
              Complete some assignments to get personalized lesson recommendations!
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Show recommendations
  return (
    <div className={`bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6 ${className}`}>
      {showTitle && (
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <h3 className="text-lg font-semibold text-purple-900">My Learning Path</h3>
          </div>
          <span className="text-sm text-purple-600 bg-purple-100 px-2 py-1 rounded-full">
            {recommendations.length} recommended
          </span>
        </div>
      )}

      <div className="space-y-3">
        {recommendations.slice(0, 3).map((rec, index) => (
          <div key={rec.lesson_id} className="bg-white rounded-lg border border-purple-100 p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center mb-2">
                  <div className="flex-shrink-0 w-3 h-3 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-xs font-medium mr-2">
                    {index + 1}
                  </div>
                  <h4 className="font-medium text-gray-900 truncate">{rec.title}</h4>
                </div>
                <p className="text-sm text-gray-600 ml-9 line-clamp-2">{rec.reason}</p>
              </div>
              
              <div className="flex items-center space-x-2 ml-4">
                <Link
                  href={`/student/classes/${classId}/lessons/${rec.lesson_id}`}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-purple-600 rounded-md hover:bg-purple-700 transition-colors"
                >
                  Open Lesson
                </Link>
                
                <RecommendationTooltip reason={rec.reason}>
                  <button
                    className="inline-flex items-center p-1.5 text-sm text-purple-600 hover:text-purple-800 hover:bg-purple-50 rounded-md transition-colors"
                    aria-label="Why this lesson?"
                  >
                  </button>
                </RecommendationTooltip>
              </div>
            </div>
          </div>
        ))}
      </div>

      {recommendations.length > 3 && (
        <div className="mt-4 text-center">
          <Link
            href={`/student/classes/${classId}/recommendations`}
            className="inline-flex items-center text-sm text-purple-600 hover:text-purple-800 font-medium"
          >
            View all {recommendations.length} recommendations
          </Link>
        </div>
      )}

      {/* Privacy Note */}
      <div className="mt-4">
        <RecommendationPrivacyNote />
      </div>
    </div>
  );
}
