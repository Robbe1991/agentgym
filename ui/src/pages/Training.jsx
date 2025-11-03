import { Play, Pause, BarChart3 } from 'lucide-react'

export default function Training() {
  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Training Sessions
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Monitor and manage your active training sessions
        </p>
      </div>

      {/* Active Sessions */}
      <div className="space-y-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Active Training
        </h2>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Customer Support Agent - Episode 150/200
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Started 2 hours ago
              </p>
            </div>
            <button className="p-2 bg-yellow-100 dark:bg-yellow-900/30 hover:bg-yellow-200 dark:hover:bg-yellow-900/50 rounded-lg transition-colors">
              <Pause className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
            </button>
          </div>

          {/* Progress */}
          <div className="mb-4">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-gray-600 dark:text-gray-400">Progress</span>
              <span className="font-medium text-gray-900 dark:text-white">75%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all"
                style={{ width: '75%' }}
              />
            </div>
          </div>

          {/* Metrics */}
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900 dark:text-white">89.2%</p>
              <p className="text-xs text-gray-600 dark:text-gray-400">Accuracy</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900 dark:text-white">+12.5</p>
              <p className="text-xs text-gray-600 dark:text-gray-400">Avg Reward</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900 dark:text-white">0.78</p>
              <p className="text-xs text-gray-600 dark:text-gray-400">Loss</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900 dark:text-white">42m</p>
              <p className="text-xs text-gray-600 dark:text-gray-400">Time Left</p>
            </div>
          </div>
        </div>

        {/* Placeholder for charts */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Training Metrics
          </h3>
          <div className="flex items-center justify-center h-64 text-gray-400">
            <div className="text-center">
              <BarChart3 className="w-16 h-16 mx-auto mb-2" />
              <p>Chart visualization will be implemented in Issue #16</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
