import { TrendingUp, Users, Target, Zap, Play } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const stats = [
  {
    name: 'Active Training Sessions',
    value: '3',
    change: '+12%',
    changeType: 'positive',
    icon: Zap,
  },
  {
    name: 'Trained Models',
    value: '24',
    change: '+8',
    changeType: 'positive',
    icon: Target,
  },
  {
    name: 'Available Scenarios',
    value: '3',
    change: 'All ready',
    changeType: 'neutral',
    icon: Users,
  },
  {
    name: 'Average Accuracy',
    value: '89.2%',
    change: '+5.4%',
    changeType: 'positive',
    icon: TrendingUp,
  },
]

export default function Dashboard() {
  const navigate = useNavigate()

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Welcome to AgentGym. Monitor your agent training progress.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 mb-8 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div
              key={stat.name}
              className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {stat.name}
                  </p>
                  <p className="mt-2 text-3xl font-semibold text-gray-900 dark:text-white">
                    {stat.value}
                  </p>
                </div>
                <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
                  <Icon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                </div>
              </div>
              <div className="mt-4">
                <span
                  className={`text-sm font-medium ${
                    stat.changeType === 'positive'
                      ? 'text-green-600 dark:text-green-400'
                      : stat.changeType === 'negative'
                      ? 'text-red-600 dark:text-red-400'
                      : 'text-gray-600 dark:text-gray-400'
                  }`}
                >
                  {stat.change}
                </span>
                <span className="text-sm text-gray-600 dark:text-gray-400 ml-2">
                  from last month
                </span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Training */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Recent Training Sessions
          </h2>
          <div className="space-y-3">
            {[
              {
                name: 'Customer Support Agent',
                scenario: 'customer_support',
                progress: 85,
                status: 'In Progress',
              },
              {
                name: 'Code Reviewer',
                scenario: 'code_review',
                progress: 100,
                status: 'Completed',
              },
              {
                name: 'Data Analyst',
                scenario: 'data_analysis',
                progress: 45,
                status: 'In Progress',
              },
            ].map((session, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
              >
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {session.name}
                  </p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    {session.scenario}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-24 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{ width: `${session.progress}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium text-gray-600 dark:text-gray-400 w-16">
                    {session.progress}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Start */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Quick Start
          </h2>
          <div className="space-y-3">
            <button
              onClick={() => navigate('/scenarios')}
              className="w-full flex items-center justify-between p-4 bg-primary-50 dark:bg-primary-900/20 hover:bg-primary-100 dark:hover:bg-primary-900/30 rounded-lg border border-primary-200 dark:border-primary-800 transition-colors"
            >
              <div className="text-left">
                <p className="text-sm font-medium text-primary-900 dark:text-primary-100">
                  Start New Training
                </p>
                <p className="text-xs text-primary-600 dark:text-primary-400">
                  Create a new training session
                </p>
              </div>
              <Play className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            </button>
            <button
              onClick={() => navigate('/scenarios')}
              className="w-full flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <div className="text-left">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  Browse Scenarios
                </p>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Explore available training scenarios
                </p>
              </div>
              <Users className="w-5 h-5 text-gray-400" />
            </button>
            <button
              onClick={() => navigate('/models')}
              className="w-full flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <div className="text-left">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  View Models
                </p>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Check your trained models
                </p>
              </div>
              <Target className="w-5 h-5 text-gray-400" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
