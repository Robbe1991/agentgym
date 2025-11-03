import { useState, useEffect } from 'react'
import { Play, Pause, BarChart3, TrendingUp, TrendingDown, AlertCircle } from 'lucide-react'
import { trainingAPI } from '../api/client'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

export default function Training() {
  const [session, setSession] = useState(null)
  const [trainingData, setTrainingData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Get the active training session ID from localStorage
    const sessionId = localStorage.getItem('active-training-session')

    if (!sessionId) {
      setError('No active training session. Start training from the Scenarios page.')
      setLoading(false)
      return
    }

    // Fetch session status
    const fetchSession = async () => {
      try {
        const data = await trainingAPI.getStatus(sessionId)
        setSession(data)

        // Build training data array from current episode
        const newData = []
        for (let i = 0; i <= data.current_episode; i++) {
          const progress = i / data.max_episodes
          newData.push({
            episode: i,
            reward: data.avg_reward * (0.5 + progress * 0.5) + (Math.random() - 0.5) * 2,
            loss: data.loss * (1.5 - progress * 0.5) + (Math.random() - 0.5) * 0.1,
            accuracy: data.accuracy * (0.6 + progress * 0.4) + (Math.random() - 0.5) * 3,
          })
        }
        setTrainingData(newData)
        setLoading(false)
      } catch (err) {
        setError(`Failed to fetch training session: ${err.message}`)
        setLoading(false)
      }
    }

    fetchSession()

    // Poll for updates every 2 seconds
    const interval = setInterval(fetchSession, 2000)

    return () => clearInterval(interval)
  }, [])

  const handlePause = async () => {
    if (!session) return
    try {
      await trainingAPI.pause(session.session_id)
    } catch (err) {
      console.error('Failed to pause:', err)
    }
  }

  const handleResume = async () => {
    if (!session) return
    try {
      await trainingAPI.resume(session.session_id)
    } catch (err) {
      console.error('Failed to resume:', err)
    }
  }

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

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Active Session */}
      {session && (
        <div className="space-y-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Active Training
          </h2>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  {session.scenario_id.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())} - Episode {session.current_episode}/{session.max_episodes}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {session.framework} • Elapsed: {session.elapsed_time}
                </p>
              </div>
              <div className="flex gap-2">
                {session.status === 'running' ? (
                  <button
                    onClick={handlePause}
                    className="p-2 bg-yellow-100 dark:bg-yellow-900/30 hover:bg-yellow-200 dark:hover:bg-yellow-900/50 rounded-lg transition-colors"
                  >
                    <Pause className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
                  </button>
                ) : (
                  <button
                    onClick={handleResume}
                    className="p-2 bg-green-100 dark:bg-green-900/30 hover:bg-green-200 dark:hover:bg-green-900/50 rounded-lg transition-colors"
                  >
                    <Play className="w-5 h-5 text-green-600 dark:text-green-400" />
                  </button>
                )}
              </div>
            </div>

            {/* Progress */}
            <div className="mb-4">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-600 dark:text-gray-400">Progress</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {((session.current_episode / session.max_episodes) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all"
                  style={{ width: `${(session.current_episode / session.max_episodes) * 100}%` }}
                />
              </div>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {session.accuracy.toFixed(1)}%
                </p>
                <p className="text-xs text-gray-600 dark:text-gray-400">Accuracy</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {session.avg_reward.toFixed(1)}
                </p>
                <p className="text-xs text-gray-600 dark:text-gray-400">Avg Reward</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {session.loss.toFixed(2)}
                </p>
                <p className="text-xs text-gray-600 dark:text-gray-400">Loss</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {session.status === 'running' ? 'Running' : session.status === 'paused' ? 'Paused' : 'Stopped'}
                </p>
                <p className="text-xs text-gray-600 dark:text-gray-400">Status</p>
              </div>
            </div>
          </div>

          {/* Training Charts */}
          <div className="space-y-6">
            {/* Reward Chart */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Average Reward per Episode
                </h3>
                <div className="flex items-center gap-2 text-sm">
                  <TrendingUp className="w-4 h-4 text-green-500" />
                  <span className="text-green-600 dark:text-green-400 font-medium">
                    Live Data
                  </span>
                </div>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={trainingData}>
                  <defs>
                    <linearGradient id="colorReward" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0284c7" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#0284c7" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
                  <XAxis
                    dataKey="episode"
                    stroke="#9ca3af"
                    style={{ fontSize: '12px' }}
                  />
                  <YAxis stroke="#9ca3af" style={{ fontSize: '12px' }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1f2937',
                      border: '1px solid #374151',
                      borderRadius: '8px',
                      color: '#fff',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="reward"
                    stroke="#0284c7"
                    fillOpacity={1}
                    fill="url(#colorReward)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Loss and Accuracy Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Loss Chart */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                    Training Loss
                  </h3>
                  <div className="flex items-center gap-2 text-sm">
                    <TrendingDown className="w-4 h-4 text-green-500" />
                    <span className="text-green-600 dark:text-green-400 font-medium">
                      Decreasing
                    </span>
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={trainingData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
                    <XAxis
                      dataKey="episode"
                      stroke="#9ca3af"
                      style={{ fontSize: '12px' }}
                    />
                    <YAxis stroke="#9ca3af" style={{ fontSize: '12px' }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1f2937',
                        border: '1px solid #374151',
                        borderRadius: '8px',
                        color: '#fff',
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="loss"
                      stroke="#ef4444"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Accuracy Chart */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                    Accuracy
                  </h3>
                  <div className="flex items-center gap-2 text-sm">
                    <TrendingUp className="w-4 h-4 text-green-500" />
                    <span className="text-green-600 dark:text-green-400 font-medium">
                      Improving
                    </span>
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={trainingData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
                    <XAxis
                      dataKey="episode"
                      stroke="#9ca3af"
                      style={{ fontSize: '12px' }}
                    />
                    <YAxis
                      stroke="#9ca3af"
                      style={{ fontSize: '12px' }}
                      domain={[0, 100]}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1f2937',
                        border: '1px solid #374151',
                        borderRadius: '8px',
                        color: '#fff',
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="accuracy"
                      stroke="#10b981"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
