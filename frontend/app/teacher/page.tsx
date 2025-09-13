'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { EmptyState } from '@/components/EmptyState';
import { CreateClassModal } from '@/components/modals/CreateClassModal';
import { InviteCodeCard } from '@/components/InviteCodeCard';
import { listClasses, createClass, type ClassData } from '@/lib/api/classes';
import { useAuthStore } from '@/lib/auth';

export default function TeacherDashboard() {
  const [classes, setClasses] = useState<ClassData[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [showInviteCode, setShowInviteCode] = useState<{ code: string; className: string } | null>(null);
  const [error, setError] = useState<string>('');
  
  const { token } = useAuthStore();

  const fetchClasses = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const response = await listClasses(token || undefined);
      if (response.data) {
        setClasses(response.data);
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

  useEffect(() => {
    fetchClasses();
  }, [fetchClasses]);

  const handleCreateClass = async (className: string) => {
    try {
      setIsCreating(true);
      setError('');
      const response = await createClass({ name: className }, token || undefined);
      
      if (response.data) {
        // Refresh the classes list
        await fetchClasses();
        // Show invite code dialog
        setShowInviteCode({
          code: response.data.invite_code,
          className: response.data.name
        });
        setIsCreateModalOpen(false);
      } else if (response.error) {
        setError(response.error);
      }
    } catch (error) {
      console.error('Failed to create class:', error);
      setError('Failed to create class');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Teacher Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage your classes, create lessons, and track student progress.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                My Classes
              </h2>
              <Button 
                onClick={() => setIsCreateModalOpen(true)}
                disabled={isCreating}
              >
                {isCreating ? 'Creating...' : 'Create Class'}
              </Button>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </div>
            )}

            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-400">Loading classes...</p>
              </div>
            ) : classes.length > 0 ? (
              <div className="space-y-4">
                {classes.map((cls) => (
                  <Card key={cls.id} className="hover:shadow-medium transition-shadow duration-200">
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                            {cls.name}
                          </h3>
                          <div className="space-y-1">
                            <p className="text-gray-600 dark:text-gray-400">
                              {cls.student_count || 0} students
                            </p>
                            <div className="flex items-center space-x-2">
                              <span className="text-sm text-gray-500 dark:text-gray-500">Invite Code:</span>
                              <code className="text-sm font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded border">
                                {cls.invite_code}
                              </code>
                            </div>
                            <p className="text-sm text-gray-500 dark:text-gray-500">
                              {cls.recent_activity || 'No recent activity'}
                            </p>
                          </div>
                        </div>
                        <div className="flex space-x-2 ml-4">
                          <Link href={`/teacher/classes/${cls.id}`}>
                            <Button variant="outline" size="sm">
                              View
                            </Button>
                          </Link>
                          <Link href={`/teacher/classes/${cls.id}/lessons`}>
                            <Button variant="outline" size="sm">
                              Manage
                            </Button>
                          </Link>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <EmptyState
                icon="🏫"
                title="No classes yet"
                description="Create your first class to get started with teaching."
                action={
                  <Button 
                    onClick={() => setIsCreateModalOpen(true)}
                    disabled={isCreating}
                  >
                    {isCreating ? 'Creating...' : 'Create Class'}
                  </Button>
                }
              />
            )}
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full justify-start" variant="outline">
                  📚 Create Lesson
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  📝 Create Assignment
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  📊 View Analytics
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Algebra Quiz</span>
                    <span className="text-gray-500">2h ago</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">New student joined</span>
                    <span className="text-gray-500">5h ago</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Lesson published</span>
                    <span className="text-gray-500">1d ago</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Create Class Modal */}
        <CreateClassModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onSubmit={handleCreateClass}
          isLoading={isCreating}
        />

        {/* Invite Code Dialog */}
        {showInviteCode && (
          <InviteCodeCard
            inviteCode={showInviteCode.code}
            className={showInviteCode.className}
            onClose={() => setShowInviteCode(null)}
          />
        )}
      </div>
    </div>
  );
}
