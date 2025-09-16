'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { getGradebook, GradebookEntry } from '@/lib/api/gradebook';
import { getAssignment, AssignmentRead } from '@/lib/api/assignments';
import { useAuthStore } from '@/lib/auth';
import { Toast } from '@/components/Toast';
import MisconceptionsPanel from '@/components/insights/MisconceptionsPanel';
import OverrideDrawer from '@/components/gradebook/OverrideDrawer';
import { GradingBadge, getGradingStatus } from '@/components/ui/GradingBadge';
import { exportGradebookCSV } from '@/lib/api/export';

interface SubmissionDetail {
  id: number;
  assignment_id: number;
  student_id: number;
  submitted_at: string;
  ai_score: number | null;
  teacher_score: number | null;
  responses: Array<{
    id: number;
    question_id: number;
    type: 'mcq' | 'short';
    student_answer: string;
    ai_score: number | null;
    ai_feedback: string | null;
    teacher_score: number | null;
    teacher_feedback: string | null;
    question_prompt: string;
  }>;
}

export default function TeacherGradebookPage() {
  const params = useParams();
  const classId = parseInt(params.id as string);
  
  const [gradebookEntries, setGradebookEntries] = useState<GradebookEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  
  // Side panel state
  const [selectedEntry, setSelectedEntry] = useState<GradebookEntry | null>(null);
  const [submissionDetail, setSubmissionDetail] = useState<SubmissionDetail | null>(null);
  const [assignmentDetail, setAssignmentDetail] = useState<AssignmentRead | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [isSidePanelOpen, setIsSidePanelOpen] = useState(false);
  
  // Override drawer state
  const [isOverrideDrawerOpen, setIsOverrideDrawerOpen] = useState(false);
  const [overrideSubmission, setOverrideSubmission] = useState<SubmissionDetail | null>(null);
  const [overrideResponses, setOverrideResponses] = useState<any[]>([]);
  
  const { token, user } = useAuthStore();

  const fetchGradebook = useCallback(async () => {
    if (!token || !classId) return;

    try {
      setIsLoading(true);
      setError(null);
      const gradebookData = await getGradebook({ classId }, token);
      setGradebookEntries(gradebookData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch gradebook');
      setToast({ message: err.message || 'Failed to fetch gradebook', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  }, [token, classId]);

  useEffect(() => {
    fetchGradebook();
  }, [fetchGradebook]);

  const handleRowClick = async (entry: GradebookEntry) => {
    if (!token) return;

    setSelectedEntry(entry);
    setIsSidePanelOpen(true);
    setIsLoadingDetail(true);

    try {
      // Fetch assignment details
      const assignment = await getAssignment(entry.assignment_id, token);
      setAssignmentDetail(assignment);

      // Fetch submission details (if endpoint exists)
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api'}/submissions/${entry.assignment_id}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const submissionData = await response.json();
          setSubmissionDetail(submissionData);
        }
      } catch (err) {
        // Submission detail endpoint might not exist yet
        console.log('Submission detail endpoint not available');
      }
    } catch (err: any) {
      setToast({ message: err.message || 'Failed to fetch submission details', type: 'error' });
    } finally {
      setIsLoadingDetail(false);
    }
  };

  const closeSidePanel = () => {
    setIsSidePanelOpen(false);
    setSelectedEntry(null);
    setSubmissionDetail(null);
    setAssignmentDetail(null);
  };

  const handleOverrideClick = async (entry: GradebookEntry, event: React.MouseEvent) => {
    event.stopPropagation(); // Prevent row click
    
    if (!token) return;

    try {
      // Fetch assignment details
      const assignment = await getAssignment(entry.assignment_id, token);
      
      // Fetch submission details
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api'}/submissions/${entry.assignment_id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const submissionData = await response.json();
        
        // Create mock responses data for the override drawer
        const mockResponses = assignment.questions.map((question, index) => ({
          id: index + 1, // Mock response ID
          question_id: question.id,
          type: question.type,
          student_answer: `Mock answer for question ${index + 1}`,
          ai_score: Math.random() * 100,
          ai_feedback: `AI feedback for question ${index + 1}`,
          teacher_score: null,
          teacher_feedback: null,
          question_prompt: question.prompt
        }));

        setOverrideSubmission({
          id: entry.assignment_id,
          assignment_id: entry.assignment_id,
          student_id: entry.student_id,
          submitted_at: entry.submitted_at,
          ai_score: entry.ai_score,
          teacher_score: entry.teacher_score,
          responses: mockResponses
        });
        setOverrideResponses(mockResponses);
        setIsOverrideDrawerOpen(true);
      } else {
        setToast({ message: 'Failed to fetch submission details for override', type: 'error' });
      }
    } catch (err: any) {
      setToast({ message: err.message || 'Failed to open override drawer', type: 'error' });
    }
  };

  const closeOverrideDrawer = () => {
    setIsOverrideDrawerOpen(false);
    setOverrideSubmission(null);
    setOverrideResponses([]);
  };

  const handleOverrideSuccess = () => {
    setToast({ message: 'Scores updated successfully!', type: 'success' });
    fetchGradebook(); // Refresh gradebook data
  };

  const handleExportCSV = async () => {
    if (!token) {
      setToast({ message: 'Authentication required', type: 'error' });
      return;
    }

    try {
      await exportGradebookCSV({ classId, token });
      setToast({ message: 'Gradebook exported successfully!', type: 'success' });
    } catch (err: any) {
      console.error('Failed to export gradebook:', err);
      setToast({ message: err.message || 'Failed to export gradebook', type: 'error' });
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatScore = (score: number | null) => {
    if (score === null) return '—';
    return `${Math.round(score)}%`;
  };

  const getScoreColor = (score: number | null) => {
    if (score === null) return 'text-gray-500';
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
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
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Gradebook</h1>
            <p className="text-gray-600 mt-2">
              View and manage student submissions and grades
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleExportCSV}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export CSV
            </button>
            <Link
              href={`/teacher/classes/${classId}/insights`}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              View Insights
            </Link>
          </div>
        </div>
      </div>

      {/* Misconceptions Panel */}
      <div className="mb-8">
        <MisconceptionsPanel classId={classId} />
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
                <h3 className="text-sm font-medium text-red-800">Error loading gradebook</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        ) : gradebookEntries.length === 0 ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No submissions yet</h3>
            <p className="mt-1 text-sm text-gray-500">Students haven't submitted any assignments yet.</p>
          </div>
        ) : (
          <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Student
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Assignment
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Submitted At
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      AI Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Teacher Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {gradebookEntries
                    .sort((a, b) => new Date(b.submitted_at).getTime() - new Date(a.submitted_at).getTime())
                    .map((entry, index) => (
                    <tr
                      key={`${entry.student_id}-${entry.assignment_id}`}
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => handleRowClick(entry)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-6 w-6">
                            <div className="h-6 w-6 rounded-full bg-blue-100 flex items-center justify-center">
                              <span className="text-sm font-medium text-blue-600">
                                {entry.student_name.charAt(0).toUpperCase()}
                              </span>
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {entry.student_name}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{entry.title}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatDate(entry.submitted_at)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-sm font-medium ${getScoreColor(entry.ai_score)}`}>
                          {formatScore(entry.ai_score)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          <span className={`text-sm font-medium ${getScoreColor(entry.teacher_score)}`}>
                            {formatScore(entry.teacher_score)}
                          </span>
                          <GradingBadge 
                            status={getGradingStatus(entry.ai_score, entry.teacher_score, false)} 
                            showIcon={false}
                          />
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={(e) => handleOverrideClick(entry, e)}
                          className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-md transition-colors"
                          title="Override scores"
                        >
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                          Override
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Side Panel */}
        {isSidePanelOpen && (
          <div className="fixed inset-0 z-50 overflow-hidden">
            <div className="absolute inset-0 bg-gray-500 bg-opacity-75" onClick={closeSidePanel}></div>
            <div className="absolute right-0 top-0 h-full w-96 bg-white shadow-xl">
              <div className="h-full flex flex-col">
                {/* Header */}
                <div className="px-6 py-4 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium text-gray-900">Submission Details</h3>
                    <button
                      onClick={closeSidePanel}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto px-6 py-4">
                  {isLoadingDetail ? (
                    <div className="flex justify-center items-center py-8">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    </div>
                  ) : selectedEntry && assignmentDetail ? (
                    <div className="space-y-6">
                      {/* Student Info */}
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Student</h4>
                        <div className="flex items-center space-x-3">
                          <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <span className="text-sm font-medium text-blue-600">
                              {selectedEntry.student_name.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {selectedEntry.student_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              Submitted {formatDate(selectedEntry.submitted_at)}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Assignment Info */}
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Assignment</h4>
                        <div className="text-sm text-gray-900">{assignmentDetail.title}</div>
                        <div className="text-sm text-gray-500">
                          {assignmentDetail.questions.length} questions
                        </div>
                      </div>

                      {/* Scores */}
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Scores</h4>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <div className="text-xs text-gray-500">AI Score</div>
                            <div className={`text-lg font-medium ${getScoreColor(selectedEntry.ai_score)}`}>
                              {formatScore(selectedEntry.ai_score)}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">Teacher Score</div>
                            <div className={`text-lg font-medium ${getScoreColor(selectedEntry.teacher_score)}`}>
                              {formatScore(selectedEntry.teacher_score)}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Questions and Responses */}
                      {assignmentDetail.questions.map((question, index) => (
                        <div key={question.id} className="border border-gray-200 rounded-lg p-4">
                          <div className="mb-3">
                            <div className="flex items-center space-x-2 mb-1">
                              <span className="text-sm font-medium text-gray-500">Q{index + 1}</span>
                              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                question.type === 'mcq' 
                                  ? 'bg-blue-100 text-blue-800' 
                                  : 'bg-green-100 text-green-800'
                              }`}>
                                {question.type === 'mcq' ? 'MCQ' : 'Short Answer'}
                              </span>
                            </div>
                            <h5 className="text-sm font-medium text-gray-900">{question.prompt}</h5>
                          </div>

                          {question.type === 'mcq' && question.options && (
                            <div className="space-y-2">
                              {question.options.map((option, optionIndex) => (
                                <div key={optionIndex} className={`p-2 rounded-md border ${
                                  question.answer_key === option 
                                    ? 'bg-green-50 border-green-200' 
                                    : 'bg-gray-50 border-gray-200'
                                }`}>
                                  <div className="flex items-center space-x-2">
                                    <span className="text-xs text-gray-500 w-4">
                                      {String.fromCharCode(65 + optionIndex)}.
                                    </span>
                                    <span className={`text-sm ${
                                      question.answer_key === option ? 'text-green-800 font-medium' : 'text-gray-700'
                                    }`}>
                                      {option}
                                    </span>
                                    {question.answer_key === option && (
                                      <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                      </svg>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}

                          {question.type === 'short' && (
                            <div className="bg-gray-50 border border-gray-200 rounded-md p-3">
                              <div className="text-xs text-gray-500 mb-1">Student Answer:</div>
                              <div className="text-sm text-gray-900">
                                {submissionDetail?.responses.find(r => r.question_id === question.id)?.student_answer || 'No answer provided'}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <p>Unable to load submission details</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Override Drawer */}
        <OverrideDrawer
          isOpen={isOverrideDrawerOpen}
          onClose={closeOverrideDrawer}
          submission={overrideSubmission}
          responses={overrideResponses}
          onSuccess={handleOverrideSuccess}
        />

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
