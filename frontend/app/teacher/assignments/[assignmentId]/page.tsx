'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { getAssignment, AssignmentRead } from '@/lib/api/assignments';
import { useAuthStore } from '@/lib/auth';
import { Toast } from '@/components/Toast';

export default function AssignmentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const assignmentId = parseInt(params.assignmentId as string);
  
  const [assignment, setAssignment] = useState<AssignmentRead | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  
  const { token, user } = useAuthStore();

  useEffect(() => {
    const fetchAssignment = async () => {
      if (!token || !assignmentId) return;

      try {
        setIsLoading(true);
        setError(null);
        const assignmentData = await getAssignment(assignmentId, token);
        setAssignment(assignmentData);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch assignment');
        setToast({ message: err.message || 'Failed to fetch assignment', type: 'error' });
      } finally {
        setIsLoading(false);
      }
    };

    fetchAssignment();
  }, [token, assignmentId]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDueDate = (dateString?: string) => {
    if (!dateString) return 'No due date set';
    const date = new Date(dateString);
    const now = new Date();
    const isOverdue = date < now;
    
    return (
      <span className={isOverdue ? 'text-red-600 font-medium' : 'text-gray-600'}>
        {formatDate(dateString)}
        {isOverdue && ' (Overdue)'}
      </span>
    );
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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !assignment) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Assignment Not Found</h1>
          <p className="text-gray-600 mb-4">{error || 'The assignment you are looking for does not exist.'}</p>
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
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <nav className="flex items-center space-x-2 text-sm text-gray-500 mb-4">
                <Link href="/teacher" className="hover:text-gray-700">Dashboard</Link>
                <span>→</span>
                <Link href={`/teacher/classes/${assignment.class_id}`} className="hover:text-gray-700">Class</Link>
                <span>→</span>
                <Link href={`/teacher/classes/${assignment.class_id}/assignments`} className="hover:text-gray-700">Assignments</Link>
                <span>→</span>
                <span className="text-gray-900">{assignment.title}</span>
              </nav>
              <h1 className="text-3xl font-bold text-gray-900">{assignment.title}</h1>
              <div className="flex items-center space-x-4 mt-2">
                <span className={`px-3 py-1 text-sm font-medium rounded-full ${
                  assignment.type === 'quiz' 
                    ? 'bg-blue-100 text-blue-800' 
                    : 'bg-green-100 text-green-800'
                }`}>
                  {assignment.type === 'quiz' ? 'Quiz' : 'Written Assignment'}
                </span>
                <span className="text-gray-600">
                  {assignment.questions.length} questions
                </span>
              </div>
            </div>
            <div className="flex space-x-3">
              <Link
                href={`/teacher/classes/${assignment.class_id}/gradebook`}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 flex items-center"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Open Gradebook
              </Link>
              <Link
                href={`/teacher/classes/${assignment.class_id}/assignments`}
                className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200 flex items-center"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Back to Assignments
              </Link>
            </div>
          </div>
        </div>

        {/* Assignment Details */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Assignment Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">Due Date</label>
              <p className="mt-1 text-sm text-gray-900">{formatDueDate(assignment.due_at)}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Created</label>
              <p className="mt-1 text-sm text-gray-900">{formatDate(assignment.created_at)}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Assignment ID</label>
              <p className="mt-1 text-sm text-gray-900">{assignment.id}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Class ID</label>
              <p className="mt-1 text-sm text-gray-900">{assignment.class_id}</p>
            </div>
          </div>
        </div>

        {/* Questions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Questions ({assignment.questions.length})</h2>
          
          {assignment.questions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No questions in this assignment.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {assignment.questions.map((question, index) => (
                <div key={question.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-500">Q{index + 1}</span>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        question.type === 'mcq' 
                          ? 'bg-blue-100 text-blue-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {question.type === 'mcq' ? 'MCQ' : 'Short Answer'}
                      </span>
                    </div>
                  </div>

                  <div className="mb-4">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Question</h3>
                    <p className="text-gray-900">{question.prompt}</p>
                  </div>

                  {question.type === 'mcq' && question.options && (
                    <div className="mb-4">
                      <h3 className="text-sm font-medium text-gray-700 mb-2">Answer Options</h3>
                      <div className="space-y-2">
                        {question.options.map((option, optionIndex) => (
                          <div key={optionIndex} className="flex items-center space-x-2">
                            <span className="text-sm text-gray-500 w-6">
                              {String.fromCharCode(65 + optionIndex)}.
                            </span>
                            <span className={`text-sm ${
                              question.answer_key === option 
                                ? 'text-green-600 font-medium' 
                                : 'text-gray-600'
                            }`}>
                              {option}
                              {question.answer_key === option && ' ✓'}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {question.skill_tags && question.skill_tags.length > 0 && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-700 mb-2">Skill Tags</h3>
                      <div className="flex flex-wrap gap-1">
                        {question.skill_tags.map((tag, tagIndex) => (
                          <span
                            key={tagIndex}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
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
