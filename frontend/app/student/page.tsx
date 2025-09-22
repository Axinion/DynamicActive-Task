'use client';

import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { EmptyState } from '@/components/EmptyState';
import { Toast } from '@/components/Toast';
import { listClasses, joinClass, type ClassData } from '@/lib/api/classes';
import { useAuthStore } from '@/lib/auth';
import LearningPathCard from '@/components/recs/LearningPathCard';
import { SkillProgressCard } from '@/components/progress/SkillProgressCard';
import { getSkillProgress } from '@/lib/api/progress';
import { useRouter } from 'next/navigation';

export default function StudentDashboard() {
  const [classes, setClasses] = useState<ClassData[]>([]);
  const [loading, setLoading] = useState(true);
  const [inviteCode, setInviteCode] = useState('');
  const [isJoining, setIsJoining] = useState(false);
  const [error, setError] = useState<string>('');
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [skillProgress, setSkillProgress] = useState<any>(null);
  const [progressLoading, setProgressLoading] = useState(false);
  
  const { token, user } = useAuthStore();
  const router = useRouter();

  const fetchClasses = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const response = await listClasses(token || undefined);
      if (Array.isArray(response)) {
        setClasses(response);
      } else if (response.error) {
        setError(response.error);
      }
    } catch (error) {
      console.error('Failed to fetch classes:', error);
      setError('Failed to load classes');
    } finally {
      setLoading(false);
    }
  }, [token]);

  const fetchSkillProgress = useCallback(async () => {
    if (!token || !user || classes.length === 0) return;
    
    try {
      setProgressLoading(true);
      // Use the first class for now, could be enhanced to show progress for all classes
      const response = await getSkillProgress(
        { classId: classes[0].id, studentId: user.id },
        token
      );
      setSkillProgress(response);
    } catch (error) {
      console.error('Failed to fetch skill progress:', error);
    } finally {
      setProgressLoading(false);
    }
  }, [token, user, classes]);

  useEffect(() => {
    fetchClasses();
  }, [fetchClasses]);

  useEffect(() => {
    if (classes.length > 0) {
      fetchSkillProgress();
    }
  }, [fetchSkillProgress]);

  const handleJoinClass = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteCode.trim()) return;

    try {
      setIsJoining(true);
      setError('');
      const response = await joinClass({ invite_code: inviteCode.trim() }, token || undefined);
      
      if (response?.success) {
        setToast({ message: 'Joined!', type: 'success' });
        setInviteCode(''); // Clear the input
        await fetchClasses(); // Refresh the list
      } else {
        const msg = response?.message || 'Failed to join class';
        setError(msg);
        setToast({ message: msg, type: 'error' });
      }
    } catch (error) {
      console.error('Failed to join class:', error);
      const errorMessage = 'Failed to join class';
      setError(errorMessage);
      setToast({ message: errorMessage, type: 'error' });
    } finally {
      setIsJoining(false);
    }
  };

  const handlePracticeNext = () => {
    if (classes.length > 0) {
      router.push(`/student/classes/${classes[0].id}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header Section - Centered */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent dark:from-purple-400 dark:to-pink-400 mb-4">
            Student Dashboard
          </h1>
          <p className="text-lg md:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-6">
            View your classes, complete assignments, and track your progress with AI-powered insights.
          </p>
          <div className="flex justify-center">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 border border-gray-100 dark:border-gray-700">
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">{classes.length}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Enrolled Classes</div>
              </div>
            </div>
          </div>
        </div>

        {/* Learning Path Card - Show for first class if available */}
        {classes.length > 0 && (
          <div className="mb-8">
            <LearningPathCard classId={classes[0].id} />
          </div>
        )}

        {/* Skill Progress Card - Show for first class if available */}
        {classes.length > 0 && (
          <div className="mb-8">
            <SkillProgressCard
              data={skillProgress?.skill_mastery || []}
              overallMastery={skillProgress?.overall_mastery_avg || 0}
              totalResponses={skillProgress?.total_responses || 0}
              onPracticeClick={handlePracticeNext}
              loading={progressLoading}
            />
          </div>
        )}

        {/* Main Content - Centered Layout */}
        <div className="max-w-4xl mx-auto">
          {/* Join Class Form - Centered */}
          <div className="text-center mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
              Join a New Class
            </h2>
            <Card className="max-w-md mx-auto">
              <CardContent className="p-6">
                <form onSubmit={handleJoinClass} className="space-y-4">
                  <div>
                    <input
                      type="text"
                      value={inviteCode}
                      onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
                      placeholder="Enter class code (e.g., ABC123)"
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-center text-lg"
                      disabled={isJoining}
                      required
                    />
                  </div>
                  <Button
                    type="submit"
                    disabled={isJoining || !inviteCode.trim()}
                    className="w-full py-3"
                  >
                    {isJoining ? 'Joining...' : 'Join Class'}
                  </Button>
                </form>
                {error && (
                  <p className="mt-3 text-sm text-red-600 dark:text-red-400 text-center">{error}</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Classes Section */}
          <div className="text-center mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
              My Classes
            </h2>

            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
                <p className="text-lg text-gray-600 dark:text-gray-400">Loading classes...</p>
              </div>
            ) : classes.length > 0 ? (
              <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                {classes.map((cls) => (
                  <Card key={cls.id} className="hover:shadow-xl transition-all duration-300 hover:scale-105">
                    <CardContent className="p-8 text-center">
                      <div className="mb-4">
                        <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                          {cls.name}
                        </h3>
                        <p className="text-gray-600 dark:text-gray-400 mb-2">
                          {cls.student_count} students enrolled
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-500 mb-4">
                          {cls.recent_activity || 'No recent activity'}
                        </p>
                      </div>
                      <div className="space-y-3">
                        <Button 
                          variant="outline" 
                          className="w-full"
                          onClick={() => router.push(`/student/classes/${cls.id}`)}
                        >
                          View Class
                        </Button>
                        <Button 
                          className="w-full"
                          onClick={() => router.push(`/student/classes/${cls.id}`)}
                        >
                          Continue Learning
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <EmptyState
                  title="No classes yet"
                  description="Use the form above to join a class with an invite code."
                />
              </div>
            )}
          </div>
        </div>

        {/* Toast Notification */}
        {toast && (
          <Toast
            message={toast.message}
            type={toast.type}
            onClose={() => setToast(null)}
          />
        )}
      </div>
    </div>
  );
}
