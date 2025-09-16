'use client';

import { useState, useEffect } from 'react';
import { getMisconceptions, MisconceptionCluster } from '@/lib/api/insights';
import { useAuthStore } from '@/lib/auth';

interface MisconceptionsPanelProps {
  classId: number;
  className?: string;
}

export default function MisconceptionsPanel({ classId, className = '' }: MisconceptionsPanelProps) {
  const [clusters, setClusters] = useState<MisconceptionCluster[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [totalResponses, setTotalResponses] = useState(0);
  const [analyzedResponses, setAnalyzedResponses] = useState(0);
  
  const { token, user } = useAuthStore();

  useEffect(() => {
    const fetchMisconceptions = async () => {
      if (!token || !user || user.role !== 'teacher') {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        const response = await getMisconceptions({ classId }, token);
        setClusters(response.clusters || []);
        setTotalResponses(response.total_responses || 0);
        setAnalyzedResponses(response.analyzed_responses || 0);
      } catch (err) {
        console.error('Failed to fetch misconceptions:', err);
        setError(err instanceof Error ? err.message : 'Failed to load misconceptions');
      } finally {
        setIsLoading(false);
      }
    };

    fetchMisconceptions();
  }, [token, user, classId]);

  // Don't render if user is not a teacher
  if (!user || user.role !== 'teacher') {
    return null;
  }

  const handleToggle = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className={`bg-white border border-gray-200 rounded-lg shadow-sm ${className}`}>
      {/* Header */}
      <button
        onClick={handleToggle}
        className="w-full px-6 py-4 text-left focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset"
        aria-expanded={isExpanded}
        aria-controls="misconceptions-content"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-orange-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900">Top Misconceptions</h3>
          </div>
          <div className="flex items-center space-x-3">
            {!isLoading && !error && clusters.length > 0 && (
              <span className="text-sm text-gray-500">
                {analyzedResponses} of {totalResponses} responses analyzed
              </span>
            )}
            <svg
              className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${
                isExpanded ? 'transform rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </button>

      {/* Content */}
      {isExpanded && (
        <div id="misconceptions-content" className="px-6 pb-6">
          {/* Loading State */}
          {isLoading && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-orange-600"></div>
              <span className="ml-3 text-gray-600">Analyzing student responses...</span>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="text-center py-6">
              <div className="text-red-600 mb-2">
                <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-sm text-red-700">Unable to load misconceptions</p>
                <p className="text-xs text-red-600 mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Empty State */}
          {!isLoading && !error && clusters.length === 0 && (
            <div className="text-center py-6">
              <div className="text-gray-500 mb-3">
                <svg className="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h4 className="font-medium text-gray-800 mb-2">No misconceptions detected</h4>
                <p className="text-sm text-gray-600">
                  Great job! Your students are performing well. Check back after more assignments are submitted.
                </p>
              </div>
            </div>
          )}

          {/* Misconceptions List */}
          {!isLoading && !error && clusters.length > 0 && (
            <div className="space-y-4">
              {clusters.map((cluster, index) => (
                <div key={index} className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="font-medium text-orange-900 mb-1">{cluster.label}</h4>
                      <div className="flex items-center space-x-2 text-sm text-orange-700">
                        <span className="bg-orange-100 px-2 py-1 rounded-full">
                          {cluster.count} student{cluster.count !== 1 ? 's' : ''}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Example Student Answers */}
                  <div className="mb-3">
                    <h5 className="text-sm font-medium text-orange-800 mb-2">Example responses:</h5>
                    <div className="space-y-2">
                      {cluster.examples.slice(0, 2).map((example, exampleIndex) => (
                        <div key={exampleIndex} className="bg-white border border-orange-200 rounded-md p-3">
                          <p className="text-sm text-gray-700 italic">"{example}"</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Suggested Skills */}
                  {cluster.suggested_skill_tags.length > 0 && (
                    <div>
                      <h5 className="text-sm font-medium text-orange-800 mb-2">Suggested focus areas:</h5>
                      <div className="flex flex-wrap gap-1">
                        {cluster.suggested_skill_tags.map((skill, skillIndex) => (
                          <span
                            key={skillIndex}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Mini-lesson Suggestion */}
                  <div className="mt-3 pt-3 border-t border-orange-200">
                    <div className="flex items-start">
                      <svg className="w-4 h-4 text-orange-600 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-orange-800">Mini-lesson idea:</p>
                        <p className="text-sm text-orange-700">
                          Create a focused lesson on {cluster.suggested_skill_tags.slice(0, 2).join(' and ')} to address this common misunderstanding.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Footer */}
          {!isLoading && !error && clusters.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500 text-center">
                Misconceptions are identified by analyzing low-scoring responses and clustering similar patterns.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
