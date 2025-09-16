'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/badge';
import InfoTooltip from '@/components/ui/InfoTooltip';
import { EmptyState } from '@/components/ui/EmptyState';
import { getMisconceptions, MisconceptionsResponse, MisconceptionCluster } from '@/lib/api/insights';
import { getMiniLessons, MiniLessonsResponse } from '@/lib/api/suggestions';
import { useAuth } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { toast } from 'react-hot-toast';
import { InsightsLoadingSkeleton } from '@/components/ui/LoadingSkeleton';
import { TruncatedText } from '@/components/ui/TruncatedText';

export default function TeacherInsightsPage() {
  const params = useParams();
  const router = useRouter();
  const { token } = useAuth();
  const classId = parseInt(params.id as string);

  const [period, setPeriod] = useState<'week' | 'month'>('week');
  const [misconceptions, setMisconceptions] = useState<MisconceptionsResponse | null>(null);
  const [miniLessons, setMiniLessons] = useState<MiniLessonsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token && classId) {
      fetchInsights();
    }
  }, [token, classId, period]);

  const fetchInsights = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch misconceptions
      const misconceptionsData = await getMisconceptions(
        { classId, period },
        token!
      );
      setMisconceptions(misconceptionsData);

      // If we have clusters, fetch mini-lessons for their suggested tags
      if (misconceptionsData.clusters.length > 0) {
        const allTags = misconceptionsData.clusters.flatMap(
          cluster => cluster.suggested_skill_tags
        );
        const uniqueTags = [...new Set(allTags)];

        if (uniqueTags.length > 0) {
          const miniLessonsData = await getMiniLessons(
            { classId, tags: uniqueTags },
            token!
          );
          setMiniLessons(miniLessonsData);
        }
      }
    } catch (err) {
      console.error('Error fetching insights:', err);
      setError('Failed to load insights data');
      toast.error('Failed to load insights data');
    } finally {
      setLoading(false);
    }
  };

  const handlePeriodChange = (newPeriod: 'week' | 'month') => {
    setPeriod(newPeriod);
  };

  const handleLessonClick = (lessonId: number) => {
    router.push(`/teacher/classes/${classId}/lessons/${lessonId}`);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const truncateText = (text: string, maxLength: number = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Insights</h1>
        </div>
        <InsightsLoadingSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Insights</h1>
        </div>
        <Card className="p-6">
          <div className="text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={fetchInsights} variant="outline">
              Try Again
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold">Insights</h1>
          <InfoTooltip content="Computed from your recent answers and rubric-aligned scores." />
        </div>
        
        {/* Period Switcher */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Period:</span>
          <div className="flex border rounded-lg">
            <Button
              variant={period === 'week' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => handlePeriodChange('week')}
              className="rounded-r-none"
            >
              Week
            </Button>
            <Button
              variant={period === 'month' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => handlePeriodChange('month')}
              className="rounded-l-none"
            >
              Month
            </Button>
          </div>
        </div>
      </div>

      {/* Time Window Info */}
      {misconceptions && (
        <Card className="p-4 bg-blue-50 border-blue-200">
          <div className="flex items-center gap-2 text-sm text-blue-800">
            <span>📅</span>
            <span>
              Analyzing data from {formatDate(misconceptions.time_window.start)} to{' '}
              {formatDate(misconceptions.time_window.end)} ({misconceptions.total_items} responses)
            </span>
          </div>
        </Card>
      )}

      {/* Top Misconceptions */}
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-6">
          <h2 className="text-xl font-semibold">
            Top 3 Misconceptions this {period}
          </h2>
          <InfoTooltip content="Computed from your recent answers and rubric-aligned scores." />
        </div>

        {misconceptions && misconceptions.clusters.length > 0 ? (
          <div className="space-y-6">
            {misconceptions.clusters.map((cluster, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start gap-4">
                  {/* Rank Badge */}
                  <div className="flex-shrink-0">
                    <Badge 
                      variant={index === 0 ? 'default' : index === 1 ? 'secondary' : 'outline'}
                      className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
                    >
                      {index + 1}
                    </Badge>
                  </div>

                  {/* Cluster Content */}
                  <div className="flex-1 space-y-3">
                    {/* Label and Count */}
                    <div className="flex items-center gap-3">
                      <h3 className="font-semibold text-lg">{cluster.label}</h3>
                      <Badge variant="outline">
                        {cluster.cluster_size} responses
                      </Badge>
                    </div>

                    {/* Example Student Answers */}
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-600">Example student answers:</h4>
                      {cluster.examples.slice(0, 2).map((example, exampleIndex) => (
                        <div key={exampleIndex} className="bg-gray-50 rounded p-3">
                          <div className="text-sm text-gray-700 mb-1">
                            <strong>Q:</strong> <TruncatedText text={example.question_prompt} maxLength={80} />
                          </div>
                          <div className="text-sm text-gray-600">
                            <strong>A:</strong> <TruncatedText text={example.student_answer} maxLength={120} />
                          </div>
                          <div className="flex items-center gap-2 mt-2">
                            <Badge variant="outline" className="text-xs">
                              Score: {example.score}%
                            </Badge>
                            <span className="text-xs text-gray-500">
                              {example.assignment_title}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Suggested Mini-Lessons */}
                    {miniLessons && (
                      <div className="space-y-2">
                        <h4 className="text-sm font-medium text-gray-600">Suggested mini-lessons:</h4>
                        <div className="flex flex-wrap gap-2">
                          {cluster.suggested_skill_tags.map((tag) => {
                            const tagSuggestion = miniLessons.suggestions.find(
                              s => s.tag === tag
                            );
                            return tagSuggestion ? (
                              <div key={tag} className="space-y-1">
                                {tagSuggestion.lessons.map((lesson) => (
                                  <Button
                                    key={lesson.lesson_id}
                                    variant="outline"
                                    size="sm"
                                    onClick={() => handleLessonClick(lesson.lesson_id)}
                                    className="text-xs"
                                  >
                                    📚 {lesson.title}
                                  </Button>
                                ))}
                              </div>
                            ) : null;
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            title="Not enough data yet"
            description={`We need more student responses to identify misconceptions. Try again after students have submitted more assignments.`}
            icon="📊"
          />
        )}
      </Card>

      {/* Analysis Summary */}
      {misconceptions && misconceptions.clusters.length > 0 && (
        <Card className="p-4 bg-gray-50">
          <div className="text-sm text-gray-600">
            <strong>Analysis Summary:</strong> {misconceptions.analysis_summary.total_clusters} misconception clusters identified from {misconceptions.total_items} low-scoring responses using {misconceptions.analysis_summary.analysis_type}.
          </div>
        </Card>
      )}
    </div>
  );
}
