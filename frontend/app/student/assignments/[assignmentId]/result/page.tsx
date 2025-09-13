'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { getAssignment, AssignmentRead, QuestionRead } from '@/lib/api/assignments';
import { useAuthStore } from '@/lib/auth';
import { Toast } from '@/components/Toast';

interface SubmissionResult {
  id: number;
  assignment_id: number;
  student_id: number;
  submitted_at: string;
  ai_score: number | null;
  teacher_score: number | null;
  breakdown: Array<{
    question_id: number;
    is_correct?: boolean;
    score?: number;
  }>;
}

export default function AssignmentResultPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const assignmentId = parseInt(params.assignmentId as string);
  const submissionId = searchParams.get('submission_id');
  
  const [assignment, setAssignment] = useState<AssignmentRead | null>(null);
  const [submission, setSubmission] = useState<SubmissionResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  
  const { token, user } = useAuthStore();

  useEffect(() => {
    const fetchData = async () => {
      if (!token || !assignmentId) return;

      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch assignment details
        const assignmentData = await getAssignment(assignmentId, token);
        setAssignment(assignmentData);
        
        // If we have a submission ID, fetch submission details
        if (submissionId) {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api'}/submissions/${submissionId}`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          if (response.ok) {
            const submissionData = await response.json();
            setSubmission(submissionData);
          }
        }
      } catch (err: any) {
        setError(err.message || 'Failed to fetch assignment data');
        setToast({ message: err.message || 'Failed to fetch assignment data', type: 'error' });
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [token, assignmentId, submissionId]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getQuestionResult = (questionId: number) => {
    if (!submission?.breakdown) return null;
    return submission.breakdown.find(b => b.question_id === questionId);
  };

  const getScoreDisplay = () => {
    if (!submission) return null;
    
    if (submission.teacher_score !== null) {
      return {
        score: submission.teacher_score,
        type: 'teacher',
        label: 'Teacher Score'
      };
    } else if (submission.ai_score !== null) {
      return {
        score: submission.ai_score,
        type: 'ai',
        label: 'Auto-Graded Score'
      };
    } else {
      return {
        score: null,
        type: 'pending',
        label: 'Awaiting Grading'
      };
    }
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
            href="/student"
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const scoreDisplay = getScoreDisplay();

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
              <h1 className="text-3xl font-bold text-gray-900">Assignment Results</h1>
              <div className="flex items-center space-x-4 mt-2">
                <span className={`px-3 py-1 text-sm font-medium rounded-full ${
                  assignment.type === 'quiz' 
                    ? 'bg-blue-100 text-blue-800' 
                    : 'bg-green-100 text-green-800'
                }`}>
                  {assignment.type === 'quiz' ? 'Quiz' : 'Written Assignment'}
                </span>
                {submission && (
                  <span className="text-gray-600">
                    Submitted {formatDate(submission.submitted_at)}
                  </span>
                )}
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

        {/* Score Summary */}
        {scoreDisplay && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">{assignment.title}</h2>
              <div className="flex items-center justify-center space-x-4">
                {scoreDisplay.score !== null ? (
                  <>
                    <div className={`text-4xl font-bold ${
                      scoreDisplay.score >= 80 ? 'text-green-600' :
                      scoreDisplay.score >= 60 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {Math.round(scoreDisplay.score)}%
                    </div>
                    <div className="text-gray-600">
                      <div className="font-medium">{scoreDisplay.label}</div>
                      <div className="text-sm">
                        {scoreDisplay.type === 'ai' && 'Auto-graded'}
                        {scoreDisplay.type === 'teacher' && 'Graded by teacher'}
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-600 mb-2">Submitted</div>
                    <div className="text-gray-600">Awaiting teacher grading</div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Questions and Results */}
        <div className="space-y-6">
          {assignment.questions.map((question, index) => {
            const result = getQuestionResult(question.id);
            return (
              <div key={question.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-500">Question {index + 1}</span>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        question.type === 'mcq' 
                          ? 'bg-blue-100 text-blue-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {question.type === 'mcq' ? 'MCQ' : 'Short Answer'}
                      </span>
                    </div>
                    {result && question.type === 'mcq' && (
                      <div className={`flex items-center space-x-1 ${
                        result.is_correct ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {result.is_correct ? (
                          <>
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                            <span className="text-sm font-medium">Correct</span>
                          </>
                        ) : (
                          <>
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                            <span className="text-sm font-medium">Incorrect</span>
                          </>
                        )}
                      </div>
                    )}
                  </div>
                  <h3 className="text-lg font-medium text-gray-900">{question.prompt}</h3>
                </div>

                {question.type === 'mcq' && question.options && (
                  <div className="space-y-2 mb-4">
                    {question.options.map((option, optionIndex) => {
                      const isCorrect = question.answer_key === option;
                      const isSelected = result && 'is_correct' in result ? 
                        (result.is_correct && isCorrect) || (!result.is_correct && option === 'selected_answer') : false;
                      
                      return (
                        <div key={optionIndex} className={`p-3 rounded-md border ${
                          isCorrect 
                            ? 'bg-green-50 border-green-200' 
                            : isSelected && !isCorrect
                            ? 'bg-red-50 border-red-200'
                            : 'bg-gray-50 border-gray-200'
                        }`}>
                          <div className="flex items-center space-x-2">
                            <span className="text-sm font-medium text-gray-500 w-6">
                              {String.fromCharCode(65 + optionIndex)}.
                            </span>
                            <span className={`text-sm ${
                              isCorrect ? 'text-green-800 font-medium' : 'text-gray-700'
                            }`}>
                              {option}
                            </span>
                            {isCorrect && (
                              <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {question.type === 'short' && (
                  <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
                    <div className="text-sm text-gray-600 mb-2">Your Answer:</div>
                    <div className="text-gray-900">
                      {result && 'answer' in result ? result.answer : 'Answer submitted'}
                    </div>
                    <div className="mt-2 text-sm text-gray-500">
                      {scoreDisplay?.type === 'pending' ? 'Awaiting teacher grading' : 'Graded by teacher'}
                    </div>
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
            );
          })}
        </div>

        {/* Action Buttons */}
        <div className="mt-8 flex justify-center">
          <Link
            href={`/student/classes/${assignment.class_id}/assignments`}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 flex items-center"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            Back to Assignments
          </Link>
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
