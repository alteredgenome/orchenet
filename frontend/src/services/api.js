/**
 * API service for communicating with OrcheNet backend
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const deviceAPI = {
  getAll: () => api.get('/api/devices'),
  getById: (id) => api.get(`/api/devices/${id}`),
  create: (device) => api.post('/api/devices', device),
  update: (id, device) => api.put(`/api/devices/${id}`, device),
  delete: (id) => api.delete(`/api/devices/${id}`),
  updateConfig: (id, config) => api.put(`/api/devices/${id}/config`, config),
}

export const taskAPI = {
  getAll: () => api.get('/api/tasks'),
  getByDeviceId: (deviceId) => api.get(`/api/tasks/device/${deviceId}`),
  getById: (id) => api.get(`/api/tasks/${id}`),
}

export default api
