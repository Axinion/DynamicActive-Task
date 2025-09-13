'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { createAssignment, AssignmentCreate, QuestionCreate } from '@/lib/api/assignments';
import { useAuthStore } from '@/lib/auth';
import QuestionBuilder from '@/components/assignments/QuestionBuilder';
import { Toast } from '@/components/Toast';

export default function NewAssignmentPage() {
  const params = useParams();
  const router = useRouter();
  const classId = parseInt(params.id as string);
  
  const [formData, setFormData] = useState({
    title: '',
    type: 'quiz' as 'quiz' | 'written',
    due_at: ''
  });
  const [questions, setQuestions] = useState<QuestionCreate[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  
  const { token, user } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    // Validation
    if (!formData.title.trim()) {
      setError('Assignment title is required');
      return;
    }

    if (questions.length === 0) {
      setError('At least one question is required');
      return;
    }

    // Validate questions
    for (let i = 0; i < questions.length; i++) {
      const question = questions[i];
      if (!question.prompt.trim()) {
        setError(`Question ${i + 1}: Prompt is required`);
        return;
      }
      
      if (question.type === 'mcq') {
        if (!question.options || question.options.length < 2) {
          setError(`Question ${i + 1}: At least 2 options are required for MCQ`);
          return;
        }
        
        if (!question.options.every(opt => opt.trim())) {
          setError(`Question ${i + 1}: All options must be filled`);
          return;
        }
        
        if (!question.answer_key) {
          setError(`Question ${i + 1}: Please select the correct answer`);
          return;
        }
      }
    }

    setIsLoading(true);
    setError(null);

    try {
      const payload: AssignmentCreate = {
        class_id: classId,
        title: formData.title.trim(),
        type: formData.type,
        due_at: formData.due_at || undefined,
        questions: questions
      };

      const createdAssignment = await createAssignment(payload, token);
      
      setToast({ message: 'Assignment created successfully!', type: 'success' });
      
      // Redirect to assignment detail page
      setTimeout(() => {
        router.push(`/teacher/assignments/${createdAssignment.id}`);
      }, 1500);

    } catch (err: any) {
      setError(err.message || 'Failed to create assignment');
      setToast({ message: err.message || 'Failed to create assignment', type: 'error' });
    } finally {
      setIsLoading(false);
    }
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

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <nav className="flex items-center space-x-2 text-sm text-gray-500 mb-4">
            <Link href="/teacher" className="hover:text-gray-700">Dashboard</Link>
            <span>→</span>
            <Link href={`/teacher/classes/${classId}`} className="hover:text-gray-700">Class</Link>
            <span>→</span>
            <Link href={`/teacher/classes/${classId}/assignments`} className="hover:text-gray-700">Assignments</Link>
            <span>→</span>
            <span className="text-gray-900">New Assignment</span>
          </nav>
          <h1 className="text-3xl font-bold text-gray-900">Create New Assignment</h1>
          <p className="text-gray-600 mt-2">
            Build an assignment with multiple choice and short answer questions
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Assignment Details */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Assignment Details</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                  Assignment Title *
                </label>
                <input
                  type="text"
                  id="title"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter assignment title"
                  disabled={isLoading}
                />
              </div>

              <div>
                <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-1">
                  Assignment Type
                </label>
                <select
                  id="type"
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value as 'quiz' | 'written' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isLoading}
                >
                  <option value="quiz">Quiz</option>
                  <option value="written">Written Assignment</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label htmlFor="due_at" className="block text-sm font-medium text-gray-700 mb-1">
                  Due Date (Optional)
                </label>
                <input
                  type="datetime-local"
                  id="due_at"
                  value={formData.due_at}
                  onChange={(e) => setFormData({ ...formData, due_at: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isLoading}
                />
              </div>
            </div>
          </div>

          {/* Question Builder */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <QuestionBuilder questions={questions} onChange={setQuestions} />
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <svg className="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Error</h3>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-3">
            <Link
              href={`/teacher/classes/${classId}/assignments`}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={isLoading || !formData.title.trim() || questions.length === 0}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating...
                </>
              ) : (
                'Create Assignment'
              )}
            </button>
          </div>
        </form>

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
