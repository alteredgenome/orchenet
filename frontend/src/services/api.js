/**
 * API service for communicating with OrcheNet backend
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT || 30000

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for error handling
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Response Error:', error.response.status, error.response.data)
    } else if (error.request) {
      // No response received
      console.error('API No Response:', error.message)
    } else {
      // Request setup error
      console.error('API Request Setup Error:', error.message)
    }
    return Promise.reject(error)
  }
)

// Device API
export const deviceAPI = {
  getAll: (params = {}) => api.get('/api/devices', { params }),
  getById: (id) => api.get(`/api/devices/${id}`),
  create: (device) => api.post('/api/devices', device),
  update: (id, device) => api.put(`/api/devices/${id}`, device),
  delete: (id) => api.delete(`/api/devices/${id}`),
  updateConfig: (id, config) => api.put(`/api/devices/${id}/config`, config),
}

// Task API
export const taskAPI = {
  getAll: (params = {}) => api.get('/api/tasks', { params }),
  getByDeviceId: (deviceId) => api.get(`/api/tasks`, { params: { device_id: deviceId } }),
  getById: (id) => api.get(`/api/tasks/${id}`),
  create: (task) => api.post('/api/tasks', task),
  update: (id, task) => api.put(`/api/tasks/${id}`, task),
  delete: (id) => api.delete(`/api/tasks/${id}`),
  retry: (id) => api.post(`/api/tasks/${id}/retry`),
}

// Check-in API
export const checkinAPI = {
  checkin: (data) => api.post('/api/checkin', data),
  submitResult: (taskId, result) => api.post(`/api/checkin/result/${taskId}`, result),
  getPending: (deviceId) => api.get(`/api/checkin/pending/${deviceId}`),
}

// Health API
export const healthAPI = {
  check: () => api.get('/health'),
  root: () => api.get('/'),
}

export default api
