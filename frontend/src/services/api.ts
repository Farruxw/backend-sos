import axios from 'axios'
import type { CallDetail, EmergencyCall, ChatMessage, NewCall } from '../types/api'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' }
})
api.interceptors.response.use(r => r, error => Promise.reject(new Error(
  error.response?.data?.detail || error.message || 'Server bilan aloqa uzildi'
)))

export const callsApi = {
  create: (data: NewCall) => api.post<EmergencyCall>('/api/calls', data).then(r => r.data),
  active: () => api.get<EmergencyCall[]>('/api/calls/active').then(r => r.data),
  detail: (id: number) => api.get<CallDetail>(`/api/calls/${id}`).then(r => r.data),
  assign: (id: number) => api.post<EmergencyCall>(`/api/calls/${id}/assign`).then(r => r.data),
  reassign: (id: number) => api.post<EmergencyCall>(`/api/calls/${id}/reassign`).then(r => r.data),
  arrive: (id: number) => api.post<EmergencyCall>(`/api/calls/${id}/arrive`).then(r => r.data),
  done: (id: number) => api.post<EmergencyCall>(`/api/calls/${id}/done`).then(r => r.data),
  cancel: (id: number) => api.post<EmergencyCall>(`/api/calls/${id}/cancel`).then(r => r.data)
}
export const chatApi = {
  history: (specialty: string) => api.get<ChatMessage[]>(`/api/chat/${encodeURIComponent(specialty)}`).then(r => r.data),
  send: (specialty: string, text: string) => api.post<ChatMessage>(`/api/chat/${encodeURIComponent(specialty)}`, { text }).then(r => r.data)
}
