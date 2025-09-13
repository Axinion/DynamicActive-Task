'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { getLesson, LessonWithClass } from '@/lib/api/lessons';
import { useAuthStore } from '@/lib/auth';
import { Toast } from '@/components/Toast';

export default function LessonDetailPage() {
  const params = useParams();
  const router = useRouter();
  const classId = parseInt(params.id as string);
  const lessonId = parseInt(params.lessonId as string);
  
  const [lesson, setLesson] = useState<LessonWithClass | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  
  const { token, user } = useAuthStore();

  useEffect(() => {
    const fetchLesson = async () => {
      if (!token || !lessonId) return;

      try {
        setIsLoading(true);
        setError(null);
        const lessonData = await getLesson(lessonId, token);
        setLesson(lessonData);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch lesson');
        setToast({ message: err.message || 'Failed to fetch lesson', type: 'error' });
      } finally {
        setIsLoading(false);
      }
    };

    fetchLesson();
  }, [token, lessonId]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
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

  if (error || !lesson) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Lesson Not Found</h1>
          <p className="text-gray-600 mb-4">{error || 'The lesson you are looking for does not exist.'}</p>
          <Link
            href={`/teacher/classes/${classId}/lessons`}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Back to Lessons
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
                <Link href={`/teacher/classes/${classId}`} className="hover:text-gray-700">Class</Link>
                <span>→</span>
                <Link href={`/teacher/classes/${classId}/lessons`} className="hover:text-gray-700">Lessons</Link>
                <span>→</span>
                <span className="text-gray-900">{lesson.title}</span>
              </nav>
              <h1 className="text-3xl font-bold text-gray-900">{lesson.title}</h1>
              <p className="text-gray-600 mt-2">
                Created on {formatDate(lesson.created_at)}
              </p>
            </div>
            <Link
              href={`/teacher/classes/${classId}/lessons`}
              className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200 flex items-center"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Lessons
            </Link>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-6">
          <nav className="flex space-x-8">
            <Link
              href={`/teacher/classes/${classId}`}
              className="text-gray-500 hover:text-gray-700 px-1 py-2 text-sm font-medium"
            >
              Overview
            </Link>
            <Link
              href={`/teacher/classes/${classId}/lessons`}
              className="text-blue-600 border-b-2 border-blue-600 px-1 py-2 text-sm font-medium"
            >
              Lessons
            </Link>
            <Link
              href={`/teacher/classes/${classId}/assignments`}
              className="text-gray-500 hover:text-gray-700 px-1 py-2 text-sm font-medium"
            >
              Assignments
            </Link>
            <Link
              href={`/teacher/classes/${classId}/gradebook`}
              className="text-gray-500 hover:text-gray-700 px-1 py-2 text-sm font-medium"
            >
              Gradebook
            </Link>
          </nav>
        </div>

        {/* Lesson Content */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6">
            {/* Skill Tags */}
            {lesson.skill_tags && lesson.skill_tags.length > 0 && (
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Skill Tags</h3>
                <div className="flex flex-wrap gap-2">
                  {lesson.skill_tags.map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Lesson Content */}
            <div className="prose max-w-none">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Lesson Content</h3>
              <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                {lesson.content}
              </div>
            </div>

            {/* Lesson Metadata */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                <div>
                  <span className="font-medium">Class:</span> {lesson.class_name}
                </div>
                <div>
                  <span className="font-medium">Created:</span> {formatDate(lesson.created_at)}
                </div>
                <div>
                  <span className="font-medium">Lesson ID:</span> {lesson.id}
                </div>
                <div>
                  <span className="font-medium">Class ID:</span> {lesson.class_id}
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
    </div>
  );
}
