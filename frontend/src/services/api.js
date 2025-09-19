import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('API Response Error:', error)
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'Server error'
      throw new Error(`${error.response.status}: ${message}`)
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network error: No response from server')
    } else {
      // Something else happened
      throw new Error(`Request error: ${error.message}`)
    }
  }
)

export const apiService = {
  // Health check
  async healthCheck() {
    const response = await api.get('/health')
    return response.data
  },

  // Run simulation or live execution
  async runSimulation(query, simulate = false, systemPrompt = null, runId = null) {
    const response = await api.post('/run/simulate', {
      query,
      simulate,
      system_prompt: systemPrompt,
      run_id: runId
    })
    return response.data
  },

  // Get telemetry data for a specific run
  async getTelemetry(runId) {
    const response = await api.get(`/telemetry/${runId}`)
    return response.data
  },

  // List all runs
  async listRuns() {
    const response = await api.get('/runs')
    return response.data
  },

  // Generate sample data
  async generateSampleData(count = 5) {
    const response = await api.post('/generate-sample-data', null, {
      params: { count }
    })
    return response.data
  },

  // Delete a run
  async deleteRun(runId) {
    const response = await api.delete(`/telemetry/${runId}`)
    return response.data
  }
}

export default apiService
