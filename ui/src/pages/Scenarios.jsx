import { useState } from 'react'
import { BookOpen, Star, Clock, Search, Filter, Play, CheckCircle, Target, Loader } from 'lucide-react'
import { trainingAPI } from '../api/client'
import { useNavigate } from 'react-router-dom'

const scenarios = [
  {
    id: 'customer_support',
    name: 'Customer Support',
    description: 'Train agents to handle customer inquiries with high reliability. Focus on tool usage, escalation handling, and response quality.',
    difficulty: 'beginner',
    duration: '2-3 hours',
    rating: 4.8,
    tasks: 5,
    frameworks: ['LangChain', 'AutoGen', 'CrewAI'],
    metrics: ['Tool Reliability', 'Response Quality', 'Resolution Rate'],
    features: ['5 sample customer issues', '8 support actions', 'Real-time feedback'],
  },
  {
    id: 'code_review',
    name: 'Code Review',
    description: 'Train agents to perform thorough code reviews. Detect bugs, suggest improvements, and provide actionable feedback.',
    difficulty: 'intermediate',
    duration: '3-4 hours',
    rating: 4.9,
    tasks: 6,
    frameworks: ['LangChain', 'AutoGen', 'CrewAI'],
    metrics: ['Review Accuracy', 'False Positive Rate', 'Completeness'],
    features: ['6 sample PRs', '11 review actions', 'Severity-based rewards'],
  },
  {
    id: 'data_analysis',
    name: 'Data Analysis',
    description: 'Train agents to analyze data, generate insights, and create visualizations. Master statistical analysis and reporting.',
    difficulty: 'intermediate',
    duration: '3-4 hours',
    rating: 4.7,
    tasks: 6,
    frameworks: ['LangChain', 'AutoGen', 'CrewAI'],
    metrics: ['Analysis Accuracy', 'Data Quality', 'Insight Quality'],
    features: ['6 analysis tasks', '15 analysis actions', 'Visualization scoring'],
  },
]

const difficultyColors = {
  beginner: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
  intermediate: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
  advanced: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
}

export default function Scenarios() {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedFramework, setSelectedFramework] = useState('All')
  const [startingScenario, setStartingScenario] = useState(null)
  const [error, setError] = useState(null)

  const frameworks = ['All', 'LangChain', 'AutoGen', 'CrewAI']

  const handleStartTraining = async (scenarioId) => {
    setStartingScenario(scenarioId)
    setError(null)

    try {
      // Get settings from localStorage (if they were saved in Settings page)
      const savedSettings = localStorage.getItem('agentgym-settings')
      const settings = savedSettings ? JSON.parse(savedSettings) : {
        framework: 'LangChain',
        maxEpisodes: 200,
        learningRate: 0.001,
      }

      // Start training session
      const response = await trainingAPI.start({
        scenario_id: scenarioId,
        framework: settings.framework,
        max_episodes: settings.maxEpisodes,
        learning_rate: settings.learningRate,
      })

      // Store session ID in localStorage for the Training page to pick up
      localStorage.setItem('active-training-session', response.session_id)

      // Navigate to training page
      navigate('/training')
    } catch (err) {
      setError(`Failed to start training: ${err.message}`)
      console.error('Failed to start training:', err)
    } finally {
      setStartingScenario(null)
    }
  }

  const filteredScenarios = scenarios.filter((scenario) => {
    const matchesSearch =
      scenario.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      scenario.description.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesFramework =
      selectedFramework === 'All' || scenario.frameworks.includes(selectedFramework)

    return matchesSearch && matchesFramework
  })

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

      {/* Search and Filters */}
      <div className="mb-6 space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search scenarios..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        {/* Framework Filter */}
        <div className="flex items-center gap-3">
          <Filter className="w-5 h-5 text-gray-500" />
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Framework:
          </span>
          <div className="flex gap-2">
            {frameworks.map((framework) => (
              <button
                key={framework}
                onClick={() => setSelectedFramework(framework)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedFramework === framework
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {framework}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Results Count */}
      <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
        Showing {filteredScenarios.length} of {scenarios.length} scenarios
      </div>

      {/* Scenarios Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
        {filteredScenarios.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <BookOpen className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              No scenarios found. Try adjusting your filters.
            </p>
          </div>
        ) : (
          filteredScenarios.map((scenario) => (
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

                {/* Framework Support */}
                <div className="mb-4">
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
                    Supported Frameworks:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {scenario.frameworks.map((framework) => (
                      <span
                        key={framework}
                        className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded text-xs font-medium"
                      >
                        {framework}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Key Metrics */}
                <div className="mb-4">
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
                    Key Metrics:
                  </p>
                  <div className="space-y-1">
                    {scenario.metrics.slice(0, 3).map((metric, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                        <CheckCircle className="w-3 h-3 text-green-500" />
                        <span>{metric}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Features */}
                <div className="mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex flex-wrap gap-2">
                    {scenario.features.map((feature, idx) => (
                      <span
                        key={idx}
                        className="text-xs text-gray-500 dark:text-gray-400"
                      >
                        • {feature}
                      </span>
                    ))}
                  </div>
                </div>

                <button
                  onClick={() => handleStartTraining(scenario.id)}
                  disabled={startingScenario === scenario.id}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
                >
                  {startingScenario === scenario.id ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      Starting...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      Start Training
                    </>
                  )}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
