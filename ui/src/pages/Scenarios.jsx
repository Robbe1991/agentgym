import { BookOpen, Star, Clock } from 'lucide-react'

const scenarios = [
  {
    id: 'customer_support',
    name: 'Customer Support',
    description: 'Train agents for 95% tool reliability in customer service',
    difficulty: 'beginner',
    duration: '2-3 hours',
    rating: 4.8,
    tasks: 5,
  },
  {
    id: 'code_review',
    name: 'Code Review',
    description: 'Train agents for accurate and thorough code reviews',
    difficulty: 'intermediate',
    duration: '3-4 hours',
    rating: 4.9,
    tasks: 6,
  },
  {
    id: 'data_analysis',
    name: 'Data Analysis',
    description: 'Train agents for accurate insights and visualizations',
    difficulty: 'intermediate',
    duration: '3-4 hours',
    rating: 4.7,
    tasks: 6,
  },
]

const difficultyColors = {
  beginner: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
  intermediate: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
  advanced: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
}

export default function Scenarios() {
  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Training Scenarios
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Choose a scenario to start training your AI agents
        </p>
      </div>

      {/* Scenarios Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
        {scenarios.map((scenario) => (
          <div
            key={scenario.id}
            className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow border border-gray-200 dark:border-gray-700 overflow-hidden"
          >
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
                  <BookOpen className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    difficultyColors[scenario.difficulty]
                  }`}
                >
                  {scenario.difficulty}
                </span>
              </div>

              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {scenario.name}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                {scenario.description}
              </p>

              <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-4">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>{scenario.duration}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  <span>{scenario.rating}</span>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <button className="w-full px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors">
                  Start Training
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
