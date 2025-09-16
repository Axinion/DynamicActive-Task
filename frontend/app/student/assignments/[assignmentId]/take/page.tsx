'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { getAssignment, AssignmentRead, QuestionRead } from '@/lib/api/assignments';
import { useAuthStore } from '@/lib/auth';
import { Toast } from '@/components/Toast';

interface Answer {
  question_id: number;
  answer: string | string[];
}

export default function TakeAssignmentPage() {
  const params = useParams();
  const router = useRouter();
  const assignmentId = parseInt(params.assignmentId as string);
  
  const [assignment, setAssignment] = useState<AssignmentRead | null>(null);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
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
        
        // Initialize answers array
        const initialAnswers: Answer[] = assignmentData.questions.map(question => ({
          question_id: question.id,
          answer: question.type === 'mcq' ? '' : ''
        }));
        setAnswers(initialAnswers);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch assignment');
        setToast({ message: err.message || 'Failed to fetch assignment', type: 'error' });
      } finally {
        setIsLoading(false);
      }
    };

    fetchAssignment();
  }, [token, assignmentId]);

  const updateAnswer = (questionId: number, answer: string) => {
    setAnswers(prev => prev.map(a => 
      a.question_id === questionId ? { ...a, answer } : a
    ));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !assignment) return;

    // Validation
    const unansweredQuestions = answers.filter(a => !a.answer || (typeof a.answer === 'string' && a.answer.trim() === ''));
    if (unansweredQuestions.length > 0) {
      setError('Please answer all questions before submitting');
      setToast({ message: 'Please answer all questions before submitting', type: 'error' });
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api'}/assignments/${assignmentId}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          answers: answers.map(a => ({
            question_id: a.question_id,
            answer: a.answer
          }))
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit assignment');
      }

      const result = await response.json();
      
      setToast({ message: 'Assignment submitted successfully!', type: 'success' });
      
      // Redirect to result page
      setTimeout(() => {
        router.push(`/student/assignments/${assignmentId}/result?submission_id=${result.id}`);
      }, 1500);

    } catch (err: any) {
      setError(err.message || 'Failed to submit assignment');
      setToast({ message: err.message || 'Failed to submit assignment', type: 'error' });
    } finally {
      setIsSubmitting(false);
    }
  };

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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
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
            href="/student"
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
                <Link href="/student" className="hover:text-gray-700">Dashboard</Link>
                <span>→</span>
                <Link href={`/student/classes/${assignment.class_id}/assignments`} className="hover:text-gray-700">Assignments</Link>
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
                <span className="text-gray-600">
                  Due: {formatDueDate(assignment.due_at)}
                </span>
              </div>
            </div>
            <Link
              href={`/student/classes/${assignment.class_id}/assignments`}
              className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200 flex items-center"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Assignments
            </Link>
          </div>
        </div>

        {/* Assignment Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex">
            <svg className="h-5 w-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">Instructions</h3>
              <p className="text-sm text-blue-700 mt-1">
                Answer all questions below. For multiple choice questions, select the best answer. 
                For short answer questions, provide a detailed response. You can review your answers before submitting.
              </p>
            </div>
          </div>
        </div>

        {/* Questions Form */}
        <form onSubmit={handleSubmit} className="space-y-8">
          {assignment.questions.map((question, index) => (
            <div key={question.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="mb-4">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-sm font-medium text-gray-500">Question {index + 1}</span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    question.type === 'mcq' 
                      ? 'bg-blue-100 text-blue-800' 
                      : 'bg-green-100 text-green-800'
                  }`}>
                    {question.type === 'mcq' ? 'MCQ' : 'Short Answer'}
                  </span>
                </div>
                <h3 className="text-lg font-medium text-gray-900">{question.prompt}</h3>
              </div>

              {question.type === 'mcq' && question.options ? (
                <div className="space-y-3">
                  {question.options.map((option, optionIndex) => (
                    <label key={optionIndex} className="flex items-center space-x-3 cursor-pointer">
                      <input
                        type="radio"
                        name={`question_${question.id}`}
                        value={option}
                        checked={answers.find(a => a.question_id === question.id)?.answer === option}
                        onChange={(e) => updateAnswer(question.id, e.target.value)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                      />
                      <span className="text-sm text-gray-700">
                        <span className="font-medium">{String.fromCharCode(65 + optionIndex)}.</span> {option}
                      </span>
                    </label>
                  ))}
                </div>
              ) : (
                <div>
                  <textarea
                    value={answers.find(a => a.question_id === question.id)?.answer as string || ''}
                    onChange={(e) => updateAnswer(question.id, e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={4}
                    placeholder="Enter your answer here..."
                  />
                </div>
              )}

              {question.skill_tags && question.skill_tags.length > 0 && (
                <div className="mt-4">
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

          {/* Submit Button */}
          <div className="flex justify-end space-x-3">
            <Link
              href={`/student/classes/${assignment.class_id}/assignments`}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {isSubmitting ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Submitting...
                </>
              ) : (
                'Submit Assignment'
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
