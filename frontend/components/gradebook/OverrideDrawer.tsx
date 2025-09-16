'use client';

import { useState, useEffect } from 'react';
import { overrideResponse, overrideSubmission, OverrideRequest } from '@/lib/api/insights';
import { useAuthStore } from '@/lib/auth';

interface QuestionResponse {
  id: number;
  question_id: number;
  type: 'mcq' | 'short';
  student_answer: string;
  ai_score: number | null;
  ai_feedback: string | null;
  teacher_score: number | null;
  teacher_feedback: string | null;
  question_prompt: string;
}

interface Submission {
  id: number;
  student_id: number;
  student_name: string;
  submitted_at: string;
  ai_score: number | null;
  teacher_score: number | null;
  assignment_title: string;
}

interface OverrideDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  submission: Submission | null;
  responses: QuestionResponse[];
  onSuccess: () => void;
}

export default function OverrideDrawer({ 
  isOpen, 
  onClose, 
  submission, 
  responses, 
  onSuccess 
}: OverrideDrawerProps) {
  const [questionOverrides, setQuestionOverrides] = useState<Record<number, {
    teacher_score: number;
    teacher_feedback: string;
  }>>({});
  const [overallScore, setOverallScore] = useState<number>(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'questions' | 'overall'>('questions');
  
  const { token } = useAuthStore();

  useEffect(() => {
    if (isOpen && submission) {
      // Initialize question overrides
      const initialOverrides: Record<number, { teacher_score: number; teacher_feedback: string }> = {};
      responses.forEach(response => {
        initialOverrides[response.id] = {
          teacher_score: response.teacher_score || response.ai_score || 0,
          teacher_feedback: response.teacher_feedback || ''
        };
      });
      setQuestionOverrides(initialOverrides);
      
      // Initialize overall score
      setOverallScore(submission.teacher_score || submission.ai_score || 0);
    }
  }, [isOpen, submission, responses]);

  const handleQuestionScoreChange = (responseId: number, score: number) => {
    setQuestionOverrides(prev => ({
      ...prev,
      [responseId]: {
        ...prev[responseId],
        teacher_score: Math.max(0, Math.min(1, score))
      }
    }));
  };

  const handleQuestionFeedbackChange = (responseId: number, feedback: string) => {
    setQuestionOverrides(prev => ({
      ...prev,
      [responseId]: {
        ...prev[responseId],
        teacher_feedback: feedback
      }
    }));
  };

  const handleOverallScoreChange = (score: number) => {
    setOverallScore(Math.max(0, Math.min(100, score)));
  };

  const handleSaveQuestionOverrides = async () => {
    if (!submission || !token) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const promises = Object.entries(questionOverrides).map(async ([responseId, override]) => {
        const response = responses.find(r => r.id === parseInt(responseId));
        if (!response) return;

        const overrideData: OverrideRequest = {
          teacher_score: override.teacher_score,
          teacher_feedback: override.teacher_feedback.trim() || undefined
        };

        return overrideResponse(parseInt(responseId), overrideData, token);
      });

      await Promise.all(promises);
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save overrides');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSaveOverallScore = async () => {
    if (!submission || !token) return;

    setIsSubmitting(true);
    setError(null);

    try {
      await overrideSubmission(submission.id, { teacher_score: overallScore }, token);
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save overall score');
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatScore = (score: number | null) => {
    if (score === null) return 'N/A';
    return `${Math.round(score * 100)}%`;
  };

  const formatOverallScore = (score: number | null) => {
    if (score === null) return 'N/A';
    return `${Math.round(score)}%`;
  };

  if (!isOpen || !submission) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose}></div>
      
      {/* Drawer */}
      <div className="absolute right-0 top-0 h-full w-full max-w-2xl bg-white shadow-xl">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Override Scores</h2>
              <p className="text-sm text-gray-600">
                {submission.student_name} • {submission.assignment_title}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
              aria-label="Close drawer"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('questions')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'questions'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Per-Question Overrides
              </button>
              <button
                onClick={() => setActiveTab('overall')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'overall'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Overall Score
              </button>
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {error && (
              <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-4">
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

            {activeTab === 'questions' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Question-by-Question Overrides</h3>
                  <p className="text-sm text-gray-600 mb-6">
                    Override individual question scores and add teacher feedback.
                  </p>
                </div>

                {responses.map((response, index) => (
                  <div key={response.id} className="bg-gray-50 rounded-lg p-4">
                    <div className="mb-3">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900">Question {index + 1}</h4>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          response.type === 'mcq' 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {response.type === 'mcq' ? 'MCQ' : 'Short Answer'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 mb-3">{response.question_prompt}</p>
                    </div>

                    <div className="mb-3">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Student Answer
                      </label>
                      <div className="bg-white border border-gray-200 rounded-md p-3">
                        <p className="text-sm text-gray-900">{response.student_answer}</p>
                      </div>
                    </div>

                    <div className="mb-3">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        AI Score: {formatScore(response.ai_score)}
                      </label>
                      {response.ai_feedback && (
                        <div className="bg-blue-50 border border-blue-200 rounded-md p-3 mb-3">
                          <p className="text-sm text-blue-700">{response.ai_feedback}</p>
                        </div>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Teacher Score (0-1)
                        </label>
                        <input
                          type="number"
                          min="0"
                          max="1"
                          step="0.01"
                          value={questionOverrides[response.id]?.teacher_score || 0}
                          onChange={(e) => handleQuestionScoreChange(response.id, parseFloat(e.target.value) || 0)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Teacher Feedback
                        </label>
                        <textarea
                          value={questionOverrides[response.id]?.teacher_feedback || ''}
                          onChange={(e) => handleQuestionFeedbackChange(response.id, e.target.value)}
                          rows={3}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="Add teacher feedback..."
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'overall' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Overall Submission Score</h3>
                  <p className="text-sm text-gray-600 mb-6">
                    Set the final score for this submission.
                  </p>
                </div>

                <div className="bg-gray-50 rounded-lg p-6">
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Current AI Score: {formatOverallScore(submission.ai_score)}
                    </label>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Current Teacher Score: {formatOverallScore(submission.teacher_score)}
                    </label>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      New Teacher Score (0-100%)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="1"
                      value={overallScore}
                      onChange={(e) => handleOverallScoreChange(parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-gray-200 p-6">
            <div className="flex justify-end space-x-3">
              <button
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                onClick={activeTab === 'questions' ? handleSaveQuestionOverrides : handleSaveOverallScore}
                disabled={isSubmitting}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {isSubmitting ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Saving...
                  </>
                ) : (
                  'Save Changes'
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
