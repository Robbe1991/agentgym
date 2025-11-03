/**
 * API Client for AgentGym Backend
 * Handles all HTTP requests to the FastAPI backend
 */

const API_BASE_URL = '/api'

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`

  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error)
    throw error
  }
}

/**
 * Scenarios API
 */
export const scenariosAPI = {
  getAll: () => fetchAPI('/scenarios'),
  getById: (id) => fetchAPI(`/scenarios/${id}`),
}

/**
 * Training API
 */
export const trainingAPI = {
  start: (params) => fetchAPI('/training/start', {
    method: 'POST',
    body: JSON.stringify(params),
  }),
  getStatus: (sessionId) => fetchAPI(`/training/${sessionId}`),
  getAll: () => fetchAPI('/training'),
  pause: (sessionId) => fetchAPI(`/training/${sessionId}/pause`, {
    method: 'POST',
  }),
  resume: (sessionId) => fetchAPI(`/training/${sessionId}/resume`, {
    method: 'POST',
  }),
  stop: (sessionId) => fetchAPI(`/training/${sessionId}/stop`, {
    method: 'POST',
  }),
}

/**
 * Models API
 */
export const modelsAPI = {
  getAll: () => fetchAPI('/models'),
  getById: (id) => fetchAPI(`/models/${id}`),
  delete: (id) => fetchAPI(`/models/${id}`, {
    method: 'DELETE',
  }),
}

/**
 * Settings API
 */
export const settingsAPI = {
  get: () => fetchAPI('/settings'),
  update: (settings) => fetchAPI('/settings', {
    method: 'PUT',
    body: JSON.stringify(settings),
  }),
}

/**
 * WebSocket connection for real-time training updates
 */
export function connectToTrainingWebSocket(sessionId, onUpdate) {
  const ws = new WebSocket(`ws://localhost:8001/ws/training/${sessionId}`)

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    onUpdate(data)
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }

  ws.onclose = () => {
    console.log('WebSocket connection closed')
  }

  return ws
}
