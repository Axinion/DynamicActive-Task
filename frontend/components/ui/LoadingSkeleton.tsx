'use client';

interface LoadingSkeletonProps {
  className?: string;
  lines?: number;
  height?: string;
}

export function LoadingSkeleton({ className = '', lines = 1, height = 'h-4' }: LoadingSkeletonProps) {
  return (
    <div className={`animate-pulse ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className={`bg-gray-200 rounded ${height} ${
            index < lines - 1 ? 'mb-2' : ''
          }`}
        />
      ))}
    </div>
  );
}

export function InsightsLoadingSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <LoadingSkeleton className="w-24 h-8" lines={1} height="h-8" />
          <LoadingSkeleton className="w-6 h-6 rounded-full" lines={1} height="h-6" />
        </div>
        <LoadingSkeleton className="w-32 h-8" lines={1} height="h-8" />
      </div>

      {/* Time window skeleton */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <LoadingSkeleton className="w-64 h-4" lines={1} />
      </div>

      {/* Misconceptions skeleton */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-6">
          <LoadingSkeleton className="w-48 h-6" lines={1} height="h-6" />
          <LoadingSkeleton className="w-6 h-6 rounded-full" lines={1} height="h-6" />
        </div>

        <div className="space-y-6">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex items-start gap-4">
                {/* Rank badge skeleton */}
                <LoadingSkeleton className="w-8 h-8 rounded-full" lines={1} height="h-8" />
                
                {/* Content skeleton */}
                <div className="flex-1 space-y-3">
                  <div className="flex items-center gap-3">
                    <LoadingSkeleton className="w-48 h-6" lines={1} height="h-6" />
                    <LoadingSkeleton className="w-20 h-5" lines={1} height="h-5" />
                  </div>
                  
                  {/* Example answers skeleton */}
                  <div className="space-y-2">
                    <LoadingSkeleton className="w-32 h-4" lines={1} />
                    {Array.from({ length: 2 }).map((_, exampleIndex) => (
                      <div key={exampleIndex} className="bg-gray-50 rounded p-3">
                        <LoadingSkeleton className="w-full h-3 mb-1" lines={1} height="h-3" />
                        <LoadingSkeleton className="w-3/4 h-3 mb-2" lines={1} height="h-3" />
                        <div className="flex items-center gap-2">
                          <LoadingSkeleton className="w-16 h-4" lines={1} height="h-4" />
                          <LoadingSkeleton className="w-24 h-3" lines={1} height="h-3" />
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {/* Mini-lessons skeleton */}
                  <div className="space-y-2">
                    <LoadingSkeleton className="w-40 h-4" lines={1} />
                    <div className="flex flex-wrap gap-2">
                      {Array.from({ length: 2 }).map((_, lessonIndex) => (
                        <LoadingSkeleton key={lessonIndex} className="w-32 h-6" lines={1} height="h-6" />
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function ProgressLoadingSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="space-y-6">
        {/* Header skeleton */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <LoadingSkeleton className="w-32 h-6" lines={1} height="h-6" />
            <LoadingSkeleton className="w-6 h-6 rounded-full" lines={1} height="h-6" />
          </div>
          <LoadingSkeleton className="w-24 h-8" lines={1} height="h-8" />
        </div>

        {/* Overall progress skeleton */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <LoadingSkeleton className="w-32 h-4" lines={1} />
            <LoadingSkeleton className="w-20 h-4" lines={1} />
          </div>
          <div className="flex items-center gap-3">
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div className="bg-gray-300 h-2 rounded-full w-3/4" />
            </div>
            <LoadingSkeleton className="w-12 h-4" lines={1} />
          </div>
          <LoadingSkeleton className="w-48 h-3 mt-1" lines={1} height="h-3" />
        </div>

        {/* Chart skeleton */}
        <div>
          <LoadingSkeleton className="w-32 h-4 mb-3" lines={1} />
          <div className="h-64 bg-gray-100 rounded-lg flex items-end justify-around p-4">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="flex flex-col items-center gap-2">
                <div 
                  className="bg-gray-300 rounded-t w-8"
                  style={{ height: `${Math.random() * 200 + 50}px` }}
                />
                <LoadingSkeleton className="w-12 h-3" lines={1} height="h-3" />
              </div>
            ))}
          </div>
        </div>

        {/* Skills list skeleton */}
        <div>
          <LoadingSkeleton className="w-32 h-4 mb-3" lines={1} />
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <LoadingSkeleton className="w-32 h-4 mb-1" lines={1} />
                  <LoadingSkeleton className="w-20 h-3" lines={1} height="h-3" />
                </div>
                <div className="flex items-center gap-2">
                  <LoadingSkeleton className="w-20 h-5" lines={1} height="h-5" />
                  <LoadingSkeleton className="w-12 h-4" lines={1} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
