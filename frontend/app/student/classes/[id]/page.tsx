'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { listClasses, ClassRead } from '@/lib/api/classes';
import { listLessons, LessonRead } from '@/lib/api/lessons';
import { listAssignments, AssignmentRead } from '@/lib/api/assignments';
import { useAuthStore } from '@/lib/auth';
import { Toast } from '@/components/Toast';

export default function StudentClassOverviewPage() {
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatDueDate = (dateString?: string) => {
    if (!dateString) return 'No due date';
    const date = new Date(dateString);
    const now = new Date();
    const isOverdue = date < now;
    const isDueSoon = date.getTime() - now.getTime() < 24 * 60 * 60 * 1000; // 24 hours
    
    return (
      <span className={
        isOverdue 
          ? 'text-red-600 font-medium' 
          : isDueSoon 
            ? 'text-orange-600 font-medium' 
            : 'text-gray-600'
      }>
        {formatDate(dateString)}
        {isOverdue && ' (Overdue)'}
        {isDueSoon && !isOverdue && ' (Due Soon)'}
      </span>
    );
  };

  const getAssignmentStatus = (assignment: AssignmentRead) => {
    if (!assignment.due_at) return 'available';
    
    const dueDate = new Date(assignment.due_at);
    const now = new Date();
    
    if (dueDate < now) return 'overdue';
    if (dueDate.getTime() - now.getTime() < 24 * 60 * 60 * 1000) return 'due-soon';
    return 'available';
  };

  if (!user || user.role !== 'student') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
          <p className="text-gray-600">Only students can access this page.</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !classData) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Class Not Found</h1>
        <p className="text-gray-600 mb-4">{error || 'The class you are looking for does not exist.'}</p>
        <Link
          href="/student"
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
              Your learning dashboard
            </p>
          </div>
        </div>
      </div>

      {/* Class Information */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Class Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Class Name</label>
            <p className="mt-1 text-sm text-gray-900">{classData.name}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Joined</label>
            <p className="mt-1 text-sm text-gray-900">{formatDate(classData.created_at)}</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Link
          href={`/student/classes/${classId}/lessons`}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Lessons</h3>
              <p className="text-sm text-gray-500">
                {lessons.length} lesson{lessons.length !== 1 ? 's' : ''} available
              </p>
            </div>
          </div>
        </Link>

        <Link
          href={`/student/classes/${classId}/assignments`}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Assignments</h3>
              <p className="text-sm text-gray-500">
                {assignments.length} assignment{assignments.length !== 1 ? 's' : ''} available
              </p>
            </div>
          </div>
        </Link>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Lessons */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Recent Lessons</h2>
            <Link
              href={`/student/classes/${classId}/lessons`}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              View All
            </Link>
          </div>
          
          {lessons.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <svg className="mx-auto h-8 w-8 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
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
                    href={`/student/classes/${classId}/lessons/${lesson.id}`}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Read
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
              href={`/student/classes/${classId}/assignments`}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              View All
            </Link>
          </div>
          
          {assignments.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <svg className="mx-auto h-8 w-8 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-sm">No assignments yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {assignments.slice(0, 3).map((assignment) => {
                const status = getAssignmentStatus(assignment);
                return (
                  <div key={assignment.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">{assignment.title}</h3>
                      <p className="text-xs text-gray-500">
                        {assignment.questions.length} questions • Due: {formatDueDate(assignment.due_at)}
                      </p>
                    </div>
                    <Link
                      href={`/student/assignments/${assignment.id}/take`}
                      className={`text-sm px-3 py-1 rounded-md font-medium ${
                        status === 'overdue'
                          ? 'bg-red-100 text-red-800'
                          : status === 'due-soon'
                          ? 'bg-orange-100 text-orange-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}
                    >
                      {status === 'overdue' ? 'Complete' : 'Start'}
                    </Link>
                  </div>
                );
              })}
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
