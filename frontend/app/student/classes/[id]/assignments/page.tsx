'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { listAssignments, AssignmentRead } from '@/lib/api/assignments';
import { useAuthStore } from '@/lib/auth';
import { Toast } from '@/components/Toast';

export default function StudentAssignmentsPage() {
  const params = useParams();
  const classId = parseInt(params.id as string);
  
  const [assignments, setAssignments] = useState<AssignmentRead[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  
  const { token, user } = useAuthStore();

  const fetchAssignments = useCallback(async () => {
    if (!token || !classId) return;

    try {
      setIsLoading(true);
      setError(null);
      const assignmentsData = await listAssignments({ classId }, token);
      setAssignments(assignmentsData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch assignments');
      setToast({ message: err.message || 'Failed to fetch assignments', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  }, [token, classId]);

  useEffect(() => {
    fetchAssignments();
  }, [fetchAssignments]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
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

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Assignments</h1>
            <p className="text-gray-600 mt-2">
              Complete your assignments and track your progress
            </p>
          </div>
        </div>
      </div>

        {/* Content */}
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <svg className="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error loading assignments</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        ) : assignments.length === 0 ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No assignments yet</h3>
            <p className="mt-1 text-sm text-gray-500">Your teacher hasn't assigned any work yet.</p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {assignments.map((assignment) => {
              const status = getAssignmentStatus(assignment);
              return (
                <div key={assignment.id} className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                  <div className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          {assignment.title}
                        </h3>
                        
                        <div className="space-y-2 text-sm text-gray-600">
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                              assignment.type === 'quiz' 
                                ? 'bg-blue-100 text-blue-800' 
                                : 'bg-green-100 text-green-800'
                            }`}>
                              {assignment.type === 'quiz' ? 'Quiz' : 'Written'}
                            </span>
                            <span>{assignment.questions.length} questions</span>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            <span>Due: {formatDueDate(assignment.due_at)}</span>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span>Created {formatDate(assignment.created_at)}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-4 flex items-center justify-between">
                      <Link
                        href={`/student/assignments/${assignment.id}/take`}
                        className={`px-4 py-2 rounded-md font-medium text-sm flex items-center ${
                          status === 'overdue'
                            ? 'bg-red-600 text-white hover:bg-red-700'
                            : status === 'due-soon'
                            ? 'bg-orange-600 text-white hover:bg-orange-700'
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                      >
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {status === 'overdue' ? 'Complete Now' : 'Start Assignment'}
                      </Link>
                      
                      {status === 'overdue' && (
                        <span className="text-xs text-red-600 font-medium">
                          Overdue
                        </span>
                      )}
                      {status === 'due-soon' && (
                        <span className="text-xs text-orange-600 font-medium">
                          Due Soon
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

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
