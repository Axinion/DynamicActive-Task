'use client';

import { Header } from '@/components/Header';
import { Sidebar } from '@/components/Sidebar';
import { RouteGuard } from '@/components/RouteGuard';
import { useAuthStore } from '@/lib/auth';

export default function TeacherLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, logout } = useAuthStore();

  return (
    <RouteGuard requiredRole="teacher">
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Header user={user || undefined} onLogout={logout} />
        <div className="flex">
          <Sidebar role="teacher" />
          <main className="flex-1">
            {children}
          </main>
        </div>
      </div>
    </RouteGuard>
  );
}
