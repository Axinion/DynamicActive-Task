import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="max-w-6xl mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-3xl flex items-center justify-center mb-6">
            <span className="text-xl">🎓</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent dark:from-blue-400 dark:to-indigo-400 mb-6">
            Welcome to K12 LMS
          </h1>
          <p className="text-lg md:text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto leading-relaxed">
            A modern learning management system designed for K-12 education with AI-powered features for personalized learning, intelligent grading, and comprehensive progress tracking.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 md:gap-8 max-w-4xl mx-auto">
          <Card className="text-center hover:shadow-2xl transition-all duration-300 border-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm hover:scale-105">
            <CardHeader className="pb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <span className="text-xl">👨‍🏫</span>
              </div>
              <CardTitle className="text-3xl font-bold text-gray-900 dark:text-gray-100">I&apos;m a Teacher</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 dark:text-gray-400 mb-8 text-lg leading-relaxed">
                Create classes, build lessons, assign work, and track student progress with AI-powered insights and automated grading.
              </p>
              <Link href="/login?role=teacher">
                <Button size="lg" className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-200">
                  Teacher Login
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="text-center hover:shadow-2xl transition-all duration-300 border-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm hover:scale-105">
            <CardHeader className="pb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <span className="text-xl">👨‍🎓</span>
              </div>
              <CardTitle className="text-3xl font-bold text-gray-900 dark:text-gray-100">I&apos;m a Student</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 dark:text-gray-400 mb-8 text-lg leading-relaxed">
                Join classes, complete assignments, and receive personalized learning recommendations with AI feedback.
              </p>
              <Link href="/login?role=student">
                <Button size="lg" className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-200">
                  Student Login
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        <div className="text-center mt-16">
          <div className="bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 max-w-2xl mx-auto border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
              Demo Access
            </h3>
            <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <p><strong>Teacher:</strong> teacher@example.com / pass</p>
              <p><strong>Student:</strong> student@example.com / pass</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}