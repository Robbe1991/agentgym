import { Link, useLocation } from 'react-router-dom'
import {
  Home,
  BookOpen,
  Play,
  Database,
  Settings,
  Activity,
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', to: '/', icon: Home },
  { name: 'Scenarios', to: '/scenarios', icon: BookOpen },
  { name: 'Training', to: '/training', icon: Play },
  { name: 'Models', to: '/models', icon: Database },
  { name: 'Settings', to: '/settings', icon: Settings },
]

export default function Layout({ children }) {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-6 border-b border-gray-200 dark:border-gray-700">
          <Activity className="w-8 h-8 text-primary-600" />
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              AgentGym
            </h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              AI Agent Training
            </p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="px-3 py-4 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.to
            const Icon = item.icon

            return (
              <Link
                key={item.name}
                to={item.to}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/50 dark:text-primary-300'
                    : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
              >
                <Icon className="w-5 h-5" />
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            Version 0.1.0
          </p>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="min-h-screen">{children}</main>
      </div>
    </div>
  )
}
