'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { listClasses, ClassRead } from '@/lib/api/classes';
import { listLessons, LessonRead } from '@/lib/api/lessons';
import { listAssignments, AssignmentRead } from '@/lib/api/assignments';
import { useAuthStore } from '@/lib/auth';
import { Toast } from '@/components/Toast';

export default function TeacherClassOverviewPage() {
  const params = useParams();
  const classId = parseInt(params.id as string);
  
  const [classData, setClassData] = useState<ClassRead | null>(null);
  const [lessons, setLessons] = useState<LessonRead[]>([]);
  const [assignments, setAssignments] = useState<AssignmentRead[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  
  const { token, user } = useAuthStore();

  const fetchClassData = useCallback(async () => {
    if (!token || !classId) return;

    try {
      setIsLoading(true);
      setError(null);
      
      // Fetch class data
      const classesData = await listClasses(token);
      const currentClass = classesData.find(c => c.id === classId);
      
      if (!currentClass) {
        throw new Error('Class not found');
      }
      
      setClassData(currentClass);
      
      // Fetch lessons and assignments in parallel
      const [lessonsData, assignmentsData] = await Promise.all([
        listLessons({ classId }, token),
        listAssignments({ classId }, token)
      ]);
      
      setLessons(lessonsData);
      setAssignments(assignmentsData);
      
    } catch (err: any) {
      setError(err.message || 'Failed to fetch class data');
      setToast({ message: err.message || 'Failed to fetch class data', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  }, [token, classId]);

  useEffect(() => {
    fetchClassData();
  }, [fetchClassData]);

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setToast({ message: `${label} copied to clipboard!`, type: 'success' });
    } catch (err) {
      setToast({ message: `Failed to copy ${label.toLowerCase()}`, type: 'error' });
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

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
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !classData) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Class Not Found</h1>
        <p className="text-gray-600 mb-4">{error || 'The class you are looking for does not exist.'}</p>
        <Link
          href="/teacher"
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Back to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{classData.name}</h1>
            <p className="text-gray-600 mt-2">
              Class overview and quick actions
            </p>
          </div>
        </div>
      </div>

      {/* Class Information */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Class Details */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Class Information</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Class Name</label>
              <p className="mt-1 text-sm text-gray-900">{classData.name}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Invite Code</label>
              <div className="mt-1 flex items-center space-x-2">
                <code className="px-3 py-2 bg-gray-100 text-gray-900 rounded-md font-mono text-sm">
                  {classData.invite_code}
                </code>
                <button
                  onClick={() => copyToClipboard(classData.invite_code, 'Invite code')}
                  className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100"
                  title="Copy invite code"
                >
                  Copy
                </button>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Created</label>
              <p className="mt-1 text-sm text-gray-900">{formatDate(classData.created_at)}</p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link
              href={`/teacher/classes/${classId}/lessons/new`}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-center"
            >
              Create Lesson
            </Link>
            <Link
              href={`/teacher/classes/${classId}/assignments/new`}
              className="w-full bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-center"
            >
              Create Assignment
            </Link>
            <Link
              href={`/teacher/classes/${classId}/gradebook`}
              className="w-full bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 text-center"
            >
              View Gradebook
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Lessons */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Recent Lessons</h2>
            <Link
              href={`/teacher/classes/${classId}/lessons`}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              View All
            </Link>
          </div>
          
          {lessons.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p className="text-sm">No lessons yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {lessons.slice(0, 3).map((lesson) => (
                <div key={lesson.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">{lesson.title}</h3>
                    <p className="text-xs text-gray-500">Created {formatDate(lesson.created_at)}</p>
                  </div>
                  <Link
                    href={`/teacher/classes/${classId}/lessons/${lesson.id}`}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    View
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Assignments */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Recent Assignments</h2>
            <Link
              href={`/teacher/classes/${classId}/assignments`}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              View All
            </Link>
          </div>
          
          {assignments.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p className="text-sm">No assignments yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {assignments.slice(0, 3).map((assignment) => (
                <div key={assignment.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">{assignment.title}</h3>
                    <p className="text-xs text-gray-500">
                      {assignment.questions.length} questions • Created {formatDate(assignment.created_at)}
                    </p>
                  </div>
                  <Link
                    href={`/teacher/assignments/${assignment.id}`}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    View
                  </Link>
                </div>
              ))}
            </div>
          )}
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
  );
}