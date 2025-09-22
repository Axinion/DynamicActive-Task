'use client';

import { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { getAssignment, AssignmentRead } from '@/lib/api/assignments';
import { useAuthStore } from '@/lib/auth';
import { Toast } from '@/components/Toast';
import { makeHint, formatAIScore, getConfidenceMessage, HintData } from '@/lib/ai/hints';
import { AITooltip } from '@/components/ui/InfoTooltip';
import GradingBadge, { getGradingStatus } from '@/components/ui/GradingBadge';
import { AssignmentPrivacyNote } from '@/components/ui/PrivacyNote';

interface SubmissionResult {
  id: number;
  assignment_id: number;
  student_id: number;
  submitted_at: string;
  ai_score: number | null;
  teacher_score: number | null;
  breakdown: Array<{
    question_id: number;
    type: 'mcq' | 'short';
    score?: number;
    ai_feedback?: string;
    matched_keywords?: string[];
    is_mcq_correct?: boolean;
    student_answer?: string;
  }>;
}

export default function AssignmentResultPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const assignmentId = parseInt(params.assignmentId as string);
  const submissionId = searchParams.get('submission_id');
  
  const [assignment, setAssignment] = useState<AssignmentRead | null>(null);
  const [submission, setSubmission] = useState<SubmissionResult | null>(null);
  const [recommendations, setRecommendations] = useState<Array<{lesson_id: number; title: string; reason: string}>>([]);
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
        
        // Fetch recommendations for the class
        try {
          const recResponse = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api'}/recommendations?class_id=${assignmentData.class_id}`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          if (recResponse.ok) {
            const recData = await recResponse.json();
            setRecommendations(recData.recommendations || []);
          }
        } catch (err) {
          // Recommendations are optional, don't fail the whole page
          console.warn('Failed to fetch recommendations:', err);
        }
      } catch (err: unknown) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch assignment data';
        setError(errorMessage);
        setToast({ message: errorMessage, type: 'error' });
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

  const generateHintForQuestion = (question: {type: string; answer_key?: string | string[]; skill_tags?: string[]}, result: {student_answer?: string; matched_keywords?: string[]; ai_feedback?: string}) => {
    if (!result || question.type !== 'short' || !result.ai_feedback) return null;
    
    // Handle answer_key which can be string or string[]
    const modelAnswer = Array.isArray(question.answer_key) 
      ? question.answer_key.join(' ') 
      : question.answer_key || '';
    
    const hintData: HintData = {
      studentAnswer: result.student_answer || '',
      modelAnswer: modelAnswer,
      matchedKeywords: result.matched_keywords || [],
      rubricKeywords: question.skill_tags || [],
      linkedLesson: recommendations.length > 0 ? {
        id: recommendations[0].lesson_id,
        title: recommendations[0].title,
        url: `/student/classes/${assignment?.class_id}/lessons/${recommendations[0].lesson_id}`
      } : undefined
    };
    
    return makeHint(hintData);
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
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-600 dark:text-gray-400">Loading results...</p>
        </div>
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
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header - Centered */}
        <div className="text-center mb-12">
          <nav className="flex items-center justify-center space-x-2 text-sm text-gray-500 mb-6">
            <Link href="/student" className="hover:text-gray-700">Dashboard</Link>
            <span>→</span>
            <Link href={`/student/classes/${assignment.class_id}/assignments`} className="hover:text-gray-700">Assignments</Link>
            <span>→</span>
            <span className="text-gray-900">{assignment.title}</span>
          </nav>
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent dark:from-purple-400 dark:to-pink-400 mb-4">
            Assignment Results
          </h1>
          <div className="flex items-center justify-center space-x-4">
            <span className={`px-4 py-2 text-sm font-medium rounded-full ${
              assignment.type === 'quiz' 
                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' 
                : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
            }`}>
              {assignment.type === 'quiz' ? 'Quiz' : 'Written Assignment'}
            </span>
            {submission && (
              <span className="text-gray-600 dark:text-gray-400">
                Submitted {formatDate(submission.submitted_at)}
              </span>
            )}
          </div>
        </div>

        {/* Score Summary - Centered */}
        {scoreDisplay && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-8 mb-8 max-w-2xl mx-auto">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">{assignment.title}</h2>
              <div className="flex items-center justify-center space-x-6">
                {scoreDisplay.score !== null ? (
                  <>
                    <div className={`text-6xl font-bold ${
                      scoreDisplay.score >= 80 ? 'text-green-600' :
                      scoreDisplay.score >= 60 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {Math.round(scoreDisplay.score)}%
                    </div>
                    <div className="text-gray-600 dark:text-gray-400">
                      <div className="font-medium text-lg">{scoreDisplay.label}</div>
                      <div className="text-sm">
                        {scoreDisplay.type === 'ai' && 'Auto-graded'}
                        {scoreDisplay.type === 'teacher' && 'Graded by teacher'}
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="text-center">
                    <div className="text-3xl font-bold text-gray-600 dark:text-gray-400 mb-2">Submitted</div>
                    <div className="text-gray-600 dark:text-gray-400">Awaiting teacher grading</div>
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
                        result.is_mcq_correct ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {result.is_mcq_correct ? (
                          <>
                            <span className="text-sm font-medium">Correct</span>
                          </>
                        ) : (
                          <>
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
                      // Handle answer_key which can be string or string[]
                      const correctAnswers = Array.isArray(question.answer_key) 
                        ? question.answer_key 
                        : [question.answer_key];
                      const isCorrect = correctAnswers.includes(option);
                      const isSelected = result && result.is_mcq_correct !== undefined ? 
                        (result.is_mcq_correct && isCorrect) || (!result.is_mcq_correct && option === result.student_answer) : false;
                      
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
                              <span className="text-green-600 text-sm">✓</span>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {question.type === 'short' && (
                  <div className="space-y-4">
                    <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
                      <div className="text-sm text-gray-600 mb-2">Your Answer:</div>
                      <div className="text-gray-900">
                        {result && result.student_answer ? result.student_answer : 'Answer submitted'}
                      </div>
                    </div>
                    
                    {/* AI Feedback and Score */}
                    {result && result.ai_feedback && (
                      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-2">
                            <h4 className="text-sm font-medium text-blue-800">AI Feedback</h4>
                            <AITooltip
                              title="How AI Scoring Works"
                              explanation="AI scores are calculated using semantic similarity (70%) and keyword matching (30%). The system compares your answer to the model answer and checks for key concepts. Teachers can review and adjust these scores."
                            >
                              <span className="text-blue-600 cursor-help">ℹ️</span>
                            </AITooltip>
                          </div>
                          {result.score !== null && result.score !== undefined && (
                            <div className="flex items-center space-x-2">
                              <AITooltip
                                title="Your Score"
                                explanation={`You scored ${formatAIScore(result.score / 100).percentage} on this question. This score is based on how well your answer matches the expected response and includes key concepts.`}
                              >
                                <span className={`text-lg font-bold ${formatAIScore(result.score / 100).color} cursor-help`}>
                                  {formatAIScore(result.score / 100).percentage}
                                </span>
                              </AITooltip>
                              <span className="text-sm text-blue-600">
                                {formatAIScore(result.score / 100).message}
                              </span>
                              <GradingBadge 
                                status={getGradingStatus(result.score, null, false)} 
                                className="ml-2"
                              />
                            </div>
                          )}
                        </div>
                        <p className="text-sm text-blue-700 mb-3">{result.ai_feedback}</p>
                        
                        {/* Confidence Message */}
                        {result.score !== null && result.score !== undefined && (
                          <p className="text-sm text-blue-600 italic">
                            {getConfidenceMessage(result.score / 100)}
                          </p>
                        )}
                      </div>
                    )}
                    
                    {/* AI Hints */}
                    {result && question.type === 'short' && (() => {
                      const hint = generateHintForQuestion(question, result);
                      if (!hint) return null;
                      
                      return (
                        <div className="bg-green-50 border border-green-200 rounded-md p-4">
                          <h4 className="text-sm font-medium text-green-800 mb-3">💡 Learning Tips</h4>
                          
                          {/* Praise */}
                          {hint.praise && (
                            <div className="mb-3">
                              <p className="text-sm text-green-700">{hint.praise}</p>
                            </div>
                          )}
                          
                          {/* Suggestions */}
                          {hint.suggestions.length > 0 && (
                            <div className="mb-3">
                              <h5 className="text-xs font-medium text-green-800 mb-2">Suggestions for improvement:</h5>
                              <ul className="space-y-1">
                                {hint.suggestions.map((suggestion, index) => (
                                  <li key={index} className="text-sm text-green-700 flex items-start">
                                    <span className="text-green-500 mr-2">•</span>
                                    {suggestion}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {/* Linked Lesson */}
                          {hint.linkedLesson && (
                            <div className="mt-3 pt-3 border-t border-green-200">
                              <p className="text-xs text-green-600 mb-2">Recommended lesson:</p>
                              <Link
                                href={hint.linkedLesson.url}
                                className="inline-flex items-center text-sm text-green-700 hover:text-green-800 font-medium"
                              >
                                {hint.linkedLesson.title}
                              </Link>
                            </div>
                          )}
                        </div>
                      );
                    })()}
                    
                    {/* Fallback for no AI feedback */}
                    {(!result || !result.ai_feedback) && (
                      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                        <div className="flex items-center">
                          <svg className="h-5 w-5 text-yellow-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <div>
                            <h4 className="text-sm font-medium text-yellow-800">Awaiting Grading</h4>
                            <p className="text-sm text-yellow-700">Your answer has been submitted and is being reviewed.</p>
                          </div>
                        </div>
                      </div>
                    )}
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

        {/* Recommendations Section */}
        {recommendations.length > 0 && (
          <div className="mt-8 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
            <div className="text-center mb-4">
              <h3 className="text-lg font-medium text-purple-900 mb-2">🎯 Personalized Learning</h3>
              <p className="text-sm text-purple-700">
                Based on your performance, we&apos;ve identified some lessons that can help you improve!
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              {recommendations.slice(0, 2).map((rec, index) => (
                <div key={index} className="bg-white rounded-md p-4 border border-purple-100">
                  <h4 className="font-medium text-gray-900 mb-2">{rec.title}</h4>
                  <p className="text-sm text-gray-600 mb-3">{rec.reason}</p>
                  <Link
                    href={`/student/classes/${assignment.class_id}/lessons/${rec.lesson_id}`}
                    className="inline-flex items-center text-sm text-purple-600 hover:text-purple-800 font-medium"
                  >
                    View Lesson
                  </Link>
                </div>
              ))}
            </div>
            
            <div className="text-center">
              <Link
                href={`/student/classes/${assignment.class_id}/recommendations`}
                className="inline-flex items-center bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 text-sm font-medium"
              >
                View All Recommendations
              </Link>
            </div>
          </div>
        )}

        {/* Privacy Note */}
        <div className="mt-6">
          <AssignmentPrivacyNote />
        </div>

        {/* Action Buttons - Centered */}
        <div className="mt-12 text-center">
          <div className="flex flex-col sm:flex-row justify-center gap-4 max-w-2xl mx-auto">
            <Link
              href={`/student/classes/${assignment.class_id}/assignments`}
              className="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-8 py-3 rounded-xl hover:bg-gray-200 dark:hover:bg-gray-600 transition-all duration-200 font-medium"
            >
              Back to Assignments
            </Link>
            
            <Link
              href={`/student/classes/${assignment.class_id}#progress`}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-3 rounded-xl transition-all duration-200 font-medium shadow-lg hover:shadow-xl"
            >
              See your progress
            </Link>
            
            {recommendations.length > 0 && (
              <Link
                href={`/student/classes/${assignment.class_id}/recommendations`}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-3 rounded-xl transition-all duration-200 font-medium shadow-lg hover:shadow-xl"
              >
                Review Recommended Lessons
              </Link>
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
    </div>
  );
}
