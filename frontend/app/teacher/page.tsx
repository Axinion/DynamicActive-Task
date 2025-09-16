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
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header Section - Centered */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent dark:from-blue-400 dark:to-indigo-400 mb-4">
            Teacher Dashboard
          </h1>
          <p className="text-lg md:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-6">
            Manage your classes, create lessons, and track student progress with AI-powered insights.
          </p>
          <div className="flex justify-center">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 border border-gray-100 dark:border-gray-700">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">{classes.length}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Active Classes</div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content - Centered Layout */}
        <div className="max-w-4xl mx-auto">
          {/* Create Class Section - Centered */}
          <div className="text-center mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
              My Classes
            </h2>
            <Button 
              onClick={() => setIsCreateModalOpen(true)}
              disabled={isCreating}
              className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 px-8 py-3 text-lg"
            >
              {isCreating ? 'Creating...' : '+ Create New Class'}
            </Button>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-center">
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <p className="text-lg text-gray-600 dark:text-gray-400">Loading classes...</p>
            </div>
          ) : classes.length > 0 ? (
            <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
              {classes.map((cls) => (
                <Card key={cls.id} className="hover:shadow-xl transition-all duration-300 hover:scale-105 border-0 bg-white dark:bg-gray-800 shadow-lg">
                  <CardContent className="p-8 text-center">
                    <div className="mb-6">
                      <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <span className="text-white font-bold text-2xl">
                          {cls.name.charAt(0)}
                        </span>
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                        {cls.name}
                      </h3>
                      <p className="text-blue-600 dark:text-blue-400 font-medium mb-3">
                        {cls.student_count || 0} students enrolled
                      </p>
                      <div className="mb-4">
                        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Invite Code:</span>
                        <code className="block text-lg font-mono bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600 text-gray-800 dark:text-gray-200 mt-1">
                          {cls.invite_code}
                        </code>
                      </div>
                      <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                        {cls.recent_activity || 'No recent activity'}
                      </p>
                    </div>
                    <div className="space-y-3">
                      <Link href={`/teacher/classes/${cls.id}`}>
                        <Button className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all duration-200">
                          View Class
                        </Button>
                      </Link>
                      <Link href={`/teacher/classes/${cls.id}/lessons`}>
                        <Button variant="outline" className="w-full border-blue-200 text-blue-600 hover:bg-blue-50 dark:border-blue-700 dark:text-blue-400 dark:hover:bg-blue-900/20">
                          Manage Lessons
                        </Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <EmptyState
                icon="🏫"
                title="No classes yet"
                description="Create your first class to get started with teaching."
                action={
                  <Button 
                    onClick={() => setIsCreateModalOpen(true)}
                    disabled={isCreating}
                    className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 px-8 py-3 text-lg"
                  >
                    {isCreating ? 'Creating...' : 'Create Your First Class'}
                  </Button>
                }
              />
            </div>
          )}
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
