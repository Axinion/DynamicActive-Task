'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { listClasses, ClassWithDetails } from '@/lib/api/classes';
import { useAuthStore } from '@/lib/auth';
import { Toast } from '@/components/Toast';

export default function ClassDetailPage() {
  const params = useParams();
  const router = useRouter();
  const classId = parseInt(params.id as string);
  
  const [classData, setClassData] = useState<ClassWithDetails | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  
  const { token, user } = useAuthStore();

  useEffect(() => {
    const fetchClass = async () => {
      if (!token) return;

      try {
        setIsLoading(true);
        setError(null);
        const classes = await listClasses(token);
        const currentClass = classes.find(c => c.id === classId);
        
        if (currentClass) {
          setClassData(currentClass);
        } else {
          setError('Class not found');
        }
      } catch (err: any) {
        setError(err.message || 'Failed to fetch class');
        setToast({ message: err.message || 'Failed to fetch class', type: 'error' });
      } finally {
        setIsLoading(false);
      }
    };

    fetchClass();
  }, [token, classId]);

  if (!user || user.role !== 'teacher') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
          <p className="text-gray-600">Only teachers can access this page.</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !classData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Class Not Found</h1>
          <p className="text-gray-600 mb-4">{error || 'The class you are looking for does not exist.'}</p>
          <Link
            href="/teacher"
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <nav className="flex items-center space-x-2 text-sm text-gray-500 mb-4">
                <Link href="/teacher" className="hover:text-gray-700">Dashboard</Link>
                <span>→</span>
                <span className="text-gray-900">{classData.name}</span>
              </nav>
              <h1 className="text-3xl font-bold text-gray-900">{classData.name}</h1>
              <p className="text-gray-600 mt-2">
                Class ID: {classData.id} • Invite Code: {classData.invite_code}
              </p>
            </div>
            <Link
              href="/teacher"
              className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200 flex items-center"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Dashboard
            </Link>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-6">
          <nav className="flex space-x-8">
            <Link
              href={`/teacher/classes/${classId}`}
              className="text-blue-600 border-b-2 border-blue-600 px-1 py-2 text-sm font-medium"
            >
              Overview
            </Link>
            <Link
              href={`/teacher/classes/${classId}/lessons`}
              className="text-gray-500 hover:text-gray-700 px-1 py-2 text-sm font-medium"
            >
              Lessons
            </Link>
            <Link
              href={`/teacher/classes/${classId}/assignments`}
              className="text-gray-500 hover:text-gray-700 px-1 py-2 text-sm font-medium"
            >
              Assignments
            </Link>
            <Link
              href={`/teacher/classes/${classId}/gradebook`}
              className="text-gray-500 hover:text-gray-700 px-1 py-2 text-sm font-medium"
            >
              Gradebook
            </Link>
          </nav>
        </div>

        {/* Overview Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Class Information */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Class Information</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Class Name</label>
                  <p className="mt-1 text-sm text-gray-900">{classData.name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Invite Code</label>
                  <div className="mt-1 flex items-center space-x-2">
                    <code className="text-sm bg-gray-100 px-2 py-1 rounded font-mono">{classData.invite_code}</code>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(classData.invite_code);
                        setToast({ message: 'Invite code copied to clipboard!', type: 'success' });
                      }}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Copy
                    </button>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Created</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {new Date(classData.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Students Enrolled</span>
                  <span className="text-lg font-semibold text-gray-900">{classData.student_count}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Class ID</span>
                  <span className="text-lg font-semibold text-gray-900">{classData.id}</span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <Link
                  href={`/teacher/classes/${classId}/lessons`}
                  className="block w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-md"
                >
                  📚 Manage Lessons
                </Link>
                <Link
                  href={`/teacher/classes/${classId}/assignments`}
                  className="block w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-md"
                >
                  📝 Manage Assignments
                </Link>
                <Link
                  href={`/teacher/classes/${classId}/gradebook`}
                  className="block w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-md"
                >
                  📊 View Gradebook
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Toast */}
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
