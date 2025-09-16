'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { listClasses, ClassRead } from '@/lib/api/classes';
import { listLessons, LessonRead } from '@/lib/api/lessons';
import { listAssignments, AssignmentRead } from '@/lib/api/assignments';
import { useAuthStore } from '@/lib/auth';
import { Toast } from '@/components/Toast';
import LearningPathCard from '@/components/recs/LearningPathCard';
import { SkillProgressCard } from '@/components/progress/SkillProgressCard';
import { getSkillProgress } from '@/lib/api/progress';

export default function StudentClassOverviewPage() {
  const params = useParams();
  const classId = parseInt(params.id as string);
  
  const [classData, setClassData] = useState<ClassRead | null>(null);
  const [lessons, setLessons] = useState<LessonRead[]>([]);
  const [assignments, setAssignments] = useState<AssignmentRead[]>([]);
  const [skillProgress, setSkillProgress] = useState<any>(null);
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
      
      // Fetch skill progress if user is available
      if (user) {
        try {
          const progressData = await getSkillProgress(
            { classId, studentId: user.id },
            token
          );
          setSkillProgress(progressData);
        } catch (progressErr) {
          console.error('Failed to fetch skill progress:', progressErr);
          // Don't fail the entire page load if progress fails
        }
      }
      
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
          href="/student"
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Back to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header - Centered */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent dark:from-purple-400 dark:to-pink-400 mb-4">
            {classData.name}
          </h1>
          <p className="text-lg md:text-xl text-gray-600 dark:text-gray-400">
            Your learning dashboard
          </p>
        </div>

      {/* Learning Path Card */}
      <div className="mb-8">
        <LearningPathCard classId={classId} />
      </div>

      {/* Skill Progress Card */}
      <div id="progress" className="mb-8">
        <SkillProgressCard
          data={skillProgress?.skill_mastery || []}
          overallMastery={skillProgress?.overall_mastery_avg || 0}
          totalResponses={skillProgress?.total_responses || 0}
          onPracticeClick={() => {
            // Navigate to assignments page for practice
            window.location.href = `/student/classes/${classId}/assignments`;
          }}
          loading={isLoading}
        />
      </div>

        {/* Main Content - Centered */}
        <div className="max-w-4xl mx-auto">
          {/* Quick Actions - Centered */}
          <div className="text-center mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
              Quick Actions
            </h2>
            <div className="grid md:grid-cols-2 gap-6 max-w-2xl mx-auto">
              <Link
                href={`/student/classes/${classId}/lessons`}
                className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-8 hover:shadow-xl transition-all duration-300 hover:scale-105 text-center"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">📚</span>
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">Lessons</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {lessons.length} lesson{lessons.length !== 1 ? 's' : ''} available
                </p>
              </Link>

              <Link
                href={`/student/classes/${classId}/assignments`}
                className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-8 hover:shadow-xl transition-all duration-300 hover:scale-105 text-center"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">📝</span>
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">Assignments</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {assignments.length} assignment{assignments.length !== 1 ? 's' : ''} available
                </p>
              </Link>
            </div>
          </div>

          {/* Recent Activity - Centered */}
          <div className="text-center mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
              Recent Activity
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-4xl mx-auto">
              {/* Recent Lessons */}
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
                <div className="text-center mb-4">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Recent Lessons</h3>
                  <Link
                    href={`/student/classes/${classId}/lessons`}
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
                      <div key={lesson.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">{lesson.title}</h4>
                          <p className="text-xs text-gray-500 dark:text-gray-400">Created {formatDate(lesson.created_at)}</p>
                        </div>
                        <Link
                          href={`/student/classes/${classId}/lessons/${lesson.id}`}
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                        >
                          Read
                        </Link>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Recent Assignments */}
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
                <div className="text-center mb-4">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Recent Assignments</h3>
                  <Link
                    href={`/student/classes/${classId}/assignments`}
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
                    {assignments.slice(0, 3).map((assignment) => {
                      const status = getAssignmentStatus(assignment);
                      return (
                        <div key={assignment.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                          <div>
                            <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">{assignment.title}</h4>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              {assignment.questions.length} questions • Due: {formatDueDate(assignment.due_at)}
                            </p>
                          </div>
                          <Link
                            href={`/student/assignments/${assignment.id}/take`}
                            className={`text-sm px-3 py-1 rounded-md font-medium ${
                              status === 'overdue'
                                ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                                : status === 'due-soon'
                                ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
                                : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
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
          </div>
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
