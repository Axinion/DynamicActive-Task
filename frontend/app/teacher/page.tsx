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

  useEffect(() => {
    fetchClasses();
  }, [fetchClasses]);

  const handleCreateClass = async (className: string) => {
    try {
      setIsCreating(true);
      setError('');
      const response = await createClass({ name: className }, token || undefined);
      
      if (response.id && response.invite_code) {
        // Refresh the classes list
        await fetchClasses();
        // Show invite code dialog
        setShowInviteCode({
          code: response.invite_code,
          className: response.name
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent dark:from-blue-400 dark:to-indigo-400 mb-2">
                Teacher Dashboard
              </h1>
              <p className="text-base md:text-lg text-gray-600 dark:text-gray-400">
                Manage your classes, create lessons, and track student progress with AI-powered insights.
              </p>
            </div>
            <div className="flex justify-center md:block">
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 md:p-6 border border-gray-100 dark:border-gray-700">
                <div className="text-center">
                  <div className="text-xl md:text-2xl font-bold text-blue-600 dark:text-blue-400">{classes.length}</div>
                  <div className="text-xs md:text-sm text-gray-500 dark:text-gray-400">Active Classes</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6 lg:gap-8">
          <div className="lg:col-span-2">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                My Classes
              </h2>
              <Button 
                onClick={() => setIsCreateModalOpen(true)}
                disabled={isCreating}
                className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 px-6 py-2"
              >
                {isCreating ? 'Creating...' : '+ Create Class'}
              </Button>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </div>
            )}

            {loading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <Card key={i} className="border-0 bg-white dark:bg-gray-800 shadow-lg">
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-3">
                            <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-xl animate-pulse"></div>
                            <div>
                              <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded-lg w-32 mb-2 animate-pulse"></div>
                              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24 animate-pulse"></div>
                            </div>
                          </div>
                          <div className="space-y-3">
                            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-40 animate-pulse"></div>
                            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-32 animate-pulse"></div>
                          </div>
                        </div>
                        <div className="flex space-x-2 ml-4">
                          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded-lg w-20 animate-pulse"></div>
                          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded-lg w-16 animate-pulse"></div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : classes.length > 0 ? (
              <div className="space-y-4">
                {classes.map((cls) => (
                  <Card key={cls.id} className="hover:shadow-xl transition-all duration-300 border-0 bg-white dark:bg-gray-800 shadow-lg hover:scale-[1.02]">
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-3">
                            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                              <span className="text-white font-bold text-lg">
                                {cls.name.charAt(0)}
                              </span>
                            </div>
                            <div>
                              <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                                {cls.name}
                              </h3>
                              <p className="text-sm text-blue-600 dark:text-blue-400 font-medium">
                                {cls.student_count || 0} students enrolled
                              </p>
                            </div>
                          </div>
                          <div className="space-y-3">
                            <div className="flex items-center space-x-2">
                              <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Invite Code:</span>
                              <code className="text-sm font-mono bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 px-3 py-1 rounded-lg border border-gray-200 dark:border-gray-600 text-gray-800 dark:text-gray-200">
                                {cls.invite_code}
                              </code>
                            </div>
                            <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                              {cls.recent_activity || 'No recent activity'}
                            </p>
                          </div>
                        </div>
                        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 ml-4">
                          <Link href={`/teacher/classes/${cls.id}`}>
                            <Button variant="primary" size="sm" className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all duration-200">
                              View Class
                            </Button>
                          </Link>
                          <Link href={`/teacher/classes/${cls.id}/lessons`}>
                            <Button variant="outline" size="sm" className="w-full sm:w-auto border-blue-200 text-blue-600 hover:bg-blue-50 dark:border-blue-700 dark:text-blue-400 dark:hover:bg-blue-900/20">
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
