'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/lib/auth';
import RouteGuard from '@/components/RouteGuard';

export default function TeacherClassLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const params = useParams();
  const classId = params.id as string;
  const { user } = useAuthStore();

  return (
    <RouteGuard requiredRole="teacher">
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Navigation Tabs */}
          <div className="mb-6">
            <nav className="flex space-x-8">
              <Link
                href={`/teacher/classes/${classId}`}
                className="text-gray-500 hover:text-gray-700 px-1 py-2 text-sm font-medium border-b-2 border-transparent hover:border-gray-300"
              >
                Overview
              </Link>
              <Link
                href={`/teacher/classes/${classId}/lessons`}
                className="text-gray-500 hover:text-gray-700 px-1 py-2 text-sm font-medium border-b-2 border-transparent hover:border-gray-300"
              >
                Lessons
              </Link>
              <Link
                href={`/teacher/classes/${classId}/assignments`}
                className="text-gray-500 hover:text-gray-700 px-1 py-2 text-sm font-medium border-b-2 border-transparent hover:border-gray-300"
              >
                Assignments
              </Link>
              <Link
                href={`/teacher/classes/${classId}/gradebook`}
                className="text-gray-500 hover:text-gray-700 px-1 py-2 text-sm font-medium border-b-2 border-transparent hover:border-gray-300"
              >
                Gradebook
              </Link>
              <Link
                href={`/teacher/classes/${classId}/insights`}
                className="text-gray-500 hover:text-gray-700 px-1 py-2 text-sm font-medium border-b-2 border-transparent hover:border-gray-300"
              >
                Insights
              </Link>
            </nav>
          </div>

          {/* Page Content */}
          {children}
        </div>
      </div>
    </RouteGuard>
  );
}
