import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            Welcome to K12 LMS
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            A modern learning management system designed for K-12 education with AI-powered features for personalized learning.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-2xl mx-auto">
          <Card className="text-center hover:shadow-medium transition-shadow duration-200">
            <CardHeader>
              <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">👨‍🏫</span>
              </div>
              <CardTitle className="text-2xl">I&apos;m a Teacher</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Create classes, build lessons, assign work, and track student progress with AI-powered insights.
              </p>
              <Link href="/login?role=teacher">
                <Button size="lg" className="w-full">
                  Teacher Login
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="text-center hover:shadow-medium transition-shadow duration-200">
            <CardHeader>
              <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">👨‍🎓</span>
              </div>
              <CardTitle className="text-2xl">I&apos;m a Student</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Join classes, complete assignments, and receive personalized learning recommendations.
              </p>
              <Link href="/login?role=student">
                <Button size="lg" className="w-full">
                  Student Login
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        <div className="text-center mt-12">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Demo credentials: teacher@example.com / student@example.com (password: pass)
          </p>
        </div>
      </div>
    </div>
  );
}